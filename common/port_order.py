#!/usr/bin/env python3
#
# port_order.py:  For the given install path, library name, and cellname,
# find the Magic layout of the cell, and set the indexes of the ports to
# match the order of the specified ports.  The names of the ports must
# match and must be a complete set;  otherwise different ports may end up
# with the same index.
# The port indexes are changed in the layout in both the mag/ (full) and maglef/
# (abstract) directories.  Option "-maglef" or "-mag" will restrict the
# use to only the view indicated by the option.
# 
# e.g.:
#
# port_order.py /path/to/sky130A \
#	sky130_fd_sc_hd sky130_fd_sc_hd__inv_1 A VGND VNB VPB VPWR Y

import os
import re
import sys

def order_ports(filename, portnames):
    with open(filename, 'r') as ifile:
        magtext = ifile.read().splitlines() 

    labrex = re.compile('<< labels >>')

    in_labs = False
    portidx = 0

    with open(filename, 'w') as ofile:
        for line in magtext:
            lmatch = labrex.match(line)
            if lmatch:
                in_labs = True
                print(line, file=ofile)
            elif in_labs:
                linetok = line.split()
                if linetok[0] == 'port':
                    if portidx > 0:
                        print(linetok[0] + ' ' + str(portidx) + ' ' + linetok[2], file=ofile)
                    else:
                        print(line, file=ofile)
                    portidx = 0
                elif linetok[0] == 'flabel':
                    portlab = linetok[-1]
                    try:
                        portidx = portnames.index(portlab) + 1
                    except:
                        print('Error: Port order list does not contain "' + portlab + '"')
                        portidx = 0
                    print(line, file=ofile)
                else:
                    print(line, file=ofile)
            else:
                print(line, file=ofile)

def usage():
    print("port_order.py <path_to_pdk> <libname> <cellname> <port_name> ... [option]")
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
        print('Not enough options given to port_order.py.')
        usage()
        sys.exit(0)

    source = arguments[0]
    libname = arguments[1]
    cellname = arguments[2]
    portnames = arguments[3:]

    # Diagnostic
    print('port_order.py:')
    print('   source     = ' + source)
    print('   library    = ' + libname)
    print('   cell       = ' + cellname)
    print('   port names = ' + ' '.join(portnames))

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
            order_ports(filename, portnames)
        else:
            fail += 1
    else:
        fail += 1

    if domaglef:
        filename = source + '/libs.ref/' + libname + '/maglef/' + cellname + '.mag'

        if os.path.isfile(filename):
            order_ports(filename, portnames)
        else:
            fail += 1
    else:
        fail += 1

    if fail == 2:
        print('Error:  No layout file in either mag/ or maglef/', file=sys.stderr)
        print('(' + source + '/libs.ref/' + libname + '/mag[lef]/'
		+ cellname + '.mag)', file=sys.stderr)

