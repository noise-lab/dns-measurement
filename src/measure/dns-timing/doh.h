#include <curl/curl.h>

typedef struct {
	unsigned char *memory;
	size_t size;
} doh_varchar;

typedef struct {
	char *domain;
	struct timespec time_start;
	CURL *curl;
	doh_varchar query_wire_fmt;
	doh_varchar response_wire_fmt;
	uint64_t elapsed;
} doh_query_t;

#define DOH_QUERY_WIRE_FMT_SIZE 512

#define DNS_CLASS_IN 0x01

#define DNS_TYPE_A	  1
#define DNS_TYPE_NS	 2
#define DNS_TYPE_CNAME 5
#define DNS_TYPE_AAAA  28

#define MAX_ADDR 128

typedef enum {
	DOH_OK,
	DOH_DNS_BAD_LABEL,	 /* 1 */
	DOH_DNS_OUT_OF_RANGE, /* 2 */
	DOH_DNS_CNAME_LOOP,	/* 3 */
	DOH_TOO_SMALL_BUFFER, /* 4 */
	DOH_OUT_OF_MEM,		 /* 5 */
	DOH_DNS_RDATA_LEN,	 /* 6 */
	DOH_DNS_MALFORMAT,	 /* 7 - wrong size or bad ID */
	DOH_DNS_BAD_RCODE,	 /* 8 - no such name */
	DOH_DNS_UNEXPECTED_TYPE,  /* 9 */
	DOH_DNS_UNEXPECTED_CLASS, /* 10 */
	DOH_NO_CONTENT,			  /* 11 */
} DOHcode;

struct addr6 {
	unsigned char byte[16];
};

struct cnamestore {
	size_t len;		 /* length of cname */
	char *alloc;		/* allocated pointer */
	size_t allocsize; /* allocated size */
};

struct dnsentry {
	unsigned int ttl;
	int numv4;
	unsigned int v4addr[MAX_ADDR];
	int numv6;
	struct addr6 v6addr[MAX_ADDR];
	int numcname;
	struct cnamestore cname[MAX_ADDR];
};

int doh(const char *recursor, char *domains[], uint16_t domains_count);

/* vim: set noet tw=100 ts=4 sw=4: */
