cmake_minimum_required(VERSION 3.16)
project(OrganizedOrderedSet LANGUAGES CXX)

if(MSVC)
    message(FATAL_ERROR "GNU libstdc++ and PBDS are required; use GCC or Clang with that library.")
endif()

add_library(organized_ordered_set INTERFACE)
target_include_directories(organized_ordered_set INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}")
target_compile_features(organized_ordered_set INTERFACE cxx_std_17)

add_executable(ordered_set_example Example.cpp)
target_link_libraries(ordered_set_example PRIVATE organized_ordered_set)

include(CTest)
if(BUILD_TESTING)
    add_executable(ordered_set_tests tests/OrderedSetTests.cpp)
    target_link_libraries(ordered_set_tests PRIVATE organized_ordered_set)
    add_test(NAME ordered_set_reference_tests COMMAND ordered_set_tests)
endif()
