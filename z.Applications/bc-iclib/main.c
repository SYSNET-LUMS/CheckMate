/*
 * Original source: https://github.com/CMUAbstract/alpaca-oopsla2017/
 * Modified 2020 for use with ICLib by Sivert Sliper, University of Southamption
 * Modified 2024 for use with Checkmate
 */

#ifdef LOCAL_RUN
#include <stdio.h>
#else
#include "support/msp430-support.h"
#endif

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

/* ------ Parameters ------ */
#define SEED 4L
#define ITER 100
#define CHAR_BIT 8

/* ------ Types ------ */

/* ------ Globals ------ */
static char bits[256] = {
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, /* 0   - 15  */
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, /* 16  - 31  */
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, /* 32  - 47  */
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, /* 48  - 63  */
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, /* 64  - 79  */
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, /* 80  - 95  */
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, /* 96  - 111 */
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, /* 112 - 127 */
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, /* 128 - 143 */
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, /* 144 - 159 */
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, /* 160 - 175 */
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, /* 176 - 191 */
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, /* 192 - 207 */
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, /* 208 - 223 */
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, /* 224 - 239 */
    4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8  /* 240 - 255 */
};

/* ------ Function definitions ------ */

int btbl_bitcnt(uint32_t x) {
  int cnt = bits[((char *)&x)[0] & 0xFF];

  if (0L != (x >>= 8))
    cnt += btbl_bitcnt(x);
  return cnt;
}

int bit_count(uint32_t x) {
  int n = 0;
  /*
  ** The loop will execute once for each bit of x set, this is in average
  ** twice as fast as the shift/test method.
  */
  if (x)
    do
      n++;
    while (0 != (x = x & (x - 1)));
  return (n);
}

void main() {
  unsigned n_0, n_1;
  uint32_t seed;
  unsigned iter;
  unsigned func;

  #ifndef LOCAL_RUN
  indicate_begin();
  #endif
  for (volatile unsigned i = 0; i < 1; i++) {
    n_0 = 0;
    n_1 = 0;
    
      seed = (uint32_t)SEED;
    for (func = 0; func < 100; func++) {
      for (iter = 0; iter < ITER; ++iter, seed += 13) {
        // n_0 += bit_count(seed);
      }
      for (iter = 0; iter < ITER; ++iter, seed += 13) {
        n_1 += btbl_bitcnt(seed);
      }
    }
  }

  #ifdef LOCAL_RUN
  printf("%u\n", n_0);
  printf("%u\n", n_1);
  #else
  indicate_end();
  #endif
}