#!/usr/bin/env python3
#
# fix_stdcell_gds.py ---
#
# Special-purpose script that does the work of what ought to be a simple
# binary diff and patch.  Except that no such thing exists as a standard
# offering on most Linux systems, so instead of adding another OS
# package requirement, I'm just writing a binary search-and-replace in
# python.
#
# The purpose of the patch is to add text for the VNW and VPW well and
# substrate connections in the standard cell layouts (except for filltie
# and endcap, which connect them to VDD and VSS), using custom GDS layer:
# purpose pairs since the foundry does not define text layers for nwell
# and pwell.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the gf180mcu Makefile.

import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'rb') as inFile:
            data = inFile.read()
    except:
        print('fix_stdcell_gds.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # orig_data looks for the label that appears in every standard cell layout that
    # has the text "& Metric 1.00".

    orig_data   = b'\x00\x12\x19\x06\x26\x20\x4d\x65\x74\x72\x69\x63\x20\x31\x2e\x30\x30\x00\x00\x04\x11\x00'

    # replace_data appends two text labels after the "& Metric 1.00", one on custom
    # layer:purpose 21:10 with text "VNW" and one on custom layer:purpose 204:10
    # with text "VPW", both at scale 0.25 (um).
    replace_data = b'\x00\x12\x19\x06\x26\x20\x4d\x65\x74\x72\x69\x63\x20\x31\x2e\x30\x30\x00\x00\x04\x11\x00\x00\x04\x0c\x00\x00\x06\x0d\x02\x00\x15\x00\x06\x16\x02\x00\x0a\x00\x06\x17\x01\x00\x05\x00\x06\x1a\x01\x00\x00\x00\x0c\x1b\x05\x40\x33\x33\x33\x33\x34\x00\x00\x00\x0c\x10\x03\x00\x00\x01\x59\x00\x00\x0f\x50\x00\x08\x19\x06\x56\x4e\x57\x00\x00\x04\x11\x00\x00\x04\x0c\x00\x00\x06\x0d\x02\x00\xcc\x00\x06\x16\x02\x00\x0a\x00\x06\x17\x01\x00\x05\x00\x06\x1a\x01\x00\x00\x00\x0c\x1b\x05\x40\x33\x33\x33\x33\x34\x00\x00\x00\x0c\x10\x03\x00\x00\x01\x54\xff\xff\xff\xab\x00\x08\x19\x06\x56\x50\x57\x00\x00\x04\x11\x00'

    # This is not efficient, but only needs to be done once.

    # Ignore cells "filltie" and "endcap"
    if 'filltie' not in inname and 'endcap' not in inname:
        data = data.replace(orig_data, replace_data)

    # If the output is a symbolic link but no modifications have been made,
    # then leave it alone.  If it was modified, then remove the symbolic
    # link before writing.
    if os.path.islink(outname):
        os.unlink(outname)

    # Write output
    try:
        with open(outname, 'wb') as ofile:
            ofile.write(data)
    except:
        print('fix_stdcell_gds.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
        return 1


if __name__ == '__main__':

    # This script expects to get one or two arguments.  One argument is
    # mandatory and is the input file.  The other argument is optional and
    # is the output file.  The output file and input file may be the same
    # name, in which case the original input is overwritten.

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item[1:])
        else:
            arguments.append(item)

    if len(arguments) > 0:
        infilename = arguments[0]

    if len(arguments) > 1:
        outfilename = arguments[1]
    else:
        outfilename = None

    result = filter(infilename, outfilename)
    sys.exit(result)
