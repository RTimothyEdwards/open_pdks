cif istyle sky130()
# Ensure unique cell names when reading multiple GDS files
#
# Note 1:  It is not possible to handle a hierarchy of modified
# names when the names haven't been changed in the GDS without
# adding a lot of bookkeeping to magic.  Therefore "gds unique"
# should not be used in conjunction with "gds readonly".
#
# Note 2:  The original issue with name collisions was addressed
# in openRAM, so this should not be needed anyway.
#
# calma unique true
