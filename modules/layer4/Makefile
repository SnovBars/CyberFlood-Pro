# Makefile for Layer 4 attacks
CC = g++
CFLAGS = -O3 -Wall -Wextra -std=c++17 -pthread
TARGETS = syn_flood icmp_flood udp_flood

# Для Android (Termux)
ifeq ($(shell uname -o), Android)
    CFLAGS += -static -s
endif

all: $(TARGETS)

syn_flood: syn_flood.cpp
	$(CC) $(CFLAGS) -o $@ $<

icmp_flood: icmp_flood.cpp
	$(CC) $(CFLAGS) -o $@ $<

udp_flood: udp_flood.cpp
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGETS)

install: all
	chmod +x $(TARGETS)