#!/usr/bin/env python3
#
# fix_digital_lef ---
#
# This script fixes the issue where the LEF files of the digital standard
# cells used to annotate the GDS for generation of new LEF files from
# magic do not have VNB and VPB pins.  This script adds the annotation
# for port use and port direction.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile.

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
        print('fix_digital_lef.py: failed to open ' + fnmIn + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    endrex = re.compile('[ \t]*END[ \t]+VGND')

    for line in llines:
        fixedlines.append(line)

        # Check for end of VGND pin in file
        ematch = endrex.match(line)
        if ematch:
            fixedlines.append('  PIN VNB')
            fixedlines.append('    DIRECTION INOUT ;')
            fixedlines.append('    USE GROUND ;')
            fixedlines.append('    PORT')
            fixedlines.append('    END')
            fixedlines.append('  END VNB')
            fixedlines.append('  PIN VPB')
            fixedlines.append('    DIRECTION INOUT ;')
            fixedlines.append('    USE POWER ;')
            fixedlines.append('    PORT')
            fixedlines.append('    END')
            fixedlines.append('  END VPB')
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
            print('fix_digital_lef.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
