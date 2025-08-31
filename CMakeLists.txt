cmake_minimum_required(VERSION 3.12)
project(core_performance)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(pybind11 REQUIRED)

# Include necessary headers
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Create the Python extension module
pybind11_add_module(core_performance 
    core_cpp/text_streamer.cpp
)

# Set properties for the module
target_compile_definitions(core_performance PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
target_compile_features(core_performance PRIVATE cxx_std_17)

# Compiler-specific optimizations
if(MSVC)
    target_compile_options(core_performance PRIVATE /O2)
else()
    target_compile_options(core_performance PRIVATE -O3 -march=native)
endif()

# Threading support
find_package(Threads REQUIRED)
target_link_libraries(core_performance PRIVATE Threads::Threads)