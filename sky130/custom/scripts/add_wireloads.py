#!/usr/bin/env python3
#
# add_wireloads ---
#
# This script adds wireload models to the digital standard cell library
# liberty timing files.  No wireload models were provided with the
# foundry set.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the lib install in the sky130 Makefile.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            stext = inFile.read()
            slines = stext.splitlines()
    except:
        print('add_wireloads.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    lutrex = re.compile('[ \t]*power_lut_template.*')

    for line in slines:

        # Check for first power_lut_template
        lmatch = lutrex.match(line)
        if lmatch and not modified:
            # Read and add the contents of "wireload.lib"
            with open('custom/scripts/wireload.lib', 'r') as libFile:
                ltext = libFile.read()
                for lline in ltext.splitlines():
                    fixedlines.append(lline)

            modified = True

        fixedlines.append(line)

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
            print('add_wireloads.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
