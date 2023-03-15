#!/usr/bin/env python3
"""
cace_gensim.py
This is the main part of the automatic characterization engine.  It takes
a JSON simulation template file as input and parses it for information on
how to construct files for the characterization simulations.  Output is
a number of simulation files (for now, at least, in ng-spice format).

Usage:

cace_gensim.py [<root_path>] [<option> ...]

    <root_path> is the root of all the other path names, if the other
    path names are not full paths.  If the other pathnames are all
    full paths, then <root_path> may be omitted.

options:

   -simdir <path>
        is the location where simulation files and data should be placed.
   -datasheetdir <path>
        is the location of the JSON file describing the characterization
   -testbenchdir <path>
        is the location of the netlists for the characterization methods
   -designdir <path>
        is the location of the netlist for the device-under-test
   -layoutdir <path>
        is the location of the layout netlist for the device-under-test
   -datasheet <name>
        is the name of the datasheet JSON file
   -method <name>, ...
        is a list of one or more names of methods to simulate.  If omitted,
        all methods are run for a complete characterization.
   -local
        indicates that cace_gensim is being run locally, not on the CACE
        server, simulation conditions should be output along with results;
        'local' mode implies that results are not posted to the marketplace
        after simulation, and result files are kept.
   -bypass
        acts like remote CACE by running all simulations in one batch and
        posting to the marketplace.  Does not generate status reports.
   -keep
        test mode:  keep all files after simulation
   -plot
        test mode:  generate plot (.png) files locally
   -nopost
        test mode:  do not post results to the marketplace
   -nosim
        test mode:  set up all files for simulation but do not simulate

Quick local run---Use:

    cace_gensim.py <root_dir> -local -method=<method_name>

e.g.,

    cace_gensim.py ~/design/XBG_1V23LC_V01 -local -method=DCVOLTAGE_VBG.1
"""

import os
import sys
import json
import re
import time
import shutil
import signal
import datetime
import subprocess
import faulthandler
from functools import reduce
from spiceunits import spice_unit_convert
from spiceunits import numeric

# Application path (path where this script is located)
apps_path = os.path.realpath(os.path.dirname(__file__))

launchproc = []

def construct_dut_from_path(pname, pathname, pinlist, foundry, node):
    # Read the indicated file, find the .subckt line, and copy out the
    # pin names and DUT name.  Complain if pin names don't match pin names
    # in the datasheet.
    # NOTE:  There may be more than one subcircuit in the netlist, so
    # insist upon the actual DUT (pname)

    subrex = re.compile('^[^\*]*[ \t]*.subckt[ \t]+(.*)$', re.IGNORECASE)
    noderex = re.compile('\*\*\* Layout tech:[ \t]+([^ \t,]+),[ \t]+foundry[ \t]+([^ \t]+)', re.IGNORECASE)
    outline = ""
    dutname = ""
    if not os.path.isfile(pathname):
        print('Error:  No design netlist file ' + pathname + ' found.')
        return outline

    # First pull in all lines of the file and concatenate all continuation
    # lines.
    with open(pathname, 'r') as ifile:
        duttext = ifile.read()

    dutlines = duttext.replace('\n+', ' ').splitlines()
    found = 0
    for line in dutlines:
        lmatch = noderex.match(line)
        if lmatch:
            nlnode = lmatch.group(1)
            nlfoundry = lmatch.group(2)
            if nlfoundry != foundry:
                print('Error:  Foundry is ' + foundry + ' in spec sheet, ' + nlfoundry + ' in netlist.')
            if nlnode != node:
                print('Error:  Node is ' + node + ' in spec sheet, ' + nlnode + ' in netlist.')

        lmatch = subrex.match(line)
        if lmatch:
            rest = lmatch.group(1) 
            tokens = rest.split()
            dutname = tokens[0]
            if dutname == pname:
                outline = outline + 'X' + dutname + ' '
                for pin in tokens[1:]:
                    upin = pin.upper()
                    try:
                        pinmatch = next(item for item in pinlist if item['name'].upper() == upin)
                    except StopIteration:
                        # Maybe this is not the DUT?
                        found = 0
                        # Try the next line (to be done)
                        break
                    else:
                        outline = outline + pin + ' '
                        found += 1
                break

    if found == 0 and dutname == "":
        print('File ' + pathname + ' does not contain any subcircuits!')
        raise SyntaxError('File ' + pathname + ' does not contain any subcircuits!')
    elif found == 0:
        if dutname != pname: 
            print('File ' + pathname + ' does not have a subcircuit named ' + pname + '!')
            raise SyntaxError('File ' + pathname + ' does not have a subcircuit named ' + pname + '!')
        else:
            print('Pins in schematic: ' + str(tokens[1:]))
            print('Pins in datasheet: ', end='')
            for pin in pinlist:
                print(pin['name'] + ' ', end='')
            print('')
            print('File ' + pathname + ' subcircuit ' + pname + ' does not have expected pins!')
            raise SyntaxError('File ' + pathname + ' subcircuit ' + pname + ' does not have expected pins!')
    elif found != len(pinlist):
        print('File ' + pathname + ' does not contain the project DUT ' + pname)
        print('or not all pins of the DUT were found.')
        print('Pinlist is : ', end='')
        for pinrec in pinlist:
            print(pinrec['name'] + ' ', end='')
        print('')
         
        print('Length of pinlist is ' + str(len(pinlist)))
        print('Number of pins found in subcircuit call is ' + str(found))
        raise SyntaxError('File ' + pathname + ' does not contain the project DUT!')
    else:
        outline = outline + dutname + '\n'
    return outline

conditiontypes = {
	"VOLTAGE":     1,
	"DIGITAL":     2,
	"CURRENT":     3,
	"RISETIME":    4,
	"FALLTIME":    5,
	"RESISTANCE":  6,
	"CAPACITANCE": 7,
	"TEMPERATURE": 8,
	"FREQUENCY":   9,
	"CORNER":      10,
	"SIGMA":       11,
	"ITERATIONS":  12,
	"TIME":	       13
}

# floating-point numeric sequence generators, to be used with condition generator

def linseq(condition, unit, start, stop, step):
    a = numeric(start)
    e = numeric(stop)
    s = numeric(step)
    while (a < e + s):
        if (a > e):
            yield (condition, unit, stop)
        else:
            yield (condition, unit, str(a))
        a = a + s

def logseq(condition, unit, start, stop, step):
    a = numeric(start)
    e = numeric(stop)
    s = numeric(step)
    while (a < e * s):
        if (a > e):
            yield (condition, unit, stop)
        else:
            yield (condition, unit, str(a))
        a = a * s
    
# binary (integer) numeric sequence generators, to be used with condition generator

def bindigits(n, bits):
    s = bin(n & int("1" * bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)

def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def bcount(condition, unit, start, stop, step):
    blen = len(start)
    a = eval('0b' + start)
    e = eval('0b' + stop)
    if a > e:
        a = twos_comp(a, blen)
        e = twos_comp(e, blen)
    s = int(step)
    while (a < e + s):
        if (a > e):
            bstr = bindigits(e, blen)
        else:
            bstr = bindigits(a, blen)
        yield (condition, unit, bstr)
        a = a + s

def bshift(condition, unit, start, stop, step):
    a = eval('0b' + start)
    e = eval('0b' + stop)
    if a > e:
        a = twos_comp(a, blen)
        e = twos_comp(e, blen)
    s = int(step)
    while (a < e * s):
        if (a > e):
            bstr = bindigits(e, blen)
        else:
            bstr = bindigits(a, blen)
        yield (condition, unit, bstr)
        a = a * s
    
# define a generator for conditions.  Given a condition (dictionary),
# return (as a yield) each specified condition as a
# 3-tuple (condition_type, value, unit)

def condition_gen(cond):
    lcond = cond['condition']
    if "unit" in cond:
        unit = cond['unit']
    else:
        unit = ''

    if "enum" in cond:
        for i in cond["enum"]:
            yield(lcond, unit, i)
    elif "min" in cond and "max" in cond and "linstep" in cond:
        if unit == "'b" or lcond.split(':', 1)[0] == 'DIGITAL':
            yield from bcount(lcond, unit, cond["min"], cond["max"], cond["linstep"])
        else:
            yield from linseq(lcond, unit, cond["min"], cond["max"], cond["linstep"])
    elif "min" in cond and "max" in cond and "logstep" in cond:
        if unit == "'b" or lcond.split(':', 1)[0] == 'DIGITAL':
            yield from bshift(lcond, unit, cond["min"], cond["max"], cond["logstep"])
        else:
            yield from logseq(lcond, unit, cond["min"], cond["max"], cond["logstep"])
    elif "min" in cond and "max" in cond and "typ" in cond:
        yield(lcond, unit, cond["min"])
        yield(lcond, unit, cond["typ"])
        yield(lcond, unit, cond["max"])
    elif "min" in cond and "max" in cond:
        yield(lcond, unit, cond["min"])
        yield(lcond, unit, cond["max"])
    elif "min" in cond and "typ" in cond:
        yield(lcond, unit, cond["min"])
        yield(lcond, unit, cond["typ"])
    elif "max" in cond and "typ" in cond:
        yield(lcond, unit, cond["typ"])
        yield(lcond, unit, cond["max"])
    elif "min" in cond:
        yield(lcond, unit, cond["min"])
    elif "max" in cond:
        yield(lcond, unit, cond["max"])
    elif "typ" in cond:
        yield(lcond, unit, cond["typ"])

# Find the maximum time to run a simulation.  This is the maximum of:
# (1) maximum value, if method is RISETIME or FALLTIME, and (2) maximum
# RISETIME or FALLTIME of any condition.
#
# "lcondlist" is the list of local conditions extended by the list of
# all global conditions that are not overridden by local values.
#
# NOTE:  This list is limited to rise and fall time values, as they are
# the only time constraints known to cace_gensim at this time.  This list
# will be extended as more simulation methods are added.

def findmaxtime(param, lcondlist):
    maxtime = 0.0
    try:
       simunit = param['unit']
    except KeyError:
       # Plots has no min/max/typ so doesn't require units.
       if 'plot' in param:
           return maxtime

    maxval = 0.0
    found = False
    if 'max' in param:
        prec = param['max']
        if 'target' in prec:
            pmax = prec['target']
            try:
                maxval = numeric(spice_unit_convert([simunit, pmax], 'time'))
                found = True
            except:
                pass
    if not found and 'typ' in param:
        prec = param['typ']
        if 'target' in prec:
            ptyp = prec['target']
            try:
                maxval = numeric(spice_unit_convert([simunit, ptyp], 'time'))
                found = True
            except:
                pass
    if not found and 'min' in param:
        prec = param['min']
        if 'target' in prec:
            pmin = prec['target']
            try:
                maxval = numeric(spice_unit_convert([simunit, pmin], 'time'))
                found = True
            except:
                pass
    if maxval > maxtime:
        maxtime = maxval
    for cond in lcondlist:
        condtype = cond['condition'].split(':', 1)[0]
        # print ('condtype ' + condtype)
        if condtype == 'RISETIME' or condtype == 'FALLTIME':
            condunit = cond['unit']
            maxval = 0.0
            if 'max' in cond:
                maxval = numeric(spice_unit_convert([condunit, cond['max']], 'time'))
            elif 'enum' in cond:
                maxval = numeric(spice_unit_convert([condunit, cond['enum'][-1]], 'time'))
            elif 'typ' in cond:
                maxval = numeric(spice_unit_convert([condunit, cond['typ']], 'time'))
            elif 'min' in cond:
                maxval = numeric(spice_unit_convert([condunit, cond['min']], 'time'))
            if maxval > maxtime:
                maxtime = maxval

    return maxtime

# Picked up from StackOverflow:  Procedure to remove non-unique entries
# in a list of lists (as always, thanks StackOverflow!).

def uniquify(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]

# Insert hints that have been selected in the characterization tool for
# aid in getting stubborn simulations to converge, or to avoid failures
# due to floating nodes, etc.  The hints are somewhat open-ended and can
# be extended as needed.  NOTE:  Hint "method" selects the parameter
# method and is handled outside this routine, which only adds lines to
# the simulation netlist.

def insert_hints(param, ofile):
    if 'hints' in param:
        phints = param['hints']
        if 'reltol' in phints:
            value = phints['reltol']
            ofile.write('.options reltol = ' + value + '\n')
        if 'rshunt' in phints:
            value = phints['rshunt']
            ofile.write('.options rshunt = ' + value + '\n')
        if 'itl1' in phints:
            value = phints['itl1']
            ofile.write('.options itl1 = ' + value + '\n')
        if 'nodeset' in phints:
            value = phints['nodeset']
            # replace '/' in nodeset with '|' to match character replacement done
            # on the output of magic.
            ofile.write('.nodeset ' + value.replace('/', '|') + '\n')
        if 'include' in phints:
            value = phints['include']
            ofile.write('.include ' + value + '\n')

# Replace the substitution token ${INCLUDE_DUT} with the contents of the DUT subcircuit
# netlist file.  "functional" is a list of IP block names that are to be searched for in
# .include lines in the netlist and replaced with functional view equivalents (if such
# exist).

def inline_dut(filename, functional, rootpath, ofile):
    comtrex = re.compile(r'^\*') # SPICE comment
    inclrex = re.compile(r'[ \t]*\.include[ \t]+["\']?([^"\' \t]+)["\']?', re.IGNORECASE) # SPICE include statement
    braktrex = re.compile(r'([^ \t]+)\[([^ \t])\]', re.IGNORECASE)  # Node name with brackets
    subcrex = re.compile(r'[ \t]*x([^ \t]+)[ \t]+(.*)$', re.IGNORECASE) # SPICE subcircuit line
    librex = re.compile(r'(.*)__(.*)', re.IGNORECASE)
    endrex = re.compile(r'[ \t]*\.end[ \t]*', re.IGNORECASE)
    endsrex = re.compile(r'[ \t]*\.ends[ \t]*', re.IGNORECASE)
    # IP names in the ridiculously complicated form
    # <user_path>/design/ip/<proj_name>/<version>/<spice-type>/<proj_name>/<proj_netlist>
    ippathrex = re.compile(r'(.+)/design/ip/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/ \t]+)')
    locpathrex = re.compile(r'(.+)/design/([^/]+)/spi/([^/]+)/([^/ \t]+)')
    # This form does not appear on servers but is used if an IP block is being prepared locally.
    altpathrex = re.compile(r'(.+)/design/([^/]+)/([^/]+)/([^/]+)/([^/ \t]+)')
    # Local IP names in the form
    # <user_path>/design/<project>/spi/<spice-type>/<proj_netlist>

    # To be completed
    with open(filename, 'r') as ifile:
        nettext = ifile.read()

    netlines = nettext.replace('\n+', ' ').splitlines()
    for line in netlines:
        subsline = line
        cmatch = comtrex.match(line)
        if cmatch:
            print(line, file=ofile)
            continue
        # Check for ".end" which should be removed (but not ".ends", which must remain)
        ematch = endrex.match(line)
        if ematch:
            smatch = endsrex.match(line)
            if not smatch:
                continue
        imatch = inclrex.match(line)
        if imatch:
            incpath = imatch.group(1)
            # Substitution behavior is complicated due to the difference between netlist
            # files from schematic capture vs. layout and read-only vs. read-write IP.
            incroot = os.path.split(incpath)[1]
            incname = os.path.splitext(incroot)[0]
            lmatch = librex.match(incname)
            if lmatch:
                ipname = lmatch.group(2)
            else:
                ipname = incname
            if ipname.upper() in functional:
                # Search for functional view (depends on if this is a read-only IP or 
                # read-write local subcircuit)
                funcpath = None
                ippath = ippathrex.match(incpath)
                if ippath:
                    userpath = ippath.group(1)
                    ipname2 = ippath.group(2)
                    ipversion = ippath.group(3)
                    spitype = ippath.group(4)
                    ipname3 = ippath.group(5)
                    ipnetlist = ippath.group(6)
                    funcpath = userpath + '/design/ip/' + ipname2 + '/' + ipversion + '/spice-func/' + ipname + '.spice'
                else:
                    locpath = locpathrex.match(incpath)
                    if locpath:
                        userpath = locpath.group(1)
                        ipname2 = locpath.group(2)
                        spitype = locpath.group(3)
                        ipnetlist = locpath.group(4)
                        funcpath = userpath + '/design/' + ipname2 + '/spi/func/' + ipname + '.spice' 
                    else:
                        altpath = altpathrex.match(incpath)
                        if altpath:
                            userpath = altpath.group(1)
                            ipname2 = altpath.group(2)
                            spitype = altpath.group(3)
                            ipname3 = altpath.group(4)
                            ipnetlist = altpath.group(5)
                            funcpath = userpath + '/design/' + ipname2 + '/spi/func/' + ipname + '.spice' 
                        
                funcpath = os.path.expanduser(funcpath)
                if funcpath and os.path.exists(funcpath):
                    print('Subsituting functional view for IP block ' + ipname)
                    print('Original netlist is ' + incpath)
                    print('Functional netlist is ' + funcpath)
                    subsline = '.include ' + funcpath
                elif funcpath:
                    print('Original netlist is ' + incpath)
                    print('Functional view specified but no functional view found.')
                    print('Tried looking for ' + funcpath)
                    print('Retaining original view.')
                else:
                    print('Original netlist is ' + incpath)
                    print('Cannot make sense of netlist path to find functional view.')

        # If include file name is in <lib>__<cell> format (from electric) and the
        # functional view is not, then find the subcircuit call and replace the
        # subcircuit name.  At least at the moment, the vice versa case does not
        # happen.
        smatch = subcrex.match(line)
        if smatch:
            subinst = smatch.group(1)
            tokens = smatch.group(2).split()
            # Need to test for parameters passed to subcircuit.  The actual subcircuit
            # name occurs before any parameters.
            params = []
            pins = []
            for token in tokens:
                if '=' in token:
                    params.append(token)
                else:
                    pins.append(token)

            subname = pins[-1]
            pins = pins[0:-1]
            lmatch = librex.match(subname)
            if lmatch:
                testname = lmatch.group(1)
                if testname.upper() in functional:
                    subsline = 'X' + subinst + ' ' + ' '.join(pins) + ' ' + testname + ' ' + ' '.join(params)

        # Remove any array brackets from node names in the top-level subcircuit, because they
        # interfere with the array notation used by XSPICE which may be present in functional
        # views (replace bracket characters with underscores).
        # subsline = subsline.replace('[', '_').replace(']', '_')
        #
        # Do this *only* when there are no spaces inside the brackets, or else any XSPICE
        # primitives in the netlist containing arrays will get messed up.
        subsline = braktrex.sub(r'\1_\2_', subsline)

        ofile.write(subsline + '\n')

    ofile.write('\n')

# Define how to write a simulation file by making substitutions into a
# template schematic.

def substitute(filename, fileinfo, template, simvals, maxtime, schemline,
		localmode, param):
    """Simulation derived by substitution into template schematic"""

    # Regular expressions
    varex = re.compile(r'(\$\{[^ \}\t]+\})')		# variable name ${name}
    defaultex = re.compile(r'\$\{([^=]+)=([^=\}]+)\}')	# name in ${name=default} format
    condpinex = re.compile(r'\$\{([^:]+):([^:\}]+)\}')	# name in ${cond:pin} format
    condex = re.compile(r'\$\{([^\}]+)\}')		# name in ${cond} format
    sweepex = re.compile(r'\$\{([^\}]+):SWEEP([^\}]+)\}') # name in ${cond:[pin:]sweep} format
    pinex = re.compile(r'PIN:([^:]+):([^:]+)')		# name in ${PIN:pin_name:net_name} format
    funcrex = re.compile(r'FUNCTIONAL:([^:]+)')		# name in ${FUNCTIONAL:ip_name} format
    colonsepex = re.compile(r'^([^:]+):([^:]+)$')	# a:b (colon-separated values)
    vectrex = re.compile(r'([^\[]+)\[([0-9]+)\]')       # pin name is a vector signal
    vect2rex = re.compile(r'([^<]+)<([0-9]+)>')         # pin name is a vector signal (alternate style)
    vect3rex = re.compile(r'([a-zA-Z][^0-9]*)([0-9]+)') # pin name is a vector signal (alternate style)
    libdirrex = re.compile(r'.lib[ \t]+(.*)[ \t]+')     # pick up library name from .lib
    vinclrex = re.compile(r'[ \t]*`include[ \t]+"([^"]+)"')	# verilog include statement

    # Information about the DUT
    simfilepath = fileinfo['simulation-path']
    schempath = fileinfo['design-netlist-path']
    schemname = fileinfo['design-netlist-name']
    testbenchpath = fileinfo['testbench-netlist-path']
    rootpath = fileinfo['root-path']
    schempins = schemline.upper().split()[1:-1]
    simpins = [None] * len(schempins)

    suffix = os.path.splitext(template)[1]
    functional = []

    # Read ifile into a list
    # Concatenate any continuation lines
    with open(template, 'r') as ifile:
        simtext = ifile.read()

    simlines = simtext.replace('\n+', ' ').splitlines()

    # Make initial pass over contents of template file, looking for SWEEP
    # entries, and collapse simvals accordingly.

    sweeps = []
    for line in simlines:
        sublist = sweepex.findall(line)
        for pattern in sublist:
            condition = pattern[0]
            try:
                entry = next(item for item in sweeps if item['condition'] == condition)
            except (StopIteration, KeyError):
                print("Did not find condition " + condition + " in sweeps.")
                print("Pattern = " + str(pattern))
                print("Sublist = " + str(sublist))
                print("Sweeps = " + str(sweeps))
                entry = {'condition':condition}
                sweeps.append(entry)

                # Find each entry in simvals with the same condition.
                # Record the minimum, maximum, and step for substitution, at the same
                # time removing that item from the entry.
                lvals = []
                units = ''
                for simval in simvals:
                    try:
                        simrec = next(item for item in simval if item[0] == condition)
                    except StopIteration:
                        print('No condition = ' + condition + ' in record:\n')
                        ptext = str(simval) + '\n'
                        sys.stdout.buffer.write(ptext.encode('utf-8'))
                    else:
                        units = simrec[1]
                        lvals.append(numeric(simrec[2]))
                        simval.remove(simrec)

                # Remove non-unique entries from lvals
                lvals = list(set(lvals))

                # Now parse lvals for minimum/maximum
                entry['unit'] = units
                minval = min(lvals)
                maxval = max(lvals)
                entry['START'] = str(minval)
                entry['END'] = str(maxval)
                numvals = len(lvals)
                if numvals > 1:
                    entry['STEPS'] = str(numvals)
                    entry['STEP'] = str((maxval - minval) / (numvals - 1))
                else:
                    entry['STEPS'] = "1"
                    entry['STEP'] = str(minval)

    # Remove non-unique entries from simvals
    simvals = uniquify(simvals)

    simnum = 0
    testbenches = []
    for simval in simvals:
        # Create the file
        simnum += 1
        simfilename = simfilepath + '/' + filename + '_' + str(simnum) + suffix
        controlblock = False
        with open(simfilename, 'w') as ofile:
            for line in simlines:

                # Check if the parser is in the ngspice control block section
                if '.control' in line:
                    controlblock = True
                elif '.endc' in line:
                    controlblock = False
                elif controlblock == True:
                    ofile.write('set sqrnoise\n')
                    # This will need to be more nuanced if controlblock is used
                    # to do more than just insert the noise sim hack.
                    controlblock = False

                # This will be replaced
                subsline = line

                # Find all variables to substitute
                for patmatch in varex.finditer(line):
                    pattern = patmatch.group(1)
                    # If variable is in ${x=y} format, it declares a default value
                    # Remove the =y default part and keep it for later if needed.
                    defmatch = defaultex.match(pattern)
                    if defmatch:
                        default = defmatch.group(2)
                        vpattern = '${' + defmatch.group(1) + '}'
                    else:
                        default = []
                        vpattern = pattern

                    repl = []
                    no_repl_ok = False
                    vtype = -1
                    sweeprec = sweepex.match(vpattern)
                    if sweeprec:
                        sweeptype = sweeprec.group(2)
                        condition = sweeprec.group(1)

                        entry = next(item for item in sweeps if item['condition'] == condition)
                        uval = spice_unit_convert((entry['unit'], entry[sweeptype]))
                        repl = str(uval)
                    else:
                        cond = condex.match(vpattern)
                        if cond:
                            condition = cond.group(1)

                            # Check if the condition contains a pin vector
                            lmatch = vectrex.match(condition)
                            if lmatch:
                                pinidx = int(lmatch.group(2))
                                vcondition = lmatch.group(1)
                                vtype = 0
                            else:
                                lmatch = vect2rex.match(condition)
                                if lmatch:
                                    pinidx = int(lmatch.group(2))
                                    vcondition = lmatch.group(1)
                                    vtype = 1
                                else:
                                    lmatch = vect3rex.match(condition)
                                    if lmatch:
                                        pinidx = int(lmatch.group(2))
                                        vcondition = lmatch.group(1)
                                        vtype = 3
                                
                            try:
                                 entry = next((item for item in simval if item[0] == condition))
                            except (StopIteration, KeyError):
                                # check against known names (to-do: change if block to array of procs)
                                if condition == 'N':
                                    repl = str(simnum)
                                elif condition == 'MAXTIME':
                                    repl = str(maxtime)
                                elif condition == 'STEPTIME':
                                    repl = str(maxtime / 100)
                                elif condition == 'DUT_PATH':
                                    repl = schempath + '/' + schemname + '\n'
                                    # DUT_PATH is required and is a good spot to
                                    # insert hints (but deprecated in fafor of INCLUDE_DUT)
                                    insert_hints(param, ofile)
                                elif condition == 'INCLUDE_DUT':
                                    if len(functional) == 0:
                                        repl = '.include ' + schempath + '/' + schemname + '\n'
                                    else:
                                        inline_dut(schempath + '/' + schemname, functional, rootpath, ofile)
                                        repl = '** End of in-line DUT subcircuit'
                                    insert_hints(param, ofile)
                                elif condition == 'DUT_CALL':
                                    repl = schemline
                                elif condition == 'DUT_NAME':
                                    # This verifies pin list of schematic vs. the netlist.
                                    repl = schemline.split()[-1]
                                elif condition == 'FILENAME':
                                    repl = filename
                                elif condition == 'RANDOM':
                                    repl = str(int(time.time() * 1000) & 0x7fffffff)
                                # Stack math operators.  Perform specified math
                                # operation on the last two values and replace.
                                #
                                # Note that ngspice is finicky about space around "=" so
                                # handle this in a way that keeps ngspice happy.
                                elif condition == '+':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-2]
                                    ntok.append(str(numeric(ltok[-2]) + numeric(ltok[-1])))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                elif condition == '-':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-2]
                                    ntok.append(str(numeric(ltok[-2]) - numeric(ltok[-1])))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                elif condition == '*':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-2]
                                    ntok.append(str(numeric(ltok[-2]) * numeric(ltok[-1])))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                elif condition == '/':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-2]
                                    ntok.append(str(numeric(ltok[-2]) / numeric(ltok[-1])))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                elif condition == 'MAX':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-2]
                                    ntok.append(str(max(numeric(ltok[-2]), numeric(ltok[-1]))))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                elif condition == 'MIN':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-2]
                                    ntok.append(str(min(numeric(ltok[-2]), numeric(ltok[-1]))))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                # 'NEG' acts on only the previous value in the string.
                                elif condition == 'NEG':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-1]
                                    ntok.append(str(-numeric(ltok[-1])))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                # 'INT' also acts on only the previous value in the string.
                                elif condition == 'INT':
                                    smatch = varex.search(subsline)
                                    watchend = smatch.start()
                                    ltok = subsline[0:watchend].replace('=', ' = ').split()
                                    ntok = ltok[:-1]
                                    ntok.append(str(int(ltok[-1])))
                                    subsline = ' '.join(ntok).replace(' = ', '=') + line[patmatch.end():]
                                    repl = ''
                                    no_repl_ok = True
                                elif condition.find('PIN:') == 0:
                                    # Parse for ${PIN:<pin_name>:<net_name>}
                                    # Replace <pin_name> with index of pin from DUT subcircuit
                                    pinrec = pinex.match(condition)
                                    pinname = pinrec.group(1).upper()
                                    netname = pinrec.group(2).upper()
                                    try:
                                       idx = schempins.index(pinname)
                                    except ValueError:
                                       repl = netname
                                    else:
                                       repl = '${PIN}'
                                       simpins[idx] = netname
                                elif condition.find('FUNCTIONAL:') == 0:
                                    # Parse for ${FUNCTIONAL:<ip_name>}
                                    # Add <ip_name> to "functional" array.
                                    # 'FUNCTIONAL' declarations must come before 'INCLUDE_DUT' or else
                                    # substitution will not be made.  'INCLUDE_DUT' must be used in place
                                    # of 'DUT_PATH' to get the correct behavior.
                                    funcrec = funcrex.match(condition)
                                    ipname = funcrec.group(1)
                                    functional.append(ipname.upper())
                                    repl = '** Using functional view for ' + ipname
                                else:
                                    if lmatch:
                                        try:
                                            entry = next((item for item in simval if item[0].split('[')[0].split('<')[0] == vcondition))
                                        except:
                                            if vtype == 3:
                                                for entry in simval:
                                                    lmatch = vect3rex.match(entry[0])
                                                    if lmatch:
                                                        if lmatch.group(1) == vcondition:
                                                            vlen = len(entry[2])
                                                            uval = entry[2][(vlen - 1) - pinidx]
                                                            repl = str(uval)
                                                            break
                                            else:
                                                # if no match, subsline remains as-is.
                                                pass
                                        else:
                                            # Handle as vector bit slice (see below)
                                            vlen = len(entry[2])
                                            uval = entry[2][(vlen - 1) - pinidx]
                                            repl = str(uval)
                                    # else if no match, subsline remains as-is.

                            else:
                                if lmatch:
                                    # pull signal at pinidx out of the vector.
                                    # Note: DIGITAL assumes binary value.  May want to
                                    # allow general case of real-valued vectors, which would
                                    # require a spice unit conversion routine without indexing.
                                    vlen = len(entry[2])
                                    uval = entry[2][(vlen - 1) - pinidx]
                                else:
                                    uval = spice_unit_convert(entry[1:])
                                repl = str(uval)

                    if not repl and default:
                        # Use default if no match was found and default was specified
                        repl = default

                    if repl:
                        # Make the variable substitution
                        subsline = subsline.replace(pattern, repl)
                    elif not no_repl_ok:
                        print('Warning: Variable ' + pattern + ' had no substitution')

                # Check if ${PIN} are in line.  If so, order by index and
                # rewrite pins in order
                for i in range(len(simpins)):
                    if '${PIN}' in subsline:
                        if simpins[i]:
                            subsline = subsline.replace('${PIN}', simpins[i], 1)
                        else:
                            print("Error:  simpins is " + str(simpins) + '\n')
                            print("        subsline is " + subsline + '\n')
                            print("        i is " + str(i) + '\n')

                # Check for a verilog include file, and if any is found, copy it
                # to the target simulation directory.  Replace any leading path
                # with the local current working directory '.'.
                vmatch = vinclrex.match(subsline)
                if vmatch:
                    incfile = vmatch.group(1)
                    incroot = os.path.split(incfile)[1]
                    curpath = os.path.split(template)[0]
                    incpath = os.path.abspath(os.path.join(curpath, incfile))
                    shutil.copy(incpath, simfilepath + '/' + incroot)
                    subsline = '   `include "./' + incroot + '"'

                # Write the modified output line (with variable substitutions)
                ofile.write(subsline + '\n')

        # Add information about testbench file and conditions to datasheet JSON,
        # which can be parsed by cace_launch.py.
        testbench = {}
        testbench['filename'] = simfilename
        testbench['prefix'] = filename
        testbench['conditions'] = simval
        testbenches.append(testbench)

    return testbenches

# Define how to write simulation devices

def generate_simfiles(datatop, fileinfo, arguments, methods, localmode):

    # pull out the relevant part, which is "data-sheet"
    dsheet = datatop['data-sheet']

    # grab values held in 'fileinfo'
    testbenchpath = fileinfo['testbench-netlist-path']

    # electrical parameter list comes from "methods" if non-NULL.
    # Otherwise, each entry in 'methods' is checked against the
    # electrical parameters.

    if 'electrical-params' in dsheet:
        eparamlist = dsheet['electrical-params']
    else:
        eparamlist = []
    if 'physical-params' in dsheet:
        pparamlist = dsheet['physical-params']
    else:
        pparamlist = []

    # If specific methods are called out for simulation using option "-method=", then
    # generate the list of electrical parameters for those methods only.

    if methods:
        neweparamlist = []
        newpparamlist = []
        for method in methods:
            # If method is <methodname>.<index>, simulate only the <index>th instance of
            # the method.
            if '.' in method:
                (method, index) = method.split('.')
            else:
                index = []

            if method == 'physical':
                usedmethods = list(item for item in pparamlist if item['condition'] == index)
                if not usedmethods:
                    print('Unknown parameter ' + index + ' requested in options.  Ignoring.\n')
                for used in usedmethods:
                    newpparamlist.append(used)

            else:
                usedmethods = list(item for item in eparamlist if item['method'] == method)
                if not usedmethods:
                    print('Unknown method ' + method + ' requested in options.  Ignoring.\n')
                if index:
                    neweparamlist.append(usedmethods[int(index)])
                else:
                    for used in usedmethods:
                        neweparamlist.append(used)

        if not neweparamlist and not newpparamlist:
            print('Warning:  No valid methods given as options, so no simulations will be done.\n')
        if neweparamlist:
            for param in neweparamlist:
                if 'display' in param:
                    ptext = 'Simulating parameter: ' + param['display'] + ' (' + param['method'] + ')\n'
                else:
                    ptext = 'Simulating method: ' + param['method'] + '\n'
                sys.stdout.buffer.write(ptext.encode('utf-8'))
        eparamlist = neweparamlist
        if newpparamlist:
            for param in newpparamlist:
                if 'display' in param:
                    ptext = 'Checking parameter: ' + param['display'] + ' (' + param['condition'] + ')\n'
                else:
                    ptext = 'Checking parameter: ' + param['condition'] + '\n'
                sys.stdout.buffer.write(ptext.encode('utf-8'))
        pparamlist = newpparamlist

    # Diagnostic
    # print('pparamlist:')
    # for param in pparamlist:
    #     ptext = param['condition'] + '\n'
    #     sys.stdout.buffer.write(ptext.encode('utf-8'))
    # print('eparamlist:')
    # for param in eparamlist:
    #     ptext = param['method'] + '\n'
    #     sys.stdout.buffer.write(ptext.encode('utf-8'))

    # major subcategories of "data-sheet"
    gcondlist = dsheet['global-conditions']

    # Make a copy of the pin list in the datasheet, and expand any vectors.
    pinlist = []
    vectrex = re.compile(r"([^\[]+)\[([0-9]+):([0-9]+)\]")
    vect2rex = re.compile(r"([^<]+)\<([0-9]+):([0-9]+)\>")
    vect3rex = re.compile(r"([^0-9]+)([0-9]+):([0-9]+)")
    for pinrec in dsheet['pins']:
        vmatch = vectrex.match(pinrec['name'])
        if vmatch:
            pinname = vmatch.group(1)
            pinmin = vmatch.group(2)
            pinmax = vmatch.group(3)
            if int(pinmin) > int(pinmax):
                pinmin = vmatch.group(3)
                pinmax = vmatch.group(2)
            for i in range(int(pinmin), int(pinmax) + 1):
                newpinrec = pinrec.copy()
                pinlist.append(newpinrec)
                newpinrec['name'] = pinname + '[' + str(i) + ']'
        else:
            vmatch = vect2rex.match(pinrec['name'])
            if vmatch:
                pinname = vmatch.group(1)
                pinmin = vmatch.group(2)
                pinmax = vmatch.group(3)
                if int(pinmin) > int(pinmax):
                    pinmin = vmatch.group(3)
                    pinmax = vmatch.group(2)
                for i in range(int(pinmin), int(pinmax) + 1):
                    newpinrec = pinrec.copy()
                    pinlist.append(newpinrec)
                    newpinrec['name'] = pinname + '<' + str(i) + '>'
            else:
                vmatch = vect3rex.match(pinrec['name'])
                if vmatch:
                    pinname = vmatch.group(1)
                    pinmin = vmatch.group(2)
                    pinmax = vmatch.group(3)
                    if int(pinmin) > int(pinmax):
                        pinmin = vmatch.group(3)
                        pinmax = vmatch.group(2)
                    for i in range(int(pinmin), int(pinmax) + 1):
                        newpinrec = pinrec.copy()
                        pinlist.append(newpinrec)
                        newpinrec['name'] = pinname + str(i)
                else:
                    pinlist.append(pinrec)

    # Make sure all local conditions define a pin.  Those that are not
    # associated with a pin will have a null string for the pin name.

    for cond in gcondlist:
        # Convert old style (separate condition, pin) to new style
        if 'pin' in cond and cond['pin'] != '':
            if ':' not in cond['condition']:
                cond['condition'] += ':' + cond['pin']
            cond.pop('pin', 0)
        if 'order' not in cond:
            try:
                cond['order'] = conditiontypes[cond['condition']]
            except:
                cond['order'] = 0

    # Find DUT netlist file and capture the subcircuit call line
    schempath = fileinfo['design-netlist-path']
    schemname = fileinfo['design-netlist-name']
    pname = fileinfo['project-name']
    dutpath = schempath + '/' + schemname
    foundry = dsheet['foundry']
    node = dsheet['node']
    try:
        schemline = construct_dut_from_path(pname, dutpath, pinlist, foundry, node)
    except SyntaxError:
        print("Failure to construct a DUT subcircuit.  Does the design have ports?")
        schemline = ''

    if schemline == '':
        # Error finding DUT file.  If only physical parameters are requested, this may
        # not be a failure (e.g., chip top level)
        if len(eparamlist) == 0:
            prescore = 'unknown'
        else:
            prescore = 'fail'
    else:
        prescore = 'pass'

    methodsfound = {}

    # electrical parameter types determine the simulation type.  Simulation
    # types will be broken into individual routines (to be done)

    for param in eparamlist:

        # Break out name, method, and conditions as variables
        simtype = param['method']

        # For methods with ":", the filename is the part before the colon.
        testbench = simtype.split(":")[0]

        # If hint 'method' is applied, append the value to the method name.
        # If no such method exists, flag a warning and revert to the original.

        testbench_orig = None
        if 'hints' in param:
            phints = param['hints']
            if 'method' in phints:
                testbench_orig = testbench
                testbench += phints['method']            

        if testbench == simtype:
            if arguments:
                if simtype not in arguments:
                    continue

            if simtype in methodsfound:
                fnum = methodsfound[simtype]
                fsuffix = '_' + str(fnum)
                methodsfound[simtype] = fnum + 1
            else:
                fsuffix = '_0'
                methodsfound[simtype] = 1
        else:
            if arguments:
                if testbench not in arguments:
                    continue

            if testbench in methodsfound:
                fnum = methodsfound[testbench]
                fsuffix = '_' + str(fnum)
                methodsfound[testbench] = fnum + 1
            else:
                fsuffix = '_0'
                methodsfound[testbench] = 1

        lcondlist = param['conditions']

        # Make sure all local conditions which define a pin are in condition:pin form

        for cond in lcondlist:
            if 'pin' in cond and cond['pin'] != '':
                if not ':' in cond['condition']:
                    cond['condition'] += ':' + cond['pin']
                cond.pop('pin', 0)
            if "order" not in cond:
                if cond["condition"].split(':', 1)[0] in conditiontypes:
                    cond["order"] = conditiontypes[cond["condition"].split(':', 1)[0]]
                else:
                    cond["order"] = 14

        # Append to lcondlist any global conditions that aren't overridden by
        # local values for the electrical parameter's set of conditions.

        grec = []
        for cond in gcondlist:
            try:
                test = next((item for item in lcondlist if item["condition"] == cond["condition"]))
            except StopIteration:
                grec.append(cond)

        lcondlist.extend(grec)	# Note this will permanently alter lcondlist

        # Find the maximum simulation time required by this method
        # Simulations are ordered so that "risetime" and "falltime" simulations
        # on a pin will set the simulation time of any simulation of any other
        # electrical parameter on that same pin.

        maxtime = findmaxtime(param, lcondlist)
        print("maxtime is " + str(maxtime))

        # Sort the list for output conditions, ordering according to 'conditiontypes'.

        list.sort(lcondlist, key=lambda k: k['order'])

        # Find the length of each generator
        cgenlen = []
        for cond in lcondlist:
            cgenlen.append(len(list(condition_gen(cond))))

        # The lengths of all generators multiplied together is the number of
        # simulations to be run
        numsims = reduce(lambda x, y: x * y, cgenlen)
        rlen = [x for x in cgenlen]	# note floor division operator

        # This code repeats each condition as necessary such that the final list
        # (transposed) is a complete set of unique condition combinations.
        cgensim = []
        for i in range(len(rlen)):
            mpre = reduce(lambda x, y: x * y, rlen[0:i], 1)
            mpost = reduce(lambda x, y: x * y, rlen[i + 1:], 1)
            clist = list(condition_gen(lcondlist[i]))
            duplist = [item for item in list(condition_gen(lcondlist[i])) for j in range(mpre)]
            cgensim.append(duplist * mpost)

        # Transpose this list
        simvals = list(map(list, zip(*cgensim)))

        # Generate filename prefix for this electrical parameter
        filename = testbench + fsuffix

        # If methodtype is the name of a schematic netlist, then use
        # it and make substitutions
        # NOTE:  Schematic methods are bundled with the DUT schematic

        template = testbenchpath + '/' + testbench.lower() + '.spice'

        if testbench_orig and not os.path.isfile(template):
            print('Warning:  Alternate testbench ' + testbench + ' cannot be found.')
            print('Reverting to original testbench ' + testbench_orig)
            testbench = testbench_orig
            filename = testbench + fsuffix
            template = testbenchpath + '/' + testbench.lower() + '.spice'

        if os.path.isfile(template):
            param['testbenches'] = substitute(filename, fileinfo, template,
			simvals, maxtime, schemline, localmode, param)

            # For cosimulations, if there is a '.tv' file corresponding to the '.spice' file,
            # then make substitutions as for the .spice file, and place in characterization
            # directory.

            vtemplate = testbenchpath + '/' + testbench.lower() + '.tv'
            if os.path.isfile(vtemplate):
                substitute(filename, fileinfo, vtemplate,
			simvals, maxtime, schemline, localmode, param)

        else:
            print('Error:  No testbench file ' + template + '.')

    for param in pparamlist:
        # Break out name, method, and conditions as variables
        cond = param['condition']
        simtype = 'physical.' + cond

        if arguments:
            if simtype not in arguments:
                continue

        if simtype in methodsfound:
            fnum = methodsfound[simtype]
            fsuffix = '_' + str(fnum)
            methodsfound[simtype] = fnum + 1
        else:
            fsuffix = '_0'
            methodsfound[simtype] = 1

        # Mark parameter as needing checking by cace_launch.
        param['check'] = 'true'

    # Remove "order" keys
    for param in eparamlist:
        lcondlist = param['conditions']
        for cond in lcondlist:
            cond.pop('order', 0)
    gconds = dsheet['global-conditions']
    for cond in gconds:
        cond.pop('order', 0)

    return prescore

def check_layout_out_of_date(spicepath, layoutpath):
    # Check if a netlist (spicepath) is out-of-date relative to the layouts
    # (layoutpath).  Need to read the netlist and check all of the subcells.
    need_capture = False
    if not os.path.isfile(spicepath):
        need_capture = True
    elif not os.path.isfile(layoutpath):
        need_capture = True
    else:
        spi_statbuf = os.stat(spicepath)
        lay_statbuf = os.stat(layoutpath)
        if spi_statbuf.st_mtime < lay_statbuf.st_mtime:
            # netlist exists but is out-of-date
            need_capture = True
        else:
            # only found that the top-level-layout is older than the
            # netlist.  Now need to read the netlist, find all subcircuits,
            # and check those dates, too.
            layoutdir = os.path.split(layoutpath)[0]
            subrex = re.compile('^[^\*]*[ \t]*.subckt[ \t]+([^ \t]+).*$', re.IGNORECASE)
            with open(spicepath, 'r') as ifile:
                duttext = ifile.read()
            dutlines = duttext.replace('\n+', ' ').splitlines()
            for line in dutlines:
                lmatch = subrex.match(line)
                if lmatch:
                    subname = lmatch.group(1)
                    sublayout = layoutdir + '/' + subname + '.mag'
                    # subcircuits that cannot be found in the current directory are
                    # assumed to be library components and therefore never out-of-date.
                    if os.path.exists(sublayout):
                        sub_statbuf = os.stat(sublayout)
                        if spi_statbuf.st_mtime < lay_statbuf.st_mtime:
                            # netlist exists but is out-of-date
                            need_capture = True
                            break
    return need_capture

def check_schematic_out_of_date(spicepath, schempath):
    # Check if a netlist (spicepath) is out-of-date relative to the schematics
    # (schempath).  Need to read the netlist and check all of the subcells.
    need_capture = False
    if not os.path.isfile(spicepath):
        print('Schematic-captured netlist does not exist.  Need to regenerate.')
        need_capture = True
    elif not os.path.isfile(schempath):
        need_capture = True
    else:
        spi_statbuf = os.stat(spicepath)
        sch_statbuf = os.stat(schempath)
        print('DIAGNOSTIC:  Comparing ' + spicepath + ' to ' + schempath)
        if spi_statbuf.st_mtime < sch_statbuf.st_mtime:
            # netlist exists but is out-of-date
            print('Netlist is older than top-level schematic')
            need_capture = True
        else:
            print('Netlist is newer than top-level schematic, but must check subcircuits')
            # only found that the top-level-schematic is older than the
            # netlist.  Now need to read the netlist, find all subcircuits,
            # and check those dates, too.
            schemdir = os.path.split(schempath)[0]
            schrex = re.compile('\*\*[ \t]*sch_path:[ \t]*([^ \t\n]+)', re.IGNORECASE)
            subrex = re.compile('^[^\*]*[ \t]*.subckt[ \t]+([^ \t]+).*$', re.IGNORECASE)
            with open(spicepath, 'r') as ifile:
                duttext = ifile.read()

            dutlines = duttext.replace('\n+', ' ').splitlines()
            for line in dutlines:
                # xschem helpfully adds a "sch_path" comment line for every subcircuit
                # coming from a separate schematic file.

                lmatch = schrex.match(line)
                if lmatch:
                    subschem = lmatch.group(1)
                    subfile = os.path.split(subschem)[1]
                    subname = os.path.splitext(subfile)[0]

                    # subcircuits that cannot be found in the current directory are
                    # assumed to be library components or read-only IP components and
                    # therefore never out-of-date.
                    if os.path.exists(subschem):
                        sub_statbuf = os.stat(subschem)
                        if spi_statbuf.st_mtime < sch_statbuf.st_mtime:
                            # netlist exists but is out-of-date
                            print('Netlist is older than subcircuit schematic ' + subname)
                            need_capture = True
                            break
    return need_capture

def printwarn(output):
    # Check output for warning or error
    if not output:
        return 0

    warnrex = re.compile('.*warning', re.IGNORECASE)
    errrex = re.compile('.*error', re.IGNORECASE)

    errors = 0
    outlines = output.splitlines()
    for line in outlines:
        try:
            wmatch = warnrex.match(line)
        except TypeError:
            line = line.decode('utf-8')
            wmatch = warnrex.match(line)
        ematch = errrex.match(line)
        if ematch:
            errors += 1
        if ematch or wmatch:
            print(line)
    return errors

def layout_netlist_includes(pexnetlist, dspath):
    # Magic does not generate netlist output for LEF-like views unless
    # the option "blackbox on" is passed to ext2spice, in which case it
    # generates stub entries.  When generating a PEX view for simulation,
    # these entries need to be generated then replaced with the correct
    # include statement to the ip/ directory.

    comtrex = re.compile(r'^\*') # SPICE comment
    subcrex = re.compile(r'^[ \t]*x([^ \t]+)[ \t]+(.*)$', re.IGNORECASE) # SPICE subcircuit line
    subrex  = re.compile(r'^[ \t]*.subckt[ \t]+([^ \t]+)[ \t]*([^ \t]+.*)', re.IGNORECASE)
    endsrex = re.compile(r'^[ \t]*\.ends[ \t]*', re.IGNORECASE)

    # Also convert commas from [X,Y] arrays to vertical bars as something
    # that can be converted back as necessary.  ngspice treats commas as
    # special characters for some reason.  ngspice also does not correctly
    # handle slash characters in node names (okay as part of the netlist but
    # fails if used in, say, ".nodeset").  Should be okay to replace all '/'
    # because the layout extracted netlist won't have .include or other
    # entries with filename paths.

    # Find project tech path
    if os.path.exists(dspath + '/.config/techdir'):
        techdir = os.path.realpath(dspath + '/.config/techdir')
        maglefdir = techdir + '/libs.ref/maglef'
    else:
        print('Warning:  Project ' + dspath + ' does not define a target process!')
        techdir = None
        maglefdir = None

    with open(pexnetlist, 'r') as ifile:
        spitext = ifile.read()

    # Find project info file (introduced with FFS, 2/2019.  Does not exist in earlier
    # projects)

    depends = {}
    ipname = ''
    if os.path.exists(dspath + '/.config/info'):
       with open(dspath + '/.config/info', 'r') as ifile:
           infolines = ifile.read().splitlines
           deprec = False
           for line in infolines:
               if 'dependencies:' in line:
                   deprec = True
               if deprec:
                   if 'version' in line:
                       version = line.split()[1].strip("'")
                       if ipname != '':
                           depends[ipname] = version
                           ipname = ''
                       else:
                           print('Error:  Badly formed info file in .config', file=sys.stderr)
                   else:
                       ipname = line.strip(':')

    spilines = spitext.replace('\n+', ' ').replace(',', '|').replace('/','|').splitlines()

    newspilines = []
    extended_names = []
    pinsorts = {}
    inbox = False
    for line in spilines:
        cmatch = comtrex.match(line)
        smatch = subrex.match(line)
        xmatch = subcrex.match(line)
        if 'Black-box' in line:
            inbox = True
        elif not inbox:
            if xmatch:
                # Pull subcircuit name from an 'X' component and see if it matches any of the
                # names that were rewritten in Electric <library>__<cell> style.  If so, replace
                # the subcircuit name with the modified name while preserving the rest of the
                # component line.
                rest = xmatch.group(2).split()
                r1 = list(i for i in rest if '=' not in i)
                r2 = list(i for i in rest if '=' in i)
                subname = r1[-1]
                r1 = r1[0:-1]

                # Re-sort the pins if needed
                if subname in pinsorts:
                    r1 = [r1[i] for i in pinsorts[subname]]

                if subname.upper() in extended_names:
                    newsubname = subname + '__' + subname
                    newspilines.append('X' + xmatch.group(1) + ' ' + ' '.join(r1) + ' ' + newsubname + ' ' + ' '.join(r2))
                else:
                    newspilines.append(line)
            else:
                newspilines.append(line)
        elif cmatch:
            newspilines.append(line)
        elif smatch:
            subname = smatch.group(1)
            pinlist = smatch.group(2).split()
            print("Parsing black-box subcircuit " + subname)
            ippath = '~/design/ip/' + subname
            ipfullpath = os.path.expanduser(ippath)
            if os.path.exists(ipfullpath):
                # Version control:  Use the versions specified in the .config/info
                # version list.  If it does not exist (legacy behavior), then use the
                # method outlined below (finds highest version number available).
                if subname in depends:
                    useversion = str(depends[subname])
                else:
                    versions = os.listdir(ipfullpath)
                    vf = list(float(i) for i in versions)
                    vi = vf.index(max(vf))
                    useversion = versions[vi]

                versionpath = ipfullpath + '/' + useversion

                # First to do:  Check for /spice/lvs entry (which is readable), and
                # check if pin order is correct.  Flag a warning if it is not, and
                # save the pin order in a record so that all X records can be pin
                # sorted correctly.

                if os.path.exists(versionpath + '/spice/lvs'):
                    lvspath = versionpath + '/spice/lvs/' + subname + '.spice'
                    # More spice file reading!  This should be quick, as these files have
                    # only a single empty subcircuit in them.
                    found = False
                    with open(lvspath, 'r') as sfile:
                        stubtext = sfile.read()
                        stublines = stubtext.replace('\n+', ' ').replace(',', '|').splitlines()
                        for line in stublines:
                            smatch = subrex.match(line)
                            if smatch:
                                found = True
                                stubname = smatch.group(1) 
                                stublist = smatch.group(2).split()
                                if stubname != subname + '__' + subname:
                                    print('Error:  Looking for subcircuit ' + subname + '__' + subname + ' in file ' + lvspath + ' but found subcircuit ' + stubname + ' instead!')
                                    print("This simulation probably isn't going to go well.")
                                else:
                                    needsort = False
                                    for stubpin, subpin in zip(stublist, pinlist):
                                        if stubpin.upper() != subpin.upper():
                                            print('Warning: pin mismatch between layout and schematic stub header on subcircuit ' + subname)
                                            print('Will sort layout netlist to match.')
                                            print('Correct pin order is: ' + smatch.group(2))
                                            needsort = True
                                            break
                                    if needsort:
                                        pinorder = [i[0] for i in sorted(enumerate(pinlist), key = lambda x:stublist.index(x[1]))]
                                        pinsorts[subname] = pinorder
                                break
                    if not found:
                        print('Error:  Cannot find subcircuit in IP spice-stub entry.') 
                else:
                    print('Warning: IP has no spice-stub entry, cannot verify pin order.')

                if os.path.exists(versionpath + '/spice/rcx'):
                    # This path is restricted and can only be seen by ngspice, which is privileged
                    # to read it.  So we can only assume that it matches the spice/stub entry.
                    # NOTE (10/16/2018): Use unexpanded tilde expression in file.
                    # rcxpath = versionpath + '/spice/rcx/' + subname + '/' + subname + '__' + subname + '.spice'
                    rcxpath = ippath + '/' + useversion + '/spice/rcx/' + subname + '/' + subname + '__' + subname + '.spice'
                    newspilines.append('* Black-box entry replaced by path to RCX netlist')
                    newspilines.append('.include ' + rcxpath)
                    extended_names.append(subname.upper())
                elif os.path.exists(ipfullpath + '/' + useversion + '/spice'):
                    # In a pinch, if there is no spice/rcx, try plain spice
                    # NOTE (10/16/2018): Use unexpanded tilde expression in file.
                    # spicepath = versionpath + '/spice/' + subname + '.spice'
                    spicepath = ippath + '/' + useversion + '/spice/' + subname + '.spice'
                    newspilines.append('* Black-box entry replaced by path to schematic netlist')
                    newspilines.append('.include ' + spicepath)
                else:
                    # Leave as is, and let it force an error
                    newspilines.append(line)
                    inbox = False
            elif maglefdir:
                # Check tech file paths
                found = False
                maglefsubdirs = os.listdir(maglefdir)
                for techsubdir in maglefsubdirs:
                    if not os.path.isdir(maglefdir + '/' + techsubdir):
                        continue
                    # print('Diagnostic:  looking in ' + str(maglefdir) + ' ' + str(techsubdir))
                    maglefcells = os.listdir(maglefdir + '/' + techsubdir)
                    if subname + '.mag' in maglefcells:
                        # print("Diagnostic: Parsing black-box subcircuit " + subname)
                        # print('from tech path ' + maglefdir + '/' + techsubdir)

                        # Like the IP directory, can't read spi/ so have to assume it's there.
                        # Problem---there is no consistency across PDKs for the naming of
                        # files in spi/!

                        newspilines.append('* Need include to schematic netlist for ' + subname)
                        # However, the CDL file can be used to check pin order
                        cdlpath = techdir + '/libs.ref/' + techsubdir + '/' + techsubdir + '.cdl'
                        if os.path.exists(cdlpath):
                            # More spice file reading!  This should be quick, as these files have
                            # only a empty subcircuits in them.
                            with open(cdlpath, 'r') as sfile:
                                stubtext = sfile.read()
                                stublines = stubtext.replace('\n+', ' ').replace(',', '|').splitlines()
                                for line in spilines:
                                    smatch = subrex.match(line)
                                    if smatch:
                                        stubname = smatch.group(1) 
                                        stublist = smatch.group(2).split()
                                        if stubname == subname:
                                            found = True
                                            needsort = False
                                            for stubpin, subpin in zip(stublist, pinlist):
                                                if stubpin.upper() != subpin.upper():
                                                    print('Warning: pin mismatch between layout and schematic stub header on subcircuit ' + subname)
                                                    print('Will sort layout netlist to match.')
                                                    print('Correct pin order is: ' + smatch.group(2))
                                                    needsort = True
                                                    break
                                            if needsort:
                                                pinorder = [i[0] for i in sorted(enumerate(pinlist), key = lambda x:stublist.index(x[1]))]
                                                pinsorts[subname] = pinorder
                                    if found:
                                        break

                        else:
                            print('No file ' + cdlpath + ' found.')
                            print('Failure to find stub netlist for checking pin order.  Good luck.')
                        break

                if not found:
                    print('Error: Subcell ' + subname + ' not found in IP or tech paths.')
                    print('This netlist is not going to simulate correctly.')
                    newspilines.append('* Unknown black-box entry ' + subname)
                    newspilines.append(line)
        elif endsrex.match(line):
            inbox = False

    with open(pexnetlist, 'w') as ofile:
        for line in newspilines:
            print(line, file=ofile)

def regenerate_netlists(localmode, dspath, dsheet):
    # When running locally, 'netlist-source' determines whether to use the
    # layout extracted netlist or the schematic captured netlist.  Also for
    # local running only, regenerate the netlist only if it is out of date,
    # or if the user has selected forced regeneration in the settings.

    dname = dsheet['ip-name']
    magpath = dspath + '/mag/'

    spicepath = dspath + '/spice/'	# Schematic netlist for sim
    pexpath = dspath + '/spice/pex/'	# Layout netlist for sim (C-parasitics)
    rcxpath = dspath + '/spice/rcx/'	# Layout netlist for sim (R+C-parasitics)
    lvspath = dspath + '/spice/lvs/'	# Layout netlist for LVS
    vlogpath = dspath + '/verilog/'	# Verilog netlist for sim and LVS

    netlistname = dname + '.spice'
    schnetlist = spicepath + netlistname
    rcxnetlist = rcxpath + netlistname
    pexnetlist = pexpath + netlistname
    lvsnetlist = lvspath + netlistname

    layoutpath = magpath + dname + '.mag'
    schempath = dspath + '/xschem/' + dname + '.sch'
    verilogpath = vlogpath + dname + '.v'
    pathlast = os.path.split(dspath)[1]
    need_sch_capture = True
    need_extract = True
    need_pex = True
    force_regenerate = False

    # Check if datasheet has been marked for forced netlist regeneration
    if 'regenerate' in dsheet:
        if dsheet['regenerate'] == 'force':
            force_regenerate = True

    if not os.path.exists(schempath):
        print('No schematic in path ' + schempath)

    # Guess the source based on the file or files in the design directory,
    # with preference given to layout.  This may be overridden in local mode.

    if localmode and ('netlist-source' in dsheet) and (not force_regenerate):
        print("Checking for out-of-date netlists.\n")
        netlist_source = dsheet['netlist-source']
        need_sch_capture = check_schematic_out_of_date(schnetlist, schempath)
        if netlist_source == 'layout':
            netlist_path = pexnetlist
            need_pex_extract = check_layout_out_of_date(pexnetlist, layoutpath)
            need_lvs_extract = check_layout_out_of_date(laynetlist, layoutpath)
        else:
            netlist_path = schnetlist
            need_lvs_extract = False
            need_pex_extract = False
    else:
        if not localmode:
            print("Remote use, ", end='');
        print("forcing regeneration of all netlists.\n")
        if 'netlist-source' in dsheet:
            netlist_source = dsheet['netlist-source']
            if netlist_source == 'layout':
                netlist_path = pexnetlist
            else:
                netlist_path = schnetlist
                need_lvs_extract = False
                need_pex_extract = False
        else:
            if os.path.exists(layoutpath):
                netlist_path = pexnetlist
                dsheet['netlist-source'] = 'layout'
            elif os.path.exists(schempath):
                netlist_path = schnetlist
                dsheet['netlist-source'] = 'schematic'
                need_lvs_extract = False
                need_pex_extract = False
            elif os.path.exists(verilogpath):
                netlist_path = verilogpath
                dsheet['netlist-source'] = 'verilog'
                need_lvs_extract = False
                need_pex_extract = False
                need_sch_capture = False
            elif os.path.exists(verilogaltpath):
                netlist_path = verilogaltpath
                dsheet['netlist-source'] = 'verilog'
                need_lvs_extract = False
                need_pex_extract = False
                need_sch_capture = False

    if need_lvs_extract or need_pex_extract:
        # Layout LVS netlist needs regenerating.  Check for magic layout.
        if not os.path.isfile(layoutpath):
            print('Error:  No netlist or layout for project ' + dname + '.')
            print('(layout master file ' + layoutpath + ' not found.)\n')
            return False

        # Check for spi/lvs/ directory
        if not os.path.exists(lvspath):
            os.makedirs(lvspath)

        # Check for spi/pex/ directory
        if not os.path.exists(pexpath):
            os.makedirs(pexpath)

        print("Extracting LVS netlist from layout. . .")
        mproc = subprocess.Popen(['magic', '-dnull', '-noconsole',
		layoutpath], stdin = subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT, cwd = dspath + '/mag',
		universal_newlines = True)
        mproc.stdin.write("select top cell\n")
        mproc.stdin.write("expand true\n")
        mproc.stdin.write("extract all\n")
        mproc.stdin.write("ext2spice hierarchy on\n")
        mproc.stdin.write("ext2spice format ngspice\n")
        mproc.stdin.write("ext2spice scale off\n")
        mproc.stdin.write("ext2spice renumber off\n")
        mproc.stdin.write("ext2spice subcircuit on\n")
        mproc.stdin.write("ext2spice global off\n")
        # Don't want black box entries, but create them so that we know which
        # subcircuits are in the ip path, then replace them.
        mproc.stdin.write("ext2spice blackbox on\n")
        if need_lvs_extract:
            mproc.stdin.write("ext2spice cthresh infinite\n")
            mproc.stdin.write("ext2spice rthresh infinite\n")
            mproc.stdin.write("ext2spice -o " + laynetlist + "\n")
        if need_pex_extract:
            mproc.stdin.write("ext2spice cthresh 0.005\n")
            mproc.stdin.write("ext2spice rthresh 1\n")
            mproc.stdin.write("ext2spice -o " + pexnetlist + "\n")
        mproc.stdin.write("quit -noprompt\n")
        magout = mproc.communicate()[0]
        printwarn(magout)
        if mproc.returncode != 0:
            print('Magic process returned error code ' + str(mproc.returncode) + '\n')

        if need_lvs_extract and not os.path.isfile(laynetlist):
            print('Error:  No LVS netlist extracted from magic.')
        if need_pex_extract and not os.path.isfile(pexnetlist):
            print('Error:  No parasitic extracted netlist extracted from magic.')

        if (mproc.returncode != 0) or (need_lvs_extract and not os.path.isfile(laynetlist)) or (need_pex_extract and not os.path.isfile(pexnetlist)):
            return False

        if need_pex_extract and os.path.isfile(pexnetlist):
            print('Generating include statements for read-only IP blocks in layout, if needed')
            layout_netlist_includes(pexnetlist, dspath)

    if need_sch_capture:
        # Netlist needs regenerating.  Check for xschem schematic
        if not os.path.isfile(schempath):
            if os.path.isfile(verilogpath):
                print('No schematic for project.')
                print('Using verilog netlist ' + verilogpath + ' for simulation and LVS.')
                return verilogpath
            elif os.path.isfile(verilogaltpath):
                print('No schematic for project.')
                print('Using verilog netlist ' + verilogaltpath + ' for simulation and LVS.')
                return verilogaltpath
            else:
                print('Error:  No netlist or schematic for project ' + dname + '.')
                print('(schematic master file ' + schempath + ' not found.)\n')
                print('Error:  No verilog netlist ' + verilogpath + ' or ' + verilogaltpath + ', either.')
                return False

    if need_sch_capture:
        print("Generating simulation netlist from schematic. . .")
        # Generate the netlist
        print('Calling xschem to generate netlist')

        if not os.path.exists(spicepath):
            os.makedirs(spicepath)

        xproc = subprocess.Popen(['xschem', '-n', '-r', '-q',
		'--tcl "set top_subckt 1',
		'-o', schnetlist, dname + '.sch'],
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
		cwd = dspath + '/xschem')

        xout = xproc.communicate()[0]
        if xproc.returncode != 0:
            for line in xout.splitlines():
                print(line.decode('utf-8'))

            print('Xschem process returned error code ' + str(xproc.returncode) + '\n')
        else:
            printwarn(xout)

        if not os.path.isfile(schnetlist):
            print('Error: No netlist found for the circuit!\n')
            print('(schematic netlist for simulation ' + schnetlist + ' not found.)\n')

    if need_sch_capture:
        if (not os.path.isfile(schnetlist)):
            return False

    return netlist_path

def cleanup_exit(signum, frame):
    global launchproc
    print("CACE gensim:  Received termination signal.")
    if launchproc:
        print("CACE gensim:  Stopping simulations now.")
        launchproc.terminate()
    else:
        sys.exit(1)

# Main entry point.  Read arguments, print usage or load the json file
# and call generate_simfiles.

if __name__ == '__main__':
    faulthandler.register(signal.SIGUSR2)
    signal.signal(signal.SIGINT, cleanup_exit)
    signal.signal(signal.SIGTERM, cleanup_exit)

    # Divide up command line into options and arguments
    options = []
    arguments = []
    localmode = False
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # Read the JSON file
    root_path = []
    if len(arguments) > 0:
        root_path = str(sys.argv[1])
        arguments = arguments[1:]
    elif len(options) == 0:
        # Print usage information when arguments don't match
        print('Usage:\n')
        print('   ' + str(sys.argv[0]) + ' [root_path] [options ...]')
        print('Where [options ...] are one or more of the following:')
        print(' -simdir <path>')
        print('      is the location where simulation files and data should be placed.')
        print(' -datasheetdir <path>')
        print('      is the location of the JSON file describing the characterization.')
        print(' -testbenchdir <path>')
        print('      is the location of the netlists for the characterization methods.')
        print(' -netlist <path>')
        print('      is the location of the netlist for the device-under-test.')
        print(' -layoutdir <path>')
        print('      is the location of the layout netlist for the device-under-test.')
        print(' -datasheet <name>')
        print('      is the name of the datasheet JSON file.')
        print(' -method <name>, ...')
        print('      is a list of one or more names of methods to simulated.  If omitted,')
        print('      all methods are run for a complete characterization.')
        print(' -local')
        print('      indicates that cace_gensim is being run locally, not on the CACE')
        print('      server, simulation conditions should be output along with results;')
        print('      "local" mode implies that results are not posted to the marketplace')
        print('      after simulation, and result files are kept.')
        print(' -keep')
        print('      test mode:  keep all files after simulation')
        print(' -plot')
        print('      test mode:  generate plot (.png) files locally')
        print(' -nopost')
        print('      test mode:  do not post results to the marketplace')
        print(' -nosim')
        print('      test mode:  set up all files for simulation but do not simulate')
        sys.exit(0)

    simulation_path = []
    datasheet_path = []
    testbench_path = []
    design_path = []
    layout_path = []
    datasheet_name = []
    methods = []
    for option in options[:]:
        result = option.split('=')
        if result[0] == '-simdir':
            simulation_path = result[1]
            options.remove(option)
        elif result[0] == '-datasheetdir':
            datasheet_path = result[1]
            options.remove(option)
        elif result[0] == '-testbenchdir':
            testbench_path = result[1]
            options.remove(option)
        elif result[0] == '-designdir':
            design_path = result[1]
            options.remove(option)
        elif result[0] == '-layoutdir':
            layout_path = result[1]
            options.remove(option)
        elif result[0] == '-datasheet':
            datasheet_name = result[1]
            options.remove(option)
        elif result[0] == '-method':
            methods.append(result[1])
            options.remove(option)
        elif result[0] == '-bypass':
            bypassmode = True
            options.remove(option)
        elif result[0] == '-local':
            localmode = True

    # To be valid, must either have a root path or all other options must have been
    # specified with full paths.
    if not root_path:
        err_result = 1
        if not simulation_path:
            print('Error:  If root_path is not provided, -simdir is required.')
        elif simulation_path[0] != '/':
            print('Error:  If root_path not provided, -simdir must be a full path.')
        if not testbench_path:
            print('Error:  If root_path is not provided, -testbenchdir is required.')
        elif testbench_path[0] != '/':
            print('Error:  If root_path not provided, -testbenchdir must be a full path.')
        if not design_path:
            print('Error:  If root_path is not provided, -designdir is required.')
        elif design_path[0] != '/':
            print('Error:  If root_path not provided, -designdir must be a full path.')
        if not layout_path:
            print('Error:  If root_path is not provided, -layoutdir is required.')
        elif layout_path[0] != '/':
            print('Error:  If root_path not provided, -layoutdir must be a full path.')
        if not datasheet_path:
            print('Error:  If root_path is not provided, -datasheetdir is required.')
        elif datasheet_path[0] != '/':
            print('Error:  If root_path not provided, -datasheetdir must be a full path.')
        else:
            err_result = 0

        if err_result:
            sys.exit(1)

    # Apply defaults where not provided as command-line options
    else:
        if not datasheet_path:
            datasheet_path = root_path
        elif not os.path.isabs(datasheet_path):
            datasheet_path = root_path + '/' + datasheet_path
        if not datasheet_name:
            datasheet_name = 'datasheet.json'
            inputfile = datasheet_path + '/' + datasheet_name
            # 2nd guess:  'project.json'
            if not os.path.isfile(inputfile):
                datasheet_name = 'project.json'
                inputfile = datasheet_path + '/' + datasheet_name
            # 3rd guess (legacy behavior):  project directory name + '.json'
            if not os.path.isfile(inputfile):
                datasheet_name = os.path.split(datasheet_path)[1] + '.json'
                inputfile = datasheet_path + '/' + datasheet_name
            if not os.path.isfile(inputfile):
                # Return to original datasheet name;  error will be generated.
                datasheet_name = 'datasheet.json'
            elif localmode and root_path:
                # Use normal path to local simulation workspace
                simulation_path = root_path + '/ngspice'

    # Check that datasheet path exists and that the datasheet is there
    if not os.path.isdir(datasheet_path):
        print('Error:  Path to datasheet ' + datasheet_path + ' does not exist.')
        sys.exit(1)
    if len(os.path.splitext(datasheet_name)) != 2:
        datasheet_name += '.json'
    inputfile = datasheet_path + '/' + datasheet_name
    if not os.path.isfile(inputfile):
        print('Error:  No datasheet file ' + inputfile )
        sys.exit(1)

    with open(inputfile) as ifile:
       datatop = json.load(ifile)

    # Pick up testbench and design paths from options now, since some of them
    # depend on the request-hash value in the JSON file.

    if not simulation_path:
        if 'request-hash' in datatop:
            hashname = datatop['request-hash']
            simulation_path = root_path + '/' + hashname
        elif os.path.isdir(root_path + '/ngspice'):
            simulation_path = root_path + '/ngspice'
        else:
            simulation_path = root_path
    elif not os.path.isabs(simulation_path):
        simulation_path = root_path + '/' + simulation_path
    if not testbench_path:
        testbench_path = root_path + '/testbench'
    elif not os.path.isabs(testbench_path):
        testbench_path = root_path + '/' + testbench_path
    if not design_path:
        design_path = root_path + '/spi'
    elif not os.path.isabs(design_path):
        design_path = root_path + '/' + design_path
    if not layout_path:
        layout_path = root_path + '/mag'
    elif not os.path.isabs(layout_path):
        layout_path = root_path + '/' + layout_path

    # Project name should be 'ip-name' in datatop['data-sheet']
    try:
        dsheet = datatop['data-sheet']
    except KeyError:
        print('Error:  File ' + inputfile + ' is not a datasheet.\n')
        sys.exit(1)
    try:
        name = dsheet['ip-name']
    except KeyError:
        print('Error:  File ' + inputfile + ' is missing ip-name.\n')
        sys.exit(1)

    if not os.path.isdir(testbench_path):
        print('Warning:  Path ' + testbench_path + ' does not exist.  ' +
			'Testbench files are not available.\n')

    if not os.path.isdir(design_path):
        print('Warning:  Path ' + design_path + ' does not exist.  ' +
			'Netlist files may not be available.\n')

    # Simulation path is where the output is dumped.  If it doesn't
    # exist, then create it.
    if not os.path.isdir(simulation_path):
        print('Creating simulation path ' + simulation_path)
        os.makedirs(simulation_path)

    if not os.path.isdir(layout_path):
        print('Creating layout path ' + layout_path)
        os.makedirs(layout_path)

    if not os.path.exists(layout_path + '/.magicrc'):
        # Make sure correct .magicrc file exists
        configdir = os.path.split(layout_path)[0]
        rcpath = configdir + '/.config/techdir/libs.tech/magic'
        pdkname = os.path.split(os.path.realpath(configdir + '/.config/techdir'))[1]
        rcfile = rcpath + '/' + pdkname + '.magicrc'
        if os.path.isdir(rcpath):
            if os.path.exists(rcfile):
                shutil.copy(rcfile, layout_path + '/.magicrc')

    # Find the electrical parameter list.  If it exists, then the
    # template has been loaded.  If not, find the template name,
    # then load it from known templates.  Templates may be local to
    # the simulation files.  Priority is (1) templates known to CACE
    # (for challenges;  cannot be overridden by a user; (2) templates
    # local to the simulation (user-generated)

    if not 'electrical-params' in dsheet and not 'physical-params' in dsheet:
        print('Error: Circuit JSON file does not have a valid characterization template!\n')
        sys.exit(1)

    fullnetlistpath = regenerate_netlists(localmode, root_path, dsheet)
    if not fullnetlistpath:
        sys.exit(1)

    netlistpath, netlistname = os.path.split(fullnetlistpath)

    # If there is a 'hints.json' file in the root path, read it and apply to the
    # electrical parameters.  The file contains exactly one hint record per
    # electrical parameter, although the hint record may be empty.
    if os.path.exists(root_path + '/hints.json'):
        with open(root_path + '/hints.json') as hfile:
            hintlist = json.load(hfile)
            i = 0
            for eparam in dsheet['electrical-params']:
                if not 'hints' in eparam:
                    if hintlist[i]:
                        eparam['hints'] = hintlist[i]
                i += 1

    # Construct fileinfo dictionary
    fileinfo = {}
    fileinfo['project-name'] = name
    fileinfo['design-netlist-name'] = netlistname
    fileinfo['design-netlist-path'] = netlistpath
    fileinfo['testbench-netlist-path'] = testbench_path
    fileinfo['simulation-path'] = simulation_path
    fileinfo['root-path'] = root_path

    # Generate the simulation files
    prescore = generate_simfiles(datatop, fileinfo, arguments, methods, localmode)
    if prescore == 'fail':
        # In case of failure
        options.append('-score=fail')

    # Remove option keys
    if 'keep' in datatop:
        options.append('-keep')
        datatop.pop('keep')
    if 'plot' in datatop:
        options.append('-plot')
        datatop.pop('plot')
    if 'nopost' in datatop:
        options.append('-nopost')
        datatop.pop('nopost')
    if 'nosim' in datatop:
        options.append('-nosim')
        datatop.pop('nosim')

    # Reconstruct the -simdir option for cace_launch
    options.append('-simdir=' + simulation_path)

    # Reconstruct the -layoutdir option for cace_launch
    options.append('-layoutdir=' + layout_path)

    # Reconstruct the -netlistdir option for cace_launch
    options.append('-netlistdir=' + design_path)

    # Reconstruct the -rootdir option for cace_launch
    if root_path:
        options.append('-rootdir=' + root_path)

    # Dump the modified JSON file
    basename = os.path.basename(inputfile)
    outputfile = simulation_path + '/' + basename
    with open(outputfile, 'w') as ofile:
        json.dump(datatop, ofile, indent = 4)

    # Launch simulator as a subprocess and wait for it to finish
    # Waiting is important, as otherwise child processes get detached and it
    # becomes very difficult to find them if the simulation needs to be stopped.
    launchname = apps_path + '/' + 'cace_launch.py'

    # Diagnostic
    print("Running: " + launchname + ' ' + outputfile)
    for a in arguments:
        print(a)
    for o in options:
        print(o)

    with subprocess.Popen([launchname, outputfile, *arguments, *options],
        		stdout=subprocess.PIPE, bufsize = 1,
			universal_newlines=True) as launchproc:
        for line in launchproc.stdout:
            print(line, end='')
            sys.stdout.flush()

        launchproc.stdout.close()
        return_code = launchproc.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, launchname)

    sys.exit(0)
