#!/bin/env python3
# Script to read all files in a directory of SPECTRE-compatible device model
# files, and convert them to a form that is compatible with ngspice. 

import os
import sys
import re
import glob

def usage():
    print('convert_spectre.py <path_to_spectre> <path_to_spice>')

# Check if a parameter value is a valid number (real, float, integer)
# or is some kind of expression.

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Parse a parameter line.  If "inparam" is true, then this is a continuation
# line of an existing parameter statement.  If "insub" is not true, then the
# paramters are global parameters (not part of a subcircuit).
#
# If inside a subcircuit, remove the keyword "parameters".  If outside,
# change it to ".param"

def parse_param_line(line, inparam, insub):

    # Regexp patterns
    parm1rex = re.compile('parameters' + '[ \t]*(.*)')
    parm2rex = re.compile('\+[ \t]*(.*)')
    parm3rex = re.compile('[ \t]*([^= \t]+)[ \t]*=[ \t]*([^ \t]+)[ \t]*(.*)')

    fmtline = []
    
    if inparam:
        pmatch = parm2rex.match(line)
        if pmatch:
            fmtline.append('+')
            rest = pmatch.group(1)
        else:
            return ''
    else:
        pmatch = parm1rex.match(line)
        if pmatch:
            if insub:
                fmtline.append('+')
            else:
                fmtline.append('.param')
            rest = pmatch.group(1)
        else:
            return ''

    while rest != '':
        pmatch = parm3rex.match(rest)
        if pmatch:
            fmtline.append(pmatch.group(1))
            fmtline.append('=')
            value = pmatch.group(2)
            rest = pmatch.group(3)

            if is_number(value):
                fmtline.append(value)
            else:
                fmtline.append('{' + value + '}')

            # These parameter sub-expressions are related to
            # monte carlo simulation and are incompatible with
            # ngspice.  So put them in an in-line comment

            if rest != '':
                nmatch = parm3rex.match(rest)
                if not nmatch:
                    fmtline.append(' $ ' + rest.replace(' ', '').replace('\t', ''))
                    rest = ''
        else:
            break

    return ' '.join(fmtline)

def convert_file(in_file, out_file):

    # Regexp patterns
    statrex = re.compile('[ \t]*statistics[ \t]*\{(.*)')
    simrex = re.compile('[ \t]*simulator[ \t]+([^= \t]+)[ \t]*=[ \t]*(.+)')
    insubrex = re.compile('[ \t]*inline[ \t]+subckt[ \t]+([^ \t]+)[ \t]*\(([^)]*)')
    endsubrex = re.compile('[ \t]*ends[ \t]+(.+)')
    modelrex = re.compile('[ \t]*model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+\{(.*)')
    binrex = re.compile('[ \t]*([0-9]+):[ \t]+type[ \t]*=[ \t]*(.*)')
    shincrex = re.compile('\.inc[ \t]+')

    stdsubrex = re.compile('\.subckt[ \t]+([^ \t]+)[ \t]+([^ \t]*)')
    stdmodelrex = re.compile('\.model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+(.*)')
    stdendsubrex = re.compile('\.ends[ \t]+(.+)')

    # Devices (resistor, capacitor, subcircuit as resistor or capacitor)
    caprex = re.compile('c([^ \t]+)[ \t]*\(([^)]*)\)[ \t]*capacitor[ \t]*(.*)', re.IGNORECASE)
    resrex = re.compile('r([^ \t]+)[ \t]*\(([^)]*)\)[ \t]*resistor[ \t]*(.*)', re.IGNORECASE)

    with open(in_file, 'r') as ifile:
        speclines = ifile.read().splitlines()

    insub = False
    inparam = False
    inmodel = False
    inpinlist = False
    isspectre = True
    spicelines = []
    calllines = []
    modellines = []
    savematch = None
    blockskip = 0
    subname = ''
    modname = ''
    modtype = ''

    for line in speclines:

        # Item 1.  C++-style // comments get replae with * comment character
        if line.strip().startswith('//'):
            # Replace the leading "//" with SPICE-style comment "*".
            if modellines != []:
                modellines.append(line.strip().replace('//', '*', 1))
            elif calllines != []:
                calllines.append(line.strip().replace('//', '*', 1))
            else:
                spicelines.append(line.strip().replace('//', '*', 1))
            continue

        # Item 2.  Handle SPICE-style comment lines
        if line.strip().startswith('*'):
            if modellines != []:
                modellines.append(line.strip())
            elif calllines != []:
                calllines.append(line.strip())
            else:
                spicelines.append(line.strip())
            continue

        # Item 3.  Flag continuation lines
        if line.strip().startswith('+'):
            contline = True
        else:
            contline = False
            if inparam:
                inparam = False 
            if inpinlist:
                inpinlist = False 

        # Item 4.  Count through { ... } blocks that are not SPICE syntax
        if blockskip > 0:
            # Warning:  Assumes one brace per line, may or may not be true
            if '{' in line:
                blockskip = blockskip + 1
            elif '}' in line:
                blockskip = blockskip - 1
                if blockskip == 0:
                    spicelines.append('* ' + line)
                    continue

        if blockskip > 0:
            spicelines.append('* ' + line)
            continue

        # Item 5.  Handle continuation lines
        if contline:
            if inparam:
                # Continue handling parameters
                fmtline = parse_param_line(line, inparam, insub)
                if fmtline != '':
                    if modellines != []:
                        modellines.append(fmtline)
                    elif calllines != []:
                        calllines.append(fmtline)
                    else:
                        spicelines.append(fmtline)
                    continue

        # Item 6.  Regexp matching

        # Catch "simulator lang="
        smatch = simrex.match(line)
        if smatch:
            if smatch.group(1) == 'lang':
                if smatch.group(2) == 'spice':
                    isspectre = False
                elif smatch.group(2) == 'spectre':
                    isspectre = True
            continue

        # If inside a subcircuit, remove "parameters".  If outside,
        # change it to ".param"
        fmtline = parse_param_line(line, inparam, insub)
        if fmtline != '':
            inparam = True
            spicelines.append(fmtline)
            continue
        
        # statistics---not sure if it is always outside an inline subcircuit
        smatch = statrex.match(line)
        if smatch:
            if '}' not in smatch.group(1):
                blockskip = 1
                spicelines.append('* ' + line)
                continue

        # model---not sure if it is always inside an inline subcircuit
        if isspectre:
            mmatch = modelrex.match(line)
        else:
            mmatch = stdmodelrex.match(line)
        if mmatch:
            modellines = []
            modname = mmatch.group(1)
            modtype = mmatch.group(2)

            if isspectre and '}' in mmatch.group(1):
                savematch = mmatch
                inmodel = 1
                # Continue to "if inmodel == 1" block below
            else:
                if not isspectre:
                    modellines.append(line)
                inmodel = 2
                continue

        if not insub:
            # Things to parse if not in a subcircuit

            if isspectre:
                imatch = insubrex.match(line)
            else:
                imatch = stdsubrex.match(line)

            if imatch:
                insub = True
                subname = imatch.group(1)
                calllines = []
                if isspectre:
                    devrex = re.compile(subname + '[ \t]*\(([^)]*)\)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
                    # If there is no close-parenthesis then we should expect it on
                    # a continuation line
                    inpinlist = True if ')' not in line else False
                    # Remove parentheses groups from subcircuit arguments
                    spicelines.append('.subckt ' + ' ' + subname + ' ' + imatch.group(2))
                else:
                    devrex = re.compile(subname + '[ \t]*([^ \t]+)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
                    inpinlist = True
                    spicelines.append(line)
                continue

        else:
            # Things to parse when inside of an "inline subckt" block

            if inpinlist:
                # Watch for pin list continuation line.
                if isspectre:
                    if ')' in line:
                        inpinlist = False
                    pinlist = line.replace(')', '')
                    spicelines.append(pinlist)
                else:
                    spicelines.append(line)
                continue
                
            else:
                if isspectre:
                    ematch = endsubrex.match(line)
                else:
                    ematch = stdendsubrex.match(line)
                if ematch:
                    if ematch.group(1) != subname:
                        print('Error:  "ends" name does not match "subckt" name!')
                        print('"ends" name = ' + ematch.group(1))
                        print('"subckt" name = ' + subname)
                    if len(calllines) > 0:
                        line = calllines[0]
                        if modtype.startswith('bsim'):
                            line = 'M' + line
                        elif modtype.startswith('nmos'):
                            line = 'M' + line
                        elif modtype.startswith('pmos'):
                            line = 'M' + line
                        elif modtype.startswith('res'):
                            line = 'R' + line
                        elif modtype.startswith('cap'):
                            line = 'C' + line
                        elif modtype.startswith('pnp'):
                            line = 'Q' + line
                        elif modtype.startswith('npn'):
                            line = 'Q' + line
                        elif modtype.startswith('d'):
                            line = 'D' + line
                        spicelines.append(line)

                        # Will need more handling here for other component types. . . 

                    for line in calllines[1:]:
                        spicelines.append(line)

                    spicelines.append('.ends ' + subname)

                    # Now add the .model after the subcircuit definition
                    spicelines.append('')
                    for line in modellines:
                        spicelines.append(line)
                    
                    insub = False
                    inmodel = False
                    subname = ''
                    continue

            # Check for close of model
            if isspectre and inmodel:
                if '}' in line:
                    inmodel = False
                    continue

            # Check for devices R and C.
            dmatch = caprex.match(line)
            if dmatch:
                fmtline = parse_param_line(dmatch.group(3), True, insub)
                if fmtline != '':
                    inparam = True
                    spicelines.append('c' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + fmtline)
                    continue
                else:
                    spicelines.append('c' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + dmatch.group(3))
                    continue

            dmatch = resrex.match(line)
            if dmatch:
                fmtline = parse_param_line(dmatch.group(3), True, insub)
                if fmtline != '':
                    inparam = True
                    spicelines.append('r' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + fmtline)
                    continue
                else:
                    spicelines.append('r' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + dmatch.group(3))
                    continue

            # Check for a line that begins with the subcircuit name
          
            dmatch = devrex.match(line)
            if dmatch:
                fmtline = parse_param_line(dmatch.group(3), True, insub)
                if fmtline != '':
                    inparam = True
                    calllines.append(subname + ' ' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + fmtline)
                    continue
                else:
                    calllines.append(subname + ' ' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + dmatch.group(3))
                    continue

        if inmodel == 1 or inmodel == 2:
            # This line should have the model bin, if there is one, and a type.
            if inmodel == 1:
                bmatch = binrex.match(savematch.group(3))
                savematch = None
            else:
                bmatch = binrex.match(line)

            if bmatch:
                bin = bmatch.group(1)
                type = bmatch.group(2)

                if type == 'n':
                    convtype = 'nmos'
                elif type == 'p':
                    convtype = 'pmos'
                else:
                    convtype = type

                modellines.append('')
                modellines.append('.model ' + modname + '.' + bin + ' ' + convtype)
                continue

            else:
                fmtline = parse_param_line(line, True, True)
                if fmtline != '':
                    modellines.append(fmtline)
                    continue

        # Copy line as-is
        spicelines.append(line)

    # Output the result to out_file.
    with open(out_file, 'w') as ofile:
        for line in spicelines:
            print(line, file=ofile)

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to convert_spectre.py.")
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 2:
        print("Wrong number of arguments given to convert_spectre.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    specpath = arguments[0]
    spicepath = arguments[1]
    do_one_file = False

    if not os.path.exists(specpath):
        print('No such source directory ' + specpath)
        sys.exit(1)

    if os.path.isfile(specpath):
        do_one_file = True

    if do_one_file:
        if os.path.exists(spicepath):
            print('Error:  File ' + spicepath + ' exists.')
            sys.exit(1)
        convert_file(specpath, spicepath)

    else:
        if not os.path.exists(spicepath):
            os.makedirs(spicepath)

        specfilelist = glob.glob(specpath + '/*')

        for filename in specfilelist:
            fileext = os.path.splitext(filename)[1]

            # Ignore verilog or verilog-A files that might be in a model directory
            if fileext == '.v' or fileext == '.va':
                continue

            froot = os.path.split(filename)[1]
            convert_file(filename, spicepath + '/' + froot)

    print('Done.')
    exit(0)
