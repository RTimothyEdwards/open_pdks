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

if len(sys.argv) <= 1:
    print('Usage: fix_spice_includes.py <path_to_file>')
    sys.exit(1)

else:
    infile_name = sys.argv[1]

    filepath = os.path.split(infile_name)[0]
    outfile_name = os.path.join(filepath, 'temp')

    infile = open(infile_name, 'r')
    outfile = open(outfile_name, 'w')

    line_number = 0
    replaced_something = False
    for line in infile:
        line_number += 1

        if 'pnp_05v5' in line:
            # Insert these additional lines
            for newdev in newdevs:
                newline = '.include "../../libs.ref/sky130_fd_pr/spice/' + newdev + '.model.spice"\n'
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

