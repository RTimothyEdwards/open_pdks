#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# make_minmax_techlef.py --
#
# From a nominal technology LEF file, create the corresponding
# technology files for the minimum and maximum process corners.
# Currently this only considers the change in layer and Via
# resistance, not parasitic capacitance.  NOTE:  None of the
# technology LEF files has via resistance values, so these are
# inserted after the ARRAYSPACING line.
#
# Usage:
#
#    make_minmax_techlef.py -variant=gf180mcuA|gf180mcuB|gf180mcuC
#		-library=7t5v0|9t5v0
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

variant = 'gf180mcuA'
lib = '7t5v0'
tlefpath = variant + '/libs.ref/gf180mcu_fd_sc_mcu' + lib + '/techlef'

if len(options) > 0:
    for option in options:
        if option.startswith('variant'):
            variant = option.split('=')[1]
        elif option.startswith('library'):
            lib = option.split('=')[1]
    tlefpath = variant + '/libs.ref/gf180mcu_fd_sc_mcu' + lib + '/techlef'
    for option in options:
        if option == 'ef_format':
            tlefpath = variant + '/libs.ref/techLEF/gf180mcu_fd_sc_mcu' + lib
elif len(arguments) > 0:
    tlefpath = arguments[0]

tlefbase = 'gf180mcu_fd_sc_mcu' + lib + '__'
tlefnom  = tlefbase + 'nom.tlef'

resrex1  = re.compile('^[ \t]*RESISTANCE RPERSQ')
resrex2  = re.compile('^[ \t]*ARRAYSPACING')
layerrex = re.compile('^[ \t]*LAYER ([^ \t\n]+)')
caprex   = re.compile('^[ \t]*CAPACITANCE CPERSQDIST')

#--------------------------------------------------------------------
# Resistance values, by layer
#--------------------------------------------------------------------

rnom = {}
rmin = {}
rmax = {}

# Nominal metal resistance values are for reference only;
# they're not used in the code below
rnom['Metal1'] = '0.090'
rnom['Via1']  = '4.5'
rnom['Metal2'] = '0.090'
rnom['Via2'] = '4.5'
if variant == 'gf180mcuA':
    rnom['Metal3'] = '0.040'
else:
    rnom['Metal3'] = '0.090'
rnom['Via3'] = '4.5'
if variant == 'gf180mcuB':
    rnom['Metal4'] = '0.060'
else:
    rnom['Metal4'] = '0.090'
rnom['Via4'] = '4.5'
rnom['Metal5'] = '0.060'

rmax['Metal1'] = '0.104'
rmax['Via1']  = '15.0'
rmax['Metal2'] = '0.104'
rmax['Via2'] = '15.0'
if variant == 'gf180mcuA':
    rmax['Metal3'] = '0.049'
else:
    rmax['Metal3'] = '0.104'
rmax['Via3'] = '15.0'
if variant == 'gf180mcuB':
    rmax['Metal4'] = '0.070'
else:
    rmax['Metal4'] = '0.104'
rmax['Via4'] = '15.0'
rmax['Metal5'] = '0.070'

rmin['Metal1'] = '0.076'
rmin['Via1']  = '0.0'
rmin['Metal2'] = '0.076'
rmin['Via2'] = '0.0'
if variant == 'gf180mcuA':
    rmin['Metal3'] = '0.031'
else:
    rmin['Metal3'] = '0.076'
rmin['Via3'] = '0.0'
if variant == 'gf180mcuB':
    rmin['Metal4'] = '0.050'
else:
    rmin['Metal4'] = '0.076'
rmin['Via4'] = '0.0'
rmin['Metal5'] = '0.050'

#--------------------------------------------------------------------
# Capacitance values, by layer
#--------------------------------------------------------------------

cnom = {}

cnom['Metal1'] = '0.0004'
cnom['Metal2'] = '0.0003'
cnom['Metal3'] = '0.00028'
cnom['Metal4'] = '0.000277'
if variant == 'gf180mcuC':
    cnom['Metal5'] = '0.000174'

#--------------------------------------------------------------------

infile_name = tlefpath + '/' + tlefnom
print('Creating minimum and maximum corner variants of ' + infile_name)

if not os.path.exists(infile_name):
    print('Error:  Cannot find file ' + infile_name)
    sys.exit(1)

for corner in ['min', 'max', 'nom']:
    tleffile  = tlefbase + corner + '.tlef'
    outfile_name = tlefpath + '/' + tleffile

    infile   = open(infile_name, 'r')
    if infile_name == outfile_name:
        outfile  = open(outfile_name + 'x', 'w')
    else:
        outfile  = open(outfile_name, 'w')
    curlayer = None
    rvalue   = None
    cvalue   = None

    for line in infile:
        cmatch  = caprex.match(line)
        rmatch1 = resrex1.match(line)
        rmatch2 = resrex2.match(line)
        lmatch  = layerrex.match(line)
        if lmatch:
            curlayer = lmatch.group(1)
            if curlayer in rnom:
                if corner == 'min':
                    try:
                        rvalue = rmin[curlayer]
                    except:
                        rvalue = None
                elif corner == 'max':
                    try:
                        rvalue = rmax[curlayer]
                    except:
                        rvalue = None
                else:
                    try:
                        rvalue = rnom[curlayer]
                    except:
                        rvalue = None
            else:
                rvalue = None
            if curlayer in cnom:
                if corner == 'min':
                    try:
                        cvalue = cmin[curlayer]
                    except:
                        cvalue = None
                elif corner == 'max':
                    try:
                        cvalue = cmax[curlayer]
                    except:
                        cvalue = None
                else:
                    try:
                        cvalue = cnom[curlayer]
                    except:
                        cvalue = None
            else:
                cvalue = None
            outfile.write(line)
        elif rvalue and rmatch1:
            print('Layer ' + curlayer + ':  Rewriting resistance rpersq as value ' + rvalue)
            outfile.write('    RESISTANCE RPERSQ ' + rvalue + ' ;\n')
        elif rvalue and rmatch2:
            outfile.write(line)
            outfile.write('')
            print('Layer ' + curlayer + ':  Adding (via) resistance as value ' + rvalue)
            outfile.write('  RESISTANCE ' + rvalue + ' ;\n')
        elif cvalue and cmatch:
            print('Layer ' + curlayer + ':  Rewriting capacitance cpersqdist as value ' + cvalue)
            outfile.write('    CAPACITANCE CPERSQDIST ' + cvalue + ' ;\n')
        else:
            outfile.write(line)

    infile.close()
    outfile.close()

    if infile_name == outfile_name:
        os.rename(outfile_name + 'x', outfile_name)

    print('Generated file ' + outfile_name + ' (Done)')
