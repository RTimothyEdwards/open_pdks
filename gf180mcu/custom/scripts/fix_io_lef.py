#!/usr/bin/env python3
#
# fix_io_lef ---
#
# This script fixes the issue where the LEF macros of the I/O cells
# are missing ports in the position of the wirebond pads, or the ports
# do not include the entire pad area.  This script inserts an extra
# port rectangle at the position of the pad on all top-level I/O cells
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the gf180mcu Makefile.

import re
import os
import sys

def filter(inname, outname):

    # Read input.  Note that there is only one LEF file for the I/O library.
    try:
        with open(inname, 'r') as inFile:
            ltext = inFile.read()
            llines = ltext.splitlines()
    except:
        print('fix_io_lef.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Map the input file name to the metal layer of the pad.
    # The file names end in _3lm.lef, _4lm.lef, and _5lm.lef, so pick up the
    # 7th character from the end.
    mlayer = 'Metal' + inname[-7]

    # The following macros need pad ports
    fixmacros = ['GF_NI_ASIG_5P0', 'GF_NI_BI_24T', 'GF_NI_BI_T', 'GF_NI_DVDD',
		 'GF_NI_DVSS', 'GF_NI_IN_C', 'GF_NI_IN_S']

    # Pin name for the pad port corresponding to each of the above macros
    fixpins = ['ASIG5V', 'PAD', 'PAD', 'DVDD', 'DVSS', 'PAD', 'PAD']

    # Process input with regexp

    fixedlines = []
    modified = False

    macrorex = re.compile('[ \t]*MACRO[ \t]+([^ \t\n]+)')
    pinrex = re.compile('[ \t]*PIN[ \t]+([^ \t\n]+)')
    userex = re.compile('[ \t]*USE[ \t]+([^ \t\n]+)')
    endrex = re.compile('[ \t]*END[ \t]+([^ \t\n]+)')

    macroidx = -1
    pinidx = -1
    pin = None
    for line in llines:
        fixedlines.append(line)

        # Check for macro end
        if macroidx >= 0:
            ematch = endrex.match(line)
            if ematch:
                macroidx = -1
                pinidx = -1

        # Check for 'MACRO' record, and get name of the macro.
        mmatch = macrorex.match(line)
        if mmatch:
            macroname = mmatch.group(1)
            if macroname in fixmacros:
                macroidx = fixmacros.index(macroname)

        # Check for pin
        if macroidx >= 0:
            pmatch = pinrex.match(line)
            if pmatch:
                if pmatch.group(1) == fixpins[macroidx]:
                    pinidx = macroidx

        if pinidx >= 0:
            umatch = userex.match(line)
            if umatch:
                # Add the extra port
                fixedlines.append('      PORT')
                fixedlines.append('      LAYER ' + mlayer + ' ;')
                fixedlines.append('      RECT 7.5 2.0 67.5 62.0 ;')
                fixedlines.append('      END')
                pinidx = -1
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
            print('fix_io_lef.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
