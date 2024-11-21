#include <stdint.h>
#include "iclib/config.h"

#define MMDATA __attribute__((section(".mmdata")))
#define PERSISTENT __attribute__((section(".persistent")))

// Global variables
extern uint16_t mmdata_snapshot[];

// Function Declarations
/**
 * @brief Initialise peripherals and sleep until supply voltage recovers beyond
 * restore threshold
 */
void ic_init(void);

/**
 * @brief Update restore and suspend thresholds based on number of bytes to be
 * suspended/restored
 *
 * @param n_suspend
 * @param n_restore
 */
void ic_update_thresholds(uint16_t n_suspend, uint16_t n_restore);
