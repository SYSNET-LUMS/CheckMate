/*
 * Copyright (c) 2018-2020, University of Southampton.
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#ifndef CM0_IC_H
#define CM0_IC_H

#define PERSISTENT __attribute__((section(".persistent")))
#define MMDATA __attribute__((section(".mmdata")))

#include <stdint.h>
#include "iclib/config.h"

// Boot function
void _start();

#endif
