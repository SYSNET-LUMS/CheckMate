CC = gcc
CFLAGS = -DLOCAL_RUN
TARGET = main
OBJS = main.o communication_trace_A.o
LIBS = -lm

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LIBS)

main.o: main.c struct.h msp430fr5994.h
	$(CC) $(CFLAGS) -c main.c

communication_trace_A.o: communication_trace_A.c struct.h msp430fr5994.h
	$(CC) $(CFLAGS) -c communication_trace_A.c

clean:
	rm -f $(TARGET) $(OBJS)