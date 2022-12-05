#!/usr/bin/env python3
#
# fix_sram_gds.py ---
#
# Special-purpose script that does the work of what ought to be a simple
# binary diff and patch.  Except that no such thing exists as a standard
# offering on most Linux systems, so instead of adding another OS
# package requirement, I'm just writing a binary search-and-replace in
# python.
#
# The purpose of the patch is to modify the PPLUS (31:0) layer in cell
# ypass_gate_* to correctly surround the DIFF instead of being offset,
# and to add the same layer to ypass_gate_a_* where it is missing
# entirely (the SRAM was at some point modified by GF by incorrectly
# patching the layer at the top level cell, which fixes the problem,
# but not in a proper way, and not in a way that allows Magic to read
# and extract the hierarchical layout).
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
        print('fix_sram_gds.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # orig_data looks for the PPLUS layer in the existing ypass_gate_* cell

    orig_data = b'\x00\x04\x08\x00\x00\x06\x0d\x02\x00\x1f\x00\x06\x0e\x02\x00\x00\x00\x2c\x10\x03\x00\x00\x00\x00\x00\x00\xa8\xac\x00\x00\x00\x00\x00\x00\xea\x83\x00\x00\x0e\x79\x00\x00\xea\x83\x00\x00\x0e\x79\x00\x00\xa8\xac\x00\x00\x00\x00\x00\x00\xa8\xac\x00\x04\x11\x00'

    # replace_data modifies the layer position to surround the diffusion

    replace_data = b'\x00\x04\x08\x00\x00\x06\x0d\x02\x00\x1f\x00\x06\x0e\x02\x00\x00\x00\x2c\x10\x03\xff\xff\xfc\xea\x00\x00\xc9\xa9\xff\xff\xfc\xea\x00\x00\xe9\xac\x00\x00\x0e\x79\x00\x00\xe9\xac\x00\x00\x0e\x79\x00\x00\xc9\xa9\xff\xff\xfc\xea\x00\x00\xc9\xa9\x00\x04\x11\x00'

    # orig_data2 is the first occurrence of layer datatype 31:0 in ypass_gate_a*

    orig_data2 = b'\x00\x04\x08\x00\x00\x06\x0d\x02\x00\x1f\x00\x06\x0e\x02\x00\x00\x00\x2c\x10\x03\x00\x00\x01\xe0\x00\x00\x63\x15\x00\x00\x01\xe0\x00\x00\x69\x7d\x00\x00\x09\x74\x00\x00\x69\x7d\x00\x00\x09\x74\x00\x00\x63\x15\x00\x00\x01\xe0\x00\x00\x63\x15\x00\x04\x11\x00'

    # This is not efficient, but only needs to be done once.

    data = data.replace(orig_data, replace_data)
    data = data.replace(orig_data2, orig_data2 + replace_data)

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
        print('fix_sram_gds.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
