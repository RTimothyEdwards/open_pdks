#!/usr/bin/env python3
#
# fix_serxtors_cdl ---
#
# This script fixes problems in SkyWater HD library cells CDL netlists
# where transistor gates in series use M=2 incorrectly.
# The topology on the left is what is implemented in the CDL, while the
# topology on the right is what's actually in the layout:
#
#               |   |               |   |
#               |   |               |   |
#             ---   ---           ---   ---
#             |       |           |       |
#           --|       |--       --|       |--
#             |       |           |       |
#             ---   ---           ---   ---
#               |   |               |   |
#               |---|               |   |
#               |   |               |   |
#             ---   ---           ---   ---
#             |       |           |       |
#           --|       |--       --|       |--
#             |       |           |       |
#             ---   ---           ---   ---
#               |   |               |   |
#               |   |               |   |
#
# The four (known) cells with this error are (sky130_fd_sc_hd__ +):
# a21o_4, o21a_4, a21bo_4, and a211o_4.

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
        print('fix_serxtors_cdl.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    errcells = [
	'sky130_fd_sc_hd__a21o_4',
	'sky130_fd_sc_hd__o21a_4',
	'sky130_fd_sc_hd__a21bo_4',
	'sky130_fd_sc_hd__a211o_4']

    fixedlines = []
    modified = False
    inmacro = False
    extor = False

    # NOTE:  All occurrences of this error are at pin A1
    # and the node is always "sndA1" ("s" for "series")

    for line in spilines:
        if inmacro == True:
            if '.ENDS ' in line:
                inmacro = False
                fixedlines.append(line)
            elif inmacro == True and 'sndA1' in line:
                extor = True
                fixedline = line.replace(' m=2', '')
                fixedlines.append(fixedline)
                saveline = fixedline.replace('sndA1', 'snd2A1').replace('MMPA', 'MMPA2').replace('MMNA', 'MMNA2')
                modified = True
            elif inmacro == True and 'pndB' in line:
                extor = True
                fixedline = line.replace(' m=2', '')
                fixedlines.append(fixedline)
                saveline = fixedline.replace('pndB', 'pnd2B').replace('MMPB', 'MMPB2').replace('MMPC', 'MMPC2')
                modified = True
            elif extor == True:
                fixedlines.append(line)
                fixedlines.append(saveline)
                fixedlines.append(line)
                extor = False
            else:
                fixedlines.append(line)
        elif '.SUBCKT ' in line:
            for cell in errcells:
                if cell in line:
                    inmacro = True
            fixedlines.append(line)
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
            print('fix_serxtors_cdl.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
