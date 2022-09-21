#!/usr/bin/env python3
#
# fix_related_bias_pins.py ---
#
# All of the sky130 standard cell liberty files share an error
# introduced by the audit script, which added "related_bias_pin"
# entries for each cell.  All of them are wrong in that they
# have VPB as the related bias for VGND and VNB as the related
# bias for VPWR.  These need to be swapped.
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
        print('fix_related_bias_pins.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False
    current_pin = ''

    related_re = re.compile('\s*related_bias_pin\s*:\s*"(.+)"\s*;')
    pg_re = re.compile('\s*pg_pin\s*\(\s*"(.+)"\s*\)\s*{')

    for line in slines:
        pmatch = pg_re.match(line)
        if pmatch:
            current_pin = pmatch.group(1)

        rmatch = related_re.match(line)
        if rmatch:
            pin_str = rmatch.group(1)
            if pin_str == 'VPB' and current_pin == 'VGND':
                modified = True
                line = line.replace(pin_str, 'VNB')
            elif pin_str == 'VNB' and current_pin == 'VPWR':
                modified = True
                line = line.replace(pin_str, 'VPB')
            else:
                print('Warning: Unknown related bias pin ' + pin_str)
            current_pin = ''

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
            print('fix_related_bias_pins.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
