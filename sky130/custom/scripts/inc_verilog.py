#!/usr/bin/env python3
#
# inc_verilog ---
#
# This script handles the verilog sources by removing `include statements
# for files that are already being added to the single consolidated
# verilog library file, and in-lining any other verilog files (namely
# the functional and timing sources).
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile.

import re
import os
import sys
import stat

def makeuserwritable(filepath):
    if os.path.exists(filepath):
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IWUSR)

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
    # check if it has a "specify" block file.  Originally, this was
    # disabled because iverilog did not handle some specify-block syntax.
    # This has been corrected in the iverilog sources (as of 7/16/2023).
    dospecify = True

    # Process input with regexp

    fixedlines = []
    modified = False
    increx = re.compile(r'[ \t]*`include[ \t]+"?([^ \t\n"]+)"?')
    ddotrex = re.compile(r'[^\.]+\.[^\.]+\.v')
    tdotrex = re.compile(r'[^\.]+\.[^\.]+\.[^\.]+\.v')
    endrex = re.compile(r'[ \t]*endmodule')
    inpath = os.path.split(inname)[0]

    for line in vlines:
        needtiming = False

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

                # If adding specify blocks, check if the include file is a
                # timing base cell.  Accept '.behavioral.' as equivalent to
                # '.timing.' for backwards-compatibility, although the use
                # of the term "behavioral" is incorrect.
                if dospecify:
                    if '.timing.' in incfilename or '.behavioral.' in incfilename:
                        specname = incfilename.split('.')[0] + '.specify.v'
                        if os.path.exists(inpath + '/' + specname):
                            print('Specfile ' + specname + ' found for cell ' + incfilename)
                            needtiming = True

                with open(inpath + '/' + incfilename, 'r') as incfile:
                    v2text = incfile.read()
                    v2lines = v2text.splitlines()
                    for line2 in v2lines:
                        i2match = increx.match(line2)
                        if not i2match:
                            # Add "specify" block.
                            if needtiming:
                                ematch = endrex.match(line2)
                                if ematch:
                                    with open(inpath + '/' + specname, 'r') as ispec:
                                        v3text = ispec.read()
                                        v3lines = v3text.splitlines()
                                        for line3 in v3lines:
                                            fixedlines.append(line3)
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
            makeuserwritable(outname)
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
