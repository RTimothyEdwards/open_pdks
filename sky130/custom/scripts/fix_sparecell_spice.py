#!/usr/bin/env python3
#
# fix_sparecell_spice ---
#
# This script fixes problems in the SkyWater HD library "macro_sparecell".
# The pin order of the instances in the macro are incorrect and need to be
# reordered to match the pin order of the individual standard cells in the
# macro.
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
            spitext = inFile.read()
            # (Don't) unwrap continuation lines
            # spilines = spitext.replace('\n+', ' ').splitlines()
            spilines = spitext.splitlines()
    except:
        print('fix_sparecell_spice.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    
    macrolines = [
	'Xsky130_fd_sc_hd__nand2_2_0 LO LO VGND VNB VPB VPWR sky130_fd_sc_hd__nor2_2_0/B',
	'+ sky130_fd_sc_hd__nand2_2',
	'Xsky130_fd_sc_hd__nand2_2_1 LO LO VGND VNB VPB VPWR sky130_fd_sc_hd__nor2_2_1/B',
	'+ sky130_fd_sc_hd__nand2_2',
	'Xsky130_fd_sc_hd__inv_2_0 sky130_fd_sc_hd__inv_2_0/A VGND VNB VPB VPWR',
	'+ sky130_fd_sc_hd__inv_2_0/Y sky130_fd_sc_hd__inv_2',
	'Xsky130_fd_sc_hd__inv_2_1 sky130_fd_sc_hd__inv_2_1/A VGND VNB VPB VPWR',
	'+ sky130_fd_sc_hd__inv_2_1/Y sky130_fd_sc_hd__inv_2',
	'Xsky130_fd_sc_hd__nor2_2_0 sky130_fd_sc_hd__nor2_2_0/B sky130_fd_sc_hd__nor2_2_0/B',
	'+ VGND VNB VPB VPWR sky130_fd_sc_hd__inv_2_0/A sky130_fd_sc_hd__nor2_2',
	'Xsky130_fd_sc_hd__nor2_2_1 sky130_fd_sc_hd__nor2_2_1/B sky130_fd_sc_hd__nor2_2_1/B',
	'+ VGND VNB VPB VPWR sky130_fd_sc_hd__inv_2_1/A sky130_fd_sc_hd__nor2_2',
	'Xsky130_fd_sc_hd__conb_1_0 VGND VNB VPB VPWR sky130_fd_sc_hd__conb_1_0/HI LO',
	'+ sky130_fd_sc_hd__conb_1']

    fixedlines = []
    modified = False
    inmacro = False

    for line in spilines:
        if 'sparecell' in line:
            inmacro = True
            fixedlines.append(line)
            for mline in macrolines:
                fixedlines.append(mline)
            modified = True
        elif inmacro == True:
            if '.ends' in line:
                inmacro = False
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
            print('fix_sparecell_spice.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
