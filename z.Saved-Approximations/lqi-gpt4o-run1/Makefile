CC = gcc
CFLAGS = -DLOCAL_RUN
LIBS = -lm

OBJS = main.o communication_trace_A.o

main: $(OBJS)
	$(CC) $(CFLAGS) -o main $(OBJS) $(LIBS)

main.o: main.c struct.h msp430fr5994.h
	$(CC) $(CFLAGS) -c main.c

communication_trace_A.o: communication_trace_A.c struct.h
	$(CC) $(CFLAGS) -c communication_trace_A.c

clean:
	rm -f main $(OBJS)