LIB = libland-al.a
SRCDIR = src

DEBUGMODE = 1

PRETTY = 1

USECPROTO = 1

include ../makefile.template

install:
	cp libland-al.a /usr/local/lib
	mkdir -p /usr/local/include/land
	cp pro/*.h pro/*.pro /usr/local/include/land
