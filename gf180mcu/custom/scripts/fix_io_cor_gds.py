#!/usr/bin/env python3
#
# fix_io_cor_gds.py ---
#
# The purpose of this filter is to add the isolated substrate layer
# (GDS layer 23:5) to the ESD_CLAMP_COR cell, which is the only way to
# get the cell to be LVS-correct at that level of hierarchy.  The layer
# is simply copied down from further up in the hierarchy.  There is no
# mask change to the corner cell itself, but the change allows the corner
# cell to be read back from GDS, extract, and pass LVS.

import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'rb') as inFile:
            data = inFile.read()
    except:
        print('fix_io_cor_gds.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # orig_data is the STRNAME record for ESD_CLAMP_COR.  Insert the isosub layer
    # data after this record.
    orig_data = b'\x00\x12\x06\x06\x45\x53\x44\x5f\x43\x4c\x41\x4d\x50\x5f\x43\x4f\x52\x00'

    append_data = b'\x00\x04\x08\x00\x00\x06\x0d\x02\x00\x17\x00\x06\x0e\x02\x00\x05\x00\x3c\x10\x03\xff\xff\xff\x2e\x00\x03\x48\x2d\xff\xff\xff\x2e\x00\x04\x5b\xd2\x00\x04\x47\xf5\x00\x04\x5b\xd2\x00\x04\x47\xf5\x00\x04\x42\x14\x00\x04\x5a\x65\x00\x04\x42\x14\x00\x04\x5a\x65\x00\x03\x48\x2d\xff\xff\xff\x2e\x00\x03\x48\x2d\x00\x04\x11\x00'

    # This is not efficient, but only needs to be done once.
    # Avoid doing it to any file other than the corner I/O.

    if '__cor' in inname:
        data = data.replace(orig_data, orig_data + append_data)

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
        print('fix_io_cor_gds.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
