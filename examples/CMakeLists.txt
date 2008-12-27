cmake_minimum_required (VERSION 2.6)
 
cmake_policy(SET CMP0009 NEW) # fon't follow symlinks
include_directories(${CMAKE_BINARY_DIR}/c)
include_directories(${CMAKE_BINARY_DIR}/examples/c)

#_______________________________________________________________________
# Step 1: Find all .py source files.
#

file(GLOB examples RELATIVE ${CMAKE_SOURCE_DIR}/examples */src)
foreach(exsrc ${examples})
    get_filename_component(ex ${exsrc} PATH)
    file(GLOB_RECURSE example_pyfiles RELATIVE ${CMAKE_SOURCE_DIR}/examples ${ex}/*.py)

    #_______________________________________________________________________
    # Step 2: Rules to create .c and .h files.
    #
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

    set(WFLAGS "-W -Wall")
    set(WFLAGS "${WFLAGS} -Wno-unused-parameter")
    set(CFLAGS "--std=gnu99")
    set(DFLAGS "-g")
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
                alld-4.3.11 alld_unsharable agld
                fudgefontd ldpng logg
                png jpeg ogg vorbis vorbisfile)
        endif (DEBUG)
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
                alld-4.3.11 alld_unsharable agld
                fudgefontd ldpng logg
                png jpeg ogg vorbis vorbisfile)
        endif (DEBUG)
        if (RELEASE)
            add_executable(${ex} ${example_cfiles})
            set_target_properties(${ex}
                PROPERTIES
                COMPILE_FLAGS "${CFLAGS} ${WFLAGS} ${RFLAGS}"
                )
            target_link_libraries(${ex}
                land
                alleg-4.3.11 alleg_unsharable agl
                fudgefont ldpng logg
                png jpeg ogg vorbis vorbisfile)
        endif (RELEASE)
    endif (SHARED)

endforeach(exsrc)
