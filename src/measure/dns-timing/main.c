#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include "common.h"
#include "dns_dot.h"
#include "doh.h"


int main(int argc, char* argv[]) {
	debug("DEBUG enabled (%d)\n", DEBUG);

	if(!(argc == 4 || argc == 5)) {
		fprintf(stderr, "Usage: %s { { do53 | dot } RECURSOR | doh RECURSOR URL } FILE (%d)\n", argv[0], argc);
		exit(EINVAL);
	}

	char *protocol_arg = argv[1];
	char *recursor_arg = argv[2];
	char *filename_arg = argv[3];

	enum protocol_t protocol = Do53;
	if(0 == strcmp(protocol_arg, "do53") || 0 == strcmp(protocol_arg, "dns")) {
		protocol = Do53;
	} else if(0 == strcmp(protocol_arg, "do53sync")) {
		protocol = Do53sync;
	} else if(0 == strcmp(protocol_arg, "dot")) {
		protocol = DoT;
	} else if(0 == strcmp(protocol_arg, "doh")) {
		protocol = DoH;
	} else {
		fprintf(stderr, "Invalid protocol mode: %s\n", protocol_arg);
		exit(EXIT_FAILURE);
	}
	debug("Protocol: %s\n", protocol == Do53 ? "Plain DNS (Do53)" :
							protocol == DoT ? "DNS over TLS (DoT)" : "DNS over HTTPS (DoH)");

	int r = 0;

	FILE *file = fopen(filename_arg, "r");
	if(NULL == file) {
		fprintf(stderr, "Unable to read file %s: ", filename_arg);
		perror(NULL);
		exit(EXIT_FAILURE);
	}

	size_t domains_count = 0, domains_allocated = 512;
	char **domains = calloc(domains_allocated, sizeof(char*));
	if(NULL == domains) {
		perror("Unable to allocate memory for domain names");
		exit(errno);
	}
	debug("domains = %p\n", domains);


	while(!feof(file) && !ferror(file)) {
		/* Need more space? */
		if(domains_count == domains_allocated) {
			domains_allocated += 512;
			domains = realloc(domains, domains_allocated * sizeof(char*));
			if(NULL == domains) {
				debug("domains = %p\n", domains);
				perror("Unable to realloc domains\n");
				exit(errno);
			}
		}

		size_t line_capacity = 0;
		char *line = NULL;

		ssize_t line_length = getline(&line, &line_capacity, file);

		if(-1 == line_length && !feof(file)) {
			perror("Unable to read line");
			exit(errno);
		}
		domains[domains_count++] = strndup(line, line_length - 1);
	}
	--domains_count;
	debug("len(domains) = %zu\n", domains_count);

	/* Shorten domains list */
	domains = realloc(domains, domains_count * sizeof(char*));
	if(NULL == domains) {
		perror("Unable to realloc domains");
		exit(ENOMEM);
	}

	fclose(file);

	struct timespec time_start;
	clock_gettime(CLOCK_MONOTONIC_RAW, &time_start);
	switch(protocol) {
		case Do53:
			r = dns_dot(false, recursor_arg, domains, domains_count);
			break;
		case Do53sync:
			r = dns_dot_sync(false, recursor_arg, domains, domains_count);
			break;
		case DoT:
			r = dns_dot(true, recursor_arg, domains, domains_count);
			break;
		case DoH:
			r = doh(recursor_arg, domains, domains_count);
			break;
		default:
			/* This should be unreachable */
			fprintf(stderr, "Invalid protocol type %d\n", protocol);
			exit(EXIT_FAILURE);
	}
	print_ok("total_run_time", nanosec_since(time_start), 0);

	exit(r);
}

/* vim: set noet tw=100 ts=4 sw=4: */
