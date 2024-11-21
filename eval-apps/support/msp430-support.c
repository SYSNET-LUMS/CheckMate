#include <stdint.h>
#include <msp430fr5994.h>
#include "support/msp430-support.h"

/* ------ SimpleMonitor ------ */
#define SIMPLE_MONITOR_KILL_SIM 0x0D1E  //! Kill simulation (success)
#define SIMPLE_MONITOR_SW_ERROR 0x5D1E  //! Indicate SW error (kills simulation)
#define SIMPLE_MONITOR_TEST_FAIL 0xFA11  //! Indicate test fail (kills sim)
#define SIMPLE_MONITOR_START_EVENT_LOG 0x000E  //! Start logging events
#define SIMPLE_MONITOR_INDICATE_BEGIN 0x0001   //! Indicate start of workload
#define SIMPLE_MONITOR_INDICATE_END 0x0002     //! Indicate end of workload

#define PERIPHERAL_START 0x0B00  //! Start address of internal peripherals

/* ------ SimpleMonitor ------ */
#define SIMPLE_MONITOR_BASE PERIPHERAL_START
#define SIMPLE_MONITOR_SIZE 0x0010
#define SIMPLE_MONITOR *((unsigned int *)SIMPLE_MONITOR_BASE)

void target_init() {}

void indicate_begin(){
  P1OUT |= BIT0;
}

void indicate_end() {
  P1OUT &= ~BIT0;
  // P1OUT &= ~BIT2;
  SIMPLE_MONITOR = SIMPLE_MONITOR_KILL_SIM;
  while(1); // Just in case
}

void wait() {
  for (volatile long int i = 0; i < (16 - FRAM_WAIT) * 10l; i++)             \
    ;
}

void __attribute__((section(".ramtext"), naked))
fastmemcpy(uint8_t *dst, uint8_t *src, size_t len) {
  __asm__(" push r5\n"
          " tst r14\n" // Test for len=0
          " jz return\n"
          " mov #2, r5\n"   // r5 = word size
          " xor r15, r15\n" // Clear r15
          " mov r14, r15\n" // r15=len
          " and #1, r15\n"  // r15 = len%2
          " sub r15, r14\n" // r14 = len - len%2
          "loopmemcpy:  \n"
          " mov.w @r13+, @r12\n"
          " add r5, r12 \n"
          " sub r5, r14 \n"
          " jnz loopmemcpy \n"
          " tst r15\n"
          " jz return\n"
          " mov.b @r13, @r12\n" // move last byte
          "return:\n"
          " pop r5\n"
          " ret\n");
}
