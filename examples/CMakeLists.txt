cmake_minimum_required (VERSION 2.6)
include(FindPkgConfig)
 
cmake_policy(SET CMP0009 NEW) # don't follow symlinks
include_directories(${CMAKE_BINARY_DIR}/c)
include_directories(${CMAKE_BINARY_DIR}/examples/c)

# FIXME: Should be auto-detected or specified by user instead.
#include_directories(/home/elias/prog/allegro/install/include)
#link_directories(/home/elias/prog/allegro/install/lib)

find_package(OpenGL)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/widget)

#_______________________________________________________________________
# Step 1: Find all .py source files.
#

set(example_exes)
file(GLOB examples RELATIVE ${CMAKE_SOURCE_DIR}/examples */src RELATIVE ${CMAKE_SOURCE_DIR}/examples */*/src)
foreach(exsrc ${examples})
    get_filename_component(ex ${exsrc} DIRECTORY)

    get_filename_component(ex_sub ${ex} DIRECTORY)
    get_filename_component(ex_bin ${ex} NAME)
    
    message(STATUS "Example found: ${ex_bin} in ${ex_sub}")

#_______________________________________________________________________
# Step 2: Rules to create .c and .h files.
#

    file(GLOB_RECURSE example_pyfiles RELATIVE ${CMAKE_SOURCE_DIR}/examples
        ${ex}/src/*.py)
    set(example_cfiles)
    foreach(py ${example_pyfiles})
        get_filename_component(path ${py} PATH)
        get_filename_component(name ${py} NAME_WE)
        set(out ${path}/${name})
        add_custom_command(
            OUTPUT "c/${out}.c" "c/${out}.h"
            COMMAND ${CMAKE_COMMAND} -E make_directory "c/${path}"
            COMMAND scramble
                -i "${CMAKE_SOURCE_DIR}/examples/${py}"
                -c "c/${out}.c"
                -h "c/${out}.h"
                -n "${out}"
                -p _LAND
            DEPENDS ${py})
        list(APPEND example_cfiles "c/${out}.c")
    endforeach(py)

    #_______________________________________________________________________
    # Step 3: Build from .c files.
    #

    set(WFLAGS "-W -Wall")
    set(WFLAGS "${WFLAGS} -Wno-unused-parameter")
    set(CFLAGS "--std=gnu99")
    set(DFLAGS "-g")
    set(PFLAGS "-g -p")
    set(RFLAGS "-O3")
    
    if (MEMLOG)
        set(CFLAGS "${CFLAGS} -DLAND_MEMLOG")
    endif ()
    
    #string (REGEX REPLACE "widget/" "" exname ${ex})
    set(exname ${ex_bin})

    if (STATIC)
        if (DEBUG OR PROFILE)
            set(LFLAGS "")
            macro(LFLAG f)
                set(LFLAGS "${LFLAGS} ${f}")
            endmacro()
            if (DEBUG)
                set(exe ${exname}-static-debug)
                set(lib ${libname}-static-debug)
                set(flags ${DFLAGS})
            else()
                set(exe ${exname}-static-profile)
                set(lib ${libname}-static-profile)
                set(flags ${PFLAGS})
                LFLAG("-p")
            endif()
            add_executable(${exe} ${example_cfiles})

            pkg_check_modules(ALLEGRO allegro_monolith-debug-static-5)
            
            set(libraries
                ${lib}
                ${ALLEGRO_STATIC_LDFLAGS}
                )
            if (OSX)
                list(APPEND libraries ${OPENGL_LIBRARIES})

                LFLAG("-framework CoreGraphics")
                LFLAG("-framework QuartzCore")
                LFLAG("-framework AudioToolbox")
                LFLAG("-framework OpenAL")
                LFLAG("-framework Foundation")
                LFLAG("-framework CoreFoundation")
                LFLAG("-framework CoreServices")
                LFLAG("-framework IOKit")
                LFLAG("-framework AppKit")
            endif()
            
            set_target_properties(${exe}
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${flags}"
                LINK_FLAGS "${LFLAGS}"
                )

            if (NOT "${ex_sub}" STREQUAL "")
                set_target_properties(${exe} PROPERTIES EXECUTABLE_OUTPUT_PATH ${ex_sub})
            endif()

            target_link_libraries(${exe}
                ${libraries}
                )
        endif (DEBUG OR PROFILE)
        if (RELEASE)
            add_executable(${exname}-static ${example_cfiles})
            set_target_properties(${exname}-static
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
                )
            target_link_libraries(${exname}-static
                ${libname}-static)
        endif (RELEASE)
    endif (STATIC)

    if (SHARED)
        set(AD -debug)
        if (DEBUG)
            add_executable(${exname}-debug ${example_cfiles})
            
            list(APPEND example_exes ${exname}-debug)
            
            set_target_properties(${exname}-debug
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
                )
            target_link_libraries(${exname}-debug
                ${libname}-debug
                yaml
                m
                GL
                )
        endif (DEBUG)
        if (RELEASE)
            add_executable(${exname} ${example_cfiles})
            list(APPEND example_exes ${exname})
            set_target_properties(${exname}
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
                )
            target_link_libraries(${exname}
                ${libname}
                yaml
                )
        endif (RELEASE)
    endif (SHARED)

endforeach(exsrc)

add_custom_target(examples
    DEPENDS ${example_exes})
