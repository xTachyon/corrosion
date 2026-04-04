cmake_minimum_required(VERSION 3.21)

project(the_build)

add_executable(the_bin main.cpp)

# -------

function(do_target name path)
    set(binary_path ${CMAKE_BINARY_DIR}/cargo/debug/${CMAKE_STATIC_LIBRARY_PREFIX}${name})
    set(output_path "${binary_path}${CMAKE_STATIC_LIBRARY_SUFFIX}")
    set(depfile_path "${binary_path}.d")
    add_custom_command(
        OUTPUT ${output_path}
        DEPFILE ${depfile_path}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/cargo
        VERBATIM
        COMMAND
            cargo build
                -p ${name}
                --manifest-path=${path}/Cargo.toml
                --target-dir=${CMAKE_BINARY_DIR}/cargo
    )

    if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(extra_libs
            Ntdll.lib
        )
    endif()

    add_library(
        ${name} INTERFACE
        ${output_path}
    )
    target_link_libraries(${name} INTERFACE ${output_path} ${extra_libs})
endfunction()

# -------

do_target(rust_lib ${CMAKE_SOURCE_DIR}/rust_lib)
target_link_libraries(the_bin rust_lib)
