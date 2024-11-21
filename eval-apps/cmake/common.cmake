#
# Copyright (c) 2019-2020, University of Southampton and Contributors.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#


# This file sets up:
#  - Compiler flags
#  - Linker flags
#  - Linker scritps
#  - Include/link directories

enable_language(C ASM)

IF(${TARGET_ARCH} STREQUAL "msp430")
  include_directories($ENV{MSP430_INC}/include) # MSP430 headers

  add_compile_options(
      -DMSP430_ARCH
      -std=c99
      -mcpu=msp430
      -msmall
      #-mhwmult=none
      -mhwmult=f5series
      -fno-common
      -Wall
      -fno-zero-initialized-in-bss # We don't want to zero out whole bss on every boot
      )

  # Linker scripts
  set(LSCRIPTS "-T$ENV{MSP430_INC}/include/msp430fr5994_symbols.ld")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${LSCRIPTS}")

  # Add to search path for linker scripts (xx_symbols.ld, included by main linker script)
  link_directories(
      $ENV{MSP430_GCC_ROOT}/msp430-elf/lib/430/
      $ENV{MSP430_GCC_ROOT}/lib/gcc/msp430-elf/8.2.0/430
      $ENV{MSP430_INC}/include
      )

  link_libraries( # Global link flags
      # Removing standard libs and startup code to prevent unnecessary initialization
      -nostdlib
      -ffreestanding
      )

  # Utility for linking targets to std libs
  set(SUPPORT_LIBS support-${TARGET_ARCH} mul_f5 gcc c)

ELSEIF(${TARGET_ARCH} STREQUAL "cm0")

  include_directories(
    $ENV{ARM_GCC_ROOT}/arm-none-eabi/include
    $ENV{HOME}/Documents/IOT/fused/include/
    )

  # Make sure only thumb-libraries are used
  add_compile_options(
      -DCM0_ARCH
      -Wall
      -std=c99
      -march=armv6s-m
      -mcpu=cortex-m0
      -mthumb
      -msoft-float
      --specs=nosys.specs
      -nostartfiles
      -ffreestanding
      -fomit-frame-pointer
    )

  link_libraries(
    -nostdlib
    -ffreestanding
    # Make sure linker doesn't pull in libraries using (32-bit) ARM-instructions!
    -mthumb
    -march=armv6s-m
    -mcpu=cortex-m0
    )

set(SUPPORT_LIBS nosys m gcc c)

ELSE()
  message(ERROR "Invalid TARGET_ARCH: ${TARGET_ARCH}")
ENDIF()
