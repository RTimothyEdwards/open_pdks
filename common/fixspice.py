#!/bin/env python3
#
# fixspice ---
#
# This script fixes problems in SPICE models to make them ngspice-compatible.
# The methods searched and corrected in this file correspond to ngspice
# version 30.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the PDK Makefile in
# open_pdks.
#
# This script converted from the bash script by Risto Bell, with improvements.
#
# This script is minimally invasive to the original SPICE file, making changes
# while preserving comments and line continuations.  In order to properly parse
# the file, comments and line continuations are recorded and removed from the
# file contents, then inserted again before the modified file is written.

import re
import os
import sys
import textwrap

def filter(inname, outname, debug=False):
    notparsed = []

    # Read input.  Note that splitlines() performs the additional fix of
    # correcting carriage-return linefeed (CRLF) line endings.
    try:
        with open(inname, 'r') as inFile:
            spitext = inFile.read()
    except:
        print('fixspice.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1
    else:
        if debug:
            print('Fixing ngspice incompatibilities in file ' + inname + '.')

    # Due to the complexity of comment lines embedded within continuation lines,
    # the result needs to be processed line by line.  Blank lines and comment
    # lines are removed from the text, replaced with tab characters, and collected
    # in a separate array.  Then the continuation lines are unfolded, and each
    # line processed.  Then it is all put back together at the end.

    # First replace all tabs with spaces so we can use tabs as markers.
    spitext = spitext.replace('\t', '    ')

    # Now do an initial line split
    spilines = spitext.splitlines()

    # Search lines for comments and blank lines and replace them with tabs
    # Replace continuation lines with tabs and preserve the position.
    spitext = ''
    for line in spilines:
        if len(line) == 0:
            notparsed.append('\n')
            spitext += '\t '
        elif line[0] == '*':
            notparsed.append('\n' + line)
            spitext += '\t '
        elif line[0] == '+':
            notparsed.append('\n+')
            spitext += '\t ' + line[1:]
        else:
            spitext += '\n' + line

    # Now split back into an array of lines
    spilines = spitext.splitlines()

    # Process input with regexp

    fixedlines = []
    modified = False

    # Regular expression to find 'agauss(a,b,c)' lines and record a, b, and c
    grex = re.compile('[^{]agauss\(([^,]*),([^,]*),([^)]*)\)', re.IGNORECASE)

    # Regular expression to determine if the line is a .PARAM card    
    paramrex = re.compile('^\.param', re.IGNORECASE)
    # Regular expression to determine if the line is a .MODEL card    
    modelrex = re.compile('^\.model', re.IGNORECASE)
    # Regular expression to detect a .SUBCKT card
    subcktrex = re.compile('^\.subckt', re.IGNORECASE)

    for line in spilines:
        devtype = line[0].upper() if len(line) > 0 else 0

        # NOTE:  All filter functions below take variable fixedline, alter it, then
        # set fixedline to the altered text for the next filter function.

        fixedline = line

        # Fix: Wrap "agauss(...)" in brackets and remove single quotes around expressions
        # Example:
        #    before: + SD_DN_CJ=agauss(7.900e-04,'1.580e-05*__LOT__',1)   dn_cj=SD_DN_CJ"
        #    after:  + SD_DN_CJ={agauss(7.900e-04,1.580e-05*__LOT__,1)}   dn_cj=SD_DN_CJ"

        # for gmatch in grex.finditer(fixedline):
        while True:
            gmatch = grex.search(fixedline)
            if gmatch:
                fixpart1 = gmatch.group(1).strip("'")
                fixpart2 = gmatch.group(2).strip("'")
                fixpart3 = gmatch.group(3).strip("'")
                fixedline = fixedline[0:gmatch.span(0)[0] + 1] + '{agauss(' + fixpart1 + ',' + fixpart2 + ',' + fixpart3 + ')}' + fixedline[gmatch.span(0)[1]:]
                if debug:
                    print('Fixed agauss() call.')
            else:
                break

        # Fix: Check for "dtemp=dtemp" and remove unless in a .param line
        pmatch = paramrex.search(fixedline)
        if not pmatch:
            altered = re.sub(' dtemp=dtemp', ' ', fixedline, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Removed dtemp=dtemp from instance call')

        # Fixes related to .MODEL cards:

        mmatch = modelrex.search(fixedline)
        if mmatch:

            modeltype = fixedline.split()[2].lower()

            if modeltype == 'nmos' or modeltype == 'pmos':

                # Fixes related specifically to MOS models:

                # Fix: Look for hspver=98.2 in FET model
                altered = re.sub(' hspver[ ]*=[ ]*98\.2', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed hspver=98.2 from ' + modeltype + ' model')

                # Fix:  Change level 53 FETs to level 49
                altered = re.sub(' (level[ ]*=[ ]*)53', ' \g<1>49', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Changed level 53 ' + modeltype + ' to level 49')

                # Fix: Look for version=4.3 or 4.5 FETs, change to 4.8.0 per recommendations
                altered = re.sub(' (version[ ]*=[ ]*)4\.[35]', ' \g<1>4.8.0',
					fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Changed version 4.3/4.5 ' + modeltype + ' to version 4.8.0')
    
                # Fix: Look for mulu0= (NOTE:  Might be supported for bsim4?)
                altered = re.sub('mulu0[ ]*=[ ]*[0-9.e+-]*', '', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed mulu0= from ' + modeltype + ' model')

                # Fix: Look for apwarn=
                altered = re.sub(' apwarn[ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed apwarn= from ' + modeltype + ' model')

                # Fix: Look for lmlt=
                altered = re.sub(' lmlt[ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed lmlt= from ' + modeltype + ' model')

                # Fix: Look for nf=
                altered = re.sub(' nf[ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed nf= from ' + modeltype + ' model')

                # Fix: Look for sa/b/c/d/=
                altered = re.sub(' s[abcd][ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed s[abcd]= from ' + modeltype + ' model')

                # Fix: Look for binflag= in MOS .MODEL
                altered = re.sub(' binflag[ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed binflag= from ' + modeltype + ' model')

                # Fix: Look for wref, lref= in MOS .MODEL (note:  could be found in other models?)
                altered = re.sub(' [wl]ref[ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
                if altered != fixedline:
                    fixedline = altered
                    if debug:
                        print('Removed lref= from MOS .MODEL')

            # TREF is a known issue for (apparently?) all device types
            # Fix: Look for tref= in .MODEL
            altered = re.sub(' tref[ ]*=[ ]*[0-9.e+-]*', ' ', fixedline, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Removed tref= from ' + modeltype + ' model')

            # Fix: Look for double-dot model binning and replace with single dot
            altered = re.sub('\.\.([0-9]+)', '.\g<1>', fixedline, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Collapsed double-dot model binning.')

        # Various deleted parameters above may appear in instances, so those must be
        # caught as well.  Need to catch expressions and variables in addition to the
        # usual numeric assignments.

        if devtype == 'M':
            altered = re.sub(' nf=[^ \'\t]+', ' ', fixedline, flags=re.IGNORECASE)
            altered = re.sub(' nf=\'[^\'\t]+\'', ' ', altered, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Removed nf= from MOSFET device instance')

            altered = re.sub(' mulu0=[^ \'\t]+', ' ', fixedline, flags=re.IGNORECASE)
            altered = re.sub(' mulu0=\'[^\'\t]+\'', ' ', altered, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Removed mulu0= from MOSFET device instance')

            altered = re.sub(' s[abcd]=[^ \'\t]+', ' ', fixedline, flags=re.IGNORECASE)
            altered = re.sub(' s[abcd]=\'[^\'\t]+\'', ' ', altered, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Removed s[abcd]= from MOSFET device instance')

        # Remove tref= from all device type instances
        altered = re.sub(' tref=[^ \'\t]+', ' ', fixedline, flags=re.IGNORECASE)
        altered = re.sub(' tref=\'[^\'\t]+\'', ' ', altered, flags=re.IGNORECASE)
        if altered != fixedline:
            fixedline = altered
            if debug:
                print('Removed tref= from device instance')

        # Check for use of ".subckt ...  <name>=l" (or <name>=w) with no antecedent
        # for 'w' or 'l'.  It is the responsibility of the technology file for extraction
        # to produce the correct name to pass to the subcircuit for length or width.

        smatch = subcktrex.match(fixedline)
        if smatch:
            altered = fixedline
            if fixedline.lower().endswith('=l'):
                if ' l=' not in fixedline.lower():
                    altered=re.sub( '=l$', '=0', fixedline, flags=re.IGNORECASE)
            elif '=l ' in fixedline.lower():
                if ' l=' not in fixedline.lower():
                    altered=re.sub( '=l ', '=0 ', altered, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Replaced use of "l" with no definition in .subckt line')

            altered = fixedline
            if fixedline.lower().endswith('=w'):
                if ' w=' not in fixedline.lower():
                    altered=re.sub( '=w$', '=0', fixedline, flags=re.IGNORECASE)
            elif '=w ' in fixedline.lower():
                if ' w=' not in fixedline.lower():
                    altered=re.sub( '=w ', '=0 ', altered, flags=re.IGNORECASE)
            if altered != fixedline:
                fixedline = altered
                if debug:
                    print('Replaced use of "w" with no definition in .subckt line')

        fixedlines.append(fixedline)
        if fixedline != line:
            modified = True

    # Reinsert embedded comments and continuation lines
    if debug:
        print('Reconstructing output')
    olines = []
    for line in fixedlines:
        while '\t ' in line:
            line = line.replace('\t ', notparsed.pop(0), 1)
        olines.append(line)

    fixedlines = '\n'.join(olines).strip()
    olines = fixedlines.splitlines()

    # Write output
    if debug:
        print('Writing output')
    if outname == None:
        for line in olines:
            print(line)
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
                for line in olines:
                    print(line, file=outFile)
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

    debug = True if 'debug' in options else False

    result = filter(infilename, outfilename, debug)
    sys.exit(result)
