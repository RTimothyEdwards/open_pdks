# Special options passed to magic for GDS import of the I/O library cells.
# This line flattens all the cells containing "__example_" in the name,
# which includes all contacts and primitive devices.  This prevents the
# primitive devices from being split across the hierarchy, which causes
# magic to misinterpret the device type.
gds flatglob *__example_*
