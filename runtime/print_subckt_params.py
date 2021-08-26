#!/usr/bin/env python3
#
# print_subckt_params.py --
#
# Print a list of subcircuit parameters, dividing them into those which
# are declared on the subcircuit line, and those that are declared inside
# the scope of the subcircuit.
# 
# The single argument is <path_to_input>
# <path_to_input> should be the path to a single file.

import os
import sys
import re
import glob

def usage():
    print('print_subckt_params.py <path_to_input>')
    print('where:')
    print('   <path_to_input> is the path to the input file to parse')

def parse_pins(line, debug):
    # Regexp patterns
    subrex = re.compile('\.subckt[ \t]+[^ \t]+[ \t]+(.*)')
    parm1rex = re.compile('([^= \t]+)[ \t]*=[ \t]*[^ \t]+[ \t]*(.*)')
    parm2rex = re.compile('([^= \t]+)[ \t]*(.*)')

    params = []

    pmatch = subrex.match(line)
    if pmatch:
        rest = pmatch.group(1)
    else:
        # Could not parse
        return []

    while rest != '':
        if rest.startswith('$ '):
            break
        pmatch = parm1rex.match(rest)
        if pmatch:
            rest = pmatch.group(2)
            params.append(pmatch.group(1))
        else:
            pmatch = parm2rex.match(rest)
            if pmatch:
                # This is a pin, so don't list it
                rest = pmatch.group(2)

    return params

# Parse a parameter line for parameters, and divide into two parts,
# returned as a list.  If a parameter name matches an entry in 'params',
# it goes in the second list.  Otherwise, it goes in the first list.
# The first list is returned as-is minus any parameters that were split
# into the second list.  The second list must begin with '+', as it will
# be output as a continuation line for the subcircuit.

def param_parse(line, debug):
    # Regexp patterns
    parm1rex = re.compile('\.param[ \t]+(.*)')
    parm2rex = re.compile('\+[ \t]*(.*)')
    parm3rex = re.compile('([^= \t]+)[ \t]*=[ \t]*[^ \t]+[ \t]*(.*)')
    parm4rex = re.compile('([^= \t]+)[ \t]*(.*)')

    if debug:
        print('Diagnostic:  param line in = "' + line + '"')

    params = []

    pmatch = parm1rex.match(line)
    if pmatch:
        rest = pmatch.group(1)
    else:
        pmatch = parm2rex.match(line)
        if pmatch:
            rest = pmatch.group(1)
        else:
            # Could not parse;  return list with line and empty string
            return []

    while rest != '':
        if rest.startswith('$ '):
            break
        pmatch = parm3rex.match(rest)
        if pmatch:
            rest = pmatch.group(2)
            params.append(pmatch.group(1))
        else:
            pmatch = parm4rex.match(rest)
            if pmatch:
                rest = pmatch.group(2)
                params.append(pmatch.group(1))

    return params

def parse_file(in_file, debug):

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

    pinparams = []
    paramlist = []
    subname = ''

    for line in inplines:

        # Item 1.  Handle comment lines
        if line.startswith('*'):
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
                    inparam = False

        # Item 3.  Handle blank lines like comment lines
        if line.strip() == '':
            continue

        # Item 4.  Handle continuation lines
        # Remove lines that have a continuation mark and nothing else.
        if contline:
            if inparam:
                # Continue handling parameters
                if insubckt:
                    # Find subcircuit parameters and record what line they were found on
                    if inpinlist:
                        pinparams.extend(param_parse(line, debug))
                    else:
                        paramlist.extend(param_parse(line, debug))
                            
            continue

        # Item 5.  Regexp matching

        # parameters
        pmatch = paramrex.match(line)
        if pmatch:
            inparam = True
            if insubckt:
                if inpinlist:
                    inpinlist = False
                # Find subcircuit parameters and record what line they were found on
                paramlist.extend(param_parse(line, debug))
            continue

        # model
        mmatch = modelrex.match(line)
        if mmatch:
            inmodel = 2
            continue

        if not insubckt:
            # Things to parse if not in a subcircuit

            imatch = subrex.match(line)
            if imatch:
                insubckt = True
                inpinlist = True
                subname = imatch.group(1)
                pinparams = parse_pins(line, debug)
                paramlist = []
                continue

        else:
            ematch = endsubrex.match(line)
            if ematch:
                insubckt = False
                inmodel = False
                # Print out results
                if debug:
                    print('File: ', end='')
                print(in_file)
                if debug:
                    print('Subcircuit: ', end='')
                print(subname)
                if debug:
                    print('Callable parameters: ', end='')
                if len(pinparams) > 0:
                    print(' '.join(pinparams))
                else:
                    print('----')
                if debug:
                    print('Internal parameters: ', end='')
                if len(paramlist) > 0:
                    print(' '.join(paramlist))
                else:
                    print('----')
                print()
                continue

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to print_subckt_params.py.")
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) < 1:
        print("Wrong number of arguments given to print_subckt_params.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    inpath = arguments[0]

    if not os.path.exists(inpath):
        print('No such source file ' + inpath)
        sys.exit(1)

    parse_file(inpath, debug)
    exit(0)
