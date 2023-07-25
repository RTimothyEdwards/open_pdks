#!/usr/bin/env python3
#
# create_verilog_library.py
#
#----------------------------------------------------------------------------
# Given a destination directory holding individual verilog files of a number
# of modules, create a single verilog library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-verilog" install.
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
    print('    create_verilog_library <destlibdir> <destlib> [-compile-only]')
    print('            [-stub] [-excludelist="file1,file2,..."]')
    print('')
    print('Create a single verilog library from a set of individual verilog files.')
    print('')
    print('where:')
    print('    <destlibdir>      is the directory containing the individual files')
    print('    <destlib>         is the root name of the library file')
    print('    -compile-only     remove the indidual files if specified')
    print('    -stub             generate file of blackbox modules for each cell')
    print('    -excludelist=     is a comma-separated list of files to ignore')
    print('')

#----------------------------------------------------------------------------

def create_verilog_library(destlibdir, destlib, do_compile_only=False, do_stub=False, excludelist=[]):

    # 'destlib' should not have an extension, because one will be generated.
    destlibroot = os.path.splitext(destlib)[0]

    allstubname = destlibdir + '/' + destlibroot + '__blackbox.v'
    alllibname = destlibdir + '/' + destlibroot + '.v'

    if os.path.isfile(alllibname):
        os.remove(alllibname)

    if do_stub:
        if os.path.isfile(allstubname):
            os.remove(allstubname)

    print('Diagnostic:  Creating consolidated verilog library ' + destlibroot + '.v')

    # If file "filelist.txt" exists in the directory, get the list of files from it
    if os.path.exists(destlibdir + '/filelist.txt'):
        print('Diagnostic:  Reading sorted verilog file list.')
        with open(destlibdir + '/filelist.txt', 'r') as ifile:
            rlist = ifile.read().splitlines()
            vlist = []
            for rfile in rlist:
                vlist.append(destlibdir + '/' + rfile)
    else:
        vlist = glob.glob(destlibdir + '/*.v')
        vlist = natural_sort.natural_sort(vlist)

    if alllibname in vlist:
        vlist.remove(alllibname)

    # Create exclude list with glob-style matching using fnmatch
    if len(vlist) > 0:
        vlistnames = list(os.path.split(item)[1] for item in vlist)
        notvlist = []
        for exclude in excludelist:
            notvlist.extend(fnmatch.filter(vlistnames, exclude))

        # Apply exclude list
        if len(notvlist) > 0:
            for file in vlist[:]:
                if os.path.split(file)[1] in notvlist:
                    vlist.remove(file)

    if len(vlist) > 1:
        print('New file is:  ' + alllibname)
        if do_stub:
            sfile = open(allstubname, 'w')
        with open(alllibname, 'w') as ofile:
            allmodules = []
            for vfile in vlist:
                if not os.path.exists(vfile):
                    print('Error: File ' + vfile + ' not found (skipping).')
                    continue
                with open(vfile, 'r') as ifile:
                    # print('Adding ' + vfile + ' to library.')
                    vtext = ifile.read()
                    modules = re.findall(r'[ \t\n]module[ \t]+([^ \t\n\(]+)', vtext)
                    mseen = list(item for item in modules if item in allmodules)
                    allmodules.extend(list(item for item in modules if item not in allmodules))
                    # NOTE:  "remove_redundant_modules" is disabled because it is
                    # not checking if duplicate modules might exist within separate
                    # blocks of an "ifdef".
                    # vfilter = remove_redundant_modules(vtext, modules, mseen)
                    if do_stub:
                        slines = create_blackboxes(vtext)
                        print(slines, file=sfile)
                    vfilter = vtext

                    # NOTE:  The following workaround resolves an issue with iverilog,
                    # which does not properly parse specify timing paths that are not in
                    # parentheses.  Easy to work around
                    vlines = re.sub(r'\)[ \t]*=[ \t]*([01]:[01]:[01])[ \t]*;', r') = ( \1 ) ;', vfilter)
                    print(vlines, file=ofile)
                print('\n//--------EOF---------\n', file=ofile)

        if do_stub:
            sfile.close()

        if do_compile_only == True:
            print('Compile-only:  Removing individual verilog files')
            for vfile in vlist:
                if os.path.isfile(vfile):
                    os.remove(vfile)
                elif os.path.islink(vfile):
                    os.unlink(vfile)
    else:
        print('Only one file (' + str(vlist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Reduce a verilog file to blackbox modules
#----------------------------------------------------------------------------

def create_blackboxes(ntext):
    updated = []

    modrex = re.compile('^[ \t]*module[ \t\n]+')
    endrex = re.compile('^[ \t]*endmodule[ \t\n]+')
    inrex = re.compile('^[ \t]*input[ \t\n]+')
    outrex = re.compile('^[ \t]*output[ \t\n]+')
    inoutrex = re.compile('^[ \t]*inout[ \t\n]+')
    ifrex = re.compile('^[ \t]*`if')
    elsrex = re.compile('^[ \t]*`els')
    endifrex = re.compile('^[ \t]*`end')
    suprex = re.compile('^[ \t]*supply')

    in_mod = False
    depth = 0
    for line in ntext.splitlines():
        # Strip any comments from line before checking
        nocline = re.sub('[ \t]*//.*', '', line)
        if not in_mod:
            mmatch = modrex.match(nocline)
            if mmatch:
                in_mod = True
                updated.append('(* blackbox *)')
                depth = 1
            updated.append(line)
                
        else:
            # "module" appearing inside a module means that there are
            # multiple module definitions in ifdef blocks.  Ideally
            # the ifdef blocks should be tracked, instead of this bit
            # of a hack.
            mmatch = modrex.match(nocline)
            if mmatch:
                updated.append('(* blackbox *)')
                depth += 1
            ematch = endrex.match(nocline)
            if ematch:
                depth -= 1
                if depth == 0:
                    in_mod = False
                updated.append(line)
            else:
                # input, output, and inout lines remain in module output
                t1match = inrex.match(nocline)
                t2match = outrex.match(nocline)
                t3match = inoutrex.match(nocline)
                tmatch = t1match or t2match or t3match

                # ifdef blocks remain in module output because they may
                # modify the set of I/Os.
                i1match = ifrex.match(nocline)
                i2match = elsrex.match(nocline)
                i3match = endifrex.match(nocline)
                imatch = i1match or i2match or i3match

                # supply1/supply0 lines remain in blackbox module output
                smatch = suprex.match(nocline)

                if tmatch or imatch or smatch:
                    updated.append(line)

    return '\n'.join(updated)

#----------------------------------------------------------------------------
# Remove redundant module entries from a verilog file.  "m2list" is a list of
# module names gleaned from all previously read files using re.findall().
# "mlist" is a list of all module names including those in "ntext".
# The reason for doing this is that some verilog files may includes modules used
# by all the files, and if included more than once, then iverilog complains.
#
# Important note:  This module has been disabled.  It needs to check if
# duplicate modules are inside mutually exclusive conditions of an ifdef
# block.
#----------------------------------------------------------------------------

def remove_redundant_modules(ntext, mlist, m2list):
    updated = ntext
    for module in mlist:
        # Determine the number of times the module appears in the text
        if module in m2list:
            # This module seen before outside of ntext, so remove all occurrances in ntext
            new = re.sub(r'[ \t\n]+module[ \t]+' + module + '[ \t\n\(]+.*?[ \t\n]endmodule', '\n', updated, flags=re.DOTALL)
            updated = new

        else:
            n = len(re.findall(r'[ \t\n]module[ \t]+' + module + '[ \t\n\(]+.*?[ \t\n]endmodule', updated, flags=re.DOTALL))
            # This module defined more than once inside ntext, so remove all but one
            # Optimization:  Just keep original text if n < 2
            if n < 2:
                continue

            # Remove all but one
            updated = re.sub(r'[ \t\n]+module[ \t]+' + module + '[ \t\n]+.*?[ \t\n]endmodule', '\n', updated, n - 1, flags=re.IGNORECASE | re.DOTALL)
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
            elif keyval[0] == 'stub':
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
        print("Not enough arguments given to create_verilog_library.py.")
        usage()
        sys.exit(1)

    destlibdir = argumentlist[0]
    destlib = argumentlist[1]
    startup_script = argumentlist[2]

    print('')
    print('Create verilog library from files:')
    print('')
    print('Path to files: ' + destlibdir)
    print('Name of compiled library: ' + destlib + '.v')
    print('Path to magic startup script: ' + startup_script)
    print('Remove individual files: ' + 'Yes' if do_compile_only else 'No')
    if len(excludelist) > 0:
        print('List of files to exclude: ')
        for file in excludelist:
            print(file)
    print('')

    create_verilog_library(destlibdir, destlib, startup_script, do_compile_only, do_stub, excludelist)
    print('Done.')
    sys.exit(0)

#----------------------------------------------------------------------------
