#include <arpa/inet.h>
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>

#include <event2/event.h>
#include <getdns/getdns.h>
#include <getdns/getdns_ext_libevent.h>

#include "common.h"
#include "dns_dot.h"

int dns_dot_sync(bool dns_over_tls, char *resolver, char *domains[], uint16_t domains_count) {
	/* getaddrinfo with resolver */
	int r = 0;
	const struct addrinfo hints = {
		.ai_family = PF_INET,
		.ai_socktype = SOCK_DGRAM,
	};
	struct addrinfo *addr;
	struct timespec time_start;
	for(int i = 0; i < domains_count; ++i) {
		clock_gettime(CLOCK_MONOTONIC_RAW, &time_start);
		r = getaddrinfo(domains[i], NULL, &hints, &addr);
		if(0 == r) {
			print_ok(domains[i], nanosec_since(time_start), 0);
		} else {
			print_error(domains[i], nanosec_since(time_start), r);
		}
		freeaddrinfo(addr);
	}
	return 0;
}

void libevent_debug(int severity, const char *msg) {
	debug("DEBUG\tlibevent %d %s\n", severity, msg);
}

void dns_dot_callback(getdns_context *context, getdns_callback_type_t callback_type,
		getdns_dict *response, void *userarg, getdns_transaction_t transaction_id) {
	switch(callback_type) {
		case GETDNS_CALLBACK_CANCEL:
			debug("Transaction with ID %"PRIu64" was cancelled.\n", transaction_id);
			return;
		case GETDNS_CALLBACK_TIMEOUT:
			debug("Transaction with ID %"PRIu64" timed out.\n", transaction_id);
			return;
		case GETDNS_CALLBACK_ERROR:
			debug("An error occurred for transaction ID %"PRIu64".\n", transaction_id);
			return;
		default:
			break;
	}
	assert(callback_type == GETDNS_CALLBACK_COMPLETE);

	dns_dot_query_t *query = (dns_dot_query_t*)userarg;

	uint32_t status;
	getdns_return_t r = getdns_dict_get_int(response, "status", &status);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Could not get \"status\" from response\n");
		goto failure;
	}

	if(GETDNS_RESPSTATUS_GOOD != status) {
		print_error(query->domain, nanosec_since(query->time_start), status);
		debug("The search had no results, and a return value of %"PRIu32".\n", status);
#if FAILERROR
		goto failure;
#endif
	} else {
		uint8_t *wire = NULL;
		size_t wire_sz = 0;
		r = getdns_msg_dict2wire(response, &wire, &wire_sz);
		if(GETDNS_RETURN_GOOD != r) {
			fprintf(stderr, "Unable to convert to wire format: %s\n", getdns_get_errorstr_by_id(r));
			goto failure;
		}
		print_ok(query->domain, nanosec_since(query->time_start), wire_sz);
		free(wire);
	}
	free(query);

	debug("response = %s\n", getdns_pretty_print_dict(response));

failure:
	getdns_dict_destroy(response);
}

int dns_dot(bool dns_over_tls, char *resolver, char *domains[], uint16_t domains_count) {
	getdns_return_t r;
	getdns_transport_t transport = dns_over_tls
		? GETDNS_TRANSPORT_TLS_ONLY_KEEP_CONNECTIONS_OPEN
		: GETDNS_TRANSPORT_UDP_ONLY;

	/* Set the upstream resolver */
	getdns_list *upstream_list = getdns_list_create();
	getdns_dict *upstream_dict = getdns_dict_create();

	char upstream_resolver[4] = "";
	if(-1 == inet_pton(AF_INET, resolver, &upstream_resolver)) {
		fprintf(stderr, "Unable to convert upstream resolver to network format\n");
		goto failure;
	}
	uint16_t tls_port = htons(853);

	const getdns_bindata address_data = {4, (uint8_t*) upstream_resolver};
	const getdns_bindata tls_port_b = {2, (uint8_t*) &tls_port};

	r = getdns_dict_set_bindata(upstream_dict, "address_data", &address_data);
	if(GETDNS_RETURN_GOOD != r) goto failure_getdns;

	r = getdns_dict_set_bindata(upstream_dict, "tls_port", &tls_port_b);
	if(GETDNS_RETURN_GOOD != r) goto failure_getdns;

	r = getdns_list_set_dict(upstream_list, 0, upstream_dict);
	if(GETDNS_RETURN_GOOD != r) goto failure_getdns;

	debug("upstream_resolvers = %s\n", getdns_pretty_print_list(upstream_list));

	getdns_context *context = NULL;
	r = getdns_context_create(&context, 0);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Trying to create the context failed\n");
		goto failure_getdns;
	}

	r = getdns_context_set_upstream_recursive_servers(context, upstream_list);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Error setting upstream resolvers\n");
		goto failure_getdns;
	}

	r = getdns_context_set_limit_outstanding_queries(context, 0);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Error setting maximum outstanding queries\n");
		goto failure_getdns;
	}

	r = getdns_context_set_timeout(context, 10000);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Error setting the TLS timeout\n");
		goto failure_getdns;
	}

	r = getdns_context_set_dns_transport(context, transport);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Error setting the transport for DNS lookups\n");
		goto failure_getdns;
	}

#if DEBUG_LIBEVENT
	fprintf(stderr, "libevent %s\n", event_get_version());
	event_enable_debug_mode();
	event_enable_debug_logging(EVENT_DBG_ALL);
	event_set_log_callback(libevent_debug);
#endif
	struct event_base* event_base = event_base_new();
	if(NULL == event_base) {
		fprintf(stderr, "Trying to create the event base failed.\n");
		goto failure;
	}

	r = getdns_extension_set_libevent_base(context, event_base);
	if(GETDNS_RETURN_GOOD != r) {
		fprintf(stderr, "Setting the event base failed\n");
		goto failure_getdns;
	}

	for(uint16_t i = 0; i < domains_count; ++i) {
		getdns_transaction_t txid;

		dns_dot_query_t *query = malloc(sizeof(dns_dot_query_t)); /* freed in the callback */
		if(NULL == query) {
			fprintf(stderr, "Unable to allocate memory for dns_dot_query_t");
			goto failure;
		}
		query->domain = domains[i];
		clock_gettime(CLOCK_MONOTONIC_RAW, &query->time_start);

		r = getdns_address(context, query->domain, NULL, query, &txid, dns_dot_callback);
		if(GETDNS_RETURN_GOOD != r) {
			fprintf(stderr, "Error scheduling asynchronous request: %s\n", getdns_get_errorstr_by_id(r));
		} else {
			debug("Scheduled query for domain %s\n", query->domain);
		}

		if(0 == i) {
			/* Simulate browser issuing the initial request first */
			switch(event_base_dispatch(event_base)) {
#if DEBUG
				case 1:
					fprintf(stderr, "No events pending or active\n");
					break;
				case 0:
					fprintf(stderr, "Dispatching events successful\n");
					break;
#endif
				case -1:
					fprintf(stderr, "Error dispatching events\n");
					break;
			}
		}
	}

	switch(event_base_dispatch(event_base)) {
#if DEBUG
		case 1:
			fprintf(stderr, "No events pending or active\n");
			break;
		case 0:
			fprintf(stderr, "Dispatching events successful\n");
			break;
#endif
		case -1:
			fprintf(stderr, "Error dispatching events\n");
			break;
	}

	if(event_base) event_base_free(event_base);
	if(context) getdns_context_destroy(context);

	return 0;

failure:
	return 1;

failure_getdns:
	fprintf(stderr, "getdns: %s", getdns_get_errorstr_by_id(r));
	return 2;
}

/* vim: set noet tw=100 ts=4 sw=4: */
