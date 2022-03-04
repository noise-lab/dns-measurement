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
	char *recursor_arg_filename = argv[2];/* File to contain resolvers (Ranya) */
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
	/* Adding code to  parse through the file of resolvers (Ranya) */
	FILE *recursor_file = fopen(recursor_arg_filename, "r");
	if(NULL == recursor_file) {
		fprintf(stderr, "Unable to read file %s: ", recursor_arg_filename);
		perror(NULL);
		exit(EXIT_FAILURE);
	}

	size_t recursors_count = 0, recursors_allocated = 512;
	char **recursors = calloc(recursors_allocated, sizeof(char*));
	if(NULL == recursors) {
		perror("Unable to allocate memory for domain names");
		exit(errno);
	}
	debug("recursors = %p\n", recursors);


	while(!feof(recursor_file) && !ferror(recursor_file)) {
		/* Need more space? */
		if(recursors_count == recursors_allocated) {
			recursors_allocated += 512;
			recursors = realloc(recursors, recursors_allocated * sizeof(char*));
			if(NULL == recursors) {
				debug("recursors = %p\n", recursors);
				perror("Unable to realloc recursors\n");
				exit(errno);
			}
		}

		size_t line_capacity = 0;
		char *line = NULL;

		ssize_t line_length = getline(&line, &line_capacity, recursor_file);

		if(-1 == line_length && !feof(recursor_file)) {
			perror("Unable to read line");
			exit(errno);
		}
		recursors[recursors_count++] = strndup(line, line_length - 1);
	}
	--recursors_count;
	debug("len(recursors) = %zu\n", recursors_count);

	/* Shorten resolvers list */
	recursors = realloc(recursors, recursors_count * sizeof(char*));
	if(NULL == recursors) {
		perror("Unable to realloc recursors");
		exit(ENOMEM);
	}

	fclose(recursor_file);/* Done reading resolvers (Ranya) */

	int i;/* Iterate through each resolver in file (Ranya) */

	struct timespec time_start;
	clock_gettime(CLOCK_MONOTONIC_RAW, &time_start);

	for (i=0;i<recursors_count;i++) { /* Run the timing for each resolver in file (Ranya) */
	        switch(protocol) {
	        	case Do53:
	        		r = dns_dot(false, recursors[i], domains, domains_count);
	        		break;
	        	case Do53sync:
	        		r = dns_dot_sync(false, recursors[i], domains, domains_count);
	        		break;
	        	case DoT:
	        		r = dns_dot(true, recursors[i], domains, domains_count);
	        		break;
	        	case DoH:
	        		r = doh(recursors[i], domains, domains_count);
	        		break;
	        	default:
	        		/* This should be unreachable */
	        		fprintf(stderr, "Invalid protocol type %d\n", protocol);
	        		exit(EXIT_FAILURE);
	        }
	}
	print_ok("total_run_time", nanosec_since(time_start), 0);

	exit(r);
}

/* vim: set noet tw=100 ts=4 sw=4: */
