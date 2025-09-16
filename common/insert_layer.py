#!/usr/bin/env python3
#
# insert_layer.py:  For the given install path, library name, and cellname,
# find the Magic layout of the cell, and add the specified layer geometry
# as given by a layer name and a string with four coordinate values.
# The layer is added to the layout in both the mag/ (full) and maglef/
# (abstract) directories.  Option "-maglef" or "-mag" will restrict the
# use to only the view indicated by the option.
#
# Extended 7/30/2023 to allow multiple rectangles to be specified by
# allowing any multiple of four coordinates.  So eight coordinates will
# generate two "rect" lines, for example.
# 
# e.g.:
#
# insert_layer.py /path/to/sky130A \
#	sky130_fd_io sky130_fd_sc_hd__a21bo_1 pwell "29 17 69 157" -mag

import os
import re
import sys

def addlayer(filename, layer, geometry):
    with open(filename, 'r') as ifile:
        magtext = ifile.read().splitlines() 

    layerrex = re.compile('<< ' + layer + ' >>')
    sectionrex = re.compile('<< ')
    labelsrex = re.compile('<< labels >>')
    propsrex = re.compile('<< properties >>')
    endrex = re.compile('<< end >>')

    in_layer = False
    done = False

    with open(filename, 'w') as ofile:
        for line in magtext:
            if not done and not in_layer:
                # Handle case in which layer did not already exist in file
                lmatch = labelsrex.match(line)
                pmatch = propsrex.match(line)
                ematch = endrex.match(line)
                if lmatch or pmatch or ematch:
                    print('<< ' + layer + ' >>', file=ofile)
                    for coords in zip(*[iter(geometry.split())]*4):
                        print('rect ' + ' '.join(coords), file=ofile)
                    done = True
            
            lmatch = layerrex.match(line)
            if lmatch or pmatch:
                in_layer = True
            elif in_layer:
                smatch = sectionrex.match(line)
                if smatch:
                    for coords in zip(*[iter(geometry.split())]*4):
                        print('rect ' + ' '.join(coords), file=ofile)
                    in_layer = False
                    done = True

            print(line, file=ofile)

def usage():
    print("insert_layer.py <path_to_pdk> <libname> <cellname> <layer> <geometry> [option]")
    print("  options:")
    print("   -mag      do only for the view in the mag/ directory")
    print("   -maglef   do only for the view in the maglef/ directory")
    return 0

if __name__ == '__main__':

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0 and len(item) > 1 and item[1].isalpha():
            options.append(item)
        else:
            arguments.append(item)

    if len(arguments) < 5:
        print("Not enough arguments given to insert_layer.py.")
        usage()
        sys.exit(0)

    source = arguments[0]
    libname = arguments[1]
    cellname = arguments[2]
    layer = arguments[3]
    geometry = arguments[4]

    # Diagnostic
    print('insert_layer.py:')
    print('   source   = ' + source)
    print('   library  = ' + libname)
    print('   cell     = ' + cellname)
    print('   layer    = ' + layer)
    print('   geometry = ' + geometry)

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
            addlayer(filename, layer, geometry)
        else:
            fail += 1
    else:
        fail += 1

    if domaglef:
        filename = source + '/libs.ref/' + libname + '/maglef/' + cellname + '.mag'

        if os.path.isfile(filename):
            addlayer(filename, layer, geometry)
        else:
            fail += 1
    else:
        fail += 1

    if fail == 2:
        print('Error:  No layout file in either mag/ or maglef/', file=sys.stderr)
        print('(' + source + '/libs.ref/' + libname + '/mag[lef]/'
		+ cellname + '.mag)', file=sys.stderr)

