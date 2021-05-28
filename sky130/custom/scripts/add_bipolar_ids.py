#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Add the special ID layers for the bipolar transistors which tell
# the extraction engine in magic to extract the device model that
# is specific to the device size.  There is no such GDS layer, so it
# can only be added after the fact.
#--------------------------------------------------------------------

import os
import re
import sys

magpath = 'sky130A/libs.ref/sky130_fd_pr/mag'

if len(sys.argv) > 1:
    magpath = sys.argv[1]

baserex = re.compile('<< [np]base >>')

# Note that the list of NPNs is not comprehensive.  However, at the
# moment only 5 special layers and 5 special models are defined in
# the magic techfile and in the device generator.  Adding more must
# start with the magic techfile, as the layers must be defined before
# this script can be run.

devlist = ['sky130_fd_pr__rf_pnp_05v5_W0p68L0p68',
	   'sky130_fd_pr__rf_pnp_05v5_W3p40L3p40',
	   'sky130_fd_pr__rf_npn_11v0_W1p00L1p00',
	   'sky130_fd_pr__rf_npn_05v5_W1p00L1p00',
	   'sky130_fd_pr__rf_npn_05v5_W1p00L2p00']

typelist = ['pnp0p68',
	    'pnp3p40',
	    'npn11p0',
	    'npn1p00',
	    'npn2p00']

#--------------------------------------------------------------------

for idx, device in enumerate(devlist):
    infile_name = magpath + '/' + device + '.mag'
    outfile_name = magpath + '/temp.mag'

    if not os.path.exists(infile_name):
        print('Error:  Cannot find file ' + infile_name)
        continue

    print('Adding special ID layer to device ' + device + ' layout')

    type = typelist[idx]
    is_baserect = False
    infile = open(infile_name, 'r')
    outfile = open(outfile_name, 'w')
    line_number = 0
    replaced_something = False

    for line in infile:
        line_number += 1

        if is_baserect:
            # Repeat the same rectangle as for the bipolar base layer,
            # using the ID type layer
            outfile.write(line)
            outfile.write('<< ' + type + ' >>\n')
            replaced_something = True
            is_baserect = False
        else:
            bmatch = baserex.match(line)
            if bmatch:
                is_baserect = True

        outfile.write(line)

    infile.close()
    outfile.close()

    if replaced_something:
        print("Something was replaced in '{}'".format(infile_name))
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

