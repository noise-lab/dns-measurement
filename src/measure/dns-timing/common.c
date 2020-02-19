#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "common.h"

uint64_t nanosec_since(struct timespec since) {
	struct timespec now;
	clock_gettime(CLOCK_MONOTONIC_RAW, &now);

	uint64_t elapsed = (now.tv_sec - since.tv_sec) * 1000000000
		+ (now.tv_nsec - since.tv_nsec);
	return elapsed;
}

void print_ok(char *domain, uint64_t nanosec, size_t size) {
	printf("ok,%s,%lf,%zu\n", domain, nanosec / 1e6, size);
}

void print_error(char *domain, uint64_t nanosec, int status) {
	printf("error,%s,%lf,%d\n", domain, nanosec / 1e6, status);
}

/* vim: set noet tw=100 ts=4 sw=4: */
