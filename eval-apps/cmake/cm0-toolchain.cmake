#
# Copyright (c) 2019-2020, University of Southampton and Contributors.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

INCLUDE(CMakeForceCompiler)

# Find toolchain programs
set(CMAKEDIR ${CMAKE_CURRENT_LIST_DIR})
set(SUPPORTDIR ${CMAKE_CURRENT_LIST_DIR}/../support)

set(BINPATHS $ENV{ARM_GCC_ROOT}/bin)
set(BIN_PREFIX arm-none-eabi)

message(STATUS "finding ${TARGET_ARCH} compiler")
find_program(TC-GCC ${BIN_PREFIX}-gcc PATHS ${BINPATHS})
find_program(TC-GXX ${BIN_PREFIX}-g++ PATHS ${BINPATHS})
find_program(TC-OBJCOPY ${BIN_PREFIX}-objcopy PATHS ${BINPATHS})
find_program(TC-SIZE ${BIN_PREFIX}-size PATHS ${BINPATHS})
find_program(TC-OBJDUMP ${BIN_PREFIX}-objdump PATHS ${BINPATHS})

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
    COMMAND echo "uploading ${EXECUTABLE}..."
    COMMAND echo "upload for ${TARGET_ARCH}not implemented!"
    DEPENDS ${EXECUTABLE})
endfunction(add_upload)
