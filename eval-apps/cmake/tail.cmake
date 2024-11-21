#
# Copyright (c) 2019-2020, University of Southampton and Contributors.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

cmake_minimum_required(VERSION 3.13)

# Commmon function to add linker script and definitions for each target

target_link_libraries( ${TESTNAME}
  LINK_PUBLIC support-${TARGET_ARCH}
  LINK_PUBLIC ic-${METHOD}-${TARGET_ARCH}
  m
  ${SUPPORT_LIBS}
  )

IF(${METHOD} STREQUAL "QR")
  target_compile_definitions( ${TESTNAME} PRIVATE -DQUICKRECALL)
ELSEIF(${METHOD} STREQUAL "AS")
  target_compile_definitions( ${TESTNAME} PRIVATE -DALLOCATEDSTATE)
ELSEIF(${METHOD} STREQUAL "MS")
  target_compile_definitions( ${TESTNAME} PRIVATE -DMANAGEDSTATE)
ELSEIF(${METHOD} STREQUAL "CS")
  target_compile_definitions( ${TESTNAME} PRIVATE -DCACHEDSTATE)
ENDIF()


IF(${TARGET_ARCH} STREQUAL "msp430")
  IF (${METHOD} STREQUAL "QR")
      target_link_options( ${TESTNAME}
          PRIVATE -T${CMAKE_CURRENT_LIST_DIR}/../support/msp430fr5994-fram-only.ld)
  ELSE ()
      target_link_options( ${TESTNAME}
          PRIVATE -T${CMAKE_CURRENT_LIST_DIR}/../support/msp430fr5994.ld)
  ENDIF()
ELSEIF(${TARGET_ARCH} STREQUAL "cm0")
  target_link_options( ${TESTNAME}
      PRIVATE -T${CMAKE_CURRENT_LIST_DIR}/../support/cm0-FS.ld)
ENDIF()

set_target_properties(${TESTNAME} PROPERTIES SUFFIX ".elf")

# Emit map, listing and hex
add_custom_command(TARGET ${TESTNAME} POST_BUILD
  COMMAND ${TC-SIZE} -A -x "$<TARGET_FILE:${TESTNAME}>" > ${TESTNAME}.map
  COMMAND ${TC-OBJDUMP} -d "$<TARGET_FILE:${TESTNAME}>" > ${TESTNAME}.lst
  COMMAND ${TC-OBJCOPY} -O ihex "$<TARGET_FILE:${TESTNAME}>" ${TESTNAME}.hex
  )

# add upload target
add_upload(${TESTNAME})
