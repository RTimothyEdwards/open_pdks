#!/usr/bin/env python3
#
# remove_label.py:  For the given install path, library name, and cellname,
# find the Magic layout of the cell, and remove any label equal to the
# given label text (which may contain glob-syntax wildcards).  Ensure that
# any port designation for any deleted label is also removed.
# The label is remove from layout in both the mag/ (full) and maglef/
# (abstract) directories.  Option "-maglef" or "-mag" will restrict the
# use to only the view indicated by the option.
#
# The cell name may also be wildcarded with glob-style syntax.
# 
# e.g.:
#
# remove_label.py /path/to/gf180mcu \
#	gf180mcu_fd_ip_sram rarray4\* BL\* -mag

import os
import re
import sys
import glob
import fnmatch

def removelabel(filename, text):
    filelist = glob.glob(filename)
    for file in filelist:
        with open(file, 'r') as ifile:
            magtext = ifile.read().splitlines() 

        sectionrex = re.compile('<< ')
        labelsrex = re.compile('<< labels >>')

        in_labels = False
        ignore = False
        watch = False

        with open(file, 'w') as ofile:
            for line in magtext:
                watch = True if ignore else False
                ignore = False
                lmatch = labelsrex.match(line)
                if lmatch:
                    in_labels = True
                elif in_labels:
                    smatch = sectionrex.match(line)
                    if smatch:
                        in_labels = False
                    else:
                        label = line.split()[-1]
                        if fnmatch.fnmatch(label, text):
                            ignore = True
                        elif watch:
                            if line.startswith('port'):
                                ignore = True

                if not ignore:
                    print(line, file=ofile)

def usage():
    print("remove_label.py <path_to_pdk> <libname> <cellname> <text> [option]")
    print("  options:")
    print("   -mag      do only for the view in the mag/ directory")
    print("   -maglef   do only for the view in the maglef/ directory")
    return 0

if __name__ == '__main__':

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    if len(arguments) < 4:
        print("Not enough options given to remove_label.py.")
        usage()
        sys.exit(0)

    source = arguments[0]
    libname = arguments[1]
    cellname = arguments[2]
    text = arguments[3]

    # Diagnostic
    print('remove_label.py:')
    print('   source   = ' + source)
    print('   library  = ' + libname)
    print('   cell     = ' + cellname)
    print('   text     = ' + text)

    fail = 0

    efformat = True if '-ef_format' in options else False

    domag = True
    domaglef = True
    if '-mag' in options and '-maglef' not in options:
        domaglef = False
    if '-maglef' in options and '-mag' not in options:
        domag = False

    if domag:
        if efformat:
            filename = source + '/libs.ref/mag/' + libname + '/' + cellname + '.mag'
        else:
            filename = source + '/libs.ref/' + libname + '/mag/' + cellname + '.mag'

        if os.path.isfile(filename):
            removelabel(filename, text)
        elif len(glob.glob(filename)) > 0:
            removelabel(filename, text)
        else:
            fail += 1
    else:
        fail += 1

    if domaglef:
        if efformat:
            filename = source + '/libs.ref/maglef/' + libname + '/' + cellname + '.mag'
        else:
            filename = source + '/libs.ref/' + libname + '/maglef/' + cellname + '.mag'

        if os.path.isfile(filename):
            removelabel(filename, text)
        elif len(glob.glob(filename)) > 0:
            removelabel(filename, text)
        else:
            fail += 1
    else:
        fail += 1

    if fail == 2:
        print('Error:  No matching layout file in either mag/ or maglef/', file=sys.stderr)
        if efformat:
            print('(' + source + '/libs.ref/mag[lef]/' + libname +
		    '/' + cellname + '.mag)', file=sys.stderr)
        else:
            print('(' + source + '/libs.ref/' + libname + '/mag[lef]/'
		    + cellname + '.mag)', file=sys.stderr)

