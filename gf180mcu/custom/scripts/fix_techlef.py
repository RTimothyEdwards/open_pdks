#!/usr/bin/env python3
#
# fix_techlef ---
#
# This script adds the missing masterslice entries for well and substrate.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the gf180mcu Makefile.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            ltext = inFile.read()
            llines = ltext.splitlines()
    except:
        print('fix_techlef.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    layerrex = re.compile(r'[ \t]*LAYER ([^ \t\n]+)') 

    for line in llines:

        lmatch = layerrex.match(line)
        if lmatch:
            if lmatch.group(1) == 'Poly2':
                fixedlines.append('LAYER Pwell')
                fixedlines.append('    TYPE MASTERSLICE ;')
                fixedlines.append('    PROPERTY LEF58_TYPE "TYPE PWELL ;" ;')
                fixedlines.append('END Pwell')
                fixedlines.append('')
                fixedlines.append('LAYER Nwell')
                fixedlines.append('    TYPE MASTERSLICE ;')
                fixedlines.append('    PROPERTY LEF58_TYPE "TYPE NWELL ;" ;')
                fixedlines.append('END Nwell')
                fixedlines.append('')

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
            print('fix_techlef.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
