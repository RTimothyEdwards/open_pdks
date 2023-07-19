#!/usr/bin/env python3
#
# 
import os
import re
import sys
import subprocess

#---------------------------------------------------------------------------
# usage:  run_all.py [-nosim] [-keep]
#
# Run ngspice simulations on all major transistor devices in the process
# (excluding high-voltage > 3V devices) at all corners, and generate
# IRSIM parameter files for each corner.
#
# The "-nosim" option assumes that simulation output files have been
# saved, and will run the parser to generate the parameterf files from
# the existing ngspice output files.
#
# The "-keep" option will retain the ngspice input and output files
# after each parameter file has been generated.  Otherwise, they will
# be removed.
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Devices must be paired P and N for each test.  There are some redundant
# devices below where one type exists that does not have a corresponding
# device in the opposite type.  In cases of redundancy, the first results
# computed will be the ones used for that device.  The third item in each
# list is the voltage range to use for the device, and determines which
# voltages are used for max/min/typ simulations.
#---------------------------------------------------------------------------
 
#---------------------------------------------------------------------------
# NOTE:  This method requires IRSIM 9.7.114, which supports multiple
# transistor device parameters and multiple supply voltages.
#---------------------------------------------------------------------------
 
#---------------------------------------------------------------------------
# To do:  Speed this up by using multiprocessing
#---------------------------------------------------------------------------

# Parse options

keep = False
nosim = False

options = []
arguments = []
for item in sys.argv[1:]:
    if item.find('-', 0) == 0:
        options.append(item)
    else:
        arguments.append(item)

if len(arguments) > 0:
    print("Usage:  run_all.py [-nosim] [-keep]")
    sys.exit(1)

if '-keep' in options:
    keep = True
    print("Keep mode:  Retaining all intermediate files.")

if '-nosim' in options:
    nosim = True
    print("No-sim mode:  Not running any simulations.")

if '-help' in options:
    print("Usage:  run_all.py [-nosim] [-keep]")
    sys.exit(0)

#---------------------------------------------------------------------------
# Each entry in "devices" list has 9 items:
#  [test-text, pFET-name, nFET-name, voltage-range,
#   p-length, p-width, n-length, n-width, load-cap]
#---------------------------------------------------------------------------
 
devices = [
	[
	   "1.8V devices",
	   "sky130_fd_pr__pfet_01v8", "sky130_fd_pr__nfet_01v8",
	   "1v8", 0.15, 1.0, 0.15, 1.0, 250
	],
	[
	   "1.8V LVT devices",
	   "sky130_fd_pr__pfet_01v8_lvt", "sky130_fd_pr__nfet_01v8_lvt",
	   "1v8", 0.35, 1.0, 0.15, 1.0, 250
	],
	[
	   "1.8V HVT pFET",
	   "sky130_fd_pr__pfet_01v8_hvt", "sky130_fd_pr__nfet_01v8",
	   "1v8", 0.45, 1.0, 0.15, 1.0, 250
	],
	[
	   "SRAM latching FETs",
	   "sky130_fd_pr__special_pfet_latch", "sky130_fd_pr__special_nfet_latch",
	   "1v8", 0.15, 0.14, 0.15, 0.21, 100
	],
	[
	   "SRAM pass nFET",
	   "sky130_fd_pr__special_nfet_pass",
	   "1v8", 0.15, 0.14, 0.15, 0.14, 100
	],
	[
	   "3.3V devices",
	   "sky130_fd_pr__pfet_g5v0d10v5", "sky130_fd_pr__nfet_g5v0d10v5",
	   "3v3", 0.50, 1.0, 0.50, 1.0, 250
	],
	[
	   "5.0V native nFET",
	   "sky130_fd_pr__pfet_g5v0d10v5", "sky130_fd_pr__nfet_05v0_nvt",
	   "3v3", 0.50, 1.0, 0.90, 1.0, 250
	]
]

voltages1v8 = [ 1.62, 1.80, 1.98 ]

voltages3v3 = [ 2.97, 3.30, 3.63 ]

vnames = [ 'low', 'nom', 'high' ]

temps = [ -40, 27, 125 ]

corners = [ "ss", "tt", "ff" ]

# Read the parameter file header and save the contents

header = []
with open('header.txt', 'r') as ifile:
    hlines = ifile.read().splitlines()

for corner in corners:
    for temp in temps:
        tname = str(temp).replace('-', 'n')
        for vidx in range(0,3):
            vname = vnames[vidx]

            generated_files = []
            ndevtypes = []
            pdevtypes = []

            ndynh = {}
            ndynl = {}
            pdynh = {}
            pdynl = {}
            nstat = {}
            pstat = {}

            for devidx in range(0, len(devices)):
                devicepair = devices[devidx]
                devset = devicepair[0]
                if len(devicepair) != 9:
                    print('Error:  Bad entry for device set ' + devset + '.\n')
                    continue
                ptype = devicepair[1]
                ntype = devicepair[2]
                vtype = devicepair[3]
                plength = devicepair[4]
                pwidth = devicepair[5]
                nlength = devicepair[6]
                nwidth = devicepair[7]
                loadcap = devicepair[8]

                if ntype not in ndevtypes:
                    ndevtypes.append(ntype)
                if ptype not in pdevtypes:
                    pdevtypes.append(ptype)

                if vtype == '1v8':
                    volt = voltages1v8[vidx]
                else:
                    volt = voltages3v3[vidx]

                if not nosim:

                    # Read template and generate SPICE simulation netlist
                    newlines = []
                    with open('circuit_template.spi', 'r') as ifile:
                        template = ifile.read().splitlines()
                        for line in template:
                            outline = re.sub('CORNER', corner, line)
                            outline = re.sub('FULL_VOLTAGE', str(volt), outline)
                            outline = re.sub('HALF_VOLTAGE', str(volt / 2.0), outline)
                            outline = re.sub('TEMPERATURE', str(temp), outline)
                            outline = re.sub('DEVICENAME_N', ntype, outline)
                            outline = re.sub('DEVICENAME_P', ptype, outline)
                            outline = re.sub('WIDTH_N', str(nwidth), outline)
                            outline = re.sub('WIDTH_P', str(pwidth), outline)
                            outline = re.sub('LENGTH_N', str(nlength), outline)
                            outline = re.sub('LENGTH_P', str(plength), outline)
                            outline = re.sub('LOADCAP', str(loadcap), outline)
                            newlines.append(outline)

                    simname = 'sky130_' + corner + '_' + vname + '_' + tname + '_devpair' + str(devidx) + '.spice'

                    with open(simname, 'w') as ofile:
                        for line in newlines:
                            print(line, file=ofile)

                    generated_files.append(simname)

                    # Run ngspice simulation

                    print('** Running simulation on ' + devset + '(file ' + simname + ')')
                    print('** Conditions: temp=' + tname + ' corner=' + corner
				+ ' volt=' + vname)
                    p = subprocess.run(['ngspice', simname],
				stdout = subprocess.PIPE,
				universal_newlines = True)
			
                    if p.stdout:
                        parameters = p.stdout.splitlines()
              
                        for parameter in parameters:
                            valueline = parameter.split()
                            if len(valueline) < 3:
                                continue
                            if valueline[0] == 'ndynh':
                                try:
                                    ndynh[ntype]
                                except:
                                    ndynh[ntype] = valueline[2]
                            elif valueline[0] == 'pdynh':
                                try:
                                    pdynh[ptype]
                                except:
                                    pdynh[ptype] = valueline[2]
                            elif valueline[0] == 'ndynl':
                                try:
                                    ndynl[ntype]
                                except:
                                    ndynl[ntype] = valueline[2]
                            elif valueline[0] == 'pdynl':
                                try:
                                    pdynl[ptype]
                                except:
                                    pdynl[ptype] = valueline[2]
                            elif valueline[0] == 'nstat':
                                try:
                                    nstat[ntype]
                                except:
                                    nstat[ntype] = valueline[2]
                            elif valueline[0] == 'pstat':
                                try:
                                    pstat[ptype]
                                except:
                                    pstat[ptype] = valueline[2]
                else:
                    print('** No file ' + outname + '; skipping.')
                        
            paramfile = 'sky130_' + corner + '_' + vname + '_' + tname + '.prm'

            with open(paramfile, 'w') as ofile:
                for line in hlines:
                    print(line, file=ofile)

                # Now output information for every device
                print('', file=ofile)

                for device in ndevtypes:
                    devicepair = next(item for item in devices if item[2] == device)
                    if not devicepair:
                        print('Error:  Bad entry for nFET device ' + device + '.\n')
                        continue
                    devset = devicepair[0]
                    if len(devicepair) != 9:
                        print('Error:  Bad entry for device set ' + devset + '.\n')
                        continue
                    ntype = devicepair[2]
                    vtype = devicepair[3]
                    nlength = devicepair[6]
                    nwidth = devicepair[7]
                    loadcap = devicepair[8]

                    print('; C=' + str(loadcap) + ', N(w=' + str(nwidth) + ', l=' + str(nlength) + ')', file=ofile)
                    print('resistance ' + ntype + ' dynamic-high   ' + str(nwidth) + '    ' + str(nlength) + '  ' + ndynh[ntype], file=ofile)
                    print('resistance ' + ntype + ' dynamic-low    ' + str(nwidth) + '    ' + str(nlength) + '  ' + ndynl[ntype], file=ofile)
                    print('resistance ' + ntype + ' static         ' + str(nwidth) + '    ' + str(nlength) + '  ' + nstat[ntype], file=ofile)
                    print('', file=ofile)

                for device in pdevtypes:
                    devicepair = next(item for item in devices if item[1] == device)
                    if not devicepair:
                        print('Error:  Bad entry for pFET device ' + device + '.\n')
                        continue
                    devset = devicepair[0]
                    if len(devicepair) != 9:
                        print('Error:  Bad entry for device set ' + devset + '.\n')
                        continue
                    ptype = devicepair[1]
                    vtype = devicepair[3]
                    plength = devicepair[4]
                    pwidth = devicepair[5]
                    loadcap = devicepair[8]

                    print('; C=' + str(loadcap) + ', P(w=' + str(pwidth) + ', l=' + str(plength) + ')', file=ofile)
                    print('resistance ' + ptype + ' dynamic-high   ' + str(pwidth) + '    ' + str(plength) + '  ' + pdynh[ptype], file=ofile)
                    print('resistance ' + ptype + ' dynamic-low    ' + str(pwidth) + '    ' + str(plength) + '  ' + pdynl[ptype], file=ofile)
                    print('resistance ' + ptype + ' static         ' + str(pwidth) + '    ' + str(plength) + '  ' + pstat[ptype], file=ofile)
                    print('', file=ofile)
            
            if not keep:
                print('**Removing generated intermediate files.')
                for file in generated_files:
                    try:
                        os.remove(file)
                    except:
                        pass

sys.exit(0)
