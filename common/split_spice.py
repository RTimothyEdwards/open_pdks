#!/bin/env python3
#
# split_spice.py --
#
# Script that reads the SPICE output from the convert_spectre.py script,
# which typically has parsed through files containing inline subcircuits
# and recast them as normal SPICE .subckt ... .ends entries, and pulled
# any model blocks inside the inline subckt out.  This script removes
# each .subckt ... .ends block from every file and moves it to its own
# file named <subckt_name>.spice.
#
# The arguments are <path_to_input> and <path_to_output>.  If there is
# only one argument, or if <path_to_input> is equal to <path_to_output>,
# then the new .spice files are added to the directory and the model
# files are modified in place.  Otherwise, all modified files are placed
# in <path_to_output>.

import os
import sys
import re
import glob

def usage():
    print('split_spice.py <path_to_input> <path_to_output>')

def convert_file(in_file, out_path, out_file):

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
    spicelines = []
    subcktlines = []
    savematch = None
    subname = ''
    modname = ''
    modtype = ''

    for line in inplines:

        # Item 1.  Handle comment lines
        if line.startswith('*'):
            if subcktlines != []:
                subcktlines.append(line.strip())
            else:
                spicelines.append(line.strip())
            continue

        # Item 2.  Flag continuation lines
        if line.startswith('+'):
            contline = True
        else:
            contline = False
            if inparam:
                inparam = False 
            if inpinlist:
                inpinlist = False 

        # Item 3.  Handle continuation lines
        if contline:
            if inparam:
                # Continue handling parameters
                if subcktlines != []:
                    subcktlines.append(line)
                else:
                    spicelines.append(line)
                continue

        # Item 4.  Regexp matching

        # If inside a subcircuit, remove "parameters".  If outside,
        # change it to ".param"
        pmatch = paramrex.match(line)
        if pmatch:
            inparam = True
            if insubckt:
                subcktlines.append(line)
            else:
                spicelines.append(line)
            continue
        
        # model
        mmatch = modelrex.match(line)
        if mmatch:
            modellines = []
            modname = mmatch.group(1)
            modtype = mmatch.group(2)

            spicelines.append(line)
            inmodel = 2
            continue

        if not insubckt:
            # Things to parse if not in a subcircuit

            imatch = subrex.match(line)
            if imatch:
                insubckt = True
                subname = imatch.group(1)
                devrex = re.compile(subname + '[ \t]*([^ \t]+)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
                inpinlist = True
                subcktlines.append(line)
                continue

        else:
            # Things to parse when inside of a ".subckt" block

            if inpinlist:
                # Watch for pin list continuation line.
                subcktlines.append(line)
                continue
                
            else:
                ematch = endsubrex.match(line)
                if ematch:
                    if ematch.group(1) != subname:
                        print('Error:  "ends" name does not match "subckt" name!')
                        print('"ends" name = ' + ematch.group(1))
                        print('"subckt" name = ' + subname)

                    subcktlines.append(line)

                    # Dump the contents of subcktlines into a file
                    subckt_file = subname + '.spice'
                    with open(out_path + '/' + subckt_file, 'w') as ofile:
                        print('* Subcircuit definition of cell ' + subname, file=ofile)
                        for line in subcktlines:
                            print(line, file=ofile)
                        subcktlines = []

                    insubckt = False
                    inmodel = False
                    subname = ''
                    continue

        # Copy line as-is
        if insubckt:
            subcktlines.append(line)
        else:
            spicelines.append(line)

    # Output the result to out_file.
    with open(out_path + '/' + out_file, 'w') as ofile:
        for line in spicelines:
            print(line, file=ofile)

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to split_spice.py.")
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
        print("Wrong number of arguments given to split_spice.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    inpath = arguments[0]
    outpath = arguments[1]
    do_one_file = False

    if not os.path.exists(inpath):
        print('No such source directory ' + inpath)
        sys.exit(1)

    if os.path.isfile(inpath):
        do_one_file = True

    if do_one_file:
        if os.path.exists(outpath):
            print('Error:  File ' + outpath + ' exists.')
            sys.exit(1)
        convert_file(inpath, outpath)

    else:
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        infilelist = glob.glob(inpath + '/*')

        for filename in infilelist:
            fileext = os.path.splitext(filename)[1]

            # Ignore verilog or verilog-A files that might be in a model directory
            if fileext == '.v' or fileext == '.va':
                continue

            froot = os.path.split(filename)[1]
            convert_file(filename, outpath, froot)

    print('Done.')
    exit(0)
