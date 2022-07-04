#!/usr/bin/env python3
#
# fix_techlefA ---
#
# This script adds the missing statement "USEMINSPACING OBS OFF" from
# the technology LEF files for Sky130, adds missing RESISTANCE
# values, and corrects the resistance value of local interconnect.
# Note that resistance values are *nominal* and need to be modified for
# corners.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile for
# variant sky130A.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            ltext = inFile.read()
            llines = ltext.splitlines()
    except:
        print('fix_techlefA.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # These are the resistance values per via type, by name.  Valuse are in
    # ohms and presented as a string.
    via_res = {}
    via_res['mcon'] = '9.30'
    via_res['via']  = '4.50'
    via_res['via2'] = '3.41'
    via_res['via3'] = '3.41'
    via_res['via4'] = '0.38'

    # Process input with regexp

    fixedlines = []
    modified = False

    proprex  = re.compile('[ \t]*MANUFACTURINGGRID')
    resrex   = re.compile('[ \t]*ENCLOSURE ABOVE')
    layerrex = re.compile('[ \t]*LAYER ([^ \t\n]+)') 
    resrex2  = re.compile('[ \t]*RESISTANCE RPERSQ 12.2 ;')
    thickrex = re.compile('[ \t]*THICKNESS')
    emptyrex = re.compile('^[ \t]*$')
    curlayer = None
    thickness_seen = False

    for line in llines:
        if thickness_seen:
            thickness_seen = False
            if curlayer and (curlayer == 'met1' or curlayer == 'met2'):
                ematch = emptyrex.match(line)
                if ematch:
                    fixedlines.append('  MINENCLOSEDAREA 0.14 ;')
                    modified = True

        rmatch = resrex2.match(line)
        if rmatch:
            fixedlines.append('  RESISTANCE RPERSQ 12.8 ;')
            modified = True
        else:
            fixedlines.append(line)

        # Check for the MANUFACTURINGGRID statement in the file, and
        # add the USEMINSPACING statement after it.

        pmatch = proprex.match(line)
        if pmatch:
            fixedlines.append('USEMINSPACING OBS OFF ;')
            modified = True

        rmatch = resrex.match(line)
        if rmatch:
            fixedlines.append('  RESISTANCE ' + via_res[curlayer] + ' ;')
            modified = True

        lmatch = layerrex.match(line)
        if lmatch:
            curlayer = lmatch.group(1)

        tmatch = thickrex.match(line)
        if tmatch:
            thickness_seen = True

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
            print('fix_techlef.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
