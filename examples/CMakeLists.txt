cmake_minimum_required (VERSION 2.6)
 
cmake_policy(SET CMP0009 NEW) # don't follow symlinks
include_directories(${CMAKE_BINARY_DIR}/c)
include_directories(${CMAKE_BINARY_DIR}/examples/c)

# FIXME: Should be auto-detected or specified by user instead.
include_directories(/home/elias/prog/allegro/install/include)
link_directories(/home/elias/prog/allegro/install/lib)

#_______________________________________________________________________
# Step 1: Find all .py source files.
#

set(example_exes)
file(GLOB examples RELATIVE ${CMAKE_SOURCE_DIR}/examples */src RELATIVE ${CMAKE_SOURCE_DIR}/examples */*/src)
foreach(exsrc ${examples})
    get_filename_component(ex ${exsrc} PATH)
    
    message(STATUS "Example found: ${ex}")

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
    
    string (REGEX REPLACE "widget/" "" exname ${ex})

    if (STATIC)
        if (DEBUG)
            add_executable(${exname}-static-debug ${example_cfiles})
            set_target_properties(${exname}-static-debug
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
                )
            target_link_libraries(${exname}-static-debug
                ${libname}-static-debug
                allegro_monolith-debug-static-${AV}
                z
                png
                jpeg
                m
                GL
                Xinerama
                Xcursor
                freetype
                )
        endif (DEBUG)
        if (PROFILE)
            add_executable(${exname}-static-profile ${example_cfiles})
            set_target_properties(${exname}-static-profile
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${PFLAGS}"
                LINK_FLAGS -p
                )
            target_link_libraries(${exname}-static-profile
                ${libname}-static-profile
                allegro_monolith-profile-static-${AV}
                z
                png
                jpeg
                m
                GL
                Xinerama
                Xcursor
                freetype
                )
        endif (PROFILE)
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
