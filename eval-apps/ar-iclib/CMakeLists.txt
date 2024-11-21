cmake_minimum_required(VERSION 3.0)

FOREACH(METHOD "MS" "AS" "QR")
  set(TESTNAME "ar-iclib-${METHOD}-${TARGET_ARCH}")
  add_executable( ${TESTNAME} 
    main.c
  )

  # add -fno-math-errno to compile options
  # target_compile_options(${TESTNAME} PRIVATE -fno-math-errno)
  
  include(${CMAKE_CURRENT_LIST_DIR}/../cmake/tail.cmake)
ENDFOREACH()
