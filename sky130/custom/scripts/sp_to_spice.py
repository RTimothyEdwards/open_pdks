#!/usr/bin/env python3
#
# sp_to_spice ---
#
# This script runs as a filter to foundry_install.sh and converts file
# names ending with ".sp" to ".spice".  If the file has multiple extensions
# then all are stripped before adding ".spice".
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile.

import os
import sys

def filter(inname):

    filepath = os.path.split(inname)[0]
    filename = os.path.split(inname)[1]

    filebits = filename.split('.')
    newname = filebits[0] + '.spice'
    outname = os.path.join(filepath, newname)
    if not os.path.isfile(inname):
        print('No such file ' + inname)
        return 1

    print('Renaming file ' + filename + ' to ' + newname)
    os.rename(inname, outname)
    return 0

if __name__ == '__main__':

    # This script expects to get one argument, which is the input file.
    # The script renames the file.

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
        sys.exit(1)

    result = filter(infilename)
    sys.exit(result)
