#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "apriltag" for configuration ""
set_property(TARGET apriltag APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(apriltag PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libapriltag.so.3.0.0"
  IMPORTED_SONAME_NOCONFIG "libapriltag.so.3"
  )

list(APPEND _IMPORT_CHECK_TARGETS apriltag )
list(APPEND _IMPORT_CHECK_FILES_FOR_apriltag "${_IMPORT_PREFIX}/lib/libapriltag.so.3.0.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
