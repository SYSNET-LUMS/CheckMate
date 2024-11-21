cmake_minimum_required(VERSION 3.0)

FOREACH(METHOD "MS" "AS" "QR")
  set(TESTNAME "stringsearch-iclib-${METHOD}-${TARGET_ARCH}")
  add_executable( ${TESTNAME} 
    search.h
    main.c
  )

  # target_link_libraries(${TESTNAME} PRIVATE m)
  target_compile_options(${TESTNAME} PRIVATE -Os)

  include(${CMAKE_CURRENT_LIST_DIR}/../cmake/tail.cmake)
ENDFOREACH()
