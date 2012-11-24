cmake_minimum_required (VERSION 2.6)
project(land) 

# This is so generated .h files will be found.
include_directories(${CMAKE_BINARY_DIR}/c)

# Settings.
set(SHARED 1 CACHE BOOL "Whether to build the shared library.")
set(STATIC 0 CACHE BOOL "Whether to build the static library.")
set(RELEASE 1 CACHE BOOL "Whether to build the release library.")
set(DEBUG 0 CACHE BOOL "Whether to build the debug library.")
set(PROFILE 0 CACHE BOOL "Whether to build the profile library.")

set(MEMLOG 0 CACHE BOOL "Whether to use the builtin memory logger.")

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
        COMMAND scramble
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
set(DFLAGS "-g3 -O2")
set(RFLAGS "-O3")
set(PFLAGS "-g3 -p -O2")
set(LFLAGS "")

if (MEMLOG)
    set(CFLAGS "${CFLAGS} -DLAND_MEMLOG") #-fmudflap
    #set(LFLAGS "${LFLAGS} -fmudflap")
endif ()

string(COMPARE EQUAL ${CMAKE_SYSTEM_NAME} Windows WINDOWS)

if (WINDOWS)
    message("Windows version")
    set(CFLAGS "${CFLAGS} -DWINDOWS")
else ()
    message("Linux version")
    set(CFLAGS "${CFLAGS} -DLINUX")
    
    # FIXME: Should be auto-detected or specified by user instead.
    #include_directories(/home/elias/prog/allegro/install/include)
endif ()

if (MEMLOG)
    set(libname "land-memlog")
else ()
    set(libname "land")
endif ()

if (STATIC)
    if (DEBUG)
        add_library(${libname}-static-debug STATIC ${cfiles})
        set_target_properties(${libname}-static-debug
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
            )
    endif (DEBUG)
    if (PROFILE)
        add_library(${libname}-static-profile STATIC ${cfiles})
        set_target_properties(${libname}-static-profile
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${PFLAGS}"
            LINK_FLAGS -p
            )
    endif (PROFILE)
    if (RELEASE)
        add_library(${libname}-static STATIC ${cfiles})
        set_target_properties(${libname}-static
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
            )
    endif (RELEASE)
endif (STATIC)

if (SHARED)
    if (DEBUG)
        add_library(${libname}-debug SHARED ${cfiles})
        set_target_properties(${libname}-debug
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
            LINK_FLAGS "-rdynamic ${LFLAGS}"
            )
        if (WINDOWS)
            target_link_libraries(${libname}-debug
                allegro-debug
                allegro_font-debug
                allegro_primitives-debug
                allegro_audio-debug
                allegro_acodec-debug
                allegro_color-debug
                allegro_ttf-debug
                allegro_image-debug
                wsock32
                z
                )
        else (WINDOWS)
            target_link_libraries(${libname}-debug
                allegro_monolith-debug
                yaml
                )
        endif (WINDOWS)
    endif (DEBUG)
    if (RELEASE)
        add_library(${libname} SHARED ${cfiles})
        set_target_properties(${libname}
            PROPERTIES
            COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
            )
        if (WINDOWS)
            target_link_libraries(${libname}
                allegro
                allegro_font
                allegro_primitives
                allegro_audio
                allegro_acodec
                allegro_color
                allegro_ttf
                allegro_image
                wsock32
                z
                )
        else (WINDOWS)
            target_link_libraries(${libname}
                allegro_monolith
                yaml
                )
        endif (WINDOWS)
    endif (RELEASE)
endif (SHARED)

add_subdirectory(examples EXCLUDE_FROM_ALL)
