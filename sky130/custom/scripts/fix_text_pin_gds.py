#!/usr/bin/env python3
#
# fix_text_pin_gds.py ---
#
# Reverses the text and pin purposes in a file;  corrects older files
# built from magic based on the documented purposes.  Changes files to
# the actual usage, which is purpose 5 for pin, and purpose 16 for text.
#

import sys

if len(sys.argv) != 2:
    print('Usage:  fix_vssio_overlay_gds.py <filename>')
    sys.exit(1)
else:
    file_name = sys.argv[1]

# rendered text:
#------------------------------------------------------------------------------
#   0x0006     # RECORD_LENGTH              Bytes of data in this record
#   0x16       # RECORD_TYPE:  TEXTTYPE     Texttype specification
#   0x02       # DATA_TYPE:    INTEGER_2    Two byte signed integer
#   0x0010     # DATA: 16
#
#   0x0006     # RECORD_LENGTH              Bytes of data in this record
#   0x17       # RECORD_TYPE:  PRESENTATION Text origin and font specification
#------------------------------------------------------------------------------
# and standard text:
#------------------------------------------------------------------------------
#   0x0006     # RECORD_LENGTH              Bytes of data in this record
#   0x16       # RECORD_TYPE:  TEXTTYPE     Texttype specification
#   0x02       # DATA_TYPE:    INTEGER_2    Two byte signed integer
#   0x0010     # DATA: 16

#   0x000c     # RECORD_LENGTH              Bytes of data in this record
#   0x10       # RECORD_TYPE:  XY           An array of XY coordinates
#   0x03       # DATA_TYPE:    INTEGER_4    Four byte signed integer
#------------------------------------------------------------------------------


# Convert this data
orig_data_0 = b'\x00\x06\x16\x02\x00\x10\x00\x06\x17\x01'

# To this data (change purpose type 16 to type 5)
new_data_0 = b'\x00\x06\x16\x02\x00\x05\x00\x06\x17\x01'

# Convert this data
orig_data_1 = b'\x00\x06\x16\x02\x00\x10\x00\x0c\x10\x03'

# To this data (change purpose type 16 to type 5)
new_data_1 = b'\x00\x06\x16\x02\x00\x05\x00\x0c\x10\x03'

# This is not efficient, but only needs to be done once.

with open(file_name, 'rb') as ifile:
    data = ifile.read()
    data = data.replace(orig_data_0, new_data_0)
    data = data.replace(orig_data_1, new_data_1)

# Write back into the same file
with open(file_name, 'wb') as ofile:
    ofile.write(data)

print("Done!")
