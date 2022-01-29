#!/usr/bin/env python3
#
# split_one_spice.py --
#
# Script that reads a SPICE file that contains multiple models and
# subcircuits, and splits it into one file per subcircuit, with each
# file containing any related in-lined models.
#
# The arguments are <path_to_input> and <path_to_output>.
# <path_to_input> should be the path to a single file, while
# <path_to_output> is the path to a directory where the split files will
# be put.

import os
import sys
import re
import glob

def usage():
    print('split_one_spice.py <path_to_input> <path_to_output>')

def convert_file(in_file, out_path):

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
    subname = ''
    modname = ''
    modtype = ''

    # Keep track of what the subcircuit names are
    subnames = []
    filenos = {}

    # Keep track of what parameters are used by what subcircuits
    paramlist = {}

    # Enumerate which lines go to which files
    linedest = [-1]*len(inplines)
    fileno = -1;
    lineno = -1;

    for line in inplines:
        lineno += 1

        # Item 1.  Handle comment lines
        if line.startswith('*'):
            linedest[lineno] = fileno
            continue

        # Item 2.  Flag continuation lines
        if line.startswith('+'):
            contline = True
        else:
            contline = False
            if line.strip() != '':
                if inparam:
                    inparam = False
                if inpinlist:
                    inpinlist = False

        # Item 3.  Handle blank lines like comment lines
        if line.strip() == '':
            linedest[lineno] = fileno
            continue

        # Item 4.  Handle continuation lines
        if contline:
            if inparam:
                # Continue handling parameters
                linedest[lineno] = fileno
                if not insubckt:
                    # Find (global) parameters and record what line they were found on
                    ptok = list(item for item in line[1:].strip().split() if item != '=')
                    for param, value in zip(*[iter(ptok)]*2):
                        paramlist[param] = lineno
                else:
                    # Find if a global parameter was used.  Assign it to this
                    # subcircuit.  If it has already been used, assign it to
                    # be a common parameter
                    for param in paramlist:
                        if param in line[1:]:
                            checkfile = linedest[paramlist[param]]
                            if checkfile == -1:
                                linedest[paramlist[param]] = fileno
                            elif checkfile != fileno:
                                linedest[paramlist[param]] = -3
                continue

        # Item 5.  Regexp matching

        # parameters
        pmatch = paramrex.match(line)
        if pmatch:
            inparam = True
            linedest[lineno] = fileno
            if not insubckt:
                # Find (global) parameters and record what line they were found on
                ptok = list(item for item in pmatch.group(1).split() if item != '=')
                for param, value in zip(*[iter(ptok)]*2):
                    paramlist[param] = lineno
            else:
                # Find if a global parameter was used.  Assign it to this
                # subcircuit.  If it has already been used, assign it to
                # be a common parameter
                for param in paramlist:
                    if param in pmatch.group(1):
                        checkfile = linedest[paramlist[param]]
                        if checkfile == -1:
                            linedest[paramlist[param]] = fileno
                        if checkfile != fileno:
                            linedest[paramlist[param]] = -3
            continue

        # model
        mmatch = modelrex.match(line)
        if mmatch:
            modname = mmatch.group(1)
            modtype = mmatch.group(2)

            linedest[lineno] = fileno
            inmodel = 2
            continue

        if not insubckt:
            # Things to parse if not in a subcircuit

            imatch = subrex.match(line)
            if imatch:
                insubckt = True
                subname = imatch.group(1)
                fileno = len(subnames)
                subnames.append(subname)
                filenos[subname] = fileno

                if fileno > 0:
                    # If this is not the first subcircuit, then add all blank
                    # and comment lines above it to the same file

                    lastno = -1
                    tline = lineno - 1
                    while tline >= 0:
                        tinp = inplines[tline]
                        # Backup through all comment and blank lines
                        if not tinp.startswith('*') and not tinp.strip() == '':
                            lastno = linedest[tline]
                            tline += 1;
                            break;
                        tline -= 1;

                    while tline < lineno:
                        # Forward through all blank lines, and assign them to
                        # the previous subcell.
                        tinp = inplines[tline]
                        if tinp.strip() != '':
                            break;
                        if linedest[tline] == -1:
                            linedest[tline] = lastno
                        tline += 1;

                    while tline < lineno:
                        linedest[tline] = fileno
                        tline += 1;
                else:
                    # If this is the first subcircuit encountered, then assign
                    # to it the nearest block of comment lines before it.  If
                    # those comment lines include a parameter or statistics
                    # block, then abandon the effort.

                    # Backup through blank lines immediately above
                    abandon = False
                    tline = lineno - 1
                    while tline >= 0:
                        tinp = inplines[tline]
                        if not tinp.strip() == '':
                            break;
                        tline -= 1;

                    while tline > 0:
                        # Backup through the next comment block above
                        tinp = inplines[tline]
                        if not tinp.startswith('*'):
                            tline += 1;
                            break;
                        elif tinp.strip('*').strip().startswith('statistics'):
                            abandon = True
                        tline -= 1;

                    if tline == 0:
                        abandon = True

                    if not abandon:
                        while tline < lineno:
                            linedest[tline] = fileno
                            tline += 1;

                devrex = re.compile(subname + '[ \t]*([^ \t]+)[ \t]*([^ \t]+)[ \t]*(.*)', re.IGNORECASE)
                inpinlist = True
                linedest[lineno] = fileno
                continue

        else:
            # Things to parse when inside of a ".subckt" block

            if inpinlist:
                # Watch for pin list continuation line.
                linedest[lineno] = fileno
                continue

            else:
                ematch = endsubrex.match(line)
                if ematch:
                    if ematch.group(1) != subname:
                        print('Error:  "ends" name does not match "subckt" name!')
                        print('"ends" name = ' + ematch.group(1))
                        print('"subckt" name = ' + subname)

                    linedest[lineno] = fileno
                    fileno = -1

                    insubckt = False
                    inmodel = False
                    subname = ''
                    continue
                else:
                    linedest[lineno] = fileno
                    continue

    # Sort subcircuit names
    subnames.sort(reverse=True)

    # Look for any lines containing parameters in paramlist.  If those lines
    # are unassigned (-1), then assign them to the same cell that the parameter
    # was assigned to.  NOTE:  Assumes that there will never be two parameters
    # on the same line that were from two different subcircuits that is not
    # already marked as a common parameter.

    lineno = -1
    for line in inplines:
        lineno += 1
        if linedest[lineno] == -1:
            for param in paramlist:
                if param in line:
                    linedest[lineno] = linedest[paramlist[param]]
                    break

    # Ad hoc method:  Look for any lines containing each cell name, and assign
    # that line to the cell.  That isolates parameters that belong to only one
    # cell.  Ignore comment lines from line 1 down to the first non-comment line.
    # Since all parameters and comment blocks have been handled, this is not
    # likely to change anything.

    lineno = -1
    for line in inplines:
        lineno = -1
        if not line.startswith('*'):
            break

    topcomm = True
    for line in inplines:
        lineno += 1
        if topcomm and not line.startswith('*'):
            topcomm = False

        if not topcomm:
            if linedest[lineno] == -1:
                for subname in subnames:
                    subno = filenos[subname]
                    if subname in line:
                        linedest[lineno] = subno
                        break

    # All lines marked -1 except for comment lines should be remarked -3
    # (go into the common file only)

    lineno = -1
    for line in inplines:
        lineno += 1
        if linedest[lineno] == -1:
            if not line.startswith('*'):
                linedest[lineno] = -3

    # All comment lines that are surrounded by lines marked -3 should
    # also be marked -3.  This keeps comments that are completely inside
    # blocks that are only in the common file out of the individual files.
    # ignore "* statistics" and "* mismatch" lines.

    lineno = 0
    for line in inplines[1:]:
        lineno += 1
        if line.startswith('*') and ('statistics' in line or 'mismatch' in line):
            continue
        if linedest[lineno] == -1 and linedest[lineno - 1] == -3:
            testline = lineno + 1
            while linedest[testline] == -1:
                testline += 1
            if linedest[testline] == -3:
                testline = lineno
                while linedest[testline] == -1:
                    linedest[testline] = -3
                    testline += 1

    froot = os.path.split(in_file)[1]
    for subname in subnames:
        subno = filenos[subname]
        fext = os.path.splitext(in_file)[1]

        # Guard against one of the split files having the same name as
        # the original, since we need to keep the original file.
        if subname == os.path.splitext(froot)[0]:
            fext = '_split' + fext

        # Output the result to out_file.
        with open(out_path + '/' + subname + fext, 'w') as ofile:
            firstline = True
            lineno = -1
            for line in inplines:
                lineno += 1
                if linedest[lineno] == subno or linedest[lineno] == -1:
                    if firstline:
                        print('* File ' + subname + fext + ' split from ' + froot + ' by split_one_spice.py', file=ofile)
                        firstline = False
                    print(line, file=ofile)

    # Debug:  Print one diagnostic file (do this before messing with the
    # linedest[] entries in the next step).  This debug file shows which
    # lines of the file are split into which file, and which lines are
    # common.

    ffile = os.path.split(in_file)[1]
    froot = os.path.splitext(ffile)[0]
    fext = os.path.splitext(ffile)[1]

    with open(out_path + '/' + froot + '_debug' + fext, 'w') as ofile:
        for subname in subnames:
            subno = filenos[subname]
            print(str(subno) + '\t' + subname, file=ofile)

        print('\n', file=ofile)

        lineno = -1
        for line in inplines:
            lineno += 1
            print(str(linedest[lineno]) + '\t' + line, file=ofile)

    # Reset all linedest[] entries except the bottommost entry for each subcircuit.
    lineno = len(inplines)
    subrefs = [0] * len(subnames)
    while lineno > 0:
        lineno -= 1
        if linedest[lineno] >= 0:
            if subrefs[linedest[lineno]] == 0:
                subrefs[linedest[lineno]] = 1
            else:
                linedest[lineno] = -2

    # Print the original file, including each of the new files.
    # Also print out all lines marked "-1" or "-3"

    with open(out_path + '/' + froot +  fext, 'w') as ofile:
        lineno = -1
        subno = -1
        for line in inplines:
            lineno += 1
            if linedest[lineno] == -1 or linedest[lineno] == -3 :
                print(line, file=ofile)
            elif linedest[lineno] >= 0:
                for subname in subnames:
                    if filenos[subname] == linedest[lineno]:
                        fext = os.path.splitext(in_file)[1]
                        if subname == os.path.splitext(froot)[0]:
                            fext = '_split' + fext
                        break
                print('.include ' + subname + fext, file=ofile)
                subno = linedest[lineno]

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to split_one_spice.py.")
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
        print("Wrong number of arguments given to split_one_spice.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    inpath = arguments[0]
    outpath = arguments[1]
    do_one_file = False

    if not os.path.exists(inpath):
        print('No such source file ' + inpath)
        sys.exit(1)

    if not os.path.isfile(inpath):
        print('Input path ' + inpath + ' is not a file.')
        sys.exit(1)

    convert_file(inpath, outpath)

    print('Done.')
    exit(0)
