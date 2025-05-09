#!/usr/bin/env python3
#
# fix_io_lef ---
#
# This script fixes the issue where the LEF files of the I/O cells, which are
# used for annotation only, interfere with the modified layouts.  The fix is
# to remove all G_CORE port geometry that is above Y=5

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
            ltext = inFile.read()
            llines = ltext.splitlines()
    except:
        print('fix_io_lef.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False
    inpin = False

    macrorex = re.compile(r'^MACRO[ \t]+([^ \t\n]+)')
    pinrex = re.compile(r'^[ \t]*PIN[ \t]+[PG]_CORE')
    endrex = re.compile(r'[ \t]*END[ \t]+[PG]_CORE')
    rectrex = re.compile(r'^[ \t]*RECT[ \t]+[0-9.]+[ \t]+([0-9.]+)[ \t]+')
    rect2rex = re.compile(r'^[ \t]*RECT[ \t]+[0-9.]+[ \t]+([0-9.]+)[ \t]+[0-9.]+[ \t]+([0-9.]+)[ \t]+')
    macroname = None

    for line in llines:

        # Check for MACRO line and record the macro name
        mmatch = macrorex.match(line)
        if mmatch:
            macroname = mmatch.group(1)

        # Check for "PIN G_CORE" or "PIN P_CORE"
        pmatch = pinrex.match(line)
        if pmatch and macroname:
            inpin = True

        ematch = endrex.match(line)
        if ematch and macroname:
            inpin = False

        if inpin:
            # Check for RECT entries and get the lower Y value
            rmatch = rectrex.match(line)
            if rmatch:
                yval = float(rmatch.group(1))
                if yval > 5.0:
                    # Reject geometry with lower Y value greater than 5um
                    continue
                # Truncate the height of any box with Y at zero that is
                # higher than 50um 
                elif yval < 1.0:
                    rmatch = rect2rex.match(line)
                    if rmatch:
                        ytop = float(rmatch.group(2))
                        if ytop > 50.0:
                            line = line.replace(rmatch.group(2), '50.000')

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
