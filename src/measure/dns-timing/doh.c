#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "common.h"
#include "doh.h"

static size_t doh_callback(void *contents, size_t size, size_t nmemb, void *userp) {
	size_t realsize = size * nmemb;

	doh_query_t *query = (doh_query_t*)userp;

	debug("respone_wire_fmt = %p\n\n", query->response_wire_fmt.memory);

	query->response_wire_fmt.memory = realloc(query->response_wire_fmt.memory,
			query->response_wire_fmt.size + realsize);
	if(NULL == query->response_wire_fmt.memory) {
		/* out of memory! */
		printf("not enough memory (realloc returned NULL): %zu\n", realsize);
		return 0;
	}

	query->elapsed = nanosec_since(query->time_start);

	memcpy(&(query->response_wire_fmt.memory[query->response_wire_fmt.size]), contents, realsize);
	query->response_wire_fmt.size += realsize;

	return realsize;
}

static size_t doh_encode(const char *host, int dnstype, unsigned char *dnsp, size_t len) {
	size_t hostlen = strlen(host);
	unsigned char *orig = dnsp;
	const char *hostp = host;

	if(len < (12 + hostlen + 4)) return DOH_TOO_SMALL_BUFFER;

	*dnsp++ = 0; /* 16 bit id */
	*dnsp++ = 0;
	*dnsp++ = 0x01; /* |QR|	Opcode  |AA|TC|RD| Set the RD bit */
	*dnsp++ = '\0'; /* |RA|	Z	 |	RCODE	|					 */
	*dnsp++ = '\0';
	*dnsp++ = 1;	 /* QDCOUNT (number of entries in the question section) */
	*dnsp++ = '\0';
	*dnsp++ = '\0'; /* ANCOUNT */
	*dnsp++ = '\0';
	*dnsp++ = '\0'; /* NSCOUNT */
	*dnsp++ = '\0';
	*dnsp++ = '\0'; /* ARCOUNT */

	/* store a QNAME */
	do {
		char *dot = strchr(hostp, '.');
		size_t labellen;
		bool found = false;

		if(dot) {
			found = true;
			labellen = dot - hostp;
		} else {
			labellen = strlen(hostp);
		}

		if(labellen > 63) return DOH_DNS_BAD_LABEL; /* too long label, error out */

		*dnsp++ = (unsigned char)labellen;
		memcpy(dnsp, hostp, labellen);
		dnsp += labellen;
		hostp += labellen + 1;
		if(!found) {
			*dnsp++ = 0; /* terminating zero */
			break;
		}
	} while(1);

	*dnsp++ = '\0'; /* upper 8 bit TYPE */
	*dnsp++ = (unsigned char)dnstype;
	*dnsp++ = '\0'; /* upper 8 bit CLASS */
	*dnsp++ = DNS_CLASS_IN; /* IN - "the Internet" */

	return dnsp - orig;
}

static DOHcode skipqname(unsigned char *doh, size_t dohlen, unsigned int *indexp) {
	unsigned char length;
	do {
		if(dohlen < (*indexp + 1)) return DOH_DNS_OUT_OF_RANGE;

		length = doh[*indexp];
		if((length & 0xc0) == 0xc0) {
			/* name pointer, advance over it and be done */
			if(dohlen < (*indexp + 2)) return DOH_DNS_OUT_OF_RANGE;
			*indexp += 2;
			break;
		}
		if(length & 0xc0) return DOH_DNS_BAD_LABEL;
		if(dohlen < (*indexp + 1 + length)) return DOH_DNS_OUT_OF_RANGE;

		*indexp += 1 + length;
	} while (length);
	return DOH_OK;
}

static unsigned short get16bit(unsigned char *doh, int index) {
	return ((doh[index] << 8) | doh[index + 1]);
}

static unsigned int get32bit(unsigned char *doh, int index) {
	return (doh[index] << 24) | (doh[index+1] << 16) | (doh[index+2] << 8) | doh[index+3];
}

static DOHcode store_a(unsigned char *doh, int index, struct dnsentry *d) {
	/* this function silently ignore address over the limit */
	if(d->numv4 < MAX_ADDR) {
		unsigned int *inetp = &d->v4addr[d->numv4++];
		*inetp = get32bit(doh, index);
	}
	return DOH_OK;
}

static DOHcode store_aaaa(unsigned char *doh, int index, struct dnsentry *d) {
	/* this function silently ignore address over the limit */
	if(d->numv6 < MAX_ADDR) {
		struct addr6 *inet6p = &d->v6addr[d->numv6++];
		memcpy(inet6p, &doh[index], 16);
	}
	return DOH_OK;
}

static DOHcode cnameappend(struct cnamestore *c, unsigned char *src, size_t len) {
	if(!c->alloc) {
		c->allocsize = len + 1;
		c->alloc = malloc(c->allocsize);
		if(!c->alloc) return DOH_OUT_OF_MEM;
	} else if(c->allocsize < (c->allocsize + len + 1)) {
		char *ptr;
		c->allocsize += len + 1;
		ptr = realloc(c->alloc, c->allocsize);
		if(!ptr) {
			free(c->alloc);
			return DOH_OUT_OF_MEM;
		}
		c->alloc = ptr;
	}
	memcpy(&c->alloc[c->len], src, len);
	c->len += len;
	c->alloc[c->len]=0; /* keep it zero terminated */
	return DOH_OK;
}

static DOHcode store_cname(unsigned char *doh, size_t dohlen, unsigned int index,
		struct dnsentry *d) {
	if(d->numcname == MAX_ADDR) return DOH_OK; /* skip! */

	struct cnamestore *c = &d->cname[d->numcname++];
	unsigned int loop = 128; /* a valid DNS name can never loop this much */
	unsigned char length;
	do {
		if(index >= dohlen) return DOH_DNS_OUT_OF_RANGE;

		length = doh[index];
		if((length & 0xc0) == 0xc0) {
			unsigned short newpos;
			/* name pointer, get the new offset (14 bits) */
			if((index +1) >= dohlen) return DOH_DNS_OUT_OF_RANGE;

			/* move to the the new index */
			newpos = (length & 0x3f) << 8 | doh[index+1];
			index = newpos;

			continue;
		} else if(length & 0xc0) {
			return DOH_DNS_BAD_LABEL; /* bad input */
		} else {
			index++;
		}

		if(length) {
			DOHcode rc;
			if(c->len) {
				rc = cnameappend(c, (unsigned char *)".", 1);
				if(rc) return rc;
			}

			if((index + length) > dohlen) return DOH_DNS_BAD_LABEL;

			rc = cnameappend(c, &doh[index], length);
			if(rc) return rc;
			index += length;
		}
	} while (length && --loop);

	if(!loop) return DOH_DNS_CNAME_LOOP;

	return DOH_OK;
}

static DOHcode rdata(unsigned char *doh, size_t dohlen, unsigned short rdlength,
		unsigned short type, int index, struct dnsentry *d) {
	/* RDATA
	- A (TYPE 1):  4 bytes
	- AAAA (TYPE 28): 16 bytes
	- NS (TYPE 2): N bytes */
	DOHcode rc;

	switch(type) {
		case DNS_TYPE_A:
			if(rdlength != 4) return DOH_DNS_RDATA_LEN;
			rc = store_a(doh, index, d);
			if(rc) return rc;
			break;
		case DNS_TYPE_AAAA:
			if(rdlength != 16) return DOH_DNS_RDATA_LEN;
			rc = store_aaaa(doh, index, d);
			if(rc) return rc;
			break;
		case DNS_TYPE_CNAME:
			rc = store_cname(doh, dohlen, index, d);
			if(rc) return rc;
			break;
		default:
			/* unsupported type, just skip it */
			break;
	}
	return DOH_OK;
}

static DOHcode doh_decode(unsigned char *doh, size_t dohlen, int dnstype, struct dnsentry *d) {
	unsigned char rcode;
	unsigned short qdcount;
	unsigned short ancount;
	unsigned short type=0;
	unsigned short class;
	unsigned short rdlength;
	unsigned short nscount;
	unsigned short arcount;
	unsigned int index = 12;
	DOHcode rc;

	if(dohlen < 12 || doh[0] || doh[1]) return DOH_DNS_MALFORMAT; /* too small or bad ID */
	rcode = doh[3] & 0x0f;
	if(rcode) return DOH_DNS_BAD_RCODE; /* bad rcode */

	qdcount = get16bit(doh, 4);
	while (qdcount) {
		rc = skipqname(doh, dohlen, &index);
		if(rc) return rc; /* bad qname */
		if(dohlen < (index + 4)) return DOH_DNS_OUT_OF_RANGE;
		index += 4; /* skip question's type and class */
		qdcount--;
	}

	ancount = get16bit(doh, 6);
	while (ancount) {
		unsigned int ttl;

		rc = skipqname(doh, dohlen, &index);
		if(rc) return rc; /* bad qname */
		if(dohlen < (index + 2)) return DOH_DNS_OUT_OF_RANGE;

		type = get16bit(doh, index);
		/* Not the same type as was asked for nor CNAME */
		if((type != DNS_TYPE_CNAME) && (type != dnstype)) return DOH_DNS_UNEXPECTED_TYPE;
		index += 2;

		if(dohlen < (index + 2)) return DOH_DNS_OUT_OF_RANGE;

		class = get16bit(doh, index);
		if(DNS_CLASS_IN != class) return DOH_DNS_UNEXPECTED_CLASS; /* unsupported */
		index += 2;

		if(dohlen < (index + 4)) return DOH_DNS_OUT_OF_RANGE;

		ttl = get32bit(doh, index);
		if(ttl < d->ttl) d->ttl = ttl;
		index += 4;

		if(dohlen < (index + 2)) return DOH_DNS_OUT_OF_RANGE;

		rdlength = get16bit(doh, index);
		index += 2;

		if(dohlen < (index + rdlength)) return DOH_DNS_OUT_OF_RANGE;

		rc = rdata(doh, dohlen, rdlength, type, index, d);
		if(rc) return rc; /* bad rdata */

		index += rdlength;
		ancount--;
	}

	nscount = get16bit(doh, 8);
	while (nscount) {
		rc = skipqname(doh, dohlen, &index);
		if(rc) return rc; /* bad qname */

		if(dohlen < (index + 8)) return DOH_DNS_OUT_OF_RANGE;

		index += 2; /* type */
		index += 2; /* class */
		index += 4; /* ttl */

		if(dohlen < (index + 2)) return DOH_DNS_OUT_OF_RANGE;

		rdlength = get16bit(doh, index);
		index += 2;

		if(dohlen < (index + rdlength)) return DOH_DNS_OUT_OF_RANGE;

		index += rdlength;
		nscount--;
	}

	arcount = get16bit(doh, 10);
	while (arcount) {
		rc = skipqname(doh, dohlen, &index);
		if(rc) return rc; /* bad qname */

		if(dohlen < (index + 8)) return DOH_DNS_OUT_OF_RANGE;

		index += 2; /* type */
		index += 2; /* class */
		index += 4; /* ttl */

		rdlength = get16bit(doh, index);
		index += 2;

		if(dohlen < (index + rdlength)) return DOH_DNS_OUT_OF_RANGE;

		index += rdlength;
		arcount--;
	}

	if(index != dohlen) return DOH_DNS_MALFORMAT;

	if((type != DNS_TYPE_NS) && !d->numcname && !d->numv6 && !d->numv4) return DOH_NO_CONTENT;

	return DOH_OK;
}

static void doh_init(struct dnsentry *d) {
	memset(d, 0, sizeof(struct dnsentry));
	d->ttl = ~0u; /* default to max */
}

static void doh_cleanup(struct dnsentry *d) {
	int i = 0;
	for(i=0; i< d->numcname; i++) {
		free(d->cname[i].alloc);
	}
}

static int doh_query_init(doh_query_t *query, char *domain, const char *recursor,
		struct curl_slist *headers) {
	query->domain = domain;
	query->query_wire_fmt.memory = malloc(DOH_QUERY_WIRE_FMT_SIZE);
	if(NULL == query->query_wire_fmt.memory) {
		fprintf(stderr, "malloc query_wire_fmt failed");
		return 1;
	}
	query->query_wire_fmt.size = doh_encode(domain, DNS_TYPE_A,
		query->query_wire_fmt.memory, DOH_QUERY_WIRE_FMT_SIZE);
	if(!query->query_wire_fmt.size) {
		fprintf(stderr, "Failed to encode DoH packet\n");
		return 2;
	}

	query->response_wire_fmt.memory = malloc(1);
	if(NULL == query->response_wire_fmt.memory) {
		fprintf(stderr, "malloc response_wire_fmt failed");
		return 1;
	}
	query->response_wire_fmt.size = 0;

	clock_gettime(CLOCK_MONOTONIC_RAW, &query->time_start);

	query->curl = curl_easy_init();
	if(query->curl) {
		curl_easy_setopt(query->curl, CURLOPT_WRITEFUNCTION, doh_callback);
		curl_easy_setopt(query->curl, CURLOPT_WRITEDATA, (void *)query);
		curl_easy_setopt(query->curl, CURLOPT_URL, recursor);
		curl_easy_setopt(query->curl, CURLOPT_USERAGENT, "curl-doh/1.0");
		curl_easy_setopt(query->curl, CURLOPT_POSTFIELDS, query->query_wire_fmt.memory);
		curl_easy_setopt(query->curl, CURLOPT_POSTFIELDSIZE, query->query_wire_fmt.size);
		curl_easy_setopt(query->curl, CURLOPT_HTTPHEADER, headers);
		curl_easy_setopt(query->curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
		curl_easy_setopt(query->curl, CURLOPT_PRIVATE, query);
		curl_easy_setopt(query->curl, CURLOPT_FOLLOWLOCATION, 1L);
		curl_easy_setopt(query->curl, CURLOPT_PIPEWAIT, 1L);
	} else {
		return 3;
	}

	return 0;
}

int doh(const char *recursor, char *domains[], uint16_t domains_count) {
	curl_global_init(CURL_GLOBAL_ALL);

	struct curl_slist *headers = curl_slist_append(NULL, "Content-Type: application/dns-message");
	headers = curl_slist_append(headers, "Accept: application/dns-message");

	CURLM *multi = curl_multi_init();
	curl_multi_setopt(multi, CURLMOPT_PIPELINING, CURLPIPE_MULTIPLEX);

	int still_running;

	for(int i = 0; i < domains_count; ++i) {
		doh_query_t *query = malloc(sizeof(doh_query_t));
		if(NULL == query) {
			fprintf(stderr, "Unable to allocate memory for doh_query_t\n");
			return 1;
		}
		bzero(query, sizeof(doh_query_t));

		doh_query_init(query, domains[i], recursor, headers);
		curl_multi_add_handle(multi, query->curl);
		debug("Scheduled query for domain %s\n", query->domain);

		if(0 == i) {
			/* Simulate browser issuing the initial request first */
			curl_multi_perform(multi, &still_running);
		}
	}

	curl_multi_perform(multi, &still_running);

	struct dnsentry d;
	doh_init(&d);
	do {
		int num_fds;

		CURLMcode mc = curl_multi_wait(multi, NULL, 0, 1000, &num_fds);

		if(mc != CURLM_OK) {
			fprintf(stderr, "curl_multi_wait() failed, code %d.\n", mc);
			break;
		}

		/* 'numfds' being zero means either a timeout or no file descriptors to
		wait for. Try timeout on first occurrence, then assume no file
		descriptors and no file descriptors to wait for means wait for 100
		milliseconds. */

		curl_multi_perform(multi, &still_running);

		CURLMsg *msg;
		int r, queued;
		while((msg = curl_multi_info_read(multi, &queued))) {
			if(msg->msg == CURLMSG_DONE) {
				doh_query_t *query;
				CURL *easy = msg->easy_handle;
				curl_easy_getinfo(easy, CURLINFO_PRIVATE, &query);

				/* Check for errors */
				if(msg->data.result == CURLE_OK) {
					long response_code;
					curl_easy_getinfo(easy, CURLINFO_RESPONSE_CODE, &response_code);
					if((response_code / 100 ) == 2) {
						r = doh_decode(query->response_wire_fmt.memory,
							query->response_wire_fmt.size,
							DNS_TYPE_A, &d);
						if(r == DOH_DNS_BAD_RCODE) {
							print_error(query->domain, nanosec_since(query->time_start), r);
						} else if(r) {
							fprintf(stderr, "Problem %d decoding %zu bytes response to probe\n",
								r, query->response_wire_fmt.size);
						} else {
							print_ok(query->domain, query->elapsed, query->response_wire_fmt.size);
						}
					} else {
						fprintf(stderr, "Query got response: %03ld\n", response_code);
					}
					free(query->response_wire_fmt.memory);
					query->response_wire_fmt.memory = NULL;
					query->response_wire_fmt.size = 0;
				} else {
					fprintf(stderr, "Query failed: %s\n", curl_easy_strerror(msg->data.result));
				}

				free(query->query_wire_fmt.memory);
				query->query_wire_fmt.memory = NULL;
				query->query_wire_fmt.size = 0;

				curl_multi_remove_handle(multi, easy);
				curl_easy_cleanup(easy);

				free(query);
			}
		}
	} while(still_running);

	doh_cleanup(&d);

	curl_slist_free_all(headers);
	curl_multi_cleanup(multi);
	curl_global_cleanup();
	return 0;
}

/* vim: set noet tw=100 ts=4 sw=4: */
