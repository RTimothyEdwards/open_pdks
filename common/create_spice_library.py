#!/usr/bin/env python3
#
# create_spice_library.py
#
#----------------------------------------------------------------------------
# Given a destination directory holding individual SPICE netlists of a number
# of cells, create a single SPICE library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-spice" install.
#----------------------------------------------------------------------------

import sys
import os
import re
import glob
import fnmatch
import natural_sort

#----------------------------------------------------------------------------

def usage():
    print('')
    print('Usage:')
    print('    create_spice_library <destlibdir> <destlib> <spiext>')
    print('            [-compile-only] [-stub] [-excludelist="file1,file2,..."]')
    print('')
    print('Create a single SPICE or CDL library from a set of individual files.')
    print('')
    print('where:')
    print('    <destlibdir>      is the directory containing the individual files')
    print('    <destlib>         is the root name of the library file')
    print('    <spiext>          is the extension used (with ".") by the SPICE or CDL files')
    print('    -compile-only     remove the indidual files if specified')
    print('    -stub             generate only .subckt ... .ends for each cell')
    print('    -excludelist=     is a comma-separated list of files to ignore')
    print('')

#----------------------------------------------------------------------------

def create_spice_library(destlibdir, destlib, spiext, do_compile_only=False, do_stub=False, excludelist=[]):

    # destlib should not have a file extension
    destlibroot = os.path.splitext(destlib)[0]

    fformat = 'CDL' if spiext == '.cdl' else 'SPICE'

    allstubname = destlibdir + '/stub' + spiext
    alllibname = destlibdir + '/' + destlibroot + spiext
    if do_stub:
        outputname = allstubname
    else:
        outputname = alllibname

    print('Diagnostic:  Creating consolidated ' + fformat + ' library ' + outputname)

    if os.path.isfile(outputname):
        os.remove(outputname)

    # If file "filelist.txt" exists in the directory, get the list of files from it
    if os.path.exists(destlibdir + '/filelist.txt'):
        with open(destlibdir + '/filelist.txt', 'r') as ifile:
            rlist = ifile.read().splitlines()
            slist = []
            for rfile in rlist:
                slist.append(destlibdir + '/' + rfile)
    else:
        if fformat == 'CDL':
            slist = glob.glob(destlibdir + '/*.cdl')
        else:
            # Sadly, there is no consensus on what a SPICE file extension should be.
            spiexts = ['.spc', '.spice', '.spi', '.ckt', '.cir']
            if spiext not in spiexts:
                spiexts.append(spiext)
            slist = []
            for extension in spiexts:
                slist.extend(glob.glob(destlibdir + '/*' + extension))

        slist = natural_sort.natural_sort(slist)

    if alllibname in slist:
        slist.remove(alllibname)

    if allstubname in slist:
        slist.remove(allstubname)

    # Create exclude list with glob-style matching using fnmatch
    if len(slist) > 0:
        slistnames = list(os.path.split(item)[1] for item in slist)
        notslist = []
        for exclude in excludelist:
            notslist.extend(fnmatch.filter(slistnames, exclude))

        # Apply exclude list
        if len(notslist) > 0:
            for file in slist[:]:
                if os.path.split(file)[1] in notslist:
                    slist.remove(file)

    if len(slist) > 1:
        with open(outputname, 'w') as ofile:
            allsubckts = []
            for sfile in slist:
                with open(sfile, 'r') as ifile:
                    # print('Adding ' + sfile + ' to library.')
                    stext = ifile.read()
                    subckts = re.findall(r'\.subckt[ \t]+([^ \t\n]+)', stext, flags=re.IGNORECASE)
                    sseen = list(item for item in subckts if item in allsubckts)
                    allsubckts.extend(list(item for item in subckts if item not in allsubckts))
                    sfilter = remove_redundant_subckts(stext, subckts, sseen)
                    print(sfilter, file=ofile)
                print('\n******* EOF\n', file=ofile)

        if do_compile_only == True:
            print('Compile-only:  Removing individual SPICE files')
            for sfile in slist:
                if os.path.isfile(sfile):
                    os.remove(sfile)
                elif os.path.islink(sfile):
                    os.unlink(sfile)
    else:
        print('Only one file (' + str(slist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Remove redundant subcircuit entries from a SPICE or CDL netlist file.  "sseen"
# is a list of subcircuit names gleaned from all previously read files using
# re.findall(). "slist" is a list of subcircuits including those in "ntext".
# If a subcircuit is defined outside of "ntext", then remove all occurrences in
# "ntext".  Otherwise, if a subcircuit is defined more than once in "ntext",
# remove all but one copy.  The reason for doing this is that some netlists will
# include primitive device definitions used by all the standard cell subcircuits.
#
# It may be necessary to remove redundant .include statements and redundant .model
# and/or .option statements as well.
#----------------------------------------------------------------------------

def remove_redundant_subckts(ntext, slist, sseen):
    updated = ntext
    for subckt in slist:
        if subckt in sseen:
            # Remove all occurrences of subckt
            updated = re.sub(r'\n\.subckt[ \t]+' + subckt + '[ \t\n]+.*?\n\.ends[ \t\n]+', '\n', updated, flags=re.IGNORECASE | re.DOTALL)

        else:
            # Determine the number of times the subcircuit appears in the text
            n = len(re.findall(r'\n\.subckt[ \t]+' + subckt + '[ \t\n]+.*?\n\.ends[ \t\n]+', updated, flags=re.IGNORECASE | re.DOTALL))
            # Optimization:  Just keep original text if n < 2
            if n < 2:
                continue

            # Remove all but one
            updated = re.sub(r'\n\.subckt[ \t]+' + subckt + '[ \t\n]+.*?\n\.ends[ \t\n]+', '\n', updated, n - 1, flags=re.IGNORECASE | re.DOTALL)
    return updated

#----------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    argumentlist = []

    # Defaults
    do_compile_only = False
    do_stub = False
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
            elif keyval[1] == 'stub':
                if len(keyval) > 0:
                    if keyval[1].tolower() == 'true' or keyval[1].tolower() == 'yes' or keyval[1] == '1':
                        do_stub = True
                else:
                    do_stub = True
            else:
                print("Unknown option '" + keyval[0] + "' (ignoring).")
        else:
            argumentlist.append(option)

    if len(argumentlist) < 3: 
        print("Not enough arguments given to create_spice_library.py.")
        usage()
        sys.exit(1)

    destlibdir = argumentlist[0]
    destlib = argumentlist[1]
    spiext = argumentlist[2]

    print('')
    if spiext == '.cdl':
        print('Create CDL library from files:')
    else:
        print('Create SPICE library from files:')
    print('')
    print('Path to files: ' + destlibdir)
    print('Name of compiled library: ' + destlib + spiext)
    print('Remove individual files: ' + 'Yes' if do_compile_only else 'No')
    if len(excludelist) > 0:
        print('List of files to exclude: ')
        for file in excludelist:
            print(file)
    print('')

    create_spice_library(destlibdir, destlib, spiext, do_compile_only, do_stub, excludelist)
    print('Done.')
    sys.exit(0)

#----------------------------------------------------------------------------
