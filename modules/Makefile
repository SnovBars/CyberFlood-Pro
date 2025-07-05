# Makefile for wireless attack modules
CC = gcc
CFLAGS = -O3 -Wall -Wextra -pthread
TARGETS = beacon_flood

all: $(TARGETS)

beacon_flood: beacon_flood.c
	$(CC) $(CFLAGS) -o $@ $<
	
clean:
	rm -f $(TARGETS)
	
install: all
	chmod +x deauth.py beacon_flood