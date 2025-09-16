#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Add a \"device\" property to the layout of specific PDK primitive
# devices that do not extract as intended.  This includes, for
# example, RF devices (which extract as non-RF devices), vertical
# parallel plate capacitors (which extract as metal wires), and any
# other device that is not represented in magic's \"extract\" section.
#
# This uses the method introduced in magic version 8.3.298 using
# property "device" with value "primitive", so that the subcell is
# output to the netlist without a corresponding subcircuit entry or
# black box entry, as the device is assumed to be defined in the PDK.
# But it is necessary to make sure that the ports are in the correct
# order for the PDK device.
#--------------------------------------------------------------------

import os
import re
import sys
import subprocess

options = []
arguments = []
for item in sys.argv[1:]:
    if item.find('-', 0) == 0:
        options.append(item[1:])
    else:
        arguments.append(item)

variant = 'sky130A'
magpath = variant + '/libs.ref/sky130_fd_pr/mag'
maglefpath = variant + '/libs.ref/sky130_fd_pr/maglef'
spicepath = variant + '/libs.ref/sky130_fd_pr/spice'

if len(options) > 0:
    for option in options:
        if option.startswith('variant'):
            variant = option.split('=')[1]
    magpath = variant + '/libs.ref/sky130_fd_pr/mag'
    maglefpath = variant + '/libs.ref/sky130_fd_pr/maglef'
    spicepath = variant + '/libs.ref/sky130_fd_pr/spice'
elif len(arguments) > 0:
    magpath = arguments[0]
    maglefpath = magpath.replace('/mag/', '/maglef/')
    spicepath = magpath.replace('/mag/', '/spice/')

# \"devlist\" is an enumeration of all devices that have both a layout
# in libs.ref/sky130_fd_pr/mag and corresponding subcircuit models
# in libs.ref/sky130_fd_pr/spice, and for which extracting the layout
# in magic does not produce the intended SPICE model.

devlist = ['sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_02p7x06p1_m1m2m3m4_shieldl1_fingercap',
	   'sky130_fd_pr__cap_vpp_02p7x11p1_m1m2m3m4_shieldl1_fingercap',
	   'sky130_fd_pr__cap_vpp_02p7x21p1_m1m2m3m4_shieldl1_fingercap',
	   'sky130_fd_pr__cap_vpp_02p7x41p1_m1m2m3m4_shieldl1_fingercap',
	   'sky130_fd_pr__cap_vpp_02p9x06p1_m1m2m3m4_shieldl1_fingercap2',
	   'sky130_fd_pr__cap_vpp_03p9x03p9_m1m2_shieldl1_floatm3',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_l1m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_l1m1m2_shieldpo_floatm3',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_shieldl1',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1m5_floatm4',
	   'sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1m5_floatm4',
	   'sky130_fd_pr__cap_vpp_05p9x05p9_m1m2m3m4_shieldl1_wafflecap',
	   'sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2m3_shieldpom4',
	   'sky130_fd_pr__cap_vpp_06p8x06p1_m1m2m3_shieldl1m4',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_l1m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_l1m1m2_shieldpo_floatm3',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_shieldl1',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1m5_floatm4',
	   'sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1m5_floatm4',
	   'sky130_fd_pr__cap_vpp_11p3x11p3_m1m2m3m4_shieldl1_wafflecap',
	   'sky130_fd_pr__cap_vpp_11p3x11p8_l1m1m2m3m4_shieldm5_nhv',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2_shieldpom3',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3_shieldm4',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3_shieldpom4',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5_x',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5_x',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_noshield',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_shieldl1',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1m5_floatm4',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1m5_floatm4',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3m4_shieldl1m5',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3m4_shieldm5',
	   'sky130_fd_pr__cap_vpp_11p5x11p7_m1m4_noshield',
	   'sky130_fd_pr__cap_vpp_44p7x23p1_pol1m1m2m3m4m5_noshield',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W1p65L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W1p65L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W1p65L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W3p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W3p00L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W3p00L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W5p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W5p00L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_bM02W5p00L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W1p65L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W1p65L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W1p65L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W3p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W3p00L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W3p00L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W5p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W5p00L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_bM04W5p00L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF02W0p42L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF02W0p84L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF02W3p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF04W0p84L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF04W3p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF08W0p84L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_aF08W3p00L0p15',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_bM02W5p00L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_bM02W5p00L0p25',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_bM04W5p00L0p18',
	   'sky130_fd_pr__rf_nfet_01v8_lvt_bM04W5p00L0p25',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM02W3p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM02W5p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM04W3p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM04W5p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM04W7p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM10W3p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM10W5p00L0p50',
	   'sky130_fd_pr__rf_nfet_g5v0d10v5_bM10W7p00L0p50',
	   'sky130_fd_pr__rf_pfet_01v8_aF02W0p84L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_aF02W1p68L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_aF02W3p00L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_aF02W5p00L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_aF04W1p68L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W1p65L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W1p65L0p18',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W1p65L0p25',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W3p00L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W3p00L0p18',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W3p00L0p25',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W5p00L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W5p00L0p18',
	   'sky130_fd_pr__rf_pfet_01v8_bM02W5p00L0p25',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W1p65L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W1p65L0p18',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W1p65L0p25',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W3p00L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W3p00L0p18',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W3p00L0p25',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W5p00L0p15',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W5p00L0p18',
	   'sky130_fd_pr__rf_pfet_01v8_bM04W5p00L0p25',
	   'sky130_fd_pr__rf_pfet_01v8_mvt_aF02W0p84L0p15']

# The portlist array contains the names of the ports used in the layout in the order that
# they appear in the device subcircuit model.  Note that none of the pin names match between
# the layout and device definition, so the usual annotation method in magic won't work.

portlist = [	['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET3'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET3'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET4'],
		['C0', 'C1', 'SUB', 'MET4'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET3'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET3'],
		['C0', 'C1', 'SUB', 'MET4'],
		['C0', 'C1', 'SUB', 'MET4'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB', 'MET5'],
		['C0', 'C1', 'SUB'],
		['C0', 'C1', 'SUB'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'SUBSTRATE'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK'],
		['DRAIN', 'GATE', 'SOURCE', 'BULK']]

# List of devices which have a layout cell name that is different
# from the parameterized cell (gencell) and so must change the
# default "gencell" property.

dev2list = ['sky130_fd_pr__rf_npn_05v5_W1p00L1p00',
	    'sky130_fd_pr__rf_npn_05v5_W1p00L2p00',
	    'sky130_fd_pr__rf_pnp_05v5_W0p68L0p68',
	    'sky130_fd_pr__rf_pnp_05v5_W3p40L3p40',
	    'sky130_fd_pr__rf_npn_11v0_W1p00L1p00'];


prop2list = ['sky130_fd_pr__npn_05v5_W1p00L1p00',
	     'sky130_fd_pr__npn_05v5_W1p00L2p00',
	     'sky130_fd_pr__pnp_05v5_W0p68L0p68',
	     'sky130_fd_pr__pnp_05v5_W3p40L3p40',
	     'sky130_fd_pr__npn_11v0_W1p00L1p00'];

#--------------------------------------------------------------------
# Do this for files both in mag/ and maglef/ . . .

pathlist = [magpath, maglefpath]

for idx, device in enumerate(devlist):
    for path in pathlist:
        infile_name = path + '/' + device + '.mag'

        if not os.path.exists(infile_name):
            print('Error:  Cannot find file ' + infile_name)
            continue

        print('Adding special extraction property to device ' + device + ' layout')

        propcmd = ['../common/insert_property.py', variant, 'sky130_fd_pr',
		device, 'device primitive']

        # Just call the insert_property.py script
        subprocess.run(propcmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

        # Now renumber the ports in the layout to match the PDK device.  The port names in
        # the layout generally don't match the port names in the PDK device definitions,
        # so ports are handled by manually listing them all out.

        devports = portlist[idx]
        modified = False

        with open(infile_name, 'r') as ifile:
            magdata = ifile.read()
            outlines = []
            for line in magdata.splitlines():
                if line.startswith('port'):
                    if lname and lname in devports:
                        tokens = line.split()
                        newindex = str(1 + devports.index(lname))
                        if newindex != tokens[1]:
                            modified = True
                        tokens[1] = newindex
                        newline = ' '.join(tokens)
                    else:
                        newline = line
                    lname = None
                elif line.startswith('flabel'):
                    lname = line.split()[-1]
                    newline = line
                elif line.startswith('rlabel'):
                    lname = line.split()[-1]
                    newline = line
                else:
                    lname = None
                    newline = line
                outlines.append(newline)

        if modified:
            print('Modifying port order in ' + infile_name)
            with open(infile_name, 'w') as ofile:
                ofile.write('\n'.join(outlines))

    # Any SPICE netlist for this device that came from extraction in magic during the
    # PDK build is invalid, and should be removed.

    infile_name = spicepath + '/' + device + '.spice'
    if os.path.isfile(infile_name):
        os.remove(infile_name)

# Handle the gencell property changes

for idx, device in enumerate(dev2list):
    for path in pathlist:
        infile_name = path + '/' + device + '.mag'

        if not os.path.exists(infile_name):
            print('Error:  Cannot find file ' + infile_name)
            continue

        print('Altering gencell property in device ' + device + ' layout')
        gencell = prop2list[idx]

        propcmd = ['../common/insert_property.py', variant, 'sky130_fd_pr',
		device, 'gencell ' + gencell]

        # Just call the insert_property.py script
        subprocess.run(propcmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

