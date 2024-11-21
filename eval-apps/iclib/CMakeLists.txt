#
# Copyright (c) 2019-2020, University of Southampton and Contributors.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

cmake_minimum_required(VERSION 3.0)

FOREACH(METHOD "MS" "AS" "QR")
    string(COMPARE EQUAL ${METHOD} "QR" QUICKRECALL)
    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/common.cmake)
    set(TESTNAME "ic-${METHOD}-${TARGET_ARCH}")

    IF(${TARGET_ARCH} STREQUAL "cm0")
      add_library(
        ${TESTNAME}
        cm0-ic.c
        cm0-ic.h
        cm0-ic.S
        memory-management.c
        memory-management.h
        )
      target_link_libraries(${TESTNAME} support-${TARGET_ARCH})
    ELSEIF(${TARGET_ARCH} STREQUAL "msp430")
      add_library(
        ${TESTNAME}
        msp430-ic.c
        msp430-ic.h
        msp430-ic.S
        memory-management.c
        memory-management.h
        dvdb.h
        )
    ENDIF()

    IF (${METHOD} STREQUAL "AS")
       target_compile_definitions( ${TESTNAME} PUBLIC -DALLOCATEDSTATE)
    ELSEIF(${METHOD} STREQUAL "MS")
       target_compile_definitions(${TESTNAME} PUBLIC -DMANAGESTATE)
    ELSEIF(${METHOD} STREQUAL "QR")
       target_compile_definitions(${TESTNAME} PUBLIC -DQUICKRECALL)
    ENDIF()

    target_link_libraries(${TESTNAME} ${SUPPORT_LIBS})
    target_include_directories(${TESTNAME}  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
ENDFOREACH()
