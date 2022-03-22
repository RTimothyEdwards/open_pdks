#!/usr/bin/env python3
# Script to read all files in a directory of SPECTRE-compatible device model
# files, and convert them to a form that is compatible with ngspice.

import os
import sys
import re
import glob

def usage():
    print('spectre_to_spice.py <path_to_spectre> <path_to_spice>')

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

def parse_param_line(line, inparam, insub, iscall, ispassed, inmod, linenum):

    # Regexp patterns
    parm1rex = re.compile('[ \t]*parameters[ \t]*(.*)')
    parm2rex = re.compile('[ \t]*params:[ \t]*(.*)')
    parm3rex = re.compile('[ \t]*\+[ \t]*(.*)')
    parm4rex = re.compile('[ \t]*([^= \t]+)[ \t]*=[ \t]*([^ \t]+)[ \t]*(.*)')
    parm5rex = re.compile('[ \t]*([^= \t]+)[ \t]*(.*)')
    parm6rex = re.compile('[ \t]*([^= \t]+)[ \t]*=[ \t]*([\'{][^\'}]+[\'}])[ \t]*(.*)')
    rtok = re.compile('([^ \t\n]+)[ \t]*(.*)')

    fmtline = []

    if iscall:
        rest = line
    elif inparam:
        pmatch = parm3rex.match(line)
        if pmatch:
            fmtline.append('+')
            rest = pmatch.group(1)
        else:
            return '', ispassed
    else:
        pmatch = parm1rex.match(line)
        if pmatch:
            if insub:
                fmtline.append('+')
            else:
                fmtline.append('.param')
            rest = pmatch.group(1)
        else:
            pmatch = parm2rex.match(line)
            if pmatch:
                if insub:
                    fmtline.append('+')
                else:
                    return '', ispassed
                rest = pmatch.group(1)
            else:
                return '', ispassed

    while rest != '':
        # It is hard to believe that this is legal even in spectre.
        # Parameter expression given with no braces or quotes around
        # the expression.  Fix the expression by removing the spaces
        # around '*'.
        rest = re.sub('[ \t]*([\*\+\-])[ \t]*', '\g<1>', rest)

        pmatch = parm4rex.match(rest)
        if pmatch:
            if ispassed and not iscall and not inmod:
                # End of passed parameters.  Break line and generate ".param"
                ispassed = False
                fmtline.append('\n.param ')

            # If expression is already in single quotes or braces, then catch
            # everything inside the delimiters, including any spaces.
            if pmatch.group(2).startswith("'") or pmatch.group(2).startswith('{'):
                pmatchx = parm6rex.match(rest)
                if pmatchx:
                    pmatch = pmatchx

            fmtline.append(pmatch.group(1))
            fmtline.append('=')
            value = pmatch.group(2)
            rest = pmatch.group(3)

            # Watch for spaces in expressions (have they no rules??!)
            # as indicated by something after a space not being an
            # alphabetical character (parameter name) or ';' (comment)

            needmore = False
            while rest != '':
                rmatch = rtok.match(rest)
                if rmatch:
                    expch = rmatch.group(1)[0]
                    if expch == ';' or expch == '$':
                        break
                    elif expch.isalpha() and not needmore:
                        break
                    else:
                        needmore = False
                        value += rmatch.group(1)
                        rest = rmatch.group(2)
                        if any((c in '+-*/({^~!') for c in rmatch.group(1)[-1]):
                            needmore = True
                        if rest != '' and any((c in '+-*/(){}^~!') for c in rest[0]):
                            needmore = True
                else:
                    break

            if is_number(value):
                fmtline.append(value)
            elif value.strip().startswith("'"):
                fmtline.append(value)
            else:
                # It is not possible to know if a spectre expression continues
                # on another line without some kind of look-ahead, but check
                # if the parameter ends in an operator.
                lastc = value.strip()[-1]
                if any((c in '*+-/,(') for c in lastc):
                    fmtline.append('{' + value)
                else:
                    fmtline.append('{' + value + '}')

            # These parameter sub-expressions are related to monte carlo
            # simulation and are incompatible with ngspice.  So put them
            # in an in-line comment.  Avoid double-commenting things that
            # were already in-line comments.

            if rest != '':
                nmatch = parm4rex.match(rest)
                if not nmatch:
                    if rest.lstrip().startswith('; '):
                        fmtline.append(rest)
                    elif rest.strip() != '':
                        fmtline.append(' ; ' + rest.replace(' ', '').replace('\t', ''))
                    rest = ''
        else:
            # Match to a CDL subckt parameter that does not have an '=' and so
            # assumes that the parameter is always passed, and therefore must
            # be part of the .subckt line.  A parameter without a value is not
            # legal SPICE, so supply a default value of 1.

            pmatch = parm5rex.match(rest)
            if pmatch:
                # NOTE: Something that is not a parameter name should be
                # extended from the previous line.  Note that this parsing
                # is not rigorous and is possible to break. . .
                if any((c in '+-*/(){}^~!') for c in pmatch.group(1).strip()):
                    fmtline.append(rest)
                    if not any((c in '*+-/,(') for c in rest.strip()[-1]):
                        fmtline.append('}')
                    rest = ''
                else:
                    fmtline.append(pmatch.group(1) + '=1')
                    ispassed = True
                    rest = pmatch.group(2)
            else:
                break

    finalline = ' '.join(fmtline)

    # ngspice does not understand round(), so replace it with the equivalent
    # floor() expression.

    finalline = re.sub('round\(', 'floor(0.5+', finalline)

    # use of "no" and "yes" as parameter values is not allowed in ngspice.

    finalline = re.sub('sw_et[ \t]*=[ \t]*{no}', 'sw_et=0', finalline)
    finalline = re.sub('sw_et[ \t]*=[ \t]*{yes}', 'sw_et=1', finalline)
    finalline = re.sub('isnoisy[ \t]*=[ \t]*{no}', 'isnoisy=0', finalline)
    finalline = re.sub('isnoisy[ \t]*=[ \t]*{yes}', 'isnoisy=1', finalline)

    # Use of "m" in parameters is forbidden.  Specifically look for "{N*m}".
    # e.g., replace "mult = {2*m}" with "mult = 2".  Note that this usage
    # is most likely an error in the source.

    finalline = re.sub('\{([0-9]+)\*[mM]\}', r'\1', finalline)

    return finalline, ispassed

def get_param_names(line):
    # Find parameter names in a ".param" line and return a list of them.
    # This is used to check if a bare word parameter name is passed to
    # a capacitor or resistor device in the position of a value but
    # without delimiters, so that it cannot be distinguished from a
    # model name.  There are only a few instances of this, so this
    # routine is not rigorously checking all parameters, just entries
    # on lines with ".param".
    parmrex = re.compile('[ \t]*([^= \t]+)[ \t]*=[ \t]*([^ \t]+)[ \t]*(.*)')
    rest = line
    paramnames = []
    while rest != '':
        pmatch = parmrex.match(rest)
        if pmatch:
            paramnames.append(pmatch.group(1))
            rest = pmatch.group(3)
        else:
            break
    return paramnames

# Dump any saved model lines to a list.  Check for "type =" syntax in a
# binned model

def addmodel(modellines, linenum):
    typerex = re.compile('([ \t]*type[ \t]*=[ \t]*)([^ \t]+)[ \t]*', re.IGNORECASE)
  
    # 'ZYXW' was left as a placeholder for the device type
    if len(modellines) > 0:
        typename = None
        for j in range(len(modellines) - 1, -1, -1):
            line = modellines[j]
            pmatch = typerex.search(line)
            if pmatch:
                typename = pmatch.group(2).strip('{}').strip()
                newline = typerex.sub(' ', line)
                modellines[j] = newline
                line = newline

            if 'ZYXW' in line:
                if typename:
                    if typename == 'n':
                        newtype = 'nmos'
                    elif typename == 'p':
                        newtype = 'pmos'
                    else:
                        newtype = typename
                    modellines[j] = re.sub('ZYXW', newtype, line)
                    typename = None
                else:
                    print('Error:  No type name for model at line ' + str(linenum))
                    modellines[j] = re.sub('ZYXW', 'unknown', line)
 
    return modellines

# Run the spectre-to-ngspice conversion

def convert_file(in_file, out_file):

    # Regexp patterns
    statrex = re.compile('[ \t]*statistics[ \t]*\{(.*)')
    simrex = re.compile('[ \t]*simulator[ \t]+([^= \t]+)[ \t]*=[ \t]*(.+)')
    insubrex = re.compile('[ \t]*inline[ \t]+subckt[ \t]+([^ \t\(]+)[ \t]*\(([^)]*)')
    cdlsubrex = re.compile('\.?subckt[ \t]+([^ \t\(]+)[ \t]*\(([^)]*)')
    endsubrex = re.compile('[ \t]*ends[ \t]+(.+)')
    endonlysubrex = re.compile('[ \t]*ends[ \t]*')
    modelrex = re.compile('[ \t]*model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+\{(.*)')
    cdlmodelrex = re.compile('[ \t]*model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]*(.*)')
    binrex = re.compile('[ \t]*([0-9]+):[ \t]*(.*)')
    shincrex = re.compile('\.inc[ \t]+')
    isexprrex = re.compile('[^0-9a-zA-Z_]')
    paramrex = re.compile('\.param[ \t]+(.*)')

    stdsubrex = re.compile('\.?subckt[ \t]+([^ \t]+)[ \t]+(.*)')
    stdmodelrex = re.compile('\.model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]*(.*)')
    stdendsubrex = re.compile('\.ends[ \t]+(.+)')
    stdendonlysubrex = re.compile('\.ends[ \t]*')

    # Devices (resistor, capacitor, subcircuit as resistor or capacitor)
    caprex = re.compile('c([^ \t]+)[ \t]*\(([^)]*)\)[ \t]*capacitor[ \t]*(.*)', re.IGNORECASE)
    resrex = re.compile('r([^ \t]+)[ \t]*\(([^)]*)\)[ \t]*resistor[ \t]*(.*)', re.IGNORECASE)
    cdlrex = re.compile('[ \t]*([npcrdlmqx])([^ \t]+)[ \t]*\(([^)]*)\)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
    stddevrex = re.compile('[ \t]*([crd])([^ \t]+)[ \t]+([^ \t]+[ \t]+[^ \t]+)[ \t]+([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
    stddev2rex = re.compile('[ \t]*([crd])([^ \t]+)[ \t]+([^ \t]+[ \t]+[^ \t]+)[ \t]+([^ \t\'{]+[\'{][^\'}]+[\'}])[ \t]*(.*)', re.IGNORECASE)
    stddev3rex = re.compile('[ \t]*([npcrdlmqx])([^ \t]+)[ \t]+(.*)', re.IGNORECASE)

    with open(in_file, 'r') as ifile:
        try:
            speclines = ifile.read().splitlines()
        except:
            print('Failure to read ' + in_file + '; not an ASCII file?')
            return

    #---------------------------------------------------------------
    # Do one pass through the file and pick up all subcircuit names,
    # because any subcircuit call could be a forward reference.
    #---------------------------------------------------------------

    allsubrex = re.compile('.*subckt[ \t]+([^ \t\(]+)')
    subnames = []
    for line in speclines:
        testline = line.strip()
        if testline.startswith('//') or testline.startswith('*'):
            continue
        smatch = allsubrex.match(testline)
        if smatch:
            subnames.append(smatch.group(1))

    #---------------------------------------------------------------
    # Now do the main pass (this is probably a bad idea and it would
    # have been more efficient to do this in multiple passes).
    #---------------------------------------------------------------

    insub = False
    inparam = False
    inmodel = False
    inpinlist = False
    isspectre = False
    ispassed = False
    spicelines = []
    calllines = []
    modellines = []
    paramnames = []
    savematch = None
    blockskip = 0
    subname = ''
    modname = ''
    modtype = ''
    othermodnames = []
    othermodtypes = []
    linenum = 0

    for line in speclines:
        linenum = linenum + 1

        # Item 1a.  C++-style // comments get replaced with * comment character
        if line.strip().startswith('//'):
            # Replace the leading "//" with SPICE-style comment "*".
            if modellines != []:
                modellines.append(line.strip().replace('//', '*', 1))
            elif calllines != []:
                calllines.append(line.strip().replace('//', '*', 1))
            else:
                spicelines.append(line.strip().replace('//', '*', 1))
            continue

        # Item 1b.  In-line C++-style // comments get replaced with ; comment character
        elif ' //' in line:
            line = line.replace(' //', ' ; ', 1)
        elif '//' in line:
            line = line.replace('//', ' ; ', 1)
        elif '\t//' in line:
            line = line.replace('\t//', '\t; ', 1) 

        # Item 2.  Handle SPICE-style comment lines
        if line.strip().startswith('*'):
            if modellines != []:
                modellines.append(line.strip())
            elif calllines != []:
                calllines.append(line.strip())
            else:
                spicelines.append(line.strip())
            continue

        # Item 4.  Flag continuation lines
        if line.strip().startswith('+'):
            contline = True
        else:
            if line.strip() != '':
                contline = False
                if inparam:
                    inparam = False
                if inpinlist:
                    inpinlist = False

        # Item 3.  Handle blank lines like comment lines
        if line.strip() == '':
            if modellines != []:
                modellines.append(line.strip())
            elif calllines != []:
                calllines.append(line.strip())
            else:
                spicelines.append(line.strip())
            continue

        # Item 5.  Count through { ... } blocks that are not SPICE syntax
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

        # Item 6.  Handle continuation lines
        if contline:
            if inparam:
                # Continue handling parameters
                fmtline, ispassed = parse_param_line(line, inparam, insub, False, ispassed, inmodel, linenum)
                if fmtline != '':
                    if modellines != []:
                        modellines.append(fmtline)
                    elif calllines != []:
                        calllines.append(fmtline)
                    else:
                        spicelines.append(fmtline)
                    continue

        # Item 7.  Regexp matching

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
        fmtline, ispassed = parse_param_line(line, inparam, insub, False, ispassed, inmodel, linenum)
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
        iscdl = False
        if isspectre:
            mmatch = modelrex.match(line)
            if not mmatch:
                mmatch = cdlmodelrex.match(line)
                if mmatch:
                    iscdl = True
        else:
            mmatch = stdmodelrex.match(line)

        if mmatch:
            if modname:
                othermodnames.append(modname)
                othermodtypes.append(modtype)
            modname = mmatch.group(1)
            modtype = mmatch.group(2)

            if isspectre and '}' in mmatch.group(1):
                savematch = mmatch
                inmodel = 1
                # Continue to "if inmodel == 1" block below
            else:
                fmtline, ispassed = parse_param_line(mmatch.group(3), True, False, True, ispassed, inmodel, linenum)
                if isspectre and (modtype == 'resistor' or modtype == 'r2'):
                    modtype = 'r'
                if isspectre and (modtype == 'diode'):
                    modtype = 'd'
                if isspectre and (modtype == 'bsim4'):
                    # "bsim4"---cast to special string so that it can be later
                    # converted to "nmos" or "pmos" based on the "type" parameter
                    modtype = 'ZYXW'
                modellines.append('.model ' + modname + ' ' + modtype + ' ' + fmtline)
                inparam = True
                inmodel = 2
                continue

        if not insub:
            # Things to parse if not in a subcircuit
            imatch = insubrex.match(line) if isspectre else None

            if not imatch:
                # Check for spectre format subckt or CDL format .subckt lines
                imatch = cdlsubrex.match(line)

            if not imatch:
                # Check for standard SPICE format .subckt lines
                # or CDL format subckt line without parentheses
                imatch = stdsubrex.match(line)
            if imatch:
                # If a model block is pending, then dump it
                if modellines != []:
                    for line in modellines:
                        spicelines.append(line)
                    modellines = []
                    inmodel = False

                insub = True
                ispassed = True
                subname = imatch.group(1)
                if isspectre:
                    devrex = re.compile('[ \t]*' + subname + '[ \t]*\(([^)]*)\)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
                else:
                    devrex = re.compile('[ \t]*' + subname + '[ \t]*([^ \t]+)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
                # If there is no close-parenthesis then we should expect it on
                # a continuation line
                inpinlist = True if ')' not in line else False
                # Remove parentheses groups from subcircuit arguments
                spicelines.append('.subckt ' + ' ' + subname + ' ' + imatch.group(2))
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
                    if not ematch:
                        ematch = endonlysubrex.match(line)
                else:
                    ematch = stdendsubrex.match(line)
                    if not ematch:
                        ematch = stdendonlysubrex.match(line)

                if ematch:
                    try:
                        endname = ematch.group(1).strip()
                    except:
                        pass
                    else:
                        if endname != subname and endname != '':
                            print('Error:  "ends" name does not match "subckt" name!')
                            print('"ends" name = ' + endname)
                            print('"subckt" name = ' + subname)
                    if modname:
                        othermodnames.append(modname)
                        othermodtypes.append(modtype)

                    for line in calllines:
                        modified = False
                        for j in range(len(othermodnames)):
                            if othermodnames[j] in line:
                                modtype = othermodtypes[j]
                                if modtype.startswith('bsim'):
                                    line = 'M' + line
                                    modified = True
                                elif modtype.startswith('nmos'):
                                    line = 'M' + line
                                    modified = True
                                elif modtype.startswith('pmos'):
                                    line = 'M' + line
                                    modified = True
                                elif modtype.startswith('res'):
                                    line = 'R' + line
                                    modified = True
                                elif modtype.startswith('cap'):
                                    line = 'C' + line
                                    modified = True
                                elif modtype.startswith('pnp'):
                                    line = 'Q' + line
                                    modified = True
                                elif modtype.startswith('npn'):
                                    line = 'Q' + line
                                    modified = True
                                elif modtype.startswith('d'):
                                    line = 'D' + line
                                    modified = True
                                elif modtype.startswith('ZYXW'):
                                    line = 'M' + line
                                    modified = True
                                else:
                                    print('Error:  No prefix at line ' + str(linenum))
                                    print('   Model type is ' + modtype)
                            if modified:
                                break
                        if not modified:
                            # Also check for "standard" models, e.g. "resistor"
                            pnames = line.split()
                            if 'resistor' in pnames[1:]:
                                pnames.remove('resistor')
                                line = 'R' + ' '.join(pnames)
                            elif 'capacitor' in pnames[1:]:
                                pnames.remove('capacitor')
                                line = 'C' + ' '.join(pnames)
                            elif len(line) > 1 and line[0].lower() != 'x' and line[0] != '*' and line[0] != '+':
                                # NOTE: Assumes that anything else being called
                                # is a known subcircuit (probably better to check)
                                line = 'X' + ' '.join(pnames)
                        spicelines.append(line)
                    calllines = []

                    # Last check:  Do any model types confict with the way they
                    # are called within the subcircuit?  Spectre makes it very
                    # hard to know what type of device is being instantiated. . .
   
                    for modelline in modellines:
                        mmatch = stdmodelrex.match(modelline)
                        if mmatch:
                            modelname = mmatch.group(1).lower().split('.')[0]
                            modeltype = mmatch.group(2).lower()
                            newspicelines = []
                            for line in spicelines:
                                cmatch = stddev3rex.match(line)
                                if cmatch:
                                    devtype = cmatch.group(1).lower()
                                    if modelname in cmatch.group(3):
                                        if devtype == 'x':
                                            if modeltype == 'pnp' or modeltype == 'npn':
                                                line = 'q' + line[1:]
                                            elif modeltype == 'c' or modeltype == 'r':
                                                line = modeltype + line[1:]
                                            elif modeltype == 'd':
                                                line = modeltype + line[1:]
                                            elif modeltype == 'nmos' or modeltype == 'pmos':
                                                line = 'm' + line[1:]
                                newspicelines.append(line)
                            spicelines = newspicelines

                    # Now add any in-circuit models
                    spicelines.append('')
                    spicelines.extend(addmodel(modellines, linenum))
                    modellines = []

                    # Complete the subcircuit definition
                    spicelines.append('.ends ' + subname)
                    insub = False
                    inmodel = False
                    subname = ''
                    modname = ''
                    modtype = ''
                    othermodnames = []
                    othermodtypes = []
                    paramnames = []
                    continue

            # Check for close of model
            if isspectre and inmodel:
                if '}' in line:
                    inmodel = False
                    continue

            # Check for devices R and C.
            dmatch = caprex.match(line)
            if dmatch:
                fmtline, ispassed = parse_param_line(dmatch.group(3), True, insub, True, ispassed, inmodel, linenum)
                if fmtline != '':
                    inparam = True
                    spicelines.append('c' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + fmtline)
                    continue
                else:
                    spicelines.append('c' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + dmatch.group(3))
                    continue

            dmatch = resrex.match(line)
            if dmatch:
                fmtline, ispassed = parse_param_line(dmatch.group(3), True, insub, True, ispassed, inmodel, linenum)
                if fmtline != '':
                    inparam = True
                    spicelines.append('r' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + fmtline)
                    continue
                else:
                    spicelines.append('r' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + dmatch.group(3))
                    continue

            cmatch = cdlrex.match(line)
            if not cmatch:
                if not isspectre or 'capacitor' in line or 'resistor' in line:
                    cmatch = stddevrex.match(line)

            if cmatch:
                ispassed = False
                devtype = cmatch.group(1)
                devmodel = cmatch.group(4)

                # Handle spectreisms. . .
                if devmodel == 'capacitor':
                    devtype = 'c'
                    devmodel = ''
                elif devmodel == 'resistor':
                    devtype = 'r'
                    devmodel = ''
                # The "device model" might be a known (inline) subcircuit in
                # which case this is really a subcircuit.
                elif devmodel in subnames:
                    devtype = 'x' + devtype
                elif devtype.lower() == 'n' or devtype.lower() == 'p':
                    # May be specific to SkyWater models, or is it a spectreism?
                    # NOTE:  There is a check, below, to revisit this assignment
                    # and ensure that it matches the model type.
                    devtype = 'x' + devtype

                # If a capacitor or resistor value is a parameter or expression,
                # it must be enclosed in single quotes.  Otherwise, if the named
                # device model is a subcircuit, then the devtype must be "x".

                elif devtype.lower() == 'c' or devtype.lower() == 'r' or devtype.lower() == 'd':
                    if devmodel in subnames:
                        devtype = 'x' + devtype
                    else:
                        devvalue = devmodel.split('=')
                        if len(devvalue) > 1:
                            if "'" in devvalue[1] or "{" in devvalue[1]:
                                # Re-parse this catching everything in delimiters,
                                # including spaces.
                                cmatch2 = stddev2rex.match(line)
                                if cmatch2:
                                    cmatch = cmatch2
                                    devtype = cmatch.group(1)
                                    devmodel = cmatch.group(4)
                                    devvalue = devmodel.split('=')

                            if  isexprrex.search(devvalue[1]):
                                if devvalue[1].strip("'") == devvalue[1]:
                                    devmodel = devvalue[0] + "='" + devvalue[1] + "'"
                        else:
                            if devmodel in paramnames or isexprrex.search(devmodel):
                                if devmodel.strip("'") == devmodel:
                                    devmodel = "'" + devmodel + "'"

                fmtline, ispassed = parse_param_line(cmatch.group(5), True, insub, True, ispassed, inmodel, linenum)
                if fmtline != '':
                    inparam = True
                    spicelines.append(devtype + cmatch.group(2) + ' ' + cmatch.group(3) + ' ' + devmodel + ' ' + fmtline)
                    continue
                else:
                    spicelines.append(devtype + cmatch.group(2) + ' ' + cmatch.group(3) + ' ' + devmodel + ' ' + cmatch.group(5))
                    continue

            # Check for a .param line and collect parameter names
            pmatch = paramrex.match(line)
            if pmatch:
                paramnames.extend(get_param_names(pmatch.group(1)))

            # Check for a line that begins with the subcircuit name

            dmatch = devrex.match(line)
            if dmatch:
                fmtline, ispassed = parse_param_line(dmatch.group(3), True, insub, True, ispassed, inmodel, linenum)
                if fmtline != '':
                    inparam = True
                    calllines.append(subname + ' ' + dmatch.group(1) + ' ' + dmatch.group(2) + ' ' + fmtline)
                    continue
                else:
                    inparam = True
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
                rest = bmatch.group(2)

                # If there is a binned model then it replaces any original
                # model line that was saved.
                if modellines[-1].startswith('.model'):
                    modellines = modellines[0:-1]
                modellines.append('')
                modellines.append('.model ' + modname + '.' + bin + ' ZYXW')

                if rest != '':
                    # Somehow model numbers are allowed to break syntax and
                    # not start a new line with a continuation character.
                    if rest[0] == '+':
                        line = rest
                    else:
                        line = '+' + rest
                else:
                    continue

            fmtline, ispassed = parse_param_line(line, True, True, False, ispassed, inmodel, linenum)
            if fmtline != '':
                modellines.append(fmtline)
                continue

        # Copy line as-is
        spicelines.append(line)

    # If any model lines remain at end, append them before output
    if modellines != []:
        spicelines.extend(addmodel(modellines, linenum))
        modellines = []
        inmodel = False

    # Any 'D'-type diode with "perim =" needs to have it changed to "pj ="
    # (NOTE:  Need more generic handling here, as perimeter parameter
    # could be in a continuation line)

    perimrex = re.compile('perim([ \t]*=[ \t]*)', re.IGNORECASE)
    for j in range(len(spicelines)):
        line = spicelines[j]
        if len(line) > 1 and line[0].lower() == 'd':
            spicelines[j] = perimrex.sub('pj\g<1>', line)

    # Catching the spectre use of "m" is difficult, so do another pass
    # on "spicelines" to catch which subcircuits use "*m" expressions,
    # then for those subcircuits, add "mult=1" to the subcircuit
    # parameters.  (NOTE:  Need a more generic regular expression here)

    sqrtrex = re.compile('.*(sqrt\([ \t]*[^ \t]+[ \t]*\*[ \t]*)m[ \t]*\)', re.IGNORECASE)
    sqsubrex = re.compile('(sqrt\([ \t]*[^ \t]+[ \t]*\*[ \t]*)m[ \t]*\)', re.IGNORECASE)
    subrex = re.compile('\.subckt[ \t]+([^ \t\(]+)[ \t]*', re.IGNORECASE)
    needmult = []
    for j in range(len(spicelines)):
        line = spicelines[j]
        smatch = subrex.match(line)
        if smatch:
            cursub = smatch.group(1)
        smatch = sqrtrex.match(line)
        if smatch:
            spicelines[j] = sqsubrex.sub('\g<1>mult)', line)
            needmult.append(cursub)

    # Now add "mult=1" parameter to any subcircuit in the "needmult" list
    for j in range(len(spicelines)):
        line = spicelines[j]
        smatch = subrex.match(line)
        if smatch:
            spicelines[j] = line + ' mult=1'

    # Check for resistor models using "tc1r" and "tc2r"
    rmodrex = re.compile('.*[ \t]+tc[12]r[ \t]+=', re.IGNORECASE)
    for j in range(len(spicelines)):
        line = spicelines[j]
        rmatch = rmodrex.match(line)
        if rmatch:
            spicelines[j] = re.sub('([ \t]+tc[12])r([ \t])', '\g<1>\g<2>', line)

    # Output the result to out_file.
    with open(out_file, 'w') as ofile:
        for line in spicelines:
            print(line, file=ofile)

    # Debug info
    # print('Defined subcircuits: ' + ' '.join(subnames))

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to spectre_to_spice.py.")
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
        print("Wrong number of arguments given to spectre_to_spice.py.")
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

            # .scs files are purely spectre and meaningless to SPICE, so ignore them.
            if fileext == '.scs':
                continue

            froot = os.path.split(filename)[1]
            convert_file(filename, spicepath + '/' + froot)

    print('Done.')
    exit(0)
