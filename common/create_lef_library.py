#!/usr/bin/env python3
#
# create_lef_library.py
#
#----------------------------------------------------------------------------
# Given a destination directory holding individual LEF files of a number
# of cells, create a single LEF library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-lef" install.
#----------------------------------------------------------------------------

import sys
import os
import glob
import fnmatch

#----------------------------------------------------------------------------

def usage():
    print('')
    print('Usage:')
    print('    create_lef_library <destlibdir> <destlib> [-compile-only]')
    print('            [-excludelist="file1,file2,..."]')
    print('')
    print('Create a single LEF library from a set of individual LEF files.')
    print('')
    print('where:')
    print('    <destlibdir>      is the directory containing the individual LEF files')
    print('    <destlib>         is the root name of the library file')
    print('    -compile-only     remove the indidual files if specified')
    print('    -excludelist=     is a comma-separated list of files to ignore')
    print('')

#----------------------------------------------------------------------------

def create_lef_library(destlibdir, destlib, do_compile_only=False, excludelist=[]):

    # destlib should not have a file extension
    destlibroot = os.path.splitext(destlib)[0]

    alllibname = destlibdir + '/' + destlibroot + '.lef'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    print('Diagnostic:  Creating consolidated LEF library ' + destlibroot + '.lef')
    llist = glob.glob(destlibdir + '/*.lef')
    if alllibname in llist:
        llist.remove(alllibname)

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
                with open(lfile, 'r') as ifile:
                    # print('Adding ' + lfile + ' to library.')
                    ltext = ifile.read()
                    llines = ltext.splitlines()
                    headerseen = False
                    for lline in llines:
                        if headerdone:
                            if not headerseen:
                                if not lline.startswith('MACRO'):
                                    continue
                                else:
                                    headerseen = True
                        ltok = lline.split()
                        if len(ltok) > 1 and ltok[0] == 'END' and ltok[1] == 'LIBRARY':
                            # Remove "END LIBRARY" line from individual files
                            pass
                        else:
                            print(lline, file=ofile)
                    headerdone = True
                print('#--------EOF---------\n', file=ofile)

            # Add "END LIBRARY" to the end of the library file
            print('', file=ofile)
            print('END LIBRARY', file=ofile)

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

    if len(argumentlist) < 2: 
        print("Not enough arguments given to create_lef_library.py.")
        usage()
        sys.exit(1)

    destlibdir = argumentlist[0]
    destlib = argumentlist[1]

    print('')
    print('Create LEF library from files:')
    print('')
    print('Path to files: ' + destlibdir)
    print('Name of compiled library: ' + destlib + '.lef')
    print('Remove individual files: ' + 'Yes' if do_compile_only else 'No')
    if len(excludelist) > 0:
        print('List of files to exclude: ')
        for file in excludelist:
            print(file)
    print('')

    create_lef_library(destlibdir, destlib, do_compile_only, excludelist)
    print('Done.')
    sys.exit(0)

#----------------------------------------------------------------------------
