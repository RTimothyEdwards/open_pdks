#!/usr/bin/env python3
#--------------------------------------------------------------------
#
# save_commit_refs.py
#
# This file is used to annotate a standard tech information JSON
# file.  Each JSON file should have a section called "reference"
# (if not, this script exits without doing anything).  The
# "reference" section contains the commit hashes of repositories
# used by the developer for generating the PDK, creating a
# reference against which issues can be compared.  The "reference"
# section is fixed and is not modified by replacement like the
# rest of the JSON file.  It is the duty of the PDK developer to
# update the references section periodically by running "make
# reference".
#
#--------------------------------------------------------------------
# Usage:
#
#	save_commit_refs.py <filename> [-D<variable> ...]
#
# Where <filename> is the name of a technology JSON file, and
# <variable> may be a <keyword>=<hash_value> pair only.
# <keyword> corresponds to the variable name in a technology Makefile
# for a commit hash that appears somewhere in <filename>.  <value>
# is the commit hash value corresponding to <keyword>.
#
# The JSON file "reference" section is expected to have entries of
# the form
#	"<name>": "<commit_hash>"
#
# where <name> must also appear elsewhere in <filename> in an entry
# of the form
#	"<name>": "<keyword>"
#
# Then, where "-D<keyword>=<hash_value>" has been passed to the
# script on the command line, the entry in the "reference" section
# is changed by replacing "<commit_hash>" with "<hash_value>".
#
# The output of the script overwrites <filename> with the modified
# contents.
#
# Example:
#	sky130.json has an entry in "reference":
#		"magic": "fe2eb6d3906ed15ade0e7a51daea80dd4e3846e2"
#	reflecting the git commit number of the program "magic" at
#	the time the developer last ran save_commit_refs.py.
#	Elsewhere in sky130.json, the following line appears:
#		"magic": "MAGIC_COMMIT"
#	If save_commit_refs.py is called as:
#		save_commit_refs.py sky130.json -DMAGIC_COMMIT=abcdef
#	then the line in "reference" will be changed to:
#		"magic": "abcdef"
#
#--------------------------------------------------------------------

import os
import re
import sys

def runsubs(keys, defines, inputfile, outputfile):

    ifile = False
    ifile = open(inputfile, 'r')
    if not ifile:
        print("Error:  Cannot open file " + inputfile + " for reading.\n", file=sys.stderr)
        return

    indist = False

    filetext = ifile.readlines()
    lastline = []

    # Input file has been read, so close it.
    ifile.close()

    # Open output file
    if not outputfile:
        outputfile = inputfile

    ofile = open(outputfile, 'w')
    if not ofile:
        print("Error:  Cannot open file " + outputfile + " for writing.\n", file=sys.stderr)
        return

    keyrex = re.compile('[ \t]*"([^"]+)":[ \t]*"[^"]+"')
    valuerex = re.compile('[ \t]*"[^"]+":[ \t]*"([a-z0-9]+)"')
    distdefs = {}
    defs = []

    for line in filetext:
        newline = line

        if indist == False:
            if '"reference":' in line:
                indist = True
            else:
                # Find values matching keywords
                for key in keys:
                    if key in line:
                        kmatch = keyrex.match(line)
                        if kmatch:
                            print('Found match "' + kmatch.group(1) + '" for key "' + key + '"')
                            distdefs[kmatch.group(1)] = defines[key]
                            defs.append(kmatch.group(1))
        else:
            # Find definitions matching keywords
            for defx in defs:
                if defx in line:
                    vmatch = valuerex.match(line)
                    if vmatch:
                        value = distdefs[defx]
                        newline = line.replace(vmatch.group(1), value)

        print(newline, file=ofile, end='')

    ofile.close()
    return

def printusage(progname):
    print('Usage: ' + progname + ' filename [-options]')
    print('   Options are:')
    print('      -help         Print this help text.')
    print('      -quiet        Stop without error if input file is not found.')
    print('      -ccomm        Remove C comments in /* ... */ delimiters.')
    print('      -D<def>       Define word <def> and set its value to 1.')
    print('      -D<def>=<val> Define word <def> and set its value to <val>.')
    print('      -I<dir>       Add <dir> to search path for input files.')
    return

if __name__ == '__main__':

   # Parse command line for options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    if len(arguments) > 0:
        inputfile = arguments[0]
        if len(arguments) > 1:
            outputfile = arguments[1]
        else:
            outputfile = []
    else:
        printusage(sys.argv[0])
        sys.exit(0)

    defines = {}
    keys = []
    for item in options:
        result = item.split('=')
        if result[0] == '-help':
            printusage(sys.argv[0])
            sys.exit(0)
        elif result[0][0:2] == '-D':
            keyword = result[0][2:]
            value = result[1]
            defines[keyword] = value
            keys.append(keyword)
        else:
            print('Bad option ' + item + ', options are -help, -D<def>\n')
            sys.exit(1)

    if not os.path.isfile(inputfile):
        if not quiet:
            print("Error:  No input file " + inputfile + " found.")
        else:
            sys.exit(0)

    runsubs(keys, defines, inputfile, outputfile)

    # Set mode of outputfile to be equal to that of inputfile (if not stdout)
    if outputfile:
        statinfo = os.stat(inputfile)
        mode = statinfo.st_mode
        os.chmod(outputfile, mode)

    sys.exit(0)
