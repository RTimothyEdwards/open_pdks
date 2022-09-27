#!/usr/bin/env python3
#
# fix_mismatched_opcond.py ---
#
# Fixes an error that appers in the HVL library only.
# There is at least one example in one file where the string passed to
# the statement "operating_conditions(...)" does not match the string
# previously passed to the statement "default_operating_conditions : ...".
# This causes some tools to throw an error.  Fixed by remembering the
# default operating condition name and correcting the operating condition
# name if it does not match the default.
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
        print('fix_mismatched_opcond.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    default_re = re.compile('\s*default_operating_conditions\s*:\s*"(.+)"\s*;')
    opcond_re = re.compile('\s*operating_conditions\s*\(\s*"(.+)"\s*\)\s*{')

    opcond_default_name = None

    for line in slines:
        dmatch = default_re.match(line)
        if dmatch:
            opcond_default_name = dmatch.group(1)

        omatch = opcond_re.match(line)
        if omatch:
            opcond_name = omatch.group(1)
            if not opcond_default_name:
                print('Error: operating condition used without a default')
            elif (opcond_name != opcond_default_name):
                # Diagnostic
                print('Found non-matching names ' + opcond_default_name + ' and ' + opcond_name)
                modified = True
                line = line.replace(opcond_name, opcond_default_name)
                opcond_default_name = ''

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
            print('fix_mismatched_opcond.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
