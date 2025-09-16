#!/usr/bin/env python3
#
# rename_models ---
#
# This script renames include paths from SPICE files in the models
# (libs.tech/ngspice) directory that point to the original ../cells/
# directory, to point to the correct location in libs.ref/sky130_fd_pr/spice/
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

    libpath = 'sky130_fd_pr/spice/'

    # Read input
    try:
        with open(inname, 'r') as inFile:
            spitext = inFile.read()
            spilines = spitext.splitlines()
    except:
        print('rename_models.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # Check specifically for the file "all.spice"
    allspice = False
    if os.path.split(inname)[1] == 'all.spice':
        allspice = True
        optionrex = re.compile('option scale=', re.IGNORECASE)

    # Process input with regexp

    fixedlines = []
    modified = False

    for line in spilines:

        # Modify: Replace "../cells/<name>/" with "../../libs.ref/sky130_fd_pr/spice/"
        fixedline = re.sub(r'\.\./cells/[^/]+/', '../../libs.ref/' + libpath, line)
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
            makeuserwritable(outname)
            with open(outname, 'w') as outFile:
                for i in fixedlines:
                    print(i, file=outFile)
        except:
            print('rename_models.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
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
    else:
        print('Usage: rename_models.py <filename> [<outfilename>]')
        sys.exit(1)

    if len(arguments) > 1:
        outfilename = arguments[1]
    else:
        outfilename = None

    result = filter(infilename, outfilename)
    sys.exit(result)
