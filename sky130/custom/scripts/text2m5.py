#!/usr/bin/env python3
#
# text2m5 ---
#
# This script changes magic layouts from the sky130_ml_xx_hd library
# by recasting the layer used from metal1 to metal5, and adding a
# scalefactor of 12 so that the characters are sized to avoid DRC
# errors on metal5.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the library install in the sky130 Makefile.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            spitext = inFile.read()
            spilines = spitext.splitlines()
    except:
        print('text2m5.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # The library is based on sky130A only.  Pick up the name of the PDK variant
    # from the input name (which is four directory levels up from inname)
    variant = inname.split('/')[-5]

    # Process input with regexp

    fixedlines = []
    modified = False

    for line in spilines:

        # These substitutions are for files originating from cells/*/*.spice
        fixedline = re.sub('<< metal1 >>', '<< metal5 >>', line)
        fixedline = re.sub('tech sky130A', 'tech ' + variant + '\nmagscale 12 1', fixedline)

        fixedlines.append(fixedline)
        if fixedline != line:
            modified = True

    # Write output
    if outname == None:
        for i in fixedlines:
            print(i)
    else:
        # If the output is a symbolic link but no modifications have been made,
        # then leave it alone.  If it was modified, then remove the symbolic
        # link before writing.
        if os.path.islink(outname):
            if not modified:
                return 0
            else:
                os.unlink(outname)
        try:
            with open(outname, 'w') as outFile:
                for i in fixedlines:
                    print(i, file=outFile)
        except:
            print('text2m5.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
