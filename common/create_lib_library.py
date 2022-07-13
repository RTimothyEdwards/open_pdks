#!/usr/bin/env python3
#
# create_lib_library.py
#
#----------------------------------------------------------------------------
# Given a destination directory holding individual liberty files of a number
# of cells, create a single liberty library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-lib" install.
#----------------------------------------------------------------------------

import sys
import os
import glob
import fnmatch
import natural_sort

#----------------------------------------------------------------------------

def usage():
    print('')
    print('Usage:')
    print('    create_lib_library <destlibdir> <destlib> [-compile-only] ')
    print('             [-excludelist="file1,file2,..."]')
    print('')
    print('Create a single liberty library from a set of individual liberty files.')
    print('')
    print('where:')
    print('    <destlibdir>      is the directory containing the individual liberty files')
    print('    <destlib>         is the root name of the library file')
    print('    -compile-only     remove the indidual files if specified')
    print('    -excludelist=     is a comma-separated list of files to ignore')
    print('')

#----------------------------------------------------------------------------
# Warning:  This script is unfinished.  Needs to parse the library header
# in each cell and generate a new library header combining the contents of
# all cell headers.  Also:  The library name in the header needs to be
# changed to the full library name.  Also:  There is no mechanism for
# collecting all files belonging to a single process corner/temperature/
# voltage.
#----------------------------------------------------------------------------

def create_lib_library(destlibdir, destlib, do_compile_only=False, excludelist=[]):

    # destlib should not have a file extension
    destlibroot = os.path.splitext(destlib)[0]

    alllibname = destlibdir + '/' + destlibroot + '.lib'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    print('Diagnostic:  Creating consolidated liberty library ' + destlibroot + '.lib')

    # If file "filelist.txt" exists in the directory, get the list of files from it
    if os.path.exists(destlibdir + '/filelist.txt'):
        with open(destlibdir + '/filelist.txt', 'r') as ifile:
            rlist = ifile.read().splitlines()
            llist = []
            for rfile in rlist:
                llist.append(destlibdir + '/' + rfile)
    else:
        llist = glob.glob(destlibdir + '/*.lib')
        llist = natural_sort.natural_sort(llist)

    # Create exclude list with glob-style matching using fnmatch
    if len(llist) > 0:
        llistnames = list(os.path.split(item)[1] for item in llist)
        notllist = []
        for exclude in excludelist:
            notllist.extend(fnmatch.filter(llistnames, exclude))

        # Apply exclude list
        if len(notllist) > 0:
            for file in llist[:]:
                if os.path.split(file)[1] in notllist:
                    llist.remove(file)

    if len(llist) > 1:
        print('New file is:  ' + alllibname)
        with open(alllibname, 'w') as ofile:
            headerdone = False
            for lfile in llist:
                if not os.path.exists(lfile):
                    print('Error: File ' + lfile + ' not found (skipping).')
                    continue
                with open(lfile, 'r') as ifile:
                    # print('Adding ' + lfile + ' to library.')
                    ltext = ifile.read()
                    llines = ltext.splitlines()
                    headerseen = False
                    for lline in llines:
                        if headerdone:
                            if not headerseen:
                                ltok = lline.split('(')
                                if len(ltok) == 0 or not ltok[0].strip() == 'cell':
                                    continue
                                else:
                                    headerseen = True
                        print(lline, file=ofile)
                    headerdone = True
                print('/*--------EOF---------*/\n', file=ofile)

        if do_compile_only == True:
            print('Compile-only:  Removing individual LEF files')
            for lfile in llist:
                if os.path.isfile(lfile):
                    os.remove(lfile)
    else:
        print('Only one file (' + str(llist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    argumentlist = []

    # Defaults
    do_compile_only = False
    excludelist = []

    # Break arguments into groups where the first word begins with "-".
    # All following words not beginning with "-" are appended to the
    # same list (optionlist).  Then each optionlist is processed.
    # Note that the first entry in optionlist has the '-' removed.

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            keyval = option[1:].split('=')
            if keyval[0] == 'compile-only':
                if len(keyval) > 0:
                    if keyval[1].tolower() == 'true' or keyval[1].tolower() == 'yes' or keyval[1] == '1':
                        do_compile_only = True
                else:
                    do_compile_only = True
            elif keyval[1] == 'exclude' or key == 'excludelist':
                if len(keyval) > 0:
                    excludelist = keyval[1].trim('"').split(',')
                else:
                    print("No items in exclude list (ignoring).")
            else:
                print("Unknown option '" + keyval[0] + "' (ignoring).")
        else:
            argumentlist.append(option)

    if len(argumentlist) < 3: 
        print("Not enough arguments given to create_lib_library.py.")
        usage()
        sys.exit(1)

    destlibdir = argumentlist[0]
    destlib = argumentlist[1]
    startup_script = argumentlist[2]

    print('')
    print('Create liberty library from files:')
    print('')
    print('Path to files: ' + destlibdir)
    print('Name of compiled library: ' + destlib + '.lib')
    print('Remove individual files: ' + 'Yes' if do_compile_only else 'No')
    if len(excludelist) > 0:
        print('List of files to exclude: ')
        for file in excludelist:
            print(file)
    print('')

    create_lib_library(destlibdir, destlib, do_compile_only, excludelist)
    print('Done.')
    sys.exit(0)

#----------------------------------------------------------------------------
