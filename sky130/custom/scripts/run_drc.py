#!/bin/env python3
#-------------------------------------------------------------------------
# run_drc.py ---  A script to run magic in batch mode and apply full DRC
# checks on a layout.  This inclues full DRC, antenna rule checks, and
# density checks.
#
# Usage:
#
#   run_drc.py <layout_name>
#
# Results:
#
#   generates a file "<layout_name>_drc.txt" containing a human-readable
#   list of the DRC errors.
# 	
#-------------------------------------------------------------------------

import subprocess
import shutil
import sys
import os
import re

# Work in progress

def run_full_drc(layout_name, output_file):
    with open('run_magic_drc.tcl', 'w') as ofile:

    # Create the GDS of the seal ring

    mproc = subprocess.run(['magic', '-dnull', '-noconsole',
	    'run_magic_drc.tcl'],
	    stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
	    stderr = subprocess.PIPE, universal_newlines = True)
    if mproc.stdout:
        for line in mproc.stdout.splitlines():
            print(line)
    if mproc.stderr:
        print('Error message output from magic:')
        for line in mproc.stderr.splitlines():
            print(line)
    if mproc.returncode != 0:
        print('ERROR:  Magic exited with status ' + str(mproc.returncode))

# If called as main, run all DRC tests

if __name__ == '__main__':

    # Divide up command line into options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # Need one argument:  path to layout
    # If two arguments, then 2nd argument is the output file.

    if len(arguments) < 3:
        layout_root = arguments[1]

    if len(arguments == 1):
        out_fileroot = layout_root + "_drc.txt"
    else:
        out_fileroot = arguments[2]

    if len(arguments) < 3:
        run_full_drc(layout_root, out_filename)
    else:
        print("Usage:  run_drc.py <layout_name> [<output_file>] [options]")
        print("Options:")
        print("   (none)")
    

