CC = gcc
CFLAGS = -DLOCAL_RUN
LIBS = -lm

OBJS = main.o

main: $(OBJS)
	$(CC) $(CFLAGS) -o main $(OBJS) $(LIBS)

main.o: main.c search.h msp430fr5994.h
	$(CC) $(CFLAGS) -c main.c

clean:
	rm -f $(OBJS) main