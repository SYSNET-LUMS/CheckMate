#ifndef _SUPPORT_H
#define _SUPPORT_H

#include <msp430fr5994.h>
#include <stddef.h>
#include <stdint.h>

#ifndef FRAM_WAIT
#define FRAM_WAIT 0
#endif

// Initialize board/target
void target_init();

// Indicate start of workload
void indicate_begin();

// Indicate end of workload
void indicate_end();

// Hand-written fast version of memcpy
void fastmemcpy(uint8_t *dst, uint8_t *src, size_t len);

// Delay between workload iterations
void wait();

// Enable interrupts
void enable_interrupts();

// Disable interrupts
void disable_interrupts();

#endif
