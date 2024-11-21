#
# Copyright (c) 2019-2020, University of Southampton and Contributors.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

INCLUDE(CMakeForceCompiler)

# Find toolchain programs
find_program(TC-GCC msp430-elf-gcc $ENV{MSP430_GCC_ROOT}/bin)
find_program(TC-GXX msp430-elf-g++ $ENV{MSP430_GCC_ROOT}/bin)
find_program(TC-OBJCOPY msp430-elf-objcopy $ENV{MSP430_GCC_ROOT}/bin)
find_program(TC-SIZE msp430-elf-size $ENV{MSP430_GCC_ROOT}/bin)
find_program(TC-OBJDUMP msp430-elf-objdump $ENV{MSP430_GCC_ROOT}/bin)
find_program(MSPDEBUG mspdebug)

# Define toolchain
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_ASM_COMPILER ${TC-GCC} CACHE INTERNAL "")
set(CMAKE_C_COMPILER ${TC-GCC} CACHE INTERNAL "")
set(CMAKE_CXX_COMPIER ${TC-GXX} CACHE INTERNAL "")

# Prevent CMake from testing the compilers
set(CMAKE_C_COMPILER_WORKS 1 CACHE INTERNAL "")
set(CMAKE_CXX_COMPILER_WORKS 1 CACHE INTERNAL "")

#Debug by default
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug CACHE STRING "Choose the type of build." FORCE)
endif(NOT CMAKE_BUILD_TYPE)

function(add_upload EXECUTABLE)
  add_custom_target(upload_${EXECUTABLE}
    COMMAND ${MSPDEBUG} tilib "erase"
    COMMAND ${MSPDEBUG} tilib "prog ${EXECUTABLE}.elf"
    DEPENDS ${EXECUTABLE})
endfunction(add_upload)
