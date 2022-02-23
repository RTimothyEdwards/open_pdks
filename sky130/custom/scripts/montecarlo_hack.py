#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Workaround for the problem that ngspice is unable to accept a
# parameter name that shadows a device name.  Parameters in the
# files critical.spice and montecarlo.spice that shadow parameter
# names have the leading sky130_fd_pr__ stripped off to prevent
# this from being a problem.
#--------------------------------------------------------------------

import os
import re
import sys
import tempfile

searchpath = ['sky130A/libs.tech/ngspice/parameters/critical.spice',
	'sky130A/libs.tech/ngspice/parameters/montecarlo.spice']

if len(sys.argv) > 1:
    searchpath = sys.argv[1]

# Flag all parameters that have the same name as devices.
# These parameters are unused and must be deleted.

excludelist = [
	'sky130_fd_pr__nfet_20v0_nvt_iso',
	'sky130_fd_pr__nfet_20v0_nvt',
	'sky130_fd_pr__nfet_20v0_iso',
	'sky130_fd_pr__nfet_20v0_zvt',
	'sky130_fd_pr__nfet_20v0',
	'sky130_fd_pr__pfet_20v0',
	'sky130_fd_pr__nfet_01v8_lvt',
	'sky130_fd_pr__pfet_01v8_mvt',
	'sky130_fd_pr__pfet_01v8',
	'sky130_fd_pr__nfet_g5v0d16v0',
	'sky130_fd_pr__pfet_g5v0d16v0',
	'sky130_fd_pr__special_nfet_pass_lvt',
	'sky130_fd_pr__pnp_05v5_W0p68L0p68']

# For each entry in the exclude list, create a regular expression
# for detecting that entry and excluding other similar cases that
# aren't the parameter.  Items with preceding "/" are the device
# filename, and items with additional text are other parameters.

rexpat = {}
rexdict = {}

for item in excludelist:
    rexpat[item] = '([^/])' + item + '(?=[^_])'
    rexdict[item] = re.compile('([^/])' + item + '(?=[^_])')

#--------------------------------------------------------------------

for infile_name in searchpath:
    filepath = os.path.split(infile_name)[0]
    filename = os.path.split(infile_name)[1]
    fileroot = os.path.splitext(filename)[0]

    infile = open(infile_name, 'r')
    handle, outfile_name = tempfile.mkstemp()
    outfile = osfdopen(handle, 'w')

    line_number = 0
    replaced_something = False
    for line in infile:
        line_number += 1

        newline = line
        for device in excludelist:
            rmatch = rexdict[device].search(line)
            if rmatch:
                replacement = device[14:]
                newline = re.sub(rexpat[device], '\g<1>' + replacement, newline)
                replaced_something = True

        outfile.write(newline)

    infile.close()
    outfile.close()
    if replaced_something:
        print("Something was replaced in '{}'".format(infile_name))
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

