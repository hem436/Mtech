#
# Makefile that builds btest and other helper programs for the data lab
#

# General variables

CC = /usr/bin/gcc
CFLAGS = -std=gnu99 -m64 -O1 -fwrapv -g -Werror -Wall -Wextra \
	 -Wstrict-prototypes -Wwrite-strings \
	 -Wno-unused-parameter -Wno-cast-function-type -Wno-bool-operation
LDLIBS = -lm

# Targets to compile
FILES = btest fshow ishow

.PHONY: all
all: $(FILES)

btest: btest.c bits.c decl.c tests.c btest.h bits.h
	$(CC) $(CFLAGS) -o btest bits.c btest.c decl.c tests.c $(LDLIBS)

fshow: fshow.c
	$(CC) $(CFLAGS) -o fshow fshow.c

ishow: ishow.c
	$(CC) $(CFLAGS) -o ishow ishow.c

# Forces a recompile. Used by the driver program.
.PHONY: btestexplicit
btestexplicit:
	$(CC) $(CFLAGS) -o btest bits.c btest.c decl.c tests.c $(LDLIBS)

.PHONY: clean
clean:
	rm -f *~ *.o
	rm -f $(FILES)

# Include rules for submit, format, etc
FORMAT_FILES = bits.c
HANDIN_FILES = bits.c
