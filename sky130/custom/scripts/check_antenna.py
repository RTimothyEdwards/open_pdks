#!/bin/env python3
#-------------------------------------------------------------------------
# check_antenna.py ---  A script to run magic in batch mode and run the
# antenna violation checks on a layout.
#
# Usage:
#
#   check_antenna.py <layout_name>
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

def run_antenna(layout_name, output_file):

    # Remove any extension from layout_name
    layout_name = os.path.splitext(layout_name)[0]

    # Is the layout file in the current directory, or a full
    # path, or is this a project directory?

    if layout_name[0] == '/':
        magpath = os.path.split(layout_name)[0]
        layout_name = os.path.split(layout_name)[1]

    else:
        if not os.path.isfile(layout_name + '.mag'):
            if not os.path.isfile('mag/' + layout_name + '.mag'):
                print('Error:  Cannot find file ' + layout_name + '.mag')
                return
            else:
                magpath = os.getcwd() + '/mag'
        else:
            magpath = os.getcwd()

    if output_file == '':
        output_file = layout_name + '_ant.txt'

    # Check for presence of a .magicrc file, or else check for environment
    # variable PDKPATH, or PDK_PATH

    myenv = os.environ.copy()
    myenv['MAGTYPE'] = 'mag'
    
    if os.path.isfile('/usr/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc'):
       rcfile = '/usr/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc'
    elif os.path.isfile(magpath + '/.magicrc'):
       rcfile = magpath + '/.magicrc'
    elif os.path.isfile(os.getcwd() + '/.magicrc'):
       rcfile = os.getcwd() + '/.magicrc'
    else:
        if 'PDKPATH' in myenv:
            rcpathroot = myenv['PDKPATH'] + '/libs.tech/magic'
            rcfile = glob.glob(rcpathroot + '/*.magicrc')[0]
        elif 'PDK_PATH' in myenv:
            rcpathroot = myenv['PDKPATH'] + '/libs.tech/magic'
            rcfile = glob.glob(rcpathroot + '/*.magicrc')[0]
        else:
            print('Error: Cannot get magic rcfile for the technology!')
            return
    
    # Generate the antenna check Tcl script

    print('Evaluating antenna rule violations on layout ' + layout_name)

    with open('run_magic_antenna.tcl', 'w') as ofile:
        print('# run_magic_antenna.tcl ---', file=ofile)
        print('#    batch script for running DRC', file=ofile)
        print('', file=ofile)
        print('crashbackups stop', file=ofile)
        print('drc off', file=ofile)
        print('snap internal', file=ofile)
        print('load ' + layout_name + ' -dereference', file=ofile)
        print('select top cell', file=ofile)
        print('expand', file=ofile)
        print('extract do local', file=ofile)
        print('extract no all', file=ofile)
        print('extract all', file=ofile)
        print('antennacheck', file=ofile)

    # Run the DRC Tcl script

    ofile = open(output_file, 'w')
    print('Antenna violation checks on cell ' + layout_name, file=ofile)
    print('--------------------------------------------', file=ofile)

    print('Running: magic -dnull -noconsole') 

    mproc = subprocess.run(['magic', '-dnull', '-noconsole',
		'-rcfile', rcfile, 'run_magic_antenna.tcl'],
		env = myenv, cwd = magpath,
		stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
		stderr = subprocess.PIPE, universal_newlines = True)
    if mproc.stdout:
        for line in mproc.stdout.splitlines():
            print(line)
            print(line, file=ofile)
    if mproc.stderr:
        print('\nError message output from magic:')
        print('\nError message output from magic:', file=ofile)
        for line in mproc.stderr.splitlines():
            print(line)
            print(line, file=ofile)
    if mproc.returncode != 0:
        print('\nERROR:  Magic exited with status ' + str(mproc.returncode))
        print('\nERROR:  Magic exited with status ' + str(mproc.returncode), file=ofile)

    ofile.close()

    print('Done!')

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

    if len(arguments) > 0 and len(arguments) < 3:
        layout_root = arguments[0]

    if len(arguments) == 1:
        out_filename = ""
    elif len(arguments) > 1:
        out_filename = arguments[1]

    if len(arguments) > 0 and len(arguments) < 3:
        run_antenna(layout_root, out_filename)
    else:
        print("Usage:  check_antenna.py <layout_name> [<output_file>] [options]")
        print("Options:")
        print("   (none)")
    

