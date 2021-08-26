#!/usr/bin/env python3
#
# split_gds.py --
#
# Script to read a GDS library and write into individual GDS files, one per cell

import os
import sys
import subprocess

def usage():
    print('split_gds.py <path_to_gds_library> <magic_techfile> [<file_with_list_of_cells>]')

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("No options given to split_gds.py.")
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 3:
        print("Wrong number of arguments given to split_gds.py.")
        usage()
        sys.exit(0)

    source = arguments[0]

    techfile = arguments[1]

    celllist = arguments[2]
    if os.path.isfile(celllist):
        with open(celllist, 'r') as ifile:
            celllist = ifile.read().splitlines()

    destdir = os.path.split(source)[0]
    gdsfile = os.path.split(source)[1]

    with open(destdir + '/split_gds.tcl', 'w') as ofile:
        print('#!/usr/bin/env wish', file=ofile)
        print('drc off', file=ofile)
        print('gds readonly true', file=ofile)
        print('gds rescale false', file=ofile)
        print('tech unlock *', file=ofile)
        print('gds read ' + gdsfile, file=ofile)

        for cell in celllist:
            print('load ' + cell, file=ofile)
            print('gds write ' + cell, file=ofile)

        print('quit -noprompt', file=ofile)

    mproc = subprocess.run(['magic', '-dnull', '-noconsole',
		'-T', techfile,
		destdir + '/split_gds.tcl'],
		stdin = subprocess.DEVNULL,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE, cwd = destdir,
		universal_newlines = True)
    if mproc.stdout:
        for line in mproc.stdout.splitlines():
            print(line)
    if mproc.stderr:
        print('Error message output from magic:')
        for line in mproc.stderr.splitlines():
            print(line)
        if mproc.returncode != 0:
            print('ERROR:  Magic exited with status ' + str(mproc.returncode))

    os.remove(destdir + '/split_gds.tcl')
    exit(0)
