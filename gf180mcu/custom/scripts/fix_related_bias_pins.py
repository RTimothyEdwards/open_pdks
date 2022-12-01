#!/usr/bin/env python3
#
# fix_related_bias_pins.py ---
#
# All liberty files are missing the bias pins VNW and VPW;  these
# needed to be added along with "related_bias_pin" statements for
# the power supplies VDD and VSS.
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the lib install in the sky130 Makefile.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            stext = inFile.read()
            slines = stext.splitlines()
    except:
        print('fix_related_bias_pins.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    if 'filltie' in inname or 'endcap' in inname:
        return 0

    # Process input with regexp

    fixedlines = []
    modified = False
    current_pin = ''

    # Values for "pg_type" other than "pwell" or "nwell"
    power_types = ['primary_power', 'primary_ground', 'backup_power',
		   'internal_power', 'internal_ground']

    pg_re = re.compile('\s*pg_pin\s*\(\s*"?([^\s]+)"?\s*\)\s*{')
    well_re = re.compile('\s*pg_type\s*:\s*"?([^\s]+)"?\s*;')

    for line in slines:
        pmatch = pg_re.match(line)
        if pmatch:
            current_pin = pmatch.group(1)
            if current_pin == 'VDD':
                fixedlines.append('    pg_pin(VPW) {')
                fixedlines.append('      voltage_name : VPW ;')
                fixedlines.append('      pg_type : pwell ;')
                fixedlines.append('      physical_connection : device_layer ;')
                fixedlines.append('    }')
                fixedlines.append('')
                fixedlines.append('    pg_pin(VNW) {')
                fixedlines.append('      voltage_name : VNW ;')
                fixedlines.append('      pg_type : nwell ;')
                fixedlines.append('      physical_connection : device_layer ;')
                fixedlines.append('    }')
                fixedlines.append('')

        wmatch = well_re.match(line)
        if wmatch:
            well_str = wmatch.group(1)
            if well_str == 'primary_power':
                modified = True
                fixedlines.append('      related_bias_pin : VNW ;')
                current_pin = ''
            elif well_str == 'primary_ground':
                modified = True
                fixedlines.append('      related_bias_pin : VPW ;')
                current_pin = ''

        fixedlines.append(line)

    # Write output
    if outname == None:
        for i in fixedlines:
            print(i)
    else:
        # If the output is a symbolic link but no modifications have been made,
        # then leave it alone.  If it was modified, then remove the symbolic
        # link before writing.
        if os.path.islink(outname):
            if not modified:
                return 0
            else:
                os.unlink(outname)
        try:
            with open(outname, 'w') as outFile:
                for i in fixedlines:
                    print(i, file=outFile)
        except:
            print('fix_related_bias_pins.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
            return 1


if __name__ == '__main__':

    # This script expects to get one or two arguments.  One argument is
    # mandatory and is the input file.  The other argument is optional and
    # is the output file.  The output file and input file may be the same
    # name, in which case the original input is overwritten.

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item[1:])
        else:
            arguments.append(item)

    if len(arguments) > 0:
        infilename = arguments[0]

    if len(arguments) > 1:
        outfilename = arguments[1]
    else:
        outfilename = None

    result = filter(infilename, outfilename)
    sys.exit(result)
