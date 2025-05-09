#!/usr/bin/env python3
#
# sp_to_spice ---
#
# This script runs as a filter to foundry_install.sh and converts file
# names ending with ".sp" to ".spice".  If the file has multiple extensions
# then all are stripped before adding ".spice".  The script is specifically
# intended to run on the SRAM macro library ".lvs.sp" files, which include
# two parasitic devices that make them compatible with the extracted layout,
# but have a few syntactical incompatibilities that can be corrected by
# filtering the file during the copy.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile.

import os
import re
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

    print('Converting file ' + filename + ' to ' + newname + ' by reversing buses and scaling l and w.')
    # Read input
    try:
        with open(inname, 'r') as inFile:
            stext = inFile.read()
            slines = stext.splitlines()
    except:
        print('sp_to_spice.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    fixedlines = []
    modified = False
    base_rex = re.compile(r'([^\[]*).*')  # regular expression for matching base signal

    for line in slines:

        # remove 'u' suffix from 'l' and 'w' parameters
        newline = re.sub(r'([ \t][lL]=[0-9\.]*)u', r'\1', line)
        newline = re.sub(r'([ \t][wW]=[0-9\.]*)u', r'\1', newline)

        # reverse bus indices - NOTE: Only works if all ports are on the subckt line
        if newline.startswith(".subckt ") or newline.startswith(".SUBCKT "):
            tokens = newline.split()
            if tokens[1] == filebits[0]:  # top subckt
                bus_start = 2
                last_base = base_rex.match(tokens[2]).group(1)
                i = 3
                while i < len(tokens):
                    base_match = base_rex.match(tokens[i])  # always matches one base net
                    if last_base != base_match.group(1):
                        tokens[bus_start:i] = tokens[i-1:bus_start-1:-1]  # reverse the bus indices
                        bus_start = i
                        last_base = base_match.group(1)
                    i += 1
                tokens[bus_start:i] = tokens[i-1:bus_start-1:-1]
                newline = " ".join(tokens)

        if line != newline:
            modified = True

        fixedlines.append(newline)

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
            print('sp_to_spice.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
            return 1

        # If the name was changed, remove the original file.
        if filename != newname:
            os.remove(inname)

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
