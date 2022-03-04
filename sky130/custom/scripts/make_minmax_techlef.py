#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# make_minmax_techlef.py --
#
# From a nominal technology LEF file, create the corresponding
# technology files for the minimum and maximum process corners.
# Currently this only considers the change in layer and via
# resistance, not parasitic capacitance.
#
# Usage:
#
#    make_minmax_techlef.py -variant=sky130A|sky130B
#		-library=hd|hs|lp|ls|ms|hdll|hvl
#		[-ef_format]
#
# Given the PDK variant and library name, finds the technology
# LEF file in the staging area with the nominal corner values,
# and creates two additional technology LEF files for the
# minimum and maximum corners.
#--------------------------------------------------------------------

import os
import re
import sys

options = []
arguments = []
for item in sys.argv[1:]:
    if item.find('-', 0) == 0:
        options.append(item[1:])
    else:
        arguments.append(item)

variant = 'sky130A'
lib = 'hd'
tlefpath = variant + '/libs.ref/sky130_fd_sc_' + lib + '/techlef'

if len(options) > 0:
    for option in options:
        if option.startswith('variant'):
            variant = option.split('=')[1]
        elif option.startswith('library'):
            lib = option.split('=')[1]
    tlefpath = variant + '/libs.ref/sky130_fd_sc_' + lib + '/techlef'
    for option in options:
        if option == 'ef_format':
            tlefpath = variant + '/libs.ref/techLEF/sky130_fd_sc_' + lib
elif len(arguments) > 0:
    tlefpath = arguments[0]

tlefbase = 'sky130_fd_sc_' + lib + '__'
tlefnom  = tlefbase + 'nom.tlef'

resrex1  = re.compile('^[ \t]*RESISTANCE RPERSQ')
resrex2  = re.compile('^[ \t]*RESISTANCE')
layerrex = re.compile('^[ \t]*LAYER ([^ \t\n]+)')

# Resistance values, by layer

rnom = {}
rmin = {}
rmax = {}

# Nominal values are for reference only;  they're not used in the code below
rnom['li1']  = '12.8'
rnom['mcon'] = '9.3'
rnom['met1'] = '0.125'
rnom['via']  = '4.5'
rnom['met2'] = '0.125'
rnom['via2'] = '3.41'
rnom['met3'] = '0.047'
rnom['via3'] = '3.41'
rnom['met4'] = '0.047'
rnom['via4'] = '0.38'
rnom['met5'] = '0.0285'

rmin['li1']  = '9.2'
rmin['mcon'] = '1.6'
rmin['met1'] = '0.105'
rmin['via']  = '2.0'
rmin['met2'] = '0.105'
rmin['via2'] = '0.5'
rmin['met3'] = '0.038'
rmin['via3'] = '0.5'
rmin['met4'] = '0.038'
rmin['via4'] = '0.012'
rmin['met5'] = '0.0212'

rmax['li1']  = '17.0'
rmax['mcon'] = '23.0'
rmax['met1'] = '0.145'
rmax['via']  = '15.0'
rmax['met2'] = '0.145'
rmax['via2'] = '8.0'
rmax['met3'] = '0.056'
rmax['via3'] = '8.0'
rmax['met4'] = '0.056'
rmax['via4'] = '0.891'
rmax['met5'] = '0.0358'

if variant == 'sky130B':
    rnom['via'] = '9.0'
    rmin['via'] = '4.0'
    rmax['via'] = '30.0'

#--------------------------------------------------------------------

infile_name = tlefpath + '/' + tlefnom
print('Creating minimum and maximum corner variants of ' + infile_name)

if not os.path.exists(infile_name):
    print('Error:  Cannot find file ' + infile_name)
    sys.exit(1)

for corner in ['min', 'max']:
    tleffile  = tlefbase + corner + '.tlef'
    outfile_name = tlefpath + '/' + tleffile

    infile   = open(infile_name, 'r')
    outfile  = open(outfile_name, 'w')
    curlayer = None
    value    = None

    for line in infile:
        rmatch1 = resrex1.match(line)
        rmatch2 = resrex2.match(line)
        lmatch  = layerrex.match(line)
        if lmatch:
            curlayer = lmatch.group(1)
            if curlayer in rnom:
                if corner == 'min':
                    value = rmin[curlayer]
                else:
                    value = rmax[curlayer]
            else:
                value = None
            outfile.write(line)
        elif value and rmatch1:
            outfile.write('  RESISTANCE RPERSQ ' + value + ' ;\n')
        elif value and rmatch2:
            outfile.write('  RESISTANCE ' + value + ' ;\n')
        else:
            outfile.write(line)

    infile.close()
    outfile.close()

