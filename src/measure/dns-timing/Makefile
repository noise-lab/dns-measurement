CC := gcc
CFLAGS := -Wall --std=gnu99
LDFLAGS :=

LIBS := -lgetdns -levent -lgetdns_ext_event -lcurl
OBJECTS := common.o dns_dot.o doh.o

TARGET := dns-timing

all: $(OBJECTS)
	$(CC) $(CFLAGS) main.c -o dns-timing $(OBJECTS) $(LDFLAGS) $(LIBS)

clean:
	rm -f *.o dns-timing
