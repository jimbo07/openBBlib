cmake_minimum_required(VERSION 3.1)
project(samplePlugin)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/modules)

set(SOURCE_FILES "pluginMain.cpp"
    "sampleCmd.cpp" "sampleCmd.h"
)

find_package(Maya REQUIRED)

add_library(samplePlugin SHARED ${SOURCE_FILES})
target_link_libraries(samplePlugin PRIVATE Maya::Maya)
target_include_directories(samplePlugin PRIVATE Maya::Maya)
MAYA_PLUGIN(samplePlugin)