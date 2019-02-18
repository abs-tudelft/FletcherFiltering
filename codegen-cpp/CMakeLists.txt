cmake_minimum_required(VERSION 3.12)
project(codegen_cpp)

set(CMAKE_CXX_STANDARD 14)

add_executable(codegen_cpp fletcherfiltering.cpp query.cpp main.cpp)