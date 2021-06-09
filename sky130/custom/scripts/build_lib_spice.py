#!/usr/bin/env python3
#
#-----------------------------------------------------------------------
# build_lib_spice.py ---
#
# Generate a complete "sky130.lib.spice" file given:
# (1) The name of the original file
# (2) The name of an addendum file.
#
# The tasks done by this script are:
# (1) Add "mc_pr_switch" and "mc_mm_switch" parameters to each
#     section
# (2) Duplicate the entire set of sections and rename each section
#     in the new set with "_mm" and set "mc_mm_switch" to 1 in those
#     sections.
# (3) Add the addendum file to the bottom
# (4) Add the name of each section after the ".endl" line, for Xyce
#     compatibility.
#
#-----------------------------------------------------------------------
#
# Usage:
#
#	build_lib_spice.py <lib_spice_file> <addendum_file>
#
# The output will replace <lib_spice_file> with the modified version.

import os
import re
import sys

if len(sys.argv) != 3:
    print('Usage: build_lib_spice.py <lib_spice_file> <addendum_file>')
    sys.exit(1)

inputfile = sys.argv[1]
addendumfile = sys.argv[2]

cornerrex = re.compile('.*\((.*)\)')

with open(inputfile, 'r') as ifile:
    spicelines = ifile.read().splitlines()

with open(addendumfile, 'r') as ifile:
    addlines = ifile.read().splitlines()

# The header is the first 16 lines (copyright notice)
header = spicelines[0:16]
spicelines = spicelines[16:]

# After each ".lib", add the monte carlo parameters
# Add the name of the corner after ".endl"

newlines = []
for line in spicelines: 
    if line.startswith('.lib'):
        corner = line.split()[1]
        newlines.append(line)
        newlines.append('.param mc_mm_switch=0')
        newlines.append('.param mc_pr_switch=0')
    elif line.startswith('.endl'):
        newlines.append(line + ' ' + corner)
    else:
        newlines.append(line)

# Duplicate all sections with mismatch analysis versions

altlines = []
for line in spicelines: 
    cmatch = cornerrex.match(line)
    if cmatch:
        corner = cmatch.group(1)
        newline = re.sub(corner, corner + '_mm', line)
        newline = re.sub('\(', 'with mismatch (', newline)
        newlines.append(newline)
    elif line.startswith('.lib'):
        corner = line.split()[1]
        newlines.append(line + '_mm')
        newlines.append('.param mc_mm_switch=1')
        newlines.append('.param mc_pr_switch=0')
    elif line.startswith('.endl'):
        newlines.append(line + ' ' + corner + '_mm')
    else:
        newlines.append(line)

# Now overwrite the original file.
with open(inputfile, 'w') as ofile:
    for line in header:
        print(line, file=ofile)
    print('', file=ofile)
    for line in newlines:
        print(line, file=ofile)
    print('', file=ofile)
    for line in altlines:
        print(line, file=ofile)
    print('', file=ofile)
    for line in addlines:
        print(line, file=ofile)

