#!/usr/bin/env python3
#
# fix_vddio_overlay_gds.py ---
#
# Special-purpose script that does the work of what ought to be a simple
# binary diff and patch.  Except that no such thing exists as a standard
# offering on most Linux systems, so instead of adding another OS
# package requirement, I'm just writing a binary search-and-replace in
# python.
#
# The purpose of the patch is to narrow down the metal 3 area under
# the vias in this cell to clear the metal3 resistor marker that has
# been added to the base cell.  Since the overlay just duplicates the
# metal 3 layer, this has no impact on the physical mask geometry.
#

import sys

if len(sys.argv) != 2:
    print('Usage:  fix_vddio_overlay_gds.py <filename>')
    sys.exit(1)
else:
    file_name = sys.argv[1]

# Convert this data
orig_data_0 = b'\x00\x00\x01\xef\x00\x00\xfa\x5a\x00\x00\x01\xef\x00\x01\x0b\xb2\x00\x00\x5f\x4b\x00\x01\x0b\xb2\x00\x00\x5f\x4b\x00\x00\xfa\x5a\x00\x00\x01\xef'

# To this data (move X position 24395 to 24370), (move X position 495 to 520)
new_data_0 = b'\x00\x00\x02\x08\x00\x00\xfa\x5a\x00\x00\x02\x08\x00\x01\x0b\xb2\x00\x00\x5f\x32\x00\x01\x0b\xb2\x00\x00\x5f\x32\x00\x00\xfa\x5a\x00\x00\x02\x08'

# Convert this data

# Convert this data
orig_data_1 = b'\x00\x00\xc4\xd6\x00\x00\xfa\x5a\x00\x00\xc4\xd6\x00\x01\x0b\xb2\x00\x01\x22\x32\x00\x01\x0b\xb2\x00\x01\x22\x32\x00\x00\xfa\x5a\x00\x00\xc4\xd6'

# To this data (move X position 50390 to 50415), (move X position 74290 to 74265)
new_data_1 = b'\x00\x00\xc4\xef\x00\x00\xfa\x5a\x00\x00\xc4\xef\x00\x01\x0b\xb2\x00\x01\x22\x19\x00\x01\x0b\xb2\x00\x01\x22\x19\x00\x00\xfa\x5a\x00\x00\xc4\xef'


# This is not efficient, but only needs to be done once.

with open(file_name, 'rb') as ifile:
    data = ifile.read()
    data = data.replace(orig_data_0, new_data_0)
    data = data.replace(orig_data_1, new_data_1)

# Write back into the same file
with open(file_name, 'wb') as ofile:
    ofile.write(data)

print("Done!")
