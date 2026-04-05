cmake_minimum_required(VERSION 3.21)

project(the_build)


# -------

function(_corrosion_import_crate crate_name manifest_path rustc_targets)
    set(default_build_type_dir "$<IF:$<OR:$<CONFIG:Debug>,$<CONFIG:>>,debug,release>")
    set(binary_path ${CMAKE_BINARY_DIR}/cargo/${default_build_type_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}${crate_name})
    set(output_path "${binary_path}${CMAKE_STATIC_LIBRARY_SUFFIX}")
    set(depfile_path "${binary_path}.d")

    set(rustc_targets_flag "")
    foreach (t IN LISTS rustc_targets)
        if (t STREQUAL "a")
            continue()
        endif()
        set(rustc_targets_flag "${rustc_targets_flag} --target ${t}")
    endforeach()

    add_custom_command(
        OUTPUT ${output_path}
        DEPFILE ${depfile_path}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/cargo
        VERBATIM
        USES_TERMINAL
        JOB_SERVER_AWARE ON
        COMMAND
            cargo build
                --package ${crate_name}
                $<IF:$<CONFIG:Debug>,--profile=dev,--profile=release>
                --manifest-path=${manifest_path}
                --target-dir=${CMAKE_BINARY_DIR}/cargo
                ${rustc_targets_flag}
                # -q
    )

    if (CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(extra_libs
            Ntdll.lib
            Ws2_32.lib
            Userenv.lib
        )
    endif()

    add_library(
        ${crate_name} INTERFACE
        ${output_path}
    )
    target_link_libraries(${crate_name} INTERFACE ${output_path} ${extra_libs})
endfunction()

function(corrosion_import_crate)
    set(OPTIONS)
    set(ONE_VALUE_KEYWORDS MANIFEST_PATH)
    set(MULTI_VALUE_KEYWORDS CRATES RUSTC_TARGETS)
    cmake_parse_arguments(ARG
        "${OPTIONS}"
        "${ONE_VALUE_KEYWORDS}"
        "${MULTI_VALUE_KEYWORDS}"
        ${ARGN}
    )
    if (NOT ARG_RUSTC_TARGETS)
        set(ARG_RUSTC_TARGETS a)
    endif()

    get_cmake_property(IS_MULTI_CONFIG GENERATOR_IS_MULTI_CONFIG)

    if (IS_MULTI_CONFIG)
        set(configs ${CMAKE_CONFIGURATION_TYPES})
    else()
        set(configs ${CMAKE_BUILD_TYPE})
    endif()

    foreach(crate_name IN LISTS ARG_CRATES)
        _corrosion_import_crate(${crate_name} ${ARG_MANIFEST_PATH} ${ARG_RUSTC_TARGETS})
    endforeach()
    
endfunction()

# -------

if (CMAKE_OSX_ARCHITECTURES)
    set(rustc_targets RUSTC_TARGETS aarch64-apple-darwin x86_64-apple-darwin)
endif()

corrosion_import_crate(
    MANIFEST_PATH ${CMAKE_SOURCE_DIR}/rust_lib/Cargo.toml
    CRATES rust_lib
    ${rustc_targets}
)

add_executable(the_bin main.cpp)
target_link_libraries(the_bin rust_lib)

# cmake .. -DCMAKE_CONFIGURATION_TYPES="Debug;Release" -DCMAKE_DEFAULT_CONFIGS="Debug;Release" -DCMAKE_CROSS_CONFIGS="Debug;Release" -G "Ninja Multi-Config"