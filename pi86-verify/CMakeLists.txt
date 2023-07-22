cmake_minimum_required(VERSION 3.7)

# set the project name
project(verify-with-pi86 VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_BUILD_TYPE Debug)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_executable(verify-with-pi86
	pi86.cpp
	x86.cpp
)

include(FindPkgConfig)

target_link_libraries(verify-with-pi86 -lwiringPi)
