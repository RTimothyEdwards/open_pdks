#!/usr/bin/env python3
#
# sort_pdkfiles.py
#
# Read "filelist.txt" which is a list of all files to be compiled.
# Do a natural sort, which puts the "base" files (those without a
# drive strength) in front of "top level" files (those with a drive
# strength), and orders the drive strengths numerically.
#
# Note that foundry_install.py executes this script using 'subprocess'
# in the directory where "filelist.txt" and the files are located.  No
# path components are in the file list.

import re
import os
import sys
import natural_sort

def pdk_sort(destdir):
    if not os.path.isfile(destdir + '/filelist.txt'):
        print('No file "filelist.txt" in ' + destdir + '. . .  Nothing to sort.')
        sys.exit()

    with open(destdir + '/filelist.txt', 'r') as ifile:
        vlist = ifile.read().splitlines()

    vlist = natural_sort.natural_sort(vlist)
    
    with open(destdir + '/filelist.txt', 'w') as ofile:
        for vfile in vlist:
            print(vfile, file=ofile)

if __name__ == '__main__':

    # This script expects to get one argument, which is a path name

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item[1:])
        else:
            arguments.append(item)

    if len(arguments) > 0:
        destdir = arguments[0]

    pdk_sort(destdir)
    sys.exit(0)

