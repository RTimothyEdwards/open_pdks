#!/usr/bin/env python3
#
# fixspice ---
#
# This script fixes problems in the SkyWater SPICE models.  This should be
# made obsolete by the forthcoming set of models from the foundry, but the
# script will get the original set working with ngspice.
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
        print('fixspice.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    for line in spilines:

        # Fix 1:  ngspice does not understand the syntax used for the dev/gauss lines,
        #  so remove them.
        fixedline = re.sub('dev/gauss[ \t]*=.*$', '', line)

        # Fix 2: Remove references to *_dlc_rotweak
        # fixedline = re.sub('\+[ \t]*[^ \t_]+_dlc_rotweak', '', fixedline)

        # Fix 2: Remove references to *_[a,p]junction_mult
        # fixedline = re.sub('\*[ \t]*[^ \t_]+_[ap]junction_mult', '', fixedline)

        fixedlines.append(fixedline)
        if fixedline != line:
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
            print('fixspice.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
