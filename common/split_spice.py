#!/usr/bin/env python3
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


import glob
import os
import re
import subprocess
import sys


def write_file(out_path, out_file, lines, mode):

    opath = os.path.join(out_path, out_file)
    if not os.path.exists(opath):
        with open(opath, 'w') as f:
            for l in lines:
                f.write(l)
                f.write('\n')
        print("Wrote new      file:", opath)
    else:
        print("Found existing file:", opath, end=" ")
        existing = open(opath).read().splitlines()

        try:
            if mode == "include":
                for line in lines:
                    assert line in existing, "Line {} missing from {}".format(repr(line), opath)
                assert "\n".join(lines) in "\n".join(existing)
                print("included")
            elif mode == "match":
                assert "\n".join(lines) == "\n".join(existing)
                print("matches")
            else:
                raise ValueError("unknown mode: {}".format(mode))
        except AssertionError:
            print(flush=True)
            print("Wrote new      file:", opath+'.new')
            with open(opath+'.new', 'w') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')

            print("-"*75)
            subprocess.call('diff -u {0} {0}.new'.format(opath), shell=True)
            print("="*75)
            print(flush=True)
            #raise


def usage():
    print('split_spice.py <path_to_input> <path_to_output>')


def convert_file(in_file, out_path, out_file):
    print("Starting to split", in_file)
    # Regexp patterns
    paramrex = re.compile('\.param[ \t]+(.*)')
    subrex = re.compile('\.subckt[ \t]+([^ \t]+)[ \t]+([^ \t]*)')
    modelrex = re.compile('\.model[ \t]+([^ \t]+)[ \t]+([^ \t]+)[ \t]+(.*)')
    endsubrex = re.compile('\.ends[ \t]+(.+)')
    increx = re.compile('\.include[ \t]+')

    with open(in_file, 'r') as ifile:
        idata = ifile.read()

    inplines = idata.splitlines()

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

        if subname == 'xrdn':
            print('handling line in xrdn, file ' + in_file + ': "' + line + '"')

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

        # Item 3.  Handle blank lines like comment lines
        if line.strip() == '':
            if subname == 'xrdn':
                print('blank line in xrdn subcircuit')
            if subcktlines != []:
                subcktlines.append(line)
            else:
                spicelines.append(line)
            continue

        # Item 4.  Handle continuation lines
        if contline:
            if inparam:
                # Continue handling parameters
                if subcktlines != []:
                    subcktlines.append(line)
                else:
                    spicelines.append(line)
                continue

        # Item 5.  Regexp matching

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
                        print('    "ends" name = ' + ematch.group(1))
                        print('  "subckt" name = ' + subname)

                    subcktlines.append(line)

                    # Dump the contents of subcktlines into a file
                    write_file(out_path, subname + '.spice', subcktlines, 'match')

                    subcktlines = []
                    # Add an include statement to this file in the source
                    spicelines.append('.include ' + subckt_file)

                    insubckt = False
                    inmodel = False
                    subname = ''
                    continue

        # Copy line as-is
        if insubckt:
            subcktlines.append(line)
        else:
            spicelines.append(line)

    assert not subcktlines, "Found subcktlines at end of parsing file!\n"+'\n'.join(subcktlines)

    # Output the result to out_file.
    write_file(out_path, out_file, spicelines, 'include')


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

    if not os.path.exists(outpath):
        os.makedirs(outpath)
    else:
        assert os.path.isdir(outpath), outpath

    if do_one_file:
        froot = os.path.basename(inpath)

        convert_file(inpath, outpath, froot)

    else:
        infilelist = glob.glob(inpath + '/*')

        for filename in infilelist:
            fileext = os.path.splitext(filename)[1]

            # Ignore verilog or verilog-A files that might be in a model directory
            if fileext == '.v' or fileext == '.va':
                continue

            froot = os.path.split(filename)[1]
            print()
            convert_file(filename, outpath, froot)
            print()

    exit(0)
