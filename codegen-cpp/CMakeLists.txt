cmake_minimum_required(VERSION 3.12)
project(codegen_cpp)

set(CMAKE_CXX_STANDARD 14)

add_library(codegen_lib SHARED fletcherfiltering.cpp query_test.cpp query.cpp)

add_executable(codegen_cpp main.cpp)

TARGET_LINK_LIBRARIES(codegen_cpp codegen_lib)