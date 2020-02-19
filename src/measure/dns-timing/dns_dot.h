#include <stdint.h>
#include <time.h>


typedef struct {
	char *domain;
	struct timespec time_start;
} dns_dot_query_t;

int dns_dot(bool dns_over_tls, char *resolver, char *domains[], uint16_t domains_count);
int dns_dot_sync(bool dns_over_tls, char *resolver, char *domains[], uint16_t domains_count);

/* vim: set noet tw=100 ts=4 sw=4: */
