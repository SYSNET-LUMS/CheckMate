cmake_minimum_required(VERSION 3.13)

IF(${TARGET_ARCH} STREQUAL "msp430")
  add_library(support-${TARGET_ARCH} "")
  target_sources(support-${TARGET_ARCH}
    PRIVATE msp430-support.c msp430-support.h)
ELSEIF(${TARGET_ARCH} STREQUAL "cm0")
  add_library(support-${TARGET_ARCH} "")
  target_sources(support-${TARGET_ARCH}
    PRIVATE cm0-support.c cm0-support.h cm0-vectors.c
    PUBLIC cm0.h)
ENDIF()
