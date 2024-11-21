main:
	gcc -o main main.c -DLOCAL_RUN -lm

clean:
	rm -f main main.o main.elf

.PHONE: main clean

iclib:
	$(MSP430_GCC_ROOT)/bin/msp430-elf-gcc -mcpu=msp430 -DMSP430_ARCH -mhwmult=f5series -fno-zero-initialized-in-bss -fno-common -c main.c -o main.o -I ../ -I $(MSP430_INC)/include
	$(MSP430_GCC_ROOT)/bin/msp430-elf-ld -I ../ -L $(MSP430_INC)/include -L ${MSP430_GCC_ROOT}/msp430-elf/lib/430/ -L ${MSP430_GCC_ROOT}/lib/gcc/msp430-elf/8.2.0/430 -nostdlib -T ../support/msp430fr5994.ld -T $(MSP430_INC)/include/msp430fr5994_symbols.ld main.o -L ./lib -lic -lsupport -lm -o main.elf -lmul_f5 -lgcc -lc