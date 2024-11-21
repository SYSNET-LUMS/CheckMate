#if defined(MSP430_ARCH)
#include "support/msp430-support.h"
#elif defined(CM0_ARCH)
#include "support/cm0-support.h"
#else
#error("No target defined")
#endif
