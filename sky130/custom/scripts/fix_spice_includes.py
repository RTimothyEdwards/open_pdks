#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# fix_spice_includes.py---
#
# This script patches the "all.spice" file to add include statements
# for several devices that got left out (namely the PNP and NPN
# devices). 
#--------------------------------------------------------------------

import os
import re
import sys

newdevs = []
newdevs.append('sky130_fd_pr__pnp_05v5_W3p40L3p40')

options = []
arguments = []
for item in sys.argv[1:]:
    if item.find('-', 0) == 0:
        options.append(item[1:])
    else:
        arguments.append(item)

if len(arguments) < 1:
    print('Usage: fix_spice_includes.py <path_to_file> [-ef_format]')
    sys.exit(1)

else:
    infile_name = arguments[0]

    libpath = 'sky130_fd_pr/spice/'
    if len(options) > 0:
        if options[0] == 'ef_format':
            libpath = 'spi/sky130_fd_pr/'

    filepath = os.path.split(infile_name)[0]
    filename = os.path.split(infile_name)[1]
    fileroot = os.path.split(filename)[0]
    outfile_name = os.path.join(filepath, fileroot + '_temp')

    infile = open(infile_name, 'r')
    outfile = open(outfile_name, 'w')

    line_number = 0
    replaced_something = False
    for line in infile:
        line_number += 1

        if 'pnp_05v5' in line:
            # Insert these additional lines
            for newdev in newdevs:
                newline = '.include "../../libs.ref/' + libpath + newdev + '.model.spice"\n'
                outfile.write(newline)
            replaced_something = True

        newline = line
        outfile.write(newline)

    infile.close()
    outfile.close()
    if replaced_something:
        print("Something was replaced in '{}'".format(infile_name))
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

