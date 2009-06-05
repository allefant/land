cmake_minimum_required (VERSION 2.6)
 
cmake_policy(SET CMP0009 NEW) # don't follow symlinks
include_directories(${CMAKE_BINARY_DIR}/examples/c)
include_directories(${CMAKE_BINARY_DIR}/examples/c)

# FIXME: Should be auto-detected or specified by user instead.
include_directories(/home/elias/prog/allegro/install4.9/include)
link_directories(/home/elias/prog/allegro/install4.9/lib)

#_______________________________________________________________________
# Step 1: Find all .py source files.
#

set(example_exes)
file(GLOB examples RELATIVE ${CMAKE_SOURCE_DIR}/examples */src)
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
            COMMAND scramble.py
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

    set(AV "4.9.11")
    set(WFLAGS "-W -Wall")
    set(WFLAGS "${WFLAGS} -Wno-unused-parameter")
    set(CFLAGS "--std=gnu99")
    set(DFLAGS "-g")
    set(PFLAGS "-g -p")
    set(RFLAGS "-O3")

    if (STATIC)
        if (DEBUG)
            add_executable(${ex}-static-debug ${example_cfiles})
            set_target_properties(${ex}-static-debug
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
                )
            target_link_libraries(${ex}-static-debug
                land-static-debug
                allegro-debug-static-${AV}
                a5_font-debug-static-${AV}
                a5_ttf-debug-static-${AV}
                a5_primitives-debug-static-${AV}
                a5_iio-debug-static-${AV}
                a5_color-debug-static-${AV}
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
            add_executable(${ex}-static-profile ${example_cfiles})
            set_target_properties(${ex}-static-profile
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${PFLAGS}"
                LINK_FLAGS -p
                )
            target_link_libraries(${ex}-static-profile
                land-static-profile
                allegro-profile-static-${AV}
                a5_font-profile-static-${AV}
                a5_ttf-profile-static-${AV}
                a5_primitives-profile-static-${AV}
                a5_iio-profile-static-${AV}
                a5_color-profile-static-${AV}
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
            add_executable(${ex}-static ${example_cfiles})
            set_target_properties(${ex}-static
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
                )
            target_link_libraries(${ex}-static
                land-static

                alleg-4.3.11 alleg_unsharable agl
                fudgefont ldpng logg
                png jpeg ogg vorbis vorbisfile)
        endif (RELEASE)
    endif (STATIC)

    if (SHARED)
        if (DEBUG)
            add_executable(${ex}-debug ${example_cfiles})
            set_target_properties(${ex}-debug
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${DFLAGS}"
                )
            target_link_libraries(${ex}-debug
                land-debug
                allegro-debug-${AV}
                a5_font-debug-${AV}
                a5_ttf-debug-${AV}
                a5_primitives-debug-${AV}
                a5_iio-debug-${AV}
                a5_color-debug-${AV}
                a5_acodec-debug-${AV}
                kcm_audio-debug-${AV}
                )
        endif (DEBUG)
        if (RELEASE)
            add_executable(${ex} ${example_cfiles})
            list(APPEND example_exes ${ex})
            set_target_properties(${ex}
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
                )
            target_link_libraries(${ex}
                land
                allegro-${AV}
                a5_font-${AV}
                a5_primitives-${AV}
                )
        endif (RELEASE)
    endif (SHARED)

endforeach(exsrc)

add_custom_target(examples
    DEPENDS ${example_exes})
