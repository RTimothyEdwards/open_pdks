#!/usr/bin/env python3
#
# convert_sc_cdl.py ---
#
# This script converts the GF CDL for the standard cells to turn them into
# valid SPICE (ngspice) syntax, using regular expression parsing.

# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            spitext = inFile.read()
            # (Don't) unwrap continuation lines
            # spilines = spitext.replace('\n+', ' ').splitlines()
            spilines = spitext.splitlines()
    except:
        print('convert_sc_cdl.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    fixedlines = []
    modified = False

    for line in spilines:
        fixedline = line

        # 1) Lines starting with M --> change to X
        fixedline = re.sub('^M', 'X', fixedline, flags=re.IGNORECASE)
        # 2) 5V transistor models --> change to 6V
        fixedline = re.sub('_05v0', '_06v0', fixedline, flags=re.IGNORECASE)
	# 3) Uppercase diode "d" for consistency
        fixedline = re.sub('^d', 'D', fixedline)
	# 4) Convert $m to M
        fixedline = re.sub('\$m=', 'M=', fixedline, flags=re.IGNORECASE)
	# 5) Fix incorrect endcap (endcap does not have VNW VPW)
        fixedline = re.sub('endcap VDD VNW VPW', 'endcap VDD', fixedline, flags=re.IGNORECASE)

        if line != fixedline:
            modified = True
        fixedlines.append(fixedline)

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
            print('convert_sc_cdl.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
