#include <stdint.h>
#include <time.h>

enum protocol_t { Do53, Do53sync, DoT, DoH };

uint64_t nanosec_since(struct timespec since);
void print_ok(char *domain, uint64_t nanosec, size_t size);
void print_ok1(const char *recursor, char *domain, uint64_t nanosec, size_t size, char *buf);
void print_error(char *domain, uint64_t nanosec, int status);
void print_error1(const char *recursor, char *domain, uint64_t nanosec, int status, char *buf);
#ifndef DEBUG
#define DEBUG 0
#endif

#ifndef DEBUG_LIBEVENT
#define DEBUG_LIBEVENT 0
#endif

#ifndef FAILERROR
#define FAILERROR 0
#endif

#define debug(fmt, ...) \
	do { \
		if(DEBUG) { \
			fprintf(stderr, "%s:%d:%s(): " fmt, __FILE__, __LINE__, __func__, __VA_ARGS__); \
		} \
	} while(0);

/* vim: set noet tw=100 ts=4 sw=4: */
