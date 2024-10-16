#!/usr/bin/env python3
#
# inc_verilog ---
#
# This script handles the verilog sources by removing `include statements
# for files that are already being added to the single consolidated
# verilog library file.  Also, it adds the well and substrate pins to
# all verilog modules having power pins.
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

    # Ignore all files with "functional" or "behavioral" in the name.
    # Only process the plain ".v" and "_func.v" files.  Other files just
    # generate an empty file.

    if 'functional' in inname or 'behavioral' in inname:
        with open(outname, 'w') as outFile:
            print('', file=outFile)
        return 0

    # Process input with regexp

    fixedlines = []
    modified = False
    increx = re.compile('[ \t]*`include[ \t]+"?([^ \t\n"]+)"?')
    endrex = re.compile('[ \t]*endmodule')
    inpath = os.path.split(inname)[0]

    for line in vlines:
        # Remove includes
        imatch = increx.match(line)
        if imatch:
            incfilename = imatch.group(1)
            modified = True
        else:
            # Add in substrate and well pins
            if 'filltie' in inname or 'endcap' in inname:
                fline = line
            else:
                fline = line.replace('VDD, VSS', 'VDD, VSS, VNW, VPW')
                fline = fline.replace('.VDD(VDD),.VSS(VSS)', '.VDD(VDD),.VSS(VSS),.VNW(VNW),.VPW(VPW)')
            if fline != line:
                modified = True
            fixedlines.append(fline)

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
