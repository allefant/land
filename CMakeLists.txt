cmake_minimum_required (VERSION 2.6)
project(land) 
#add_subdirectory(examples)

# This is so generated .h files will be found.
include_directories(${CMAKE_BINARY_DIR}/c)

# FIXME: Should be auto-detected or specified by user instead.
include_directories(/home/elias/prog/allegro/install4.9/include)

# Settings.
set(SHARED 1 CACHE BOOL "Whether to build the shared library.")
set(STATIC 0 CACHE BOOL "Whether to build the static library.")
set(RELEASE 1 CACHE BOOL "Whether to build the release library.")
set(DEBUG 0 CACHE BOOL "Whether to build the debug library.")

#_______________________________________________________________________
# Step 1: Find all .py source files.
#
file(GLOB_RECURSE pyfiles RELATIVE ${CMAKE_SOURCE_DIR}/src src/*.py)

#_______________________________________________________________________
# Step 2: Rules to create .c and .h files.
#
set(cfiles)
foreach(py ${pyfiles})
    get_filename_component(path ${py} PATH)
    get_filename_component(name ${py} NAME_WE)
    if (path)
        set(out land/${path}/${name})
    else ()
        set(out land/${name})
    endif ()
    add_custom_command(
        OUTPUT "c/${out}.c" "c/${out}.h"
        COMMAND ${CMAKE_COMMAND} -E make_directory "c/land/${path}"
        COMMAND scramble.py
            -i "${CMAKE_SOURCE_DIR}/src/${py}"
            -c "c/${out}.c"
            -h "c/${out}.h"
            -n "${out}"
            -p _LAND
        DEPENDS src/${py})
    list(APPEND cfiles "c/${out}.c")
endforeach(py)

#_______________________________________________________________________
# Step 3: Build from .c files.
#

set(WFLAGS "-W -Wall")
set(WFLAGS "${WFLAGS} -Wno-unused-parameter")
set(CFLAGS "--std=gnu99")
set(DFLAGS "-g")
set(RFLAGS "-O3")

if (STATIC)
    if (DEBUG)
        add_library(land-static-debug STATIC ${cfiles})
        set_target_properties(land-static-debug
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
            )
    endif (DEBUG)
    if (RELEASE)
        add_library(land-static STATIC ${cfiles})
        set_target_properties(land-static
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
            )
    endif (RELEASE)
endif (STATIC)

if (SHARED)
    if (DEBUG)
        add_library(land-debug SHARED ${cfiles})
        set_target_properties(land-debug
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
            )
    endif (DEBUG)
    if (RELEASE)
        add_library(land SHARED ${cfiles})
        set_target_properties(land
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
            )
    endif (RELEASE)
endif (SHARED)
