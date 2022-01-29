#!/usr/bin/env python3
#
# fix_subckt_params.py --
#
# Modify SPICE subcircuit definitions in files where parameters are listed
# in a ".param" block in the subcircuit and are therefore local parameters
# that cannot be passed to the subcircuit, and move them into the subcircuit
# pin list as parameters that can be passed to the subcircuit.
#
# The arguments are <path_to_input>, <path_to_output>, and <param> ...
# <path_to_input> should be the path to a single file, while
# <path_to_output> is the path to a directory where the split files will
# be put.  <params> ... is a whitespace-separated (i.e., one parameter,
# one argument) list of parameter names that should be moved up from the
# ".param" section to the ".subckt" line.  If <param> is preceded with "-",
# then the parameter will be moved from the .subckt line down to the
# .param section.

import os
import sys
import re
import glob

def usage():
    print('fix_subckt_params.py <path_to_input> <path_to_output> <param> ...')
    print('where:')
    print('   <path_to_input> is the path to the input file to parse')
    print('   <path_to_output> is the directory to place the modified input file')
    print('   <param> ... is a space-separated list of parameters that should')
    print('        be in the subcircuit line and not the .param block')

# Parse a parameter line for parameters, and divide into two parts,
# returned as a list.  If a parameter name matches an entry in 'params',
# it goes in the second list.  Otherwise, it goes in the first list.
# The first list is returned as-is minus any parameters that were split
# into the second list.  The second list must begin with '+', as it will
# be output as a continuation line for the subcircuit.

def param_split(line, params, debug):
    # Regexp patterns
    parm1rex = re.compile('(\.param[ \t]+)(.*)')
    parm2rex = re.compile('(\+[ \t]*)(.*)')
    parm3rex = re.compile('([^= \t]+)([ \t]*=[ \t]*[^ \t]+[ \t]*)(.*)')
    parm4rex = re.compile('([^= \t]+)([ \t]*)(.*)')

    part1 = ''
    part2 = ''

    if debug:
        print('Diagnostic:  param line in = "' + line + '"')

    pmatch = parm1rex.match(line)
    if pmatch:
        part1 = pmatch.group(1)
        rest = pmatch.group(2)
    else:
        pmatch = parm2rex.match(line)
        if pmatch:
            rest = pmatch.group(2)
        else:
            # Could not parse;  return list with line and empty string
            return [line, '']

    while rest != '':
        pmatch = parm3rex.match(rest)
        if pmatch:
            rest = pmatch.group(3)
            pname = pmatch.group(1)
            if pname in params:
                if part2 == '':
                    part2 = '+ '
                part2 += pname + pmatch.group(2)
            else:
                if part1 == '':
                    part1 = '+ '
                part1 += pname + pmatch.group(2)
        else:
            pmatch = parm4rex.match(rest)
            if pmatch:
                rest = pmatch.group(3)
                pname = pmatch.group(1)
                if pname in params:
                    if part2 == '':
                        part2 = '+ '
                    part2 += pname + pmatch.group(2)
                else:
                    if part1 == '':
                        part1 = '+ '
                    part1 += pname + pmatch.group(2)

    if debug:
        print('Diagnostic:  param line out = "' + part1 + '" and "' + part2 + '"')
    return [part1, part2]

def convert_file(in_file, out_path, params, debug):

    # Regexp patterns
    paramrex = re.compile('\.param[ \t]+(.*)')
    subrex = re.compile('\.subckt[ \t]+([^ \t]+)[ \t]+([^ \t]*)')
    modelrex = re.compile('\.model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+(.*)')
    endsubrex = re.compile('\.ends[ \t]+(.+)')
    increx = re.compile('\.include[ \t]+')

    with open(in_file, 'r') as ifile:
        inplines = ifile.read().splitlines()

    insubckt = False
    inparam = False
    inmodel = False
    inpinlist = False

    # Output lines
    spicelines = []
    paramlines = []
    subparams = []

    for line in inplines:

        # Item 1.  Handle comment lines
        if line.startswith('*'):
            spicelines.append(line.strip())
            continue

        # Item 2.  Flag continuation lines.
        if line.startswith('+'):
            contline = True
        else:
            contline = False
            if line.strip() != '':
                if inpinlist:
                    inpinlist = False
                if inparam:
                    # Dump additional subcircuit parameters and clear
                    if subparams:
                        spicelines.extend(subparams)
                        subparams = []

                    # Dump parameters to file contents and clear
                    spicelines.extend(paramlines)
                    paramlines = []
                    inparam = False

        # Item 3.  Handle blank lines like comment lines
        if line.strip() == '':
            if inparam:
                paramlines.append(line)
            else:
                spicelines.append(line)
            continue

        # Item 4.  Handle continuation lines
        # Remove lines that have a continuation mark and nothing else.
        if contline:
            if inparam:
                # Continue handling parameters
                if insubckt:
                    # Find subcircuit parameters and record what line they were found on
                    psplit = param_split(line, params, debug)
                    if psplit[0]:
                        paramlines.append(psplit[0])
                    if psplit[1]:
                        subparams.append(psplit[1])
                else:
                    paramlines.append(line)
            else:
                if line.strip() != '+':
                    spicelines.append(line)
            continue

        # Item 5.  Regexp matching

        # parameters
        pmatch = paramrex.match(line)
        if pmatch:
            inparam = True
            if insubckt:
                # Find subcircuit parameters and record what line they were found on
                psplit = param_split(line, params, debug)
                if psplit[0]:
                    paramlines.append(psplit[0])
                if psplit[1]:
                    subparams.append(psplit[1])
            else:
                paramlines.append(line)
            continue

        # model
        mmatch = modelrex.match(line)
        if mmatch:
            spicelines.append(line)
            continue
            inmodel = 2
            continue

        if not insubckt:
            # Things to parse if not in a subcircuit

            imatch = subrex.match(line)
            if imatch:
                insubckt = True
                inpinlist = True
                spicelines.append(line)
                continue

        else:
            # Things to parse when inside of a ".subckt" block

            if inpinlist:
                spicelines.append(line)
                continue

            else:
                ematch = endsubrex.match(line)
                if ematch:
                    spicelines.append(line)
                    insubckt = False
                    inmodel = False
                    continue

        # Copy line as-is
        spicelines.append(line)

    # Output the result to out_file.
    out_file = os.path.split(in_file)[1]
    with open(out_path + '/' + out_file, 'w') as ofile:
        for line in spicelines:
            print(line, file=ofile)

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to fix_subckt_params.py.")
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) < 3:
        print("Wrong number of arguments given to fix_subckt_params.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    inpath = arguments[0]
    outpath = arguments[1]
    params = arguments[2:]

    if not os.path.exists(inpath):
        print('No such source file ' + inpath)
        sys.exit(1)

    if not os.path.isfile(inpath):
        print('Input path ' + inpath + ' is not a file.')
        sys.exit(1)

    convert_file(inpath, outpath, params, debug)

    print('Done.')
    exit(0)
