#!/usr/bin/env python3
#
# rename_models ---
#
# This script renames include paths from SPICE files in the models
# (libs.tech/ngspice) directory that point to the original ../cells/
# directory, to point to the correct location in libs.ref/sky130_fd_pr/spice/
#
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile.

import re
import os
import sys

def filter(inname, outname, ef_format = True):

    if ef_format:
        libpath = 'spi/sky130_fd_pr/'
    else:
        libpath = 'sky130_fd_pr/spice/'

    # Read input
    try:
        with open(inname, 'r') as inFile:
            spitext = inFile.read()
            spilines = spitext.splitlines()
    except:
        print('rename_models.py: failed to open ' + fnmIn + ' for reading.', file=sys.stderr)
        return 1

    # Process input with regexp

    fixedlines = []
    modified = False

    for line in spilines:

        # Fix: Replace "../cells/<name>/" with "../../libs.ref/sky130_fd_pr/spice/"
        fixedline = re.sub('\.\./cells/[^/]+/', '../../libs.ref/' + libpath, line)

        # This subsitution makes SPICE files compatible with Xyce without
        # breaking ngspice compatibility ('$' comments changed to ';')
        fixedline = re.sub('(.*[ \t]+)\$([ \t+].*)', '\g<1>;\g<2>', fixedline)

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
        print('Usage: rename_models.py <filename> [<outfilename>] [-ef_format]')
        sys.exit(1)

    if len(arguments) > 1:
        outfilename = arguments[1]
    else:
        outfilename = None

    ef_format = False
    if len(options) > 0:
        if options[0] == 'ef_format':
            ef_format = True

    result = filter(infilename, outfilename, ef_format)
    sys.exit(result)
