#!/usr/bin/env python3
"""
cace_launch.py
A simple script that pulls in a JSON file and uses the hash key to find the
directory of spice simulation netlists associated with that file, and runs
them.  The output of all files in a category <SKU>_<METHOD>_<PIN>_* is
analyzed, and the result written back to the data structure.  Then the
annotated structure is passed back to the marketplace.
"""

# NOTE:  This file is only a local stand-in for the script that launches
# and manages jobs in parallel and that communicates job status with the
# front-end.  This stand-alone version should not be used for any significant
# project, as all simulations are run sequentially and will tie up resources.

import os
import sys
import shutil
import tarfile
import json
import re
import math
import signal
import datetime
import requests
import subprocess
import faulthandler
from spiceunits import spice_unit_unconvert
from spiceunits import spice_unit_convert

import file_compressor
import cace_makeplot

import og_config

# Values imported from og_config:
#
mktp_server_url = og_config.mktp_server_url
# obs: og_server_url = og_config.og_server_url
simulation_path = og_config.simulation_path

# Variables needing to be global until this file is properly made into a class
simfiles_path = []
layout_path = []
netlist_path = []
root_path = []
hashname = ""
spiceproc = None
localmode = False
bypassmode = False
statdoc = {}

# Send the simulation status to the remote Open Galaxy host
def send_status(doc):
    result = requests.post(og_server_url + '/opengalaxy/send_status_cace', json=doc)
    print('send_status_cace ' + str(result.status_code))

# Make request to server sending annotated json back
def send_doc(doc):
    result = requests.post(mktp_server_url + '/cace/save_result', json=doc)
    print('send_doc ' + str(result.status_code))

# Pure HTTP post here.  Add the file to files object and the hash/filename
# to the data params.
def send_file(hash, file, file_name):
    files = {'file': file.getvalue()}
    data = {'request-hash': hash, 'file-name': file_name}
    result = requests.post(mktp_server_url + '/cace/save_result_files', files=files, data=data)
    print('send_file ' + str(result.status_code))

# Clean up and exit on termination signal
def cleanup_exit(signum, frame):
    global root_path
    global simfiles_path
    global simulation_path
    global spiceproc
    global statdoc
    global localmode
    if spiceproc:
        print("CACE launch:  Termination signal received.")
        spiceproc.terminate()
        spiceproc.wait()

    # Remove simulation files
    print("CACE launch:  Simulations have been terminated.")
    if localmode == False:
        test = os.path.split(root_path)[0]
        if test != simulation_path:
            print('Error:  Root path is not in the system simulation path.  Not deleting.')
            print('Root path is ' + root_path + '; simulation path is ' + simulation_path)
        else:
            subprocess.run(['rm', '-r', root_path])
    else:
        # Remove all .spi files, .data files, .raw files and copy of datasheet
        os.chdir(simfiles_path)
        if os.path.exists('datasheet.json'):
            os.remove('datasheet.json')
        files = os.listdir(simfiles_path)
        for filename in files:
            try:
                fileext = os.path.splitext(filename)[1]
            except:
                pass
            else:
                if fileext == '.spi' or fileext == '.data' or fileext == '.raw':
                    os.remove(filename)
                elif fileext == '.tv' or fileext == '.tvo' or fileext == '.lxt' or fileext == '.vcd':
                    os.remove(filename)

    # Post exit status back to Open Galaxy
    if statdoc and not localmode:
        status['message'] = 'canceled'
        send_status(statdoc)

    # Exit
    sys.exit(0)

# Handling of 2s complement values in calculations (e.g., "1000" is -8, not +8)
# If a value should be unsigned, then the units for the value should be one bit
# larger than represented.  e.g., if unit = "4'b" and value = "1000" then value
# is -8, but if unit = "5'b" and value = "1000" then value is +8.

def twos_complement(val, bits):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

# Calculation of results from collected data for an output record,
# given the type of calculation to perform in 'calctype'.  Known
# calculations are minimum, maximum, and average (others can be
# added as needed).

def calculate(record, rawdata, conditions, calcrec, score, units, param):
    # Calculate result from rawdata based on calctype;  place
    # result in record['value'].

    # "calcrec" is parsed as "calctype"-"limittype", where:
    #     "calctype" is one of:  avg, min, max
    #     "limittype" is one of: above, below, exact

    # "min" alone implies "min-above"
    # "max" alone implies "max-below"
    # "avg" alone implies "avg-exact"

    # Future development:
    # Add "minimax", "maximin", and "typ" to calctypes (needs extra record(s))
    # Add "range" to limittypes (needs extra record or tuple for target)

    binrex = re.compile(r'([0-9]*)\'([bodh])', re.IGNORECASE)

    data = rawdata
    if 'filter' in record:
        # Filter data by condition range.
        filtspec = record['filter'].split('=')
        if len(filtspec) == 2:
            condition = filtspec[0].upper()
            valuerange = filtspec[1].split(':')
            # Pick data according to filter, which specifies a condition and value, or condition
            # and range of values in the form "a:b".  Syntax is limited and needs to be expanded. 
            if condition in conditions:
                condvec = conditions[condition]
                if len(valuerange) == 2:
                    valuemin = int(valuerange[0])
                    valuemax = int(valuerange[1])
                    data = list(i for i, j in zip(rawdata, condvec) if j >= valuemin and j <= valuemax)
                else:
                    try:
                        valueonly = float(valuerange[0])
                    except ValueError:
                        valueonly = valuerange[0]
                    vtype = type(valueonly)
                    if vtype == type('str') or vtype == type('int'):
                        data = list(i for i, j in zip(rawdata, condvec) if j == valueonly)
                        if not data:
                            print('Error: no data match ' + condition + ' = ' + str(valueonly))
                            data = rawdata
                    else:
                        # Avoid round-off problems from floating-point values
                        d = valueonly * 0.001
                        data = list(i for i, j in zip(rawdata, condvec) if j - d < valueonly and j + d > valueonly)
                        if not data:
                            print('Error: no data match ' + condition + ' ~= ' + str(valueonly))
                            data = rawdata

        # For "filter: typical", limit data to those taken for any condition value
        # which is marked as typical for that condition.

        elif record['filter'] == 'typ' or record['filter'] == 'typical':

            # Create a boolean vector to track which results are under typical conditions
            typvec = [True] * len(rawdata)
            for condition in conditions:
                # Pull record of the condition (this must exist by definition)
                condrec = next(item for item in param['conditions'] if item['condition'] == condition)
                if 'typ' not in condrec:
                    continue
                try:
                    valueonly = float(condrec['typ'])
                except ValueError:
                    valueonly = condrec['typ']
                condvec = conditions[condition]
                typloc = list(i == valueonly for i in condvec)
                typvec = list(i and j for i, j in zip(typloc, typvec))
            # Limit data to marked entries
            data = list(i for i, j in zip(rawdata, typvec) if j)
    try:
        calctype, limittype = calcrec.split('-')
    except ValueError:
        calctype = calcrec
        if calctype == 'min':
            limittype = 'above'
        elif calctype == 'max':
            limittype = 'below'
        elif calctype == 'avg':
            limittype = 'exact'
        elif calctype == 'diffmin':
            limittype = 'above'
        elif calctype == 'diffmax':
            limittype = 'below'
        else:
            return 0
    
    # Quick format sanity check---may need binary or hex conversion
    # using the new method of letting units be 'b or 'h, etc.
    # (to be done:  signed conversion, see cace_makeplot.py)
    if type(data[0]) == type('str'):
        bmatch = binrex.match(units)
        if (bmatch):
            digits = bmatch.group(1)
            if digits == '':
                digits = len(data[0])
            else:
                digits = int(digits)
            base = bmatch.group(2)
            if base == 'b':
                a = list(int(x, 2) for x in data)
            elif base == 'o':
                a = list(int(x, 8) for x in data)
            elif base == 'd':
                a = list(int(x, 10) for x in data)
            else:
                a = list(int(x, 16) for x in data)
            data = list(twos_complement(x, digits) for x in a)
        else:
            print("Warning: result data do not correspond to specified units.")
            print("Data = " + str(data))
            return 0

    # The target and result should both match the specified units, so convert
    # the target if it is a binary, hex, etc., value.
    if 'target' in record:
        targval = record['target']
        bmatch = binrex.match(units)
        if (bmatch):
            digits = bmatch.group(1)
            base = bmatch.group(2)
            if digits == '':
                digits = len(targval)
            else:
                digits = int(digits)
            try:
                if base == 'b':
                    a = int(targval, 2)
                elif base == 'o':
                    a = int(targval, 8)
                elif base == 'd':
                    a = int(targval, 10)
                else:
                    a = int(targval, 16)
                targval = twos_complement(a, digits)
            except:
                print("Warning: target data do not correspond to units; assuming integer.")

    # First run the calculation to get the single result value

    if calctype == 'min':
        # Result is the minimum of the data
        value = min(data)
    elif calctype == 'max':
        # Result is the maximum of the data
        value = max(data)
    elif calctype == 'avg':
        # Result is the average of the data
        value = sum(data) / len(data)
    elif calctype[0:3] == 'std':
        # Result is the standard deviation of the data
        mean = sum(data) / len(data)
        value = pow(sum([((i - mean) * (i - mean)) for i in data]) / len(data), 0.5)
        # For "stdX", where "X" is an integer, multiply the standard deviation by X
        if len(calctype) > 3:
            value *= int(calctype[3])

        if len(calctype) > 4:
            # For "stdXn", subtract X times the standard deviation from the mean
            if calctype[4] == 'n':
                value = mean - value
            # For "stdXp", add X times the standard deviation to the mean
            elif calctype[4] == 'p':
                value = mean + value
    elif calctype == 'diffmax':
        value = max(data) - min(data)
    elif calctype == 'diffmin':
        value = min(data) - max(data)
    else:
        return 0

    try:
        record['value'] = '{0:.4g}'.format(value)
    except ValueError:
        print('Warning: Min/Typ/Max value is not not numeric; value is ' + value)
        return 0

    # Next calculate the score based on the limit type

    if limittype == 'above':
        # Score a penalty if value is below the target
        if 'target' in record:
            targval = float(targval)
            dopassfail = False
            if 'penalty' in record:
                if record['penalty'] == 'fail':
                    dopassfail = True
                else:
                    penalty = float(record['penalty'])
            else:
                penalty = 0
            print('min = ' + str(value))
            # NOTE: 0.0005 value corresponds to formatting above, so the
            # value is not marked in error unless it would show a different
            # value in the display.
            if value < targval - 0.0005:
                if dopassfail:
                    locscore = 'fail'
                    score = 'fail'
                    print('fail: target = ' + str(record['target']) + '\n')
                else:
                    locscore = (targval - value) * penalty
                    print('fail: target = ' + str(record['target'])
					+ ' penalty = ' + str(locscore))
                    if score != 'fail':
                        score += locscore
            elif math.isnan(value):
                locscore = 'fail'
                score = 'fail'
            else:
                if dopassfail:
                    locscore = 'pass'
                else:
                    locscore = 0
                print('pass')
            if dopassfail:
                record['score'] = locscore
            else:
                record['score'] = '{0:.4g}'.format(locscore)

    elif limittype == 'below':
        # Score a penalty if value is above the target
        if 'target' in record:
            targval = float(targval)
            dopassfail = False
            if 'penalty' in record:
                if record['penalty'] == 'fail':
                    dopassfail = True
                else:
                    penalty = float(record['penalty'])
            else:
                penalty = 0
            print('max = ' + str(value))
            # NOTE: 0.0005 value corresponds to formatting above, so the
            # value is not marked in error unless it would show a different
            # value in the display.
            if value > targval + 0.0005:
                if dopassfail:
                    locscore = 'fail'
                    score = 'fail'
                    print('fail: target = ' + str(record['target']) + '\n')
                else:
                    locscore = (value - targval) * penalty
                    print('fail: target = ' + str(record['target'])
					+ ' penalty = ' + str(locscore))
                    if score != 'fail':
                        score += locscore
            elif math.isnan(value):
                locscore = 'fail'
                score = 'fail'
            else:
                if dopassfail:
                    locscore = 'pass'
                else:
                    locscore = 0
                print('pass')
            if dopassfail:
                record['score'] = locscore
            else:
                record['score'] = '{0:.4g}'.format(locscore)

    elif limittype == 'exact':
        # Score a penalty if value is not equal to the target
        if 'target' in record:
            targval = float(targval)
            dopassfail = False
            if 'penalty' in record:
                if record['penalty'] == 'fail':
                    dopassfail = True
                else:
                    penalty = float(record['penalty'])
            else:
                penalty = 0

            if value != targval:
                if dopassfail:
                    locscore = 'fail'
                    score = 'fail'
                    print('off-target failure')
                else:
                    locscore = abs(targval - value) * penalty
                    print('off-target: target = ' + str(record['target'])
					+ ' penalty = ' + str(locscore))
                    if score != 'fail':
                        score += locscore
            elif math.isnan(value):
                locscore = 'fail'
                score = 'fail'
            else:
                print('on-target')
                if dopassfail:
                    locscore = 'pass'
                else:
                    locscore = 0

            if dopassfail:
                record['score'] = locscore
            else:
                record['score'] = '{0:.4g}'.format(locscore)

    elif limittype == 'legacy':
        # Score a penalty if the value is not equal to the target, except
        # that a lack of a minimum record implies no penalty below the
        # target, and lack of a maximum record implies no penalty above
        # the target.  This is legacy behavior for "typ" records, and is
        # used if no "calc" key appears in the "typ" record.  "legacy" may
        # also be explicitly stated, although it is considered deprecated
        # in favor of "avg-max" and "avg-min".

        if 'target' in record:
            targval = float(targval)
            if record['penalty'] == 'fail':
                # "typical" should never be pass-fail
                penalty = 0
            else:
                penalty = float(record['penalty'])
            print('typ = ' + str(value))
            if value != targval:
                if 'max' in param and value > targval:
                    # max specified, so values below 'typ' are not costed
                    # this method deprecated, use 'calc' = 'avg-max' instead.
                    locscore = (value - targval) * penalty
                    print('above-target: target = ' + str(record['target'])
					+ ' penalty = ' + str(locscore))
                elif 'min' in param and value < targval:
                    # min specified, so values above 'typ' are not costed
                    # this method deprecated, use 'calc' = 'avg-min' instead.
                    locscore = (targval - value) * penalty
                    print('below-target: target = ' + str(record['target'])
					+ ' penalty = ' + str(locscore))
                elif 'max' not in param and 'min' not in param:
                    # Neither min and max specified, so value is costed on
                    # both sides of the target.
                    locscore = abs(targval - value) * penalty
                    print('off-target: target = ' + str(record['target'])
					+ ' penalty = ' + str(locscore))
                else:
                    locscore = 0
                if score != 'fail':
                    score += locscore
            else:
                locscore = 0
                print('on-target')
            record['score'] = '{0:.4g}'.format(locscore)

    # Note:  Calctype 'none' performs no calculation.  Record is unchanged,
    # and "score" is returned unchanged.

    return score

def run_and_analyze_lvs(dsheet):
    ipname = dsheet['ip-name']
    node = dsheet['node']
    # Hack---node XH035 should have been specified as EFXH035A; allow
    # the original one for backwards compatibility.
    if node == 'XH035':
        node = 'EFXH035A'
    mag_path = netlist_path + '/lvs/' + ipname + '.spi'
    schem_path = netlist_path + '/stub/' + ipname + '.spi'

    if not os.path.exists(schem_path):
        schem_path = netlist_path + '/' + ipname + '.spi'
    if not os.path.exists(schem_path):
        if os.path.exists(root_path + '/verilog'):
            schem_path = root_path + '/verilog/' + ipname + '.v'

    # Check the netlist to see if the cell to match is a subcircuit.  If
    # not, then assume it is the top level.

    is_subckt = False
    subrex = re.compile('^[^\*]*[ \t]*.subckt[ \t]+([^ \t]+).*$', re.IGNORECASE)
    with open(mag_path) as ifile:
        spitext = ifile.read()

    dutlines = spitext.replace('\n+', ' ').splitlines()
    for line in dutlines:
        lmatch = subrex.match(line)
        if lmatch:
            subname = lmatch.group(1)
            if subname.lower() == ipname.lower():
                is_subckt = True
                break

    if is_subckt:
        layout_arg = mag_path + ' ' + ipname
    else:
        layout_arg = mag_path

    # Get PDK name for finding the netgen setup file
    if os.path.exists(root_path + '/.ef-config'):
        pdkdir = os.path.realpath(root_path + '/.ef-config/techdir')
    else:
        foundry = dsheet['foundry']
        pdkdir = '/ef/tech/' + foundry + '/' + node
    lvs_setup = pdkdir + '/libs.tech/netgen/' + node + '_setup.tcl'

    # Run LVS as a subprocess and wait for it to finish.  Use the -json
    # switch to get a file that is easy to parse.

    print('cace_launch.py:  running /ef/apps/bin/netgen -batch lvs ')
    print(layout_arg + ' ' + schem_path + ' ' + ipname + ' ' + lvs_setup + ' comp.out -json -blackbox')

    lvsproc = subprocess.run(['/ef/apps/bin/netgen', '-batch', 'lvs',
		layout_arg, schem_path + ' ' + ipname,
		lvs_setup, 'comp.out', '-json', '-blackbox'], cwd=layout_path,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

    with open(layout_path + '/comp.json', 'r') as cfile:
        lvsdata = json.load(cfile)

    # Count errors in the JSON file
    failures = 0
    ncells = len(lvsdata)
    for c in range(0, ncells):
        cellrec = lvsdata[c]
        if c == ncells - 1:
            topcell = True
        else:
            topcell = False

        # Most errors must only be counted for the top cell, because individual
        # failing cells are flattened and the matching attempted again on the
        # flattened netlist.

        if topcell:
            if 'devices' in cellrec:
                devices = cellrec['devices']
                devlist = [val for pair in zip(devices[0], devices[1]) for val in pair]
                devpair = list(devlist[p:p + 2] for p in range(0, len(devlist), 2))
                for dev in devpair:
                    c1dev = dev[0]
                    c2dev = dev[1]
                    diffdevs = abs(c1dev[1] - c2dev[1])
                    failures += diffdevs

            if 'nets' in cellrec:
                nets = cellrec['nets']
                diffnets = abs(nets[0] - nets[1])
                failures += diffnets

            if 'badnets' in cellrec:
                badnets = cellrec['badnets']
                failures += len(badnets)

            if 'badelements' in cellrec:
                badelements = cellrec['badelements']
                failures += len(badelements)

            if 'pins' in cellrec:
                pins = cellrec['pins']
                pinlist = [val for pair in zip(pins[0], pins[1]) for val in pair]
                pinpair = list(pinlist[p:p + 2] for p in range(0, len(pinlist), 2))
                for pin in pinpair:
                    if pin[0].lower() != pin[1].lower():
                        failures += 1

        # Property errors must be counted for every cell
        if 'properties' in cellrec:
            properties = cellrec['properties']
            failures += len(properties)

    return failures

def apply_measure(varresult, measure, variables):
    # Apply a measurement (record "measure") using vectors found in
    # "varresult" and produce new vectors which overwrite the original
    # ones.  Operations may reduce "varresult" vectors to a single value.

    # 'condition' defaults to TIME;  but this only applies to transient analysis data!
    if 'condition' in measure:
        condition = measure['condition']
        if condition == 'RESULT':
            # 'RESULT' can either be a specified name (not recommended), or else it is
            # taken to be the variable set as the result variable. 
            try:
                activevar = next(item for item in variables if item['condition'] == condition)
            except StopIteration:
                try:
                    activevar = next(item for item in variables if 'result' in item)
                except StopIteration:
                    print('Error: measurement condition ' + condition + ' does not exist!')
                    return 0
                else:
                    condition = activevar['condition']
                
    else:
        condition = 'TIME'

    # Convert old-style separate condition, pin to new style combined
    if 'pin' in measure:
        if ':' not in measure['condition']:
            measure['condition'] += ':' + measure['pin']
        measure.pop('pin', 0)

    try:
        activevar = next(item for item in variables if item['condition'] == condition)
    except:
        activeunit = ''
    else:
        if 'unit' in activevar:
            activeunit = activevar['unit']
        else:
            activeunit = ''

    try:
        activetrace = varresult[condition]
    except KeyError:
        print("Measurement error:  Condition " + condition + " does not exist in results.")
        # No active trace;  cannot continue.
        return

    rsize = len(activetrace)
 
    if 'TIME' in varresult:
        timevector = varresult['TIME']
        try:
            timevar = next(item for item in variables if item['condition'] == 'TIME')
        except:
            timeunit = 's'
        else:
            if 'unit' in timevar:
                timeunit = timevar['unit']
            else:
                timeunit = 's'
    else:
        timevector = []
        timeunit = ''

    calctype = measure['calc']
    # Diagnostic
    # print("Measure calctype = " + calctype)

    if calctype == 'RESULT':
        # Change the 'result' marker to the indicated condition.
        for var in variables:
            if 'result' in var:
                var.pop('result')

        activevar['result'] = True

    elif calctype == 'REMOVE':
        # Remove the indicated condition vector.
        varresult.pop(condition)

    elif calctype == 'REBASE':
        # Rebase specified vector (subtract minimum value from all components)
        base = min(activetrace)
        varresult[condition] = [i - base for i in activetrace]

    elif calctype == 'ABS':
        # Take absolute value of activetrace.
        varresult[condition] = [abs(i) for i in activetrace]
        
    elif calctype == 'NEGATE':
        # Negate the specified vector
        varresult[condition] = [-i for i in activetrace]
        
    elif calctype == 'ADD':
        if 'value' in measure:
            v = float(measure['value'])
            varresult[condition] = [i + v for i in activetrace]
        else: 
            # Add the specified vector to the result and replace the result
            varresult[condition] = [i + j for i, j in zip(activetrace, paramresult)]
        
    elif calctype == 'SUBTRACT':
        if 'value' in measure:
            v = float(measure['value'])
            varresult[condition] = [i - v for i in activetrace]
        else: 
            # Subtract the specified vector from the result
            varresult[condition] = [j - i for i, j in zip(activetrace, paramresult)]

    elif calctype == 'MULTIPLY':
        if 'value' in measure:
            v = float(measure['value'])
            varresult[condition] = [i * v for i in activetrace]
        else: 
            # Multiply the specified vector by the result (e.g., to get power)
            varresult[condition] = [j * i for i, j in zip(activetrace, paramresult)]
        
    elif calctype == 'CLIP':
        if timevector == []:
            return
        # Clip specified vector to the indicated times
        if 'from' in measure:
            fromtime = float(spice_unit_convert([timeunit, measure['from'], 'time']))
        else:
            fromtime = timevector[0] 
        if 'to' in measure:
            totime = float(spice_unit_convert([timeunit, measure['to'], 'time']))
        else:
            totime = timevector[-1]

        try:
            fromidx = next(i for i, j in enumerate(timevector) if j >= fromtime)
        except StopIteration:
            fromidx = len(timevector) - 1
        try:
            toidx = next(i for i, j in enumerate(timevector) if j >= totime)
            toidx += 1
        except StopIteration:
            toidx = len(timevector)

        for key in varresult:
            vector = varresult[key]
            varresult[key] = vector[fromidx:toidx]

        rsize = toidx - fromidx

    elif calctype == 'MEAN':
        if timevector == []:
            return

        # Get the mean value of all traces in the indicated range.  Results are 
	# collapsed to the single mean value.
        if 'from' in measure:
            fromtime = float(spice_unit_convert([timeunit, measure['from'], 'time']))
        else:
            fromtime = timevector[0] 
        if 'to' in measure:
            totime = float(spice_unit_convert([timeunit, measure['to'], 'time']))
        else:
            totime = timevector[-1]

        try:
            fromidx = next(i for i, j in enumerate(timevector) if j >= fromtime)
        except StopIteration:
            fromidx = len(timevector) - 1
        try:
            toidx = next(i for i, j in enumerate(timevector) if j >= totime)
            toidx += 1
        except StopIteration:
            toidx = len(timevector)

        # Correct time average requires weighting according to the size of the
        # time slice.
        tsum = timevector[toidx - 1] - timevector[fromidx]

        for key in varresult:
            vector = varresult[key]
            try:
                # Test if condition is a numeric value
                varresult[key] = vector[fromidx] + 1
            except TypeError:
                # Some conditions like 'corner' cannot be averaged, so just take the
                # first entry (may want to consider different handling)
                varresult[key] = [vector[fromidx]]
            else:
                vtot = 0.0
                for i in range(fromidx + 1, toidx):
                    # Note:  This expression can and should be optimized!
                    vtot += ((vector[i] + vector[i - 1]) / 2) * (timevector[i] - timevector[i - 1])
                varresult[key] = [vtot / tsum]

        rsize = 1
        
    elif calctype == 'RISINGEDGE':
        if timevector == []:
            return

        # RISINGEDGE finds the time of a signal rising edge.
        # parameters used are:
        # 'from':   start time of search (default zero)
        # 'to':     end time of search (default end)
        # 'number': edge number (default first edge, or zero) (to be done)
        # 'cross':  measure time when signal crosses this value
        # 'keep':  determines what part of the vectors to keep
        if 'from' in measure:
            fromtime = float(spice_unit_convert([timeunit, measure['from'], 'time']))
        else:
            fromtime = timevector[0] 
        if 'to' in measure:
            totime = float(spice_unit_convert([timeunit, measure['to'], 'time']))
        else:
            totime = timevector[-1]
        if 'cross' in measure:
            crossval = float(measure['cross'])
        else:
            crossval = (max(activetrace) + min(activetrace)) / 2;
        try:
            fromidx = next(i for i, j in enumerate(timevector) if j >= fromtime)
        except StopIteration:
            fromidx = len(timevector) - 1
        try:
            toidx = next(i for i, j in enumerate(timevector) if j >= totime)
            toidx += 1
        except StopIteration:
            toidx = len(timevector)
        try:
            startidx = next(i for i, j in enumerate(activetrace[fromidx:toidx]) if j < crossval)
        except StopIteration:
            startidx = 0
        startidx += fromidx
        try:
            riseidx = next(i for i, j in enumerate(activetrace[startidx:toidx]) if j >= crossval)
        except StopIteration:
            riseidx = toidx - startidx - 1
        riseidx += startidx

        # If not specified, 'keep' defaults to 'INSTANT'.
        if 'keep' in measure:
            keeptype = measure['keep']
            if keeptype == 'BEFORE':
                istart = 0
                istop = riseidx
            elif keeptype == 'AFTER':
                istart = riseidx
                istop = len(timevector)
            else:
                istart = riseidx
                istop = riseidx + 1
        else:
            istart = riseidx
            istop = riseidx + 1

        for key in varresult:
            vector = varresult[key]
            varresult[key] = vector[istart:istop]

        rsize = istop - istart
        
    elif calctype == 'FALLINGEDGE':
        if timevector == []:
            return

        # FALLINGEDGE finds the time of a signal rising edge.
        # parameters used are:
        # 'from':   start time of search (default zero)
        # 'to':     end time of search (default end)
        # 'number': edge number (default first edge, or zero) (to be done)
        # 'cross':  measure time when signal crosses this value
        # 'keep':  determines what part of the vectors to keep
        if 'from' in measure:
            fromtime = float(spice_unit_convert([timeunit, measure['from'], 'time']))
        else:
            fromtime = timevector[0] 
        if 'to' in measure:
            totime = float(spice_unit_convert([timeunit, measure['to'], 'time']))
        else:
            totime = timevector[-1]
        if 'cross' in measure:
            crossval = measure['cross']
        else:
            crossval = (max(activetrace) + min(activetrace)) / 2;
        try:
            fromidx = next(i for i, j in enumerate(timevector) if j >= fromtime)
        except StopIteration:
            fromidx = len(timevector) - 1
        try:
            toidx = next(i for i, j in enumerate(timevector) if j >= totime)
            toidx += 1
        except StopIteration:
            toidx = len(timevector)
        try:
            startidx = next(i for i, j in enumerate(activetrace[fromidx:toidx]) if j > crossval)
        except StopIteration:
            startidx = 0
        startidx += fromidx
        try:
            fallidx = next(i for i, j in enumerate(activetrace[startidx:toidx]) if j <= crossval)
        except StopIteration:
            fallidx = toidx - startidx - 1
        fallidx += startidx

        # If not specified, 'keep' defaults to 'INSTANT'.
        if 'keep' in measure:
            keeptype = measure['keep']
            if keeptype == 'BEFORE':
                istart = 0
                istop = fallidx
            elif keeptype == 'AFTER':
                istart = fallidx
                istop = len(timevector)
            else:
                istart = fallidx
                istop = fallidx + 1
        else:
            istart = fallidx
            istop = fallidx + 1

        for key in varresult:
            vector = varresult[key]
            varresult[key] = vector[istart:istop]

        rsize = istop - istart

    elif calctype == 'STABLETIME':
        if timevector == []:
            return

        # STABLETIME finds the time at which the signal stabilizes
        # parameters used are:
        # 'from':  start time of search (default zero)
        # 'to':    end time of search (works backwards from here) (default end)
        # 'slope': measure time when signal rate of change equals this slope
        # 'keep':  determines what part of the vectors to keep
        if 'from' in measure:
            fromtime = float(spice_unit_convert([timeunit, measure['from'], 'time']))
        else:
            fromtime = timevector[0] 
        if 'to' in measure:
            totime = float(spice_unit_convert([timeunit, measure['to'], 'time']))
        else:
            totime = timevector[-1]
        if 'limit' in measure:
            limit = float(measure['limit'])
        else:
            # Default is 5% higher or lower than final value
            limit = 0.05
        try:
            fromidx = next(i for i, j in enumerate(timevector) if j >= fromtime)
        except StopIteration:
            fromidx = len(timevector) - 1
        try:
            toidx = next(i for i, j in enumerate(timevector) if j >= totime)
        except StopIteration:
            toidx = len(timevector) - 1
        finalval = activetrace[toidx]
        toidx += 1
        highval = finalval * (1.0 + limit)
        lowval = finalval * (1.0 - limit)
        try:
            breakidx = next(i for i, j in reversed(list(enumerate(activetrace[fromidx:toidx]))) if j >= highval or j <= lowval)
        except StopIteration:
            breakidx = 0
        breakidx += fromidx

        # If not specified, 'keep' defaults to 'INSTANT'.
        if 'keep' in measure:
            keeptype = measure['keep']
            if keeptype == 'BEFORE':
                istart = 0
                istop = breakidx
            elif keeptype == 'AFTER':
                istart = breakidx
                istop = len(timevector)
            else:
                istart = breakidx
                istop = breakidx + 1
        else:
            istart = breakidx
            istop = breakidx + 1

        for key in varresult:
            vector = varresult[key]
            varresult[key] = vector[istart:istop]

        rsize = istop - istart

    elif calctype == 'INSIDE':
        if timevector == []:
            return

        # INSIDE retains only values which are inside the indicated limits
        # 'min':  minimum value limit to keep results
        # 'max':  maximum value limit to keep results
        if 'from' in measure:
            fromtime = float(spice_unit_convert([timeunit, measure['from'], 'time']))
        else:
            fromtime = timevector[0] 
        if 'to' in measure:
            totime = float(spice_unit_convert([timeunit, measure['to'], 'time']))
        else:
            totime = timevector[-1]
        if 'min' in measure:
            minval = float(spice_unit_convert([activeunit, measure['min']]))
        else:
            minval = min(activetrace)
        if 'max' in measure:
            maxval = float(spice_unit_convert([activeunit, measure['max']]))
        else:
            maxval = max(activetrace)

        try:
            fromidx = next(i for i, j in enumerate(timevector) if j >= fromtime)
        except StopIteration:
            fromidx = len(timevector) - 1
        try:
            toidx = next(i for i, j in enumerate(timevector) if j >= totime)
            toidx += 1
        except StopIteration:
            toidx = len(timevector)
        goodidx = list(i for i, j in enumerate(activetrace[fromidx:toidx]) if j >= minval and j <= maxval)
        # Diagnostic
        if goodidx == []:
            print('All vector components failed bounds test.  max = ' + str(max(activetrace[fromidx:toidx])) + '; min = ' + str(min(activetrace[fromidx:toidx])))

        goodidx = [i + fromidx for i in goodidx]
        for key in varresult:
            vector = varresult[key]
            varresult[key] = [vector[i] for i in goodidx]

        rsize = len(goodidx)

    return rsize

def read_ascii_datafile(file, *args):
    # Read a file of data produced by the 'wrdata' command in ngspice
    # (simple ASCII data in columnar format)
    # No unit conversions occur at this time.
    #
    # Arguments always include the analysis variable vector.  If additional
    # arguments are present in "args", they are value vectors representing
    # additional columns in the data file, and should be treated similarly
    # to the analysis variable.  Note, however, that the wrdata format
    # redundantly puts the analysis variable in every other column.

    if not args:
        print('Error:  testbench does not specify contents of data file!')
        return

    dmatrix = []
    filepath = simfiles_path + '/' + file
    if not os.path.isfile(filepath):
        # Handle ngspice's stupid handling of file extensions for the argument
        # passed to the 'wrdata' command, which sometimes adds the .data
        # extension and sometimes doesn't, regardless of whether the argument
        # has an extension or not.  Method here is to always include the
        # extension in the argument, then look for possible ".data.data" files.
        if os.path.isfile(filepath + '.data'):
            filepath = filepath + '.data'
        else:
            return 0

    with open(filepath, 'r') as afile:
        for line in afile.readlines():
            ldata = line.split()
            if ldata:
                # Note: dependent variable (e.g., TIME) is repeated
                # every other column, so record this only once, then
                # read the remainder while skipping every other column.
                dvec = []
                dvec.append(float(ldata[0]))
                dvec.extend(list(map(float, ldata[1::2])))
                dmatrix.append(dvec)

        # Transpose dmatrix
        try:
            dmatrix = list(map(list, zip(*dmatrix)))
        except TypeError:
            print("last line data are " + str(ldata))
            print("dmatrix is " + str(dmatrix))

        for dvalues, dvec in zip(dmatrix, args):
            dvec.extend(dvalues)

        try:
            rval = len(ldata[0])
        except TypeError:
            rval = 1
        return rval

if __name__ == '__main__':

    # Exit in response to terminate signal by terminating ngspice processes
    faulthandler.register(signal.SIGUSR2)
    signal.signal(signal.SIGINT, cleanup_exit)
    signal.signal(signal.SIGTERM, cleanup_exit)
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # track the circuit score (for simulation;  layout handled separately)
    # (initial score may be overridden by passing -score=value to cace_launch.py)
    score = 0.0

    # read the JSON file
    keepmode = False
    plotmode = False
    postmode = True
    if len(arguments) > 0:
        inputfile = arguments[0]
    else:
        raise SyntaxError('Usage: ' + sys.argv[0] + ' json_file [-options]\n')

    if os.path.splitext(inputfile)[1] != '.json':
        raise SyntaxError('Usage: ' + sys.argv[0] + ' json_file [-options]\n')

    for item in options:
        result = item.split('=')
        if result[0] == '-keep':
            keepmode = True
        elif result[0] == '-plot':
            plotmode = True
        elif result[0] == '-nosim':
            # Diagnostic
            print('No simulations specified. . . cace_launch exiting.\n')
            sys.exit(0)
        elif result[0] == '-nopost':
            postmode = False
            keepmode = True
        elif result[0] == '-simdir':
            simfiles_path = result[1]
        elif result[0] == '-layoutdir':
            layout_path = result[1]
        elif result[0] == '-netlistdir':
            netlist_path = result[1]
        elif result[0] == '-rootdir':
            root_path = result[1]
        elif result[0] == '-local':
            localmode = True
            bypassmode = False
            postmode = False
            keepmode = False
        elif result[0] == '-bypass':
            bypassmode = True
            localmode = True
            postmode = True
            keepmode = False
        elif result[0] == '-score':
            score = result[1]
        else:
            raise SyntaxError('Bad option ' + item + ', options are -keep, -nosim, -nopost, -local, and -simdir=\n')

    # Various information could be obtained from the input JSON file
    # name, but it will be assumed that all information should be
    # obtained from the contents of the JSON file itself.

    with open(inputfile) as ifile:
       datatop = json.load(ifile)

    # Option passing through the JSON:  use "nopost" or "keep" defined at the top level.
    if 'nopost' in datatop:
        postmode = False
        datatop.pop('nopost')
    if 'keep' in datatop:
        keepmode = True
        datatop.pop('keep')
    if 'local' in datatop:
        localmode = True
        datatop.pop('local')

    if 'request-hash' in datatop:
        hashname = datatop['request-hash']
    else:
        print("Document JSON missing request-hash.")
        sys.exit(1)

    # Simfiles should be put in path specified by -simdir, or else
    # put them in the working directory.  Normally "-simdir" will
    # be given on the command line.

    if not simfiles_path:
        if root_path:
            simfiles_path = root_path + '/' + hashname
        else:
            simfiles_path = og_config.simulation_path + '/' + hashname

    if not os.path.isdir(simfiles_path):
        print('Error:  Simulation folder ' + simfiles_path + ' does not exist.')
        sys.exit(1)

    if not layout_path:
        if root_path:
            layout_path = root_path + '/mag'

    if not netlist_path:
        if root_path:
            netlist_path = root_path + '/spi'

    # Change location to the simulation directory
    os.chdir(simfiles_path)

    # pull out the relevant part of the JSON file, which is "data-sheet"
    dsheet = datatop['data-sheet']

    # Prepare a dictionary for the status and pass critical values from datatop.
    try:
        statdoc['UID'] = datatop['UID']
        statdoc['request-hash'] = datatop['request-hash']
        if 'project-folder' in datatop:
            statdoc['project'] = datatop['project-folder']
        else:
            statdoc['project'] = dsheet['ip-name']
        status = {}
        status['message'] = 'initializing'
        status['completed'] = '0'
        status['total'] = 'unknown'
        status['hash'] = datatop['request-hash']
        statdoc['status'] = status
        if not localmode:
            send_status(statdoc)
    except KeyError:
        if not localmode:
            print("Failed to generate status record.")
        else:
            pass

    # find the eparamlist.  If it exists, then the template has been
    # loaded.  If not, find the template name, then load it from known
    # templates.

    if 'electrical-params' in dsheet:
        eparamlist = dsheet['electrical-params']
    else:
        eparamlist = []
    if 'physical-params' in dsheet:
        pparamlist = dsheet['physical-params']
    else:
        pparamlist = []

    if eparamlist == [] and pparamlist == []:
        print('Circuit JSON file does not have a characterization template!')
        sys.exit(0)

    simulations = 0
    has_aux_files = False

    # Diagnostic:  find and print the number of files to be simulated
    # Names are methodname, pinname, and simulation number.
    totalsims = 0
    filessimmed = []
    for param in eparamlist:
        if 'testbenches' in param:
            totalsims += len(param['testbenches'])
    print('Total files to simulate: ' + str(totalsims))

    # Status
    if statdoc and not localmode:
        status['message'] = 'starting'
        status['completed'] = '0'
        status['total'] = str(totalsims)
        send_status(statdoc)

    for param in eparamlist:
        # Process only entries in JSON that have 'testbenches' record
        if 'testbenches' not in param:
            continue

        # Information needed to construct the filenames
        simtype = param['method']

        # For methods with ":", the filename is the part before the colon.
        methodname = simtype.split(":")
        if len(methodname) > 1:
            testbench = methodname[0]
            submethod = ":" + methodname[1]
        else:
            testbench = simtype
            submethod = ""

        # Simple outputs are followed by a single value
        outrex = re.compile("[ \t]*\"?([^ \t\"]+)\"?(.*)$", re.IGNORECASE)
        # conditions always follow as key=value pairs
        dictrex = re.compile("[ \t]*([^ \t=]+)=([^ \t=]+)(.*)$", re.IGNORECASE)
        # conditions specified as min:step:max match a result vector.
        steprex = re.compile("[ \t]*([^:]+):([^:]+):([^:]+)$", re.IGNORECASE)
        # specification of units as a binary, hex, etc., string in verilog format
        binrex = re.compile(r'([0-9]*)\'([bodh])', re.IGNORECASE)

        paramresult = []	# List of results
        paramname = 'RESULT'	# Name of the result parameter (default 'RESULT')
        condresult = {}		# Dictionary of condition names and values for each result
        simfailures = 0		# Track simulations that don't generate results

        # Run ngspice on each prepared simulation file
        # FYI; ngspice generates output directly to the TTY, bypassing stdout
        # and stdin, so that it can update the simulation time at the bottom
        # of the screen without scrolling.  Subvert this in ngspice, if possible.
        # It is a bad practice of ngspice to output to the TTY in batch mode. . .

        testbenches = param['testbenches']
        print('Files to simulate method ' + testbenches[0]['prefix'] + ': ' + str(len(testbenches)))

        for testbench in testbenches:
            filename = testbench['filename']
            filessimmed.append(filename)
            fileprefix = testbench['prefix']
            # All output lines start with prefix
            outrexall = re.compile(fileprefix + submethod + "[ \t]+=?[ \t]*(.+)$", re.IGNORECASE)
            # "measure" statements act on results of individual simulations,
            # so keep the results separate until after measurements have been made
            locparamresult = []
            loccondresult = {}
            locvarresult = {}

            # Cosimulation:  If there is a '.tv' file in the simulation directory
            # with the same root name as the netlist file, then run iverilog and
            # vvp.  vvp will call ngspice from the verilog.
            verilog = os.path.splitext(filename)[0] + '.tv'
            my_env = os.environ.copy()
            if os.path.exists(verilog):
                cosim = True
                simulator = '/ef/apps/bin/vvp'
                simargs = ['-M.', '-md_hdl_vpi']
                filename = verilog + 'o'
                # Copy the d_hdl object file into the simulation directory
                shutil.copy('/ef/efabless/lib/iverilog/d_hdl_vpi.vpi', simfiles_path)
                # Generate the output executable (.tvo) file for vvp.
                subprocess.call(['/ef/apps/bin/iverilog', '-o' + filename, verilog])
                # Specific version of ngspice must be used for cosimulation
                # (Deprecated; default version of ngspice now supports cosimulation)
                # my_env['NGSPICE_VERSION'] = 'cosim1'

                # There must not be a file 'simulator_pipe' in the directory or vvp will fail.
                if os.path.exists('simulator_pipe'):
                    os.remove('simulator_pipe')
            else:
                cosim = False
                simulator = '/ef/apps/bin/ngspice'
                simargs = ['-b']
                # Do not generate LXT files, as CACE does not have any methods to handle
                # the data in them anyway.
                my_env['NGSPICE_LXT2NO'] = '1'

            # ngspice writes to both stdout and stderr;  capture all
            # output equally.  Print each line in real-time, flush the
            # output buffer, and then accumulate the lines for processing.

            # Note:  bufsize = 1 and universal_newlines = True sets line-buffered output

            print('Running: ' + simulator + ' ' + ' '.join(simargs) + ' ' + filename)

            with subprocess.Popen([simulator, *simargs, filename],
			stdout=subprocess.PIPE,
			bufsize=1, universal_newlines=True, env=my_env) as spiceproc:
                for line in spiceproc.stdout:
                    print(line, end='')
                    sys.stdout.flush()

                    # Each netlist can have as many results as there are in
                    # the "measurements" list for the electrical parameter,
                    # grouped according to common testbench netlist file and
                    # common set of conditions.

                    matchline = outrexall.match(line)
                    if matchline:
                        # Divide result into tokens.  Space-separated values in quotes
                        # become a result vector;  all other entries should be in the
                        # form <key>=<value>.  Result value becomes "result":[<vector>]
                        # dictionary entry.
                        rest = matchline.group(1)

                        # ASCII file format handling:  Data are in the indicated
                        # file in pairs of analysis variable (e.g., TIME for transients)
                        # and 'result'.  Note that the analysis variable is
                        # always the first and every other column of the data file.
                        # The primary result is implicit.  All other columns
                        # must be explicitly called out on the echo line.
                        if '.data' in rest:
                            print('Reading data from ASCII file.')

                            # "variables" are similar to conditions but describe what is
                            # being output from ngspice.  There should be one entry for
                            # each (unique) column in the data file, matching the names
                            # given in the testbench file.

                            if 'variables' in param:
                                pvars = param['variables']
                                # Convert any old-style condition, pin
                                for var in pvars:
                                    if 'pin' in var:
                                        if not ':' in var['condition']:
                                            var['condition'] += ':' + var['pin']
                                        var.pop('pin')
                            else:
                                pvars = []

                            # Parse all additional variables.  At least one (the
                            # analysis variable) must be specified.
                            data_args = []
                            extra = rest.split()

                            if len(extra) == 1:
                                # If the testbench specifies no vectors, then they
                                # must all be specified in order in 'variables' in
                                # the datasheet entry for the electrical parameters.
                                for var in pvars:
                                    extra.append(var['condition'])
                                if not pvars:
                                    print('Error:  No variables specified in testbench or datasheet.')
                                    rest = ''

                            if len(extra) > 1:
                                for varname in extra[1:]:
                                    if varname not in locvarresult:
                                        locvarresult[varname] = []
                                    data_args.append(locvarresult[varname])

                                rsize = read_ascii_datafile(extra[0], *data_args)

                                # All values in extra[1:] should be param['variables'].  If not, add
                                # an entry and flag a warning because information may be incomplete.

                                for varname in extra[1:]:
                                    try:
                                        var = next(item for item in pvars if item['condition'] == varname)
                                    except StopIteration:
                                        print('Variable ' + varname + ' not specified;  ', end='')
                                        print('information may be incomplete.')
                                        var = {}
                                        var['condition'] = varname
                                        pvars.append(var)                                    

                                # By default, the 2nd result is the result
                                if len(extra) > 2:
                                    varname = extra[2]
                                    varrec = next(item for item in pvars if item['condition'] == varname)
                                    varrec['result'] = True
                                    print('Setting condition ' + varname + ' as the result vector.')

                                # "measure" records are applied to individual simulation outputs,
                                # usually to reduce a time-based vector to a single value by
                                # measuring a steady-state value, peak-peak, frequency, etc.

                                if 'measure' in param:
                                    # Diagnostic
                                    # print('Applying measurements.')

                                    for measure in param['measure']:
                                        # Convert any old-style condition, pin
                                        if 'pin' in measure:
                                            if not ':' in measure['condition']:
                                                measure['condition'] += ':' + measure['pin']
                                            measure.pop('pin')
                                        rsize = apply_measure(locvarresult, measure, pvars)
                                        # Diagnostic
                                        # print("after measure, rsize = " + str(rsize))
                                        # print("locvarresult = " + str(locvarresult))
    
                                    # Now recast locvarresult back into loccondresult.
                                    for varname in locvarresult:
                                        varrec = next(item for item in pvars if item['condition'] == varname)
                                        if 'result' in varrec:
                                            # print('Result for ' + varname + ' = ' + str(locvarresult[varname]))
                                            locparamresult = locvarresult[varname]
                                            paramname = varname
                                        else:
                                            # print('Condition ' + varname + ' = ' + str(locvarresult[varname]))
                                            loccondresult[varname] = locvarresult[varname]
                                        # Diagnostic
                                        # print("Variable " + varname + " length = " + str(len(locvarresult[varname])))
                                    rest = ''

                                else:
                                    # For plots, there is not necessarily any measurements.  Just
                                    # copy values into locparamresult and loccondresult.
                                    for varname in locvarresult:
                                        varrec = next(item for item in pvars if item['condition'] == varname)
                                        if 'result' in varrec:
                                            # print('Result for ' + varname + ' = ' + str(locvarresult[varname]))
                                            locparamresult = locvarresult[varname]
                                            rsize = len(locparamresult)
                                            paramname = varname
                                        else:
                                            # print('Condition ' + varname + ' = ' + str(locvarresult[varname]))
                                            loccondresult[varname] = locvarresult[varname]
                                    rest = ''
                        else:
                            rsize = 0

                        # To-do:  Handle raw files in similar manner to ASCII files.
                          
                        while rest:
                            # This code depends on values coming first, followed by conditions.
                            matchtext = dictrex.match(rest)
                            if matchtext:
                                # Diagnostic!
                                condname = matchtext.group(1)
                                # Append to the condition list
                                if condname not in loccondresult:
                                    loccondresult[condname] = []

                                # Find the condition name in the condition list, so values can
                                # be converted back to the expected units.
                                try:
                                    condrec = next(item for item in param['conditions'] if item['condition'] == condname)
                                except StopIteration:
                                    condunit = ''
                                else:
                                    condunit = condrec['unit']

                                rest = matchtext.group(3)
                                matchstep = steprex.match(matchtext.group(2))
                                if matchstep:
                                    # condition is in form min:step:max, and the
                                    # number of values must match rsize.
                                    cmin = float(matchstep.group(1))
                                    cstep = float(matchstep.group(2))
                                    cmax = float(matchstep.group(3))
                                    cnum = int(round((cmax + cstep - cmin) / cstep))
                                    if cnum != rsize:
                                        print("Warning: Number of conditions (" + str(cnum) + ") is not")
                                        print("equal to the number of results (" + str(rsize) + ")")
                                        # Back-calculate the correct step size.  Usually this
                                        # means that the testbench did not add margin to the
                                        # DC or AC stop condition, and the steps fell 1 short of
                                        # the max.
                                        if rsize > 1:
                                            cstep = (float(cmax) - float(cmin)) / float(rsize - 1)

                                    condvec = []
                                    for r in range(rsize):
                                        condvec.append(cmin)
                                        cmin += cstep

                                    cresult = spice_unit_unconvert([condunit, condvec])
                                    condval = loccondresult[condname]
                                    for cr in cresult:
                                        condval.append(str(cr))

                                else:
                                    # If there is a vector of results but only one condition, copy the
                                    # condition for each result.  Note that value may not be numeric.

                                    # (To do:  Apply 'measure' records here)
                                    condval = loccondresult[condname]
                                    try:
                                        test = float(matchtext.group(2))
                                    except ValueError:
                                        cval = matchtext.group(2)
                                    else:
                                        cval = str(spice_unit_unconvert([condunit, test]))
                                    for r in range(rsize):
                                        condval.append(cval)
                            else:
                                # Not a key=value pair, so must be a result value
                                matchtext = outrex.match(rest)
                                if matchtext:
                                    rest = matchtext.group(2)
                                    rsize += 1
                                    # Result value units come directly from the param record.
                                    if 'unit' in param:
                                        condunit = param['unit']
                                    else:
                                        condunit = ''
                                    if binrex.match(condunit):
                                        # Digital result with units 'b, 'h, etc. are kept as strings.
                                        locparamresult.append(matchtext.group(1))
                                    else:
                                        locparamresult.append(float(matchtext.group(1)))
                                else:
                                    print('Error:  Result line cannot be parsed.')
                                    print('Bad part of line is: ' + rest)
                                    print('Full line is: ' + line)
                                    break

                        # Values passed in testbench['conditions'] are common to each result
                        # value.  From one line there are rsize values, so append each known
                        # condition to loccondresult rsize times.
                        for condrec in testbench['conditions']:
                            condname = condrec[0]
                            if condname in locvarresult:
                                print('Error:  name ' + condname + ' is both a variable and a condition!')
                                print('Ignoring the condition.')
                                continue
                            if condname not in loccondresult:
                                loccondresult[condname] = []
                            condval = loccondresult[condname]
                            if 'unit' in condrec:
                                condunit = condrec['unit']
                            else:
                                condunit = ''
                            for r in range(rsize):
                                if condname.split(':')[0] == 'DIGITAL' or condname == 'CORNER':
                                    # Values that are known to be strings
                                    condval.append(condrec[2])
                                elif binrex.match(condunit):
                                    # Alternate digital specification using units 'b, 'h, etc.
                                    condval.append(condrec[2])
                                elif condname == 'ITERATIONS':
                                    # Values that are known to be integers
                                    condval.append(int(float(condrec[2])))
                                else:
                                    # All other values to be treated as floats unless
                                    # they are non-numeric, in which case they are
                                    # treated as strings and copied as-is.
                                    try:
                                        condval.append(float(condrec[2]))
                                    except ValueError:
                                        # Values that are not numeric just get copied
                                        condval.append(condrec[2])

                spiceproc.stdout.close()
                return_code = spiceproc.wait()
                if return_code != 0:
                    raise subprocess.CalledProcessError(return_code, 'ngspice')

                if len(locparamresult) > 0:
                    # Fold local results into total results
                    paramresult.extend(locparamresult)
                    for key in loccondresult:
                        if not key in condresult:
                            condresult[key] = loccondresult[key]
                        else:
                            condresult[key].extend(loccondresult[key])

                else:
                    # Catch simulation failures
                    simfailures += 1

            simulations += 1

            # Clean up pipe file after cosimulation, also the .lxt file and .tvo files
            if cosim:
                if os.path.exists('simulator_pipe'):
                    os.remove('simulator_pipe')
                # Remove all '.tvo', '.lxt', and '.vcd' files from the work area.
                if keepmode == False:
                    files = os.listdir(simfiles_path)
                    for filename in files:
                        try:
                            fileext = os.path.splitext(filename)[1]
                        except:
                            pass
                        else:
                            if fileext == '.lxt' or fileext == '.vcd' or fileext == '.tvo' or fileext == '.vpi':
                                os.remove(filename)
               

            # Other files to clean up
            if os.path.exists('b3v32check.log'):
                os.remove('b3v32check.log')

            # Status
            if statdoc and not localmode:
                if simulations < totalsims:
                    status['message'] = 'in progress'
                else:
                    status['message'] = 'completed'
                status['completed'] = str(simulations)
                status['total'] = str(totalsims)
                send_status(statdoc)

        # Evaluate concatentated results after all files for this electrical parameter
        # have been run through simulation.

        if paramresult:
            print(simtype + ':')

            # Diagnostic
            # print("paramresult length " + str(len(paramresult)))
            # for key in condresult:
            #     print("condresult length " + str(len(condresult[key])))

            # Write out all results into the JSON file.
            # Results are a list of lists;  the first list is a list of
            # methods, and the rest are sets of values corresponding to unique
            # conditions.  The first item in each lists is the result value
            # for that set of conditions.

            # Always keep results, even for remote CACE.

            outnames = [paramname]
            outunits = []

            if 'unit' in param:
                outunits.append(param['unit'])
            else:
                outunits.append('')
            for key in condresult:
                outnames.append(key)
                try:
                    condrec = next(item for item in param['conditions'] if item['condition'] == key) 
                except:
                    try:
                        condrec = next(item for item in param['variables'] if item['condition'] == key) 
                    except:
                        outunits.append('')
                    else:
                        if 'unit' in condrec:
                            outunits.append(condrec['unit'])
                            # 'variable' entries need to be unconverted
                            cconv = spice_unit_unconvert([condrec['unit'], condresult[key]])
                            condresult[key] = cconv
                        else:
                            outunits.append('')
                else:
                    if 'unit' in condrec:
                        outunits.append(condrec['unit'])
                    else:
                        outunits.append('')

            # Evaluate a script to transform the output, if there is an 'evaluate'
            # record in the electrical parameter.

            if 'evaluate' in param:

                evalrec = param['evaluate']
                try:
                    tool = evalrec['tool']
                except:
                    print("Error:  Evaluate record does not indicate a tool to run.")
                    break
                else:
                    if tool != 'octave' and tool != 'matlab':
                        print("Error:  CASE does not know how to use tool '" + tool + "'")
                        break

                try:
                    script = evalrec['script']
                except:
                    print("Error:  Evaluate record does not indicate a script to run.")
                    break
                else:
                    if os.path.isdir(root_path + '/testbench'):
                        tb_path = root_path + '/testbench/' + script
                        if not os.path.exists(tb_path):
                            if os.path.exists(tb_path + '.m'):
                                tb_path += '.m'
                            else:
                                print("Error:  No script '" + script + "' found in testbench path.")
                                break
                    else:
                        print("Error:  testbench directory not found in root path.")
                        break

                # General purpose tool-based evaluation.  For complex operations of
                # any kind, dump the simulation results to a file "results.json" and
                # invoke the specified tool, which should read the results and
                # generate an output in the form of modified 'paramresult'.
                # e.g., input is an array of transient vectors, output is an FFT
                # analysis.  Input is a voltage, output is an INL value.  Note that
                # 'unit' is the unit produced by the script.  The script is supposed
                # to know what units it gets as input and what it produces as output.

                # Create octave-compatible output with structures for the condition
                # names, units, and data.
                with open('results.dat', 'w') as ofile:
                    print('# Created by cace_gensim.py', file=ofile)
                    print('# name: results', file=ofile)
                    print('# type: scalar struct', file=ofile)
                    print('# ndims: 2', file=ofile)
                    print('# 1 1', file=ofile)
                    numentries = len(outnames)
                    print('# length: ' + str(2 + numentries), file=ofile)
                    print('# name: NAMES', file=ofile)
                    print('# type: cell', file=ofile)
                    print('# rows: ' + str(numentries), file=ofile)
                    print('# columns: 1', file=ofile)
                    for name in outnames:
                        print('# name: <cell-element>', file=ofile)
                        print('# type: sq_string', file=ofile)
                        print('# elements: 1', file=ofile)
                        print('# length: ' + str(len(name)), file=ofile)
                        print(name, file=ofile)
                        print('', file=ofile)
                        print('', file=ofile)

                    print('', file=ofile)
                    print('', file=ofile)
                    print('# name: UNITS', file=ofile)
                    print('# type: cell', file=ofile)
                    print('# rows: ' + str(len(outunits)), file=ofile)
                    print('# columns: 1', file=ofile)
                    for unit in outunits:
                        print('# name: <cell-element>', file=ofile)
                        print('# type: sq_string', file=ofile)
                        print('# elements: 1', file=ofile)
                        print('# length: ' + str(len(unit)), file=ofile)
                        print(unit, file=ofile)
                        print('', file=ofile)
                        print('', file=ofile)
                    print('', file=ofile)
                    print('', file=ofile)

                    # Each condition is output as a 1D array with structure
                    # entry name equal to the condition name.  If the units
                    # is empty then the array is a string.  Otherwise, the
                    # array is numeric (as far as octave is concerned).

                    # First entry is the result (paramresult).  This should never
                    # be a string (at least not in this version of CACE)

                    idx = 0
                    print('# name: ' + outnames[idx], file=ofile)
                    units = outunits[idx]
                    print('# type: matrix', file=ofile)
                    print('# rows: ' + str(len(paramresult)), file=ofile)
                    print('# columns: 1', file=ofile)
                    for value in paramresult:
                        print(' ' + str(value), file=ofile)
                    print('', file=ofile)
                    print('', file=ofile)

                    idx += 1
                    # The rest of the entries are the conditions.  Note that the
                    # name must be a valid octave variable (letters, numbers,
                    # underscores) and so cannot use the condition name.  However,
                    # each condition name is held in the names list, so it can be
                    # recovered.  Each condition is called CONDITION2, CONDITION3,
                    # etc.

                    for key, entry in condresult.items():

                        print('# name: CONDITION' + str(idx + 1), file=ofile)
                        units = outunits[idx]
                        if units == '':
                            # Use cell array for strings
                            print('# type: cell', file=ofile)
                            print('# rows: ' + str(len(entry)), file=ofile)
                            print('# columns: 1', file=ofile)
                            for value in entry:
                                print('# name: <cell-element>', file=ofile)
                                print('# type: sq_string', file=ofile)
                                print('# elements: 1', file=ofile)
                                print('# length: ' + str(len(str(value))), file=ofile)
                                print(str(value), file=ofile)
                                print('', file=ofile)
                                print('', file=ofile)
                        else:
                            print('# type: matrix', file=ofile)
                            print('# rows: ' + str(len(entry)), file=ofile)
                            print('# columns: 1', file=ofile)
                            for value in entry:
                                print(' ' + str(value), file=ofile)

                        print('', file=ofile)
                        print('', file=ofile)
                        idx += 1

                # Now run the specified octave script on the result.  Script
                # generates an output file.  stdout/stderr can be ignored.
                # May want to watch stderr for error messages and/or handle
                # exit status.

                postproc = subprocess.Popen(['/ef/apps/bin/octave-cli', tb_path],
			stdout = subprocess.PIPE)
                rvalues = postproc.communicate()[0].decode('ascii').splitlines()

                # Replace paramresult with the numeric result
                paramresult = list(float(item) for item in rvalues)

            # pconv is paramresult scaled to the units used by param.
            if 'unit' in param:
                pconv = spice_unit_unconvert([param['unit'], paramresult])
            else:
                pconv = paramresult

            outresult = []
            outresult.append(outnames)
            outresult.append(outunits)

            for p in range(len(pconv)):
                outvalues = []
                outvalues.append(str(pconv[p]))
                for key, value in condresult.items():
                    try:
                        outvalues.append(str(value[p]))
                    except IndexError:
                        # Note:  This should not happen. . . 
                        print("Error:  number of values in result and conditions do not match!")
                        print("Result: " + str(len(pconv)))
                        print("Conditions: " + str(len(condresult)))
                        break

                outresult.append(outvalues)

            param['results'] = outresult

            if 'unit' in param:
                units = param['unit']
            else:
                units = ''

            # Catch simulation failures.
            if simfailures > 0:
                print('Simulation failures:  ' + str(simfailures))
                score = 'fail'

            if 'min' in param:
                minrec = param['min']
                if 'calc' in minrec:
                    calc = minrec['calc']
                else:
                    calc = 'min-above'
                minscore = calculate(minrec, pconv, condresult, calc, score, units, param)
                if score != 'fail':
                    score = minscore

            if 'max' in param:
                maxrec = param['max']
                if 'calc' in maxrec:
                    calc = maxrec['calc']
                else:
                    calc = 'max-below'
                maxscore = calculate(maxrec, pconv, condresult, calc, score, units, param)
                if score != 'fail':
                    score = maxscore

            if 'typ' in param:
                typrec = param['typ']
                if 'calc' in typrec:
                    calc = typrec['calc']
                else:
                    calc = 'avg-legacy'
                typscore = calculate(typrec, pconv, condresult, calc, score, units, param)
                if score != 'fail':
                    score = typscore

            if 'plot' in param:
                # If not in localmode, or if in plotmode then create a plot and
                # save it to a file.
                plotrec = param['plot']
                if localmode == False or bypassmode == True or plotmode == True:
                    if 'variables' in param:
                        variables = param['variables']
                    else:
                        variables = []
                    result = cace_makeplot.makeplot(plotrec, param['results'], variables)
                    # New behavior implemented 3/28/2017:  Always keep results.
                    # param.pop('results')
                    if result:
                        plotrec['status'] = 'done'
                        has_aux_files = True
                    else:
                        print('Failure:  No plot from file ' + filename + '\n')
                else:
                    plotrec['status'] = 'done'
        else:
            try:
                print('Failure:  No output from file ' + filename + '\n')
            except NameError:
                print('Failure:  No simulation file, so no output\n')
                continue

            # Handle errors where simulation generated no output.
            # This is the one case where 'typ' can be treated as pass-fail.
            # "score" will be set to "fail" for any of "min", "max", and
            # "typ" that exists in the electrical parameters record and
            # which specifies a target value.  "value" is set to "failure"
            # for display.
            score = 'fail'
            if 'typ' in param:
                typrec = param['typ']
                if 'target' in typrec:
                    typrec['score'] = 'fail'
                typrec['value'] = 'failure'
            if 'max' in param:
                maxrec = param['max']
                if 'target' in maxrec:
                    maxrec['score'] = 'fail'
                maxrec['value'] = 'failure'
            if 'min' in param:
                minrec = param['min']
                if 'target' in minrec:
                    minrec['score'] = 'fail'
                minrec['value'] = 'failure'

        # Pop the testbenches record, which has been replaced by the 'results' record.
        param.pop('testbenches')

        # Final cleanup step:  Remove any remaining '.tv' files from the work area.
        if keepmode == False:
            files = os.listdir(simfiles_path)
            for filename in files:
                try:
                    fileext = os.path.splitext(filename)[1]
                except:
                    pass
                else:
                    if fileext == '.tv':
                        os.remove(filename)

    # Report the final score, and save it to the JSON data

    print('Completed ' + str(simulations) + ' of ' + str(totalsims) + ' simulations');
    print('Circuit pre-extraction simulation total score (lower is better) = '
			+ str(score))

    if score == 'fail':
        dsheet['score'] = 'fail'
    else:
        dsheet['score'] = '{0:.4g}'.format(score)

    # Now handle physical parameters
    netlist_source = dsheet['netlist-source']
    areaval = 0.0

    totalchecks = 0
    for param in pparamlist:
        if 'check' in param:
            totalchecks += 1
    print('Total physical parameters to check: ' + str(totalchecks))

    for param in pparamlist:
        # Process only entries in JSON that have the 'check' record
        if 'check' not in param:
            continue
        if param['check'] != 'true':
            continue

        cond = param['condition']

        if cond == 'device_area':
            areaest = 0
            ipname = dsheet['ip-name']
            foundry = dsheet['foundry']
            node = dsheet['node']
            # Hack---node XH035 should have been specified as EFXH035A; allow
            # the original one for backwards compatibility.
            if node == 'XH035':
                node = 'EFXH035A'

            if layout_path and netlist_path:

                # Run the device area (area estimation) script
                if os.path.exists(netlist_path + '/' + ipname + '.spi'):
                    estproc = subprocess.Popen(['/ef/efabless/bin/layout_estimate.py',
				netlist_path + '/' + ipname + '.spi', node.lower()],
				stdout=subprocess.PIPE,
				cwd = layout_path, universal_newlines = True)
                    outlines = estproc.communicate()[0]
                    arealine = re.compile('.*=[ \t]*([0-9]+)[ \t]*um\^2')
                    for line in outlines.splitlines():
                        lmatch = arealine.match(line)
                        if lmatch:
                            areaum2 = lmatch.group(1)
                            areaest = int(areaum2)

            if areaest > 0:
                score = 'pass'
                maxrec = param['max']
                targarea = float(maxrec['target'])
                maxrec['value'] = str(areaest)
                if 'penalty' in maxrec:
                    if maxrec['penalty'] == 'fail':
                        if areaest > targarea:
                            score = 'fail'
                        else:
                            score = 'pass'
                    else:
                        try:
                            if areaest > targarea:
                                score = str((areaest - targarea) * float(maxrec['penalty']))
                            else:
                                score = 'pass'
                        except:
                            if areaest > targarea:
                                score = maxrec['penalty']
                            else:
                                score = 'pass'
                else:
                    score = 'pass'
                maxrec['score'] = score

        if cond == 'area' or cond == 'height' or cond == 'width':

            # First time for any of these, run the check and get values

            if areaval == 0 and not netlist_source == 'schematic':

                ipname = dsheet['ip-name']
                foundry = dsheet['foundry']
                node = dsheet['node']
                # Hack---node XH035 should have been specified as EFXH035A; allow
                # the original one for backwards compatibility.
                if node == 'XH035':
                    node = 'EFXH035A'

                if layout_path:

                    # Find the layout directory and check if there is a layout
                    # for the cell there.  If not, use the layout estimation
                    # script.  Result is either an actual area or an area estimate.

                    if os.path.exists(layout_path + '/' + ipname + '.mag'):
                        areaproc = subprocess.Popen(['/ef/apps/bin/magic',
				'-dnull', '-noconsole', layout_path + '/' + ipname + '.mag'],
				stdin = subprocess.PIPE, stdout = subprocess.PIPE,
				cwd = layout_path, universal_newlines = True)
                        areaproc.stdin.write("select top cell\n")
                        areaproc.stdin.write("box\n")
                        areaproc.stdin.write("quit -noprompt\n")
                        outlines = areaproc.communicate()[0]
                        magrex = re.compile('microns:[ \t]+([0-9.]+)[ \t]*x[ \t]*([0-9.]+)[ \t]+.*[ \t]+([0-9.]+)[ \t]*$')
                        for line in outlines.splitlines():
                            lmatch = magrex.match(line)
                            if lmatch:
                                widthval = float(lmatch.group(1))
                                heightval = float(lmatch.group(2))
                                areaval = float(lmatch.group(3))

                if areaval > 0:

                    # Now work through the physical parameters --- pass 1
                    # If area was estimated, then find target width and height
                    # for estimating actual width and height.

                    for checkparam in dsheet['physical-params']:
                        checkcond = checkparam['condition']
                        maxrec = checkparam['max']
                        if checkcond == 'area':
                            targarea = float(maxrec['target'])
                        elif checkcond == 'width':
                            targwidth = float(maxrec['target'])
                        elif checkcond == 'height':
                            targheight = float(maxrec['target'])

            maxrec = param['max']
            unit = param['unit']

            if cond == 'area':
                if areaval > 0:
                    maxrec['value'] = str(areaval)
                    if areaval > targarea:
                        score = 'fail'
                        maxrec['score'] = 'fail'
                    else:
                        maxrec['score'] = 'pass'
            elif cond == 'width':
                if areaval > 0:
                    maxrec['value'] = str(widthval)
                    if widthval > targwidth:
                        score = 'fail'
                        maxrec['score'] = 'fail'
                    else:
                        maxrec['score'] = 'pass'

            elif cond == 'height':
                if areaval > 0:
                    maxrec['value'] = str(heightval)
                    if heightval > targheight:
                        score = 'fail'
                        maxrec['score'] = 'fail'
                    else:
                        maxrec['score'] = 'pass'

        elif cond == 'DRC_errors':

            ipname = dsheet['ip-name']

            if layout_path and not netlist_source == 'schematic':
                if os.path.exists(layout_path + '/' + ipname + '.mag'):

                    # Find the layout directory and check if there is a layout
                    # for the cell there.

                    areaproc = subprocess.Popen(['/ef/apps/bin/magic',
				'-dnull', '-noconsole', layout_path + '/' + ipname + '.mag'],
				stdin = subprocess.PIPE, stdout = subprocess.PIPE,
				cwd = layout_path, universal_newlines = True)
                    areaproc.stdin.write("drc on\n")
                    areaproc.stdin.write("select top cell\n")
                    areaproc.stdin.write("drc check\n")
                    areaproc.stdin.write("drc catchup\n")
                    areaproc.stdin.write("set dcount [drc list count total]\n")
                    areaproc.stdin.write("puts stdout \"drc = $dcount\"\n")
                    outlines = areaproc.communicate()[0]
                    magrex = re.compile('drc[ \t]+=[ \t]+([0-9.]+)[ \t]*$')
                    for line in outlines.splitlines():
                        # Diagnostic
                        print(line)
                        lmatch = magrex.match(line)
                        if lmatch:
                            drccount = int(lmatch.group(1))
                            maxrec = param['max']
                            maxrec['value'] = str(drccount)
                            if drccount > 0:
                                maxrec['score'] = 'fail'
                            else:
                                maxrec['score'] = 'pass'

        # Check on LVS from comp.out file (must be more recent than both netlists)
        elif cond == 'LVS_errors':
            ipname = dsheet['ip-name']
            foundry = dsheet['foundry']
            node = dsheet['node']
            # Hack---node XH035 should have been specified as EFXH035A; allow
            # the original one for backwards compatibility.
            if node == 'XH035':
                node = 'EFXH035A'

            # To do even a precheck, the layout path must exist and must be populated
            # with the .magicrc file.
            if not os.path.exists(layout_path):
                os.makedirs(layout_path)
            if not os.path.exists(layout_path + '/.magicrc'):
                pdkdir = '/ef/tech/' + foundry + '/' + node + '/libs.tech/magic/current'
                if os.path.exists(pdkdir + '/' + node + '.magicrc'):
                    shutil.copy(pdkdir + '/' + node + '.magicrc', layout_path + '/.magicrc')

            # Netlists should have been generated by cace_gensim.py
            has_layout_nl = os.path.exists(netlist_path + '/lvs/' + ipname + '.spi')
            has_schem_nl = os.path.exists(netlist_path + '/' + ipname + '.spi')
            has_vlog_nl = os.path.exists(root_path + '/verilog/' + ipname + '.v')
            has_stub_nl = os.path.exists(netlist_path + '/stub/' + ipname + '.spi')
            if has_layout_nl and has_stub_nl and not netlist_source == 'schematic':
                failures = run_and_analyze_lvs(dsheet)
            elif has_layout_nl and has_vlog_nl and not netlist_source == 'schematic':
                failures = run_and_analyze_lvs(dsheet)
            elif netlist_path and has_schem_nl:
                if not has_layout_nl or not has_stub_nl:
                    if not has_layout_nl:
                        print("Did not find layout LVS netlist " + netlist_path + '/lvs/' + ipname + '.spi')
                    if not has_stub_nl:
                        print("Did not find schematic LVS netlist " + netlist_path + '/' + ipname + '.spi')
                print("Running layout device pre-check.")
                if localmode == True:
                    if keepmode == True:
                        precheck_opts = ['-log', '-debug']
                    else:
                        precheck_opts = ['-log']
                    print('/ef/efabless/bin/layout_precheck.py ' + netlist_path + '/' + ipname + '.spi ' + node.lower() + ' ' + ' '.join(precheck_opts))
                    chkproc = subprocess.Popen(['/ef/efabless/bin/layout_precheck.py',
				netlist_path + '/' + ipname + '.spi', node.lower(), *precheck_opts],
				stdout=subprocess.PIPE,
				cwd = layout_path, universal_newlines = True)
                else:
                    chkproc = subprocess.Popen(['/ef/efabless/bin/layout_precheck.py',
				netlist_path + '/' + ipname + '.spi', node.lower()],
				stdout=subprocess.PIPE,
				cwd = layout_path, universal_newlines = True)
                outlines = chkproc.communicate()[0]
                failline = re.compile('.*=[ \t]*([0-9]+)[ \t]*')
                for line in outlines.splitlines():
                    lmatch = failline.match(line)
                    if lmatch:
                        failures = int(lmatch.group(1))
            else:
                failures = -1

            if failures >= 0:
                maxrec = param['max']
                maxrec['value'] = str(failures)
                if failures > int(maxrec['target']):
                    score = 'fail'
                    maxrec['score'] = 'fail'
                else:
                    maxrec['score'] = 'pass'

        # Pop the 'check' record, which has been replaced by the 'value' record.
        param.pop('check')

    # Remove 'project-folder' from document if it exists, as this document
    # is no longer related to an Open Galaxy account.
    if 'project-folder' in datatop:
        datatop.pop('project-folder')

    # Write the annotated JSON file (NOTE:  In the absence of further
    # processing on the CACE side, this file is just getting deleted
    # right after it's made.  But the file appears to be correctly
    # pushed back to the marketplace server, so this can be removed.

    filem = os.path.splitext(inputfile)
    if filem[1]:
        outputfile = filem[0] + '_anno' + filem[1]
    else:
        outputfile = inputfile + '_anno.json'

    with open(outputfile, 'w') as ofile:
        json.dump(datatop, ofile, indent = 4)

    # Create tarball of auxiliary files and send them as well.
    # Note that the files themselves are tarballed, not the directory

    if has_aux_files:
        tar = file_compressor.tar_directory_contents(simfiles_path + '/simulation_files')
        if 'ip-name' in dsheet:
            tarballname = dsheet['ip-name'] + '_result_files.tar.gz'
        else:
            tarballname = 'result_files.tar.gz'

    # In addition to dumping the file locally, also send back to the
    # marketplace, along with the tarball of simulation-generated files.
    if postmode == True:
        send_doc(datatop)
        if has_aux_files:
            send_file(hashname, tar, tarballname)
    else:
        print('Posting to marketplace was disabled by -nopost\n')

    # Clean up by removing simulation directory
    if keepmode == False:
        if localmode == True:
            print('Simulation results retained per -local option\n')
            # If cace_gensim and cace_launch are run locally, keep the results
            # since they won't be posted, but remove all other generated files.
            os.chdir(simfiles_path)
            if os.path.exists('datasheet.json'):
                os.remove('datasheet.json')
            for filename in filessimmed:
                os.remove(filename)
                # Remove any generated ASCII data files
                dfile = os.path.splitext(filename)[0] + '.data'
                if os.path.exists(dfile):
                    os.remove(dfile)
                # Stupid ngspice handling of wrdata command. . .
                dfile = os.path.splitext(filename)[0] + '.data.data'
                if os.path.exists(dfile):
                    os.remove(dfile)
                # Remove any generated raw files
                dfile = os.path.splitext(filename)[0] + '.raw'
                if os.path.exists(dfile):
                    os.remove(dfile)
                # Remove any cosim verilog files
                verilog = os.path.splitext(filename)[0] + '.tv'
                if os.path.exists(verilog):
                    os.remove(verilog)
        else:
            # Remove the entire simulation directory.  To avoid horrible
            # consequences of, e.g., "-rootdir /" insist that the last path
            # component of root_path must be the hashname.
            test = os.path.split(root_path)[0]
            if test != simulation_path:
                print('Error:  Root path is not in the system simulation path.  Not deleting.')
                print('Root path is ' + root_path + '; simulation path is ' + simulation_path)
            else:
                subprocess.run(['rm', '-rf', root_path])
    else:
        print('Simulation directory retained per -keep option\n')

    sys.exit(0)
