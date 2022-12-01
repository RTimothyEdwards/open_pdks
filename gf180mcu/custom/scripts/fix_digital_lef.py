#!/usr/bin/env python3
#
# fix_digital_lef ---
#
# This script fixes the issue where the LEF files of the digital standard
# cells do not have VNW and VPW pins.  This script adds the pin entries
# for these pins.
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
        print('fix_digital_lef.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    endrex = re.compile('[ \t]*END[ \t]+VSS')
    macrorex = re.compile('^MACRO[ \t]+([^ \t\n]+)')
    macroname = None

    for line in llines:

        # Check for MACRO line and record the macro name
        # NOTE:  The "filltie" and "endcap" cells connect the biases to
	# the power supplies and must be excluded from this modification.

        mmatch = macrorex.match(line)
        if mmatch:
            macroname = mmatch.group(1)

        fixedlines.append(line)

        # Check for end of VSS pin in file
        ematch = endrex.match(line)
        if ematch and 'filltie' not in inname and 'endcap' not in inname:
            fixedlines.append('  PIN VPW')
            fixedlines.append('    DIRECTION INOUT ;')
            fixedlines.append('    USE ground ;')
            fixedlines.append('    PORT')
            fixedlines.append('       LAYER Pwell ;')
            fixedlines.append('         RECT 0.05 -0.25 0.55 0.25 ;')
            fixedlines.append('    END')
            fixedlines.append('  END VPW')
            fixedlines.append('  PIN VNW')
            fixedlines.append('    DIRECTION INOUT ;')
            fixedlines.append('    USE power ;')
            fixedlines.append('    PORT')
            fixedlines.append('       LAYER Nwell ;')
            fixedlines.append('         RECT 0.05 3.67 0.55 4.17 ;')
            fixedlines.append('    END')
            fixedlines.append('  END VNW')
            modified = True
            macroname = None

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
