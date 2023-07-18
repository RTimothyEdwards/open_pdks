#!/usr/bin/env python3
#
# inc_verilog ---
#
# This script handles the verilog sources by removing `include statements
# for files that are already being added to the single consolidated
# verilog library file, and in-lining any other verilog files (namely
# the functional and behavioral sources).
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
            vtext = inFile.read()
            vlines = vtext.splitlines()
    except:
        print('inc_verilog.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Check if input file is a base cell or strength-specific cell, and
    # check if it has a "specify" block file.  To enable this, change
    # dospecify from False to True.
    dospecify = True

    # Process input with regexp

    fixedlines = []
    modified = False
    increx = re.compile('[ \t]*`include[ \t]+"?([^ \t\n"]+)"?')
    ddotrex = re.compile('[^\.]+\.[^\.]+\.v')
    tdotrex = re.compile('[^\.]+\.[^\.]+\.[^\.]+\.v')
    endrex = re.compile('[ \t]*endmodule')
    inpath = os.path.split(inname)[0]

    for line in vlines:
        isbehav = False

        # Check includes
        imatch = increx.match(line)
        if imatch:
            incfilename = imatch.group(1)
            dmatch = ddotrex.match(incfilename)
            tmatch = tdotrex.match(incfilename)
            if dmatch or tmatch:
                # double-dot or triple-dot:  Include this file in-line
                # NOTE:  These files are assumed not to need in-line
                # includes, but includes of primitives need to be ignored.

                # Quick hack:  Remove this when the filenames are corrected
                if not os.path.exists(inpath + '/' + incfilename):
                    print('Detected incorrect filename')
                    print('   Old filename was: ' + incfilename)
                    dlist = incfilename.split('.')
                    ilist = dlist[0:-3]
                    ilist.append(dlist[-2])
                    ilist.append(dlist[-3])
                    ilist.append(dlist[-1])
                    incfilename = '.'.join(ilist)
                    print('   New filename is: ' + incfilename)

                # If adding specify blocks, check if the include file is a
                # behavioral base cell.
                if dospecify:
                    if '.behavioral.' in incfilename:
                        specname = incfilename.split('.')[0] + '.specify.v'
                        if os.path.exists(inpath + '/' + specname):
                            print('Specfile ' + specname + ' found for cell ' + incfilename)
                            isbehav = True

                with open(inpath + '/' + incfilename, 'r') as incfile:
                    v2text = incfile.read()
                    v2lines = v2text.splitlines()
                    for line2 in v2lines:
                        i2match = increx.match(line2)
                        if not i2match:
                            # Experimental:  Put back "specify" block.
                            if isbehav:
                                ematch = endrex.match(line2)
                                if ematch:
                                    with open(inpath + '/' + specname, 'r') as ispec:
                                        v3text = ispec.read()
                                        v3lines = v3text.splitlines()
                                        for line3 in v3lines:

                                            # Fix issues in specify files
                                            line3 = line3.replace('RESETB_delayed', 'RESET_B_delayed')
                                            line3 = line3.replace('GATEN_delayed', 'GATE_N_delayed')
                                            line3 = line3.replace('SETB_delayed', 'SET_B_delayed')
                                            line3 = line3.replace('CLKN_delayed', 'CLK_N_delayed')
                                            line3 = line3.replace('AWAKE', 'awake')
                                            line3 = line3.replace('COND0', 'cond0')
                                            line3 = line3.replace('COND1', 'cond1')
                                            line3 = line3.replace('COND2', 'cond2')
                                            line3 = line3.replace('COND3', 'cond3')
                                            line3 = line3.replace('COND4', 'cond4')
                                            line3 = line3.replace('CONDB', 'condb')
                                            line3 = line3.replace('COND_D', 'cond_D')
                                            line3 = line3.replace('COND_SCD', 'cond_SCD')
                                            line3 = line3.replace('COND_SCE', 'cond_SCE')
                                            fixedlines.append(line3)

                            # Fix issues in included files
                            if '    wire 1             ;' in line2:
                                continue

                            line2 = line2.replace('\tB2', '   ')
                            line2 = line2.replace('\tCIN', '    ')
                            line2 = line2.replace('\tcsi_opt_276,', '             ')
                            line2 = line2.replace('\tB1', '   ')
                            line2 = line2.replace('\tA4', '   ')
                            line2 = line2.replace('\tC1', '   ')
                            line2 = line2.replace('\tX', '  ')
                            line2 = line2.replace('\tD', '  ')
                            line2 = line2.replace('\tbuf_Q', '      ')
                            line2 = line2.replace('\tgate', '     ')
                            line2 = line2.replace('\tcsi_opt_296,', '             ')
                            line2 = line2.replace('\tY', '  ')

                            line2 = line2.replace('    wire  N not0_out          ;', '    wire    not0_out          ;')
                            line2 = line2.replace('    wire  N nor0_out          ;', '    wire    nor0_out          ;')
                            line2 = line2.replace('    wire  N nand0_out         ;', '    wire    nand0_out         ;')

                            fixedlines.append(line2)
            else:
                # single-dot:  Ignore this line
                pass
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
            print('inc_verilog.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
