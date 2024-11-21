/*
 * Copyright (c) 2018-2020, University of Southampton.
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#ifndef SRC_CONFIG_H_
#define SRC_CONFIG_H_

/* ------ Section sizes -----------------------------------------------------*/
/* Allocates (plenty of) space for snapshot in NVM. Note that these can be made
 * smaller for most apps*/
#define STACK_SIZE 0x400
#define BSS_SIZE 0x1000
#define DATA_SIZE 0x2000
#define MMDATA_SIZE 0x2000

/* ------ Memory manager ----------------------------------------------------*/
#define PAGE_SIZE 128u
#define MAX_DIRTY_PAGES 20

/* ------ Threshold Calculation ---------------------------------------------*/
#define VMAX 3665  // 3.58 V maximum operating voltage
#define VON 1945   // On-voltage

// DVDT: 1024 x voltage delta per byte saved/restored
#ifdef ALLOCATEDSTATE
#define DVDT (33 * 5)  //(33 * 5) // (60*5)
#else
#define DVDT (60 * 5)  //(33 * 5) // (60*5)
#endif

#define V_C 102  // 205 // ~0.2 V Voltage buffer for useful compute

#endif /* SRC_CONFIG_H_ */
