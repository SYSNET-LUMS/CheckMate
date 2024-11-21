/*
 * Copyright (c) 2018-2020, University of Southampton.
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

/***************************** Include Files *********************************/
#include <stdint.h>
#include <string.h>
#include "iclib/ic.h"
#include "iclib/memory-management.h"
#include "support/support.h"

/*************************** Global Definitions ******************************/

static uint16_t mm_n_dirty_pages = 0;
static uint16_t mm_n_active_pages = 0;

/************************** Constant Definitions *****************************/
extern uint8_t __mmdata_start;
extern uint8_t __mmdata_end;
extern uint8_t __mmdata_loadStart;

struct LRU_candidate {
  uint8_t pageNumber;
  uint8_t tableIdx;
};

/**************************** Type Definitions *******************************/

/***************** Macros ****************************************************/
#define NPAGES (MMDATA_SIZE / PAGE_SIZE)

#if NPAGES > 254
#error Too many pages, increase page size or reduce memory usage
#endif

#define DUMMY_PAGE 255   //! Used for LRU table
#define REFCNT_MASK 0x3F //! Reference count
#define LOADED 0x80      //! Mask to check if loaded
#define MODIFIED 0x40    //! Mask to check if modified

/************************** Function Prototypes ******************************/
static void writePageFRAM(uint8_t pageNumber);
static void loadPage(uint8_t pageNumber);
static void addLRU(uint8_t pageNumber);
static void clearLRU(uint8_t index);
static void clearLRUPage(uint8_t pageNumber);

/*************************** Extern Functions ********************************/

/************************** Variable Definitions *****************************/

static uint8_t attributeTable[NPAGES] = {0};
static uint8_t lruTable[MAX_DIRTY_PAGES];

/*************************** Function definitions ****************************/

int mm_acquire(const uint8_t *memPtr, mm_mode mode) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  return 0;
#endif
  if ((&__mmdata_start > (uint8_t *)memPtr) ||
      (&__mmdata_end < (uint8_t *)memPtr)) {
    while (1)
      ; // Error: Pointer out of bounds.
  }

  uint16_t pageNumber =
      ((uint16_t)memPtr - (uint16_t)&__mmdata_start) / PAGE_SIZE;

  if ((attributeTable[pageNumber] & REFCNT_MASK) >= 64) {
    while (1)
      ; // Error: Too many references to a single page
  }

  if (mode == MM_READWRITE) { // && !(attributeTable[pageNumber] & MODIFIED)){
    if (mm_n_dirty_pages >= MAX_DIRTY_PAGES) {
      // Need to write back an inactive and dirty page first
      for (int i = MAX_DIRTY_PAGES - 1; i >= 0; i--) {
        uint8_t candidate = lruTable[i];
        if (candidate != DUMMY_PAGE) {
          if ((attributeTable[candidate] & REFCNT_MASK) == 0 &&
              (attributeTable[candidate] & LOADED) &&
              (attributeTable[candidate] & MODIFIED)) {
            writePageFRAM(candidate);
            clearLRU(i);
            break;
          }
        }
      }

      if (mm_n_dirty_pages >= MAX_DIRTY_PAGES) {
        while (1)
          ; // Error: MAX_DIRTY_PAGES exceeded
      }
    }

    if (!(attributeTable[pageNumber] &
          MODIFIED)) { // if page isn't already dirty
      mm_n_dirty_pages++;
      attributeTable[pageNumber] |= MODIFIED;
    }

    // Update LRU with the new dirty page
    addLRU(pageNumber);
  }

  loadPage(pageNumber);

  if ((attributeTable[pageNumber] & REFCNT_MASK) == 0) {
    mm_n_active_pages++;
  }
  attributeTable[pageNumber]++;

  // Update suspend/restore thresholds
  static int oldPageTotal = 0;
  if (oldPageTotal != mm_n_dirty_pages + mm_n_active_pages) {
    ic_update_thresholds(mm_n_dirty_pages * PAGE_SIZE,
                         mm_n_active_pages * PAGE_SIZE);
    oldPageTotal = mm_n_dirty_pages + mm_n_active_pages;
  }

  return 0;
}

int mm_release(const uint8_t *memPtr) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  return 0;
#endif
  uint16_t pageNumber =
      ((uint16_t)memPtr - (uint16_t)&__mmdata_start) / PAGE_SIZE;
  if ((attributeTable[pageNumber] & REFCNT_MASK) > 0) {
    attributeTable[pageNumber]--;
    if ((attributeTable[pageNumber] & REFCNT_MASK) == 0) {
      mm_n_active_pages--;
    }
  } else {
    while (1)
      ; // Error: Attempt to release inactive page
  }
  return 0;
}

void mm_restore(void) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  fastmemcpy(&__mmdata_start, &__mmdata_loadStart,
             &__mmdata_end - &__mmdata_start);
  return;
#endif

  for (int pageNumber = 0; pageNumber < NPAGES; pageNumber++) {
    // Clear loaded pages (bits are set again when calling loadPage)
    attributeTable[pageNumber] &= ~LOADED;

    if ((attributeTable[pageNumber] & REFCNT_MASK) > 0) {
      loadPage(pageNumber);
    }
  }
}

unsigned mm_flush(void) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  // Save entire section
  fastmemcpy(&__mmdata_loadStart, &__mmdata_start,
             &__mmdata_end - &__mmdata_start);
  return (size_t)(&__mmdata_end - &__mmdata_start);
#endif
  unsigned pagesSaved = 0;

  for (int pageNumber = 0; pageNumber < NPAGES; pageNumber++) {
    if (mm_n_dirty_pages == 0) {
      break;
    } else if (attributeTable[pageNumber] & MODIFIED) {
      writePageFRAM(pageNumber);
      pagesSaved++;
      if ((attributeTable[pageNumber] & REFCNT_MASK) == 0) {
        clearLRUPage(pageNumber);
      }
    }
  }

  ic_update_thresholds(mm_n_dirty_pages * PAGE_SIZE,
                       mm_n_active_pages * PAGE_SIZE);

  return pagesSaved * PAGE_SIZE;
}

/**
 * @brief Write a page to FRAM
 * @param pageNumber
 */
static void writePageFRAM(uint8_t pageNumber) {
  uint16_t dstStart;
  uint16_t srcStart;
  uint16_t pageOffset = pageNumber * PAGE_SIZE;
  uint16_t len;

  if (!(attributeTable[pageNumber] & MODIFIED)) {
    return;
  }

  uint16_t old_gie = __get_SR_register() & GIE;
  __disable_interrupt(); // Critical section (attributes get messed up if
                         // interrupted)
  srcStart = (uint16_t)&__mmdata_start + pageOffset;
  dstStart = (uint16_t)(&__mmdata_loadStart) + pageOffset;
  len = PAGE_SIZE;
  if (srcStart + PAGE_SIZE > (uint16_t)&__mmdata_end) {
    len = (uint16_t)&__mmdata_end - srcStart;
  }

  // Save page
  fastmemcpy((uint8_t *)dstStart, (uint8_t *)srcStart, len);

  if ((attributeTable[pageNumber] & REFCNT_MASK) == 0) {
    // Page is clean
    attributeTable[pageNumber] &= ~MODIFIED;
    mm_n_dirty_pages--;
  }
  if (old_gie) {
    __enable_interrupt();
  }
}

int mm_acquire_array(const uint8_t *memPtr, size_t len, mm_mode mode) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  return 0;
#endif
  int status = 0;
  // Acquire each page referenced
  const uint8_t *ptr = memPtr;
  size_t remaining = len;
  while (remaining > 0) {
    status = mm_acquire(ptr, mode);
    if (remaining > PAGE_SIZE) {
      ptr += PAGE_SIZE;
      remaining -= PAGE_SIZE;
    } else {
      ptr += remaining;
      remaining = 0;
    }
  }
  return status;
}

int mm_release_array(const uint8_t *memPtr, size_t len) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  return 0;
#endif
  int status = 0;

  // Error check
  if ((memPtr > &__mmdata_end) || (memPtr < &__mmdata_start) ||
      (memPtr + len) > &__mmdata_end) {
    while (1)
      ; // Error: access out of bounds
  }

  // Release each page referenced
  const uint8_t *ptr = memPtr;
  size_t remaining = len;
  while (remaining > 0) {
    status = mm_release(ptr);
    if (remaining > PAGE_SIZE) {
      ptr += PAGE_SIZE;
      remaining -= PAGE_SIZE;
    } else {
      ptr += remaining;
      remaining = 0;
    }
  }
  return status;
}

size_t mm_get_n_active_pages(void) {
  size_t nActive = 0;
  for (int i = 0; i < NPAGES; i++) {
    if ((attributeTable[i] & REFCNT_MASK) > 0) {
      nActive++;
    }
  }
  return nActive;
}

size_t mm_get_n_dirty_pages(void) { return mm_n_dirty_pages; }

int mm_acquire_page(const uint8_t *memPtr, size_t nElements, size_t elementSize,
                    mm_mode mode) {
#if defined(ALLOCATEDSTATE) || defined(QUICKRECALL)
  return nElements;
#endif
  int bytesAcquired;

  // Check if first element crosses a page boundary
  uint16_t pageNumberStart = (memPtr - &__mmdata_start) / PAGE_SIZE;
  uint16_t pageNumberEnd =
      (memPtr + elementSize - 1 // end address of first element
       - &__mmdata_start        // - start address
       ) /
      PAGE_SIZE;

  if (pageNumberStart != pageNumberEnd) {
    // Need to load 2 pages
    mm_acquire(memPtr, mode);
    mm_acquire(memPtr + elementSize - 1, mode);
    bytesAcquired = (pageNumberStart + 1) * PAGE_SIZE -
                    (memPtr - &__mmdata_start) + PAGE_SIZE;
  } else {
    mm_acquire(memPtr, mode);
    bytesAcquired =
        (pageNumberStart + 1) * PAGE_SIZE - (memPtr - &__mmdata_start);
  }

  // Don't report acquiring more elements than requested
  if (bytesAcquired / elementSize >= nElements) {
    return nElements;
  } else {
    return bytesAcquired / elementSize;
  }
}

/**
 * @brief Load page from FRAM if it is not already loaded.
 * @param pageNumber
 */
static void loadPage(uint8_t pageNumber) {
  if (!(attributeTable[pageNumber] & LOADED)) {
    uint8_t *srcStart;
    uint8_t *dstStart;
    uint16_t len;
    uint16_t pageOffset = pageNumber * PAGE_SIZE;

    dstStart = &__mmdata_start + pageOffset;     // Memory address
    srcStart = &__mmdata_loadStart + pageOffset; // Snapshot address
    len = PAGE_SIZE;
    if ((uint16_t)dstStart + PAGE_SIZE > (uint16_t)&__mmdata_end) {
      len = (uint16_t)&__mmdata_end - (uint16_t)dstStart;
    }

    fastmemcpy((uint8_t *)dstStart, (uint8_t *)srcStart, len);
    attributeTable[pageNumber] |= LOADED;
  }
}

/**
 * @brief Initialise LRU table with dummy pages
 */
void mm_init_lru(void) {
  for (int i = 0; i < MAX_DIRTY_PAGES; i++) {
    lruTable[i] = DUMMY_PAGE;
  }
}

/**
 * @brief Add a new reference to LRU table.
 * @param pageNumber
 */
static void addLRU(uint8_t pageNumber) {
  uint8_t tmp1, tmp2;

  if (pageNumber > NPAGES) {
    while (1)
      ; // Error: page number out of bounds.
  }

  tmp1 = pageNumber;
  for (int i = 0; i < MAX_DIRTY_PAGES; i++) {
    if (lruTable[i] == pageNumber) {
      lruTable[i] = tmp1;
      for (int j = i + 1; j < MAX_DIRTY_PAGES; j++) {
        if (lruTable[j] == tmp1) {
          lruTable[j] = DUMMY_PAGE;
          break;
        }
      }
      break;
    } else if (lruTable[i] == DUMMY_PAGE) {
      lruTable[i] = tmp1;
      for (int j = i + 1; j < MAX_DIRTY_PAGES; j++) {
        if (lruTable[j] == tmp1) {
          lruTable[j] = DUMMY_PAGE;
          break;
        }
      }
      break;
    } else {
      tmp2 = lruTable[i];
      lruTable[i] = tmp1;
      tmp1 = tmp2;
    }
  }
}

/**
 * @brief Clear a page from the LRU table at index.
 * @param index
 */
static void clearLRU(uint8_t index) { lruTable[index] = DUMMY_PAGE; }

/**
 * @brief Clear a page from the LRU table.
 * @param pageNumber
 */
static void clearLRUPage(uint8_t pageNumber) {
  for (int i = MAX_DIRTY_PAGES - 1; i >= 0; i--) {
    if (lruTable[i] == pageNumber) {
      lruTable[i] = DUMMY_PAGE;
      return;
    }
  }
}

