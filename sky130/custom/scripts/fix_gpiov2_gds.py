#!/usr/bin/env python3
#
# fix_gpiov2_gds.py ---
#
# Special-purpose script that does the work of what ought to be a simple
# binary diff and patch.  Except that no such thing exists as a standard
# offering on most Linux systems, so instead of adding another OS
# package requirement, I'm just writing a binary search-and-replace in
# python.
#
# The purpose of the patch is to correct the coordinates of the deep nwell
# and nwell layers in the cell amux_switch_1v2b, as the SkyWater cell
# contains DRC errors.
#
# Specifically, DNWELL coordinate (34.450, 0.035) is moved to (34.905, 0.035)
# and NWELL coordinate (35.055, -0.365) is moved to (35.390, -0.365)

import sys

if len(sys.argv) != 2:
    print('Usage:  fix_gpiov2_gds.py <filename>')
    sys.exit(1)
else:
    file_name = sys.argv[1]

orig_data_1    = b'\x00\x00\x86\x92\x00\x00\x00\x23\x00\x00\x86\x92'
replace_data_1 = b'\x00\x00\x88\x59\x00\x00\x00\x23\x00\x00\x88\x59'

orig_data_2    = b'\x00\x00\x88\xef\xff\xff\xff\x8d\x00\x00\x47\xef\xff\xff\xff\x8d'
replace_data_2 = b'\x00\x00\x8a\x3e\x00\x00\x00\x91\x00\x00\x47\xef\x00\x00\x00\x91'

orig_data_3    = b'\x00\x00\x88\xef\xff\xff\xfe\x93\x00\x00\x88\xef\xff\xff\xff\x8d'
replace_data_3 = b'\x00\x00\x8a\x3e\xff\xff\xfe\x93\x00\x00\x8a\x3e\x00\x00\x00\x91'

# This is not efficient, but only needs to be done once.

with open(file_name, 'rb') as ifile:
    data = ifile.read()
    data = data.replace(orig_data_1, replace_data_1)
    data = data.replace(orig_data_2, replace_data_2)
    data = data.replace(orig_data_3, replace_data_3)

# Write back into the same file
with open(file_name, 'wb') as ofile:
    ofile.write(data)

print("Done!")
