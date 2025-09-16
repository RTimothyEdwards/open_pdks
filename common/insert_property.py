#!/usr/bin/env python3
#
# insert_property.py:  For the given install path, library name, and cellname,
# find the Magic layout of the cell, and add the specified property string.
# If the property exists and is the same as specified, then it remains the
# same.  If the property exists but has a different value, it is replaced.
# The property is added to the layout in both the mag/ (full) and maglef/
# (abstract) directories.  Option "-maglef" or "-mag" will restrict the
# use to only the view indicated by the option.
# 
# e.g.:
#
# insert_property.py /path/to/sky130A \
#	sky130_fd_io sky130_fd_io__top_gpiov2 "MASKHINTS_HVI 0 607 15000 40200"

import os
import re
import sys

def addprop(filename, propstring, noupdate):
    with open(filename, 'r') as ifile:
        magtext = ifile.read().splitlines() 

    propname = propstring.split()[0]
    proprex = re.compile('<< properties >>')
    endrex = re.compile('<< end >>')

    in_props = False
    printed = False
    done = False

    with open(filename, 'w') as ofile:
        for line in magtext:
            pmatch = proprex.match(line)
            if pmatch:
                in_props = True
            elif in_props:
                linetok = line.split()
                if linetok[0] == 'string':
                    testname = linetok[1]
                    testval = linetok[2]
                    if testname == propname:
                        if noupdate == False:
                            print('string ' + propstring, file=ofile)
                            printed = True
                        done = True

            ematch = endrex.match(line)
            if ematch:
                if in_props == False:
                    print('<< properties >>', file=ofile)
                if done == False:
                    print('string ' + propstring, file=ofile)

            if not printed:
                print(line, file=ofile)
            printed = False

def usage():
    print("insert_property.py <path_to_pdk> <libname> <cellname> <prop_string> [option]")
    print("  options:")
    print("   -mag      do only for the view in the mag/ directory")
    print("   -maglef   do only for the view in the maglef/ directory")
    print("   -noupdate do not replace the property if it already exists in the file")
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
        print("Not enough options given to insert_property.py.")
        usage()
        sys.exit(0)

    source = arguments[0]
    libname = arguments[1]
    cellname = arguments[2]
    propstring = arguments[3]

    # Diagnostic
    print('insert_property.py:')
    print('   source   = ' + source)
    print('   library  = ' + libname)
    print('   cell     = ' + cellname)
    print('   property = ' + propstring)

    noupdate = True if '-noupdate' in options else False
    fail = 0

    domag = True
    domaglef = True
    if '-mag' in options and '-maglef' not in options:
        domaglef = False
    if '-maglef' in options and '-mag' not in options:
        domag = False

    if domag:
        filename = source + '/libs.ref/' + libname + '/mag/' + cellname + '.mag'

        if os.path.isfile(filename):
            addprop(filename, propstring, noupdate)
        else:
            fail += 1
    else:
        fail += 1

    if domaglef:
        filename = source + '/libs.ref/' + libname + '/maglef/' + cellname + '.mag'

        if os.path.isfile(filename):
            addprop(filename, propstring, noupdate)
        else:
            fail += 1
    else:
        fail += 1

    if fail == 2:
        print('Error:  No layout file in either mag/ or maglef/', file=sys.stderr)
        print('(' + source + '/libs.ref/' + libname + '/mag[lef]/'
		+ cellname + '.mag)', file=sys.stderr)

