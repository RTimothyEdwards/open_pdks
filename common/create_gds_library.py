#!/usr/bin/env python3
#
# create_gds_library.py
#
#----------------------------------------------------------------------------
# Given a destination directory holding individual GDS files of a number
# of cells, create a single GDL library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-gds" install.
#----------------------------------------------------------------------------

import os
import sys
import glob
import fnmatch
import subprocess
import natural_sort

#----------------------------------------------------------------------------

def usage():
    print('')
    print('Usage:')
    print('    create_gds_library <destlibdir> <destlib> <startup_script> ')
    print('             [-compile-only] [-excludelist="file1,file2,..."] [-keep]')
    print('')
    print('Create a single GDS library from a set of individual GDS files.')
    print('')
    print('where:')
    print('    <destlibdir>      is the directory containing the individual GDS files')
    print('    <destlib>         is the root name of the library file')
    print('    <startup_script>  is the full path to a magic startup script')
    print('    -compile-only     removes the indidual files if specified')
    print('    -excludelist=     is a comma-separated list of files to ignore')
    print('    -keep             keep the Tcl script used to generate the library')
    print('')

#----------------------------------------------------------------------------

def create_gds_library(destlibdir, destlib, startup_script, do_compile_only=False, excludelist=[], keep=False):

    # destlib should not have a file extension
    destlibroot = os.path.splitext(destlib)[0]

    alllibname = destlibdir + '/' + destlibroot + '.gds'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    # If file "filelist.txt" exists in the directory, get the list of files from it
    if os.path.exists(destlibdir + '/filelist.txt'):
        with open(destlibdir + '/filelist.txt', 'r') as ifile:
            rlist = ifile.read().splitlines()
            glist = []
            for rfile in rlist:
                glist.append(destlibdir + '/' + rfile)
    else:
        glist = glob.glob(destlibdir + '/*.gds')
        glist.extend(glob.glob(destlibdir + '/*.gdsii'))
        glist.extend(glob.glob(destlibdir + '/*.gds2'))
        glist = natural_sort.natural_sort(glist)

    if alllibname in glist:
        glist.remove(alllibname)

    # Create exclude list with glob-style matching using fnmatch
    if len(glist) > 0:
        glistnames = list(os.path.split(item)[1] for item in glist)
        notglist = []
        for exclude in excludelist:
            notglist.extend(fnmatch.filter(glistnames, exclude))

        # Apply exclude list
        if len(notglist) > 0:
            for file in glist[:]:
                if os.path.split(file)[1] in notglist:
                    glist.remove(file)

    if len(glist) > 1:
        print('New file is:  ' + alllibname)

        if os.path.isfile(startup_script):
            # If the symbolic link exists, remove it.
            if os.path.isfile(destlibdir + '/.magicrc'):
                os.remove(destlibdir + '/.magicrc')
            os.symlink(startup_script, destlibdir + '/.magicrc')

        # A GDS library is binary and requires handling in Magic
        print('Creating magic generation script to generate GDS library.') 
        with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
            print('#!/usr/bin/env wish', file=ofile)
            print('#--------------------------------------------', file=ofile)
            print('# Script to generate .gds library from files   ', file=ofile)
            print('#--------------------------------------------', file=ofile)
            print('drc off', file=ofile)
            print('locking off', file=ofile)
            print('gds readonly true', file=ofile)
            # print('gds flatten true', file=ofile)
            print('gds polygon subcell true', file=ofile)
            print('gds rescale false', file=ofile)
            print('tech unlock *', file=ofile)

            for gdsfile in glist:
                print('gds read ' + gdsfile, file=ofile)

            # Remove any cell named "(UNNAMED)"
            print('cellname delete \(UNNAMED\)', file=ofile)

            # Get list of cell names, which may be different than the
            # file names.
            print('set glist [cellname list top]', file=ofile)

            print('puts stdout "Creating cell ' + destlibroot + '"', file=ofile)
            print('load ' + destlibroot, file=ofile)
            print('puts stdout "Adding cells to library"', file=ofile)
            print('box values 0 0 0 0', file=ofile)

            # for gdsfile in glist:
            #     gdsroot = os.path.split(gdsfile)[1]
            #     gdsname = os.path.splitext(gdsroot)[0]
            #     print('getcell ' + gdsname, file=ofile)
            #     # Could properly make space for the cell here. . . 
            #     print('box move e 200', file=ofile)

            print('foreach gcell $glist {', file=ofile)
            print('    getcell $gcell', file=ofile)
            print('    box move e 200', file=ofile)
            print('}', file=ofile)
                                
            print('puts stdout "Writing GDS library ' + destlibroot + '"', file=ofile)
            print('gds library true', file=ofile)
            print('gds write ' + destlibroot, file=ofile)
            print('puts stdout "Done."', file=ofile)
            print('quit -noprompt', file=ofile)

        # Run magic to read in the individual GDS files and
        # write out the consolidated GDS library

        print('Running magic to create GDS library.')
        sys.stdout.flush()

        mproc = subprocess.run(['magic', '-dnull', '-noconsole',
			destlibdir + '/generate_magic.tcl'],
			stdin = subprocess.DEVNULL,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, cwd = destlibdir,
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
        if do_compile_only == True:
            print('Compile-only:  Removing individual GDS files')
            for gfile in glist:
                if os.path.isfile(gfile):
                    os.remove(gfile)
        if not keep:
            os.remove(destlibdir + '/generate_magic.tcl')
    else:
        print('Only one file (' + str(glist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    argumentlist = []

    # Defaults
    do_compile_only = False
    keep = False
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
            elif keyval[1] == 'keep':
                keep = True
            else:
                print("Unknown option '" + keyval[0] + "' (ignoring).")
        else:
            argumentlist.append(option)

    if len(argumentlist) < 3: 
        print("Not enough arguments given to create_gds_library.py.")
        usage()
        sys.exit(1)

    destlibdir = argumentlist[0]
    destlib = argumentlist[1]
    startup_script = argumentlist[2]

    print('')
    print('Create GDS library from files:')
    print('')
    print('Path to files: ' + destlibdir)
    print('Name of compiled library: ' + destlib + '.gds')
    print('Path to magic startup script: ' + startup_script)
    print('Remove individual files: ' + 'Yes' if do_compile_only else 'No')
    if len(excludelist) > 0:
        print('List of files to exclude: ')
        for file in excludelist:
            print(file)
    print('Keep generating script: ' + 'Yes' if keep else 'No')
    print('')

    create_gds_library(destlibdir, destlib, startup_script, do_compile_only, excludelist, keep)
    print('Done.')
    sys.exit(0)

#----------------------------------------------------------------------------
