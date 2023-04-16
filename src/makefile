# Makefile for building main.so

.PHONY: all deps clean

all: main.so

deps:
	@if ! command -v psql >/dev/null ; then \
		echo "Installing libpq..." ; \
		sudo apt-get install libpq-dev ; \
	fi

main.so: main.c | deps
	gcc -shared -o main.so main.c -fpic -lpq

clean:
	rm -f main.so
