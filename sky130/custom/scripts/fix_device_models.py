#!/usr/bin/env python3
#
# fix_device_models ---
#
# This script fixes the issue where devices in the digital libraries did
# not get the proper name conversion;  specifically, the "conb" cell has
# resistor type "short" which should be "sky130_fd_pr__res_generic_po",
# and the pw2nd device model name is missing the suffix "_05v5".
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
            stext = inFile.read()
            slines = stext.splitlines()
    except:
        print('fix_device_models.py: failed to open ' + fnmIn + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    dioderex = re.compile('.*[ \t]+sky130_fd_pr__diode_pw2nd[ \t]+')
    ndioderex = re.compile('.*[ \t]+ndiode_h[ \t]+')
    shortrex = re.compile('.*[ \t]+short[ \t]+')

    for line in slines:

        # Check for incorrect diode reference
        dmatch = dioderex.match(line)
        # Check for incorrect HVL diode ("ndiode_h") reference
        nmatch = ndioderex.match(line)
        # Check for incorrect resistor reference
        smatch = shortrex.match(line)
        if dmatch:
            fline = re.sub('pw2nd', 'pw2nd_05v5', line)
            fline = re.sub('^X', 'D', fline)
            fline = re.sub('a=', 'area=', fline)
            fline = re.sub('p=', 'pj=', fline)
            fixedlines.append(fline)
            modified = True
        elif nmatch:
            fline = re.sub('ndiode_h', 'sky130_fd_pr__diode_pw2nd_11v0', line)
            fline = re.sub('^X', 'D', fline)
            fline = re.sub('a=', 'area=', fline)
            fline = re.sub('p=', 'pj=', fline)
            fixedlines.append(fline)
            modified = True
        elif smatch:
            fline = re.sub(' VNB short', ' sky130_fd_pr__res_generic_po', line)
            fline = re.sub('short', 'sky130_fd_pr__res_generic_po', fline)
            fline = re.sub('^X', 'R', fline)
            fixedlines.append(fline)
            modified = True
        else:
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
            print('fix_device_models.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
