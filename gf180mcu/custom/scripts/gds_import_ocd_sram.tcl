# Set GDS import styles as needed to deal with the Open Circuit Design
# SRAM layouts.  The SRAM layouts within the library are validated
# directly from the magic version.  Therefore do *not* use the default
# "gds flatten true" because it messes with the hierarchy and produces
# a result that has not been directly validated.
gds flatten false
