#!/usr/bin/env python3
#
#-------------------------------------------------------------------
#  makestub.py
#
# Read a CDL or SPICE netlist and remove all contents from subcircuits,
# leaving only the .SUBCKT ... .ENDS wrapper.  Used as a filter, so it
# replaces the original file with the modified one.  If the original
# file is a symbolic link, then it is first unlinked and replaced with
# the new contents.
#
# Use:
#
# 	makestub.py <path_to_netlist_file>
#
#-------------------------------------------------------------------

import os
import re
import sys
import stat
import textwrap

def makeuserwritable(filepath):
    if os.path.exists(filepath):
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IWUSR)

def generate_stubs(netlist_path, output_path):
    netlist_dir = os.path.split(netlist_path)[0]
    netlist_filename = os.path.split(netlist_path)[1]
    netlist_root = os.path.splitext(netlist_filename)[0]
    netlist_ext = os.path.splitext(netlist_filename)[1]

    if not os.path.exists(netlist_path):
        print('Error:  Specified file "' + netlist_path + '" does not exist!')
        return

    if output_path == None:
        output_path = netlist_path

    with open(netlist_path, 'r') as ifile:
        spicetext = ifile.read().splitlines()

    # Remove blank lines and comment lines
    spicelines = []
    for line in spicetext:
        if len(line) > 0:
            if line[0] != '*':
                spicelines.append(line)

    # Remove line extensions
    spicetext = '\n'.join(spicelines)
    spicelines = spicetext.replace('\n+', ' ').splitlines()

    # SPICE subcircuit definition:
    subcrex = re.compile(r'[ \t]*\.subckt[ \t]+([^ \t]+)[ \t]+(.*)$', re.IGNORECASE)
    endsrex = re.compile(r'[ \t]*\.ends[ \t]*', re.IGNORECASE)

    spiceoutlines = []

    insub = False
    for line in spicelines:
        if insub:
            ematch = endsrex.match(line)
            if ematch:
                insub = False
                spiceoutlines.append(line)
        else:
            smatch = subcrex.match(line)
            if smatch:
                insub = True
                spiceoutlines.append('')
                spiceoutlines.append('*----------------------------------------------')
                spiceoutlines.append('* SPICE stub entry for ' + smatch.group(1) + '.')
                spiceoutlines.append('*----------------------------------------------')
                spiceoutlines.append('')
            spiceoutlines.append(line)

    if output_path == netlist_path:
        if os.path.islink(netlist_path):
            os.unlink(netlist_path)

    # Re-wrap continuation lines at 100 characters
    wrappedlines = []
    for line in spiceoutlines:
        wrappedlines.append('\n+ '.join(textwrap.wrap(line, 100)))

    # Just in case the file in the source repo is not user-writable
    if os.path.exists(output_path):
        makeuserwritable(output_path)

    with open(output_path, 'w') as ofile:
        for line in wrappedlines:
            print(line, file=ofile)

# If called as main, run generate_stubs

if __name__ == '__main__':

    # Divide up command line into options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # Need one argument:  path to CDL or SPICE netlist
    # If two arguments, then 2nd argument is the output file.

    if len(arguments) == 2:
        netlist_path = arguments[0]
        output_path = arguments[1]
        generate_stubs(netlist_path, output_path)
    elif len(arguments) != 1:
        print("Usage:  makestub.py <file_path> [<output_path>]")
    elif len(arguments) == 1:
        netlist_path = arguments[0]
        generate_stubs(netlist_path, None)

