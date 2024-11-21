CC = gcc
CFLAGS = -DLOCAL_RUN

OBJS = main.o

main: $(OBJS)
	$(CC) $(CFLAGS) -o main $(OBJS)

main.o: main.c search.h msp430fr5994.h
	$(CC) $(CFLAGS) -c main.c

clean:
	rm -f $(OBJS) main