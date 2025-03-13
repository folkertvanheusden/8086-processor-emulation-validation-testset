cmake_minimum_required(VERSION 3.7)

# set the project name
project(with-pi86 VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_BUILD_TYPE RelWithDebInfo)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE TRUE)

add_compile_options(-Wall)

add_executable(verify-with-pi86
	pi86.cpp
	x86.cpp
)

add_executable(cycles-with-pi86
	cycles.cpp
	x86.cpp
)

include(FindPkgConfig)

target_link_libraries(verify-with-pi86 -lwiringPi)
target_link_libraries(cycles-with-pi86 -lwiringPi)
