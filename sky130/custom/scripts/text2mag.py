#!/bin/env python3

# text2mag.py
#
# Read a text file from standard input and write out the text as an
# array of magic cells using the sky130_ml_xx_hd library.
#
# Adapted from the script by Paul Schulz <paul@mawsonlakes.org> in
# the sky130_ml_xx_hd repository.  Modified for open_pdks standard
# paths, and to take the text string as an argument in addition to
# stdin.

import getopt
import sys
import os
import subprocess


# Options
options, remainder = getopt.getopt(sys.argv[1:],
                                   'c:p:m:kh',
                                   ['cellname',
				    'pdk',
				    'message',
				    'keep',
                                    'help',
                                   ])

def usage(ofile):
    print('text2mag.py <options>', file=ofile)
    print('', file=ofile)
    print('  Options:', file=ofile)
    print('    [-c|--cellname]   - Required. Cell name to use.', file=ofile)
    print('    [-m|--message]    - Text to convert (default: use stdin).', file=ofile)
    print('    [-k|--keep]       - Keep generator script', file=ofile)     
    print('    [-h|--help]       - Display these details', file=ofile)

keep = False
message = None
cellname = None
for opt, arg in options:
    if opt in ('-c', '--cellname'):
        cellname = arg
    elif opt in ('-m', '--message'):
        message = arg
    elif opt in ('-k', '--keep'):
        keep = True
    elif opt in ('-h', '--help'):
        usage(sys.stdout)
        sys.exit(0)
    else:
        usage(sys.stderr)
        sys.exit(1)

if not cellname:
    usage(sys.stderr)
    print('', file=sys.stderr)
    print('*** cellname required', file=sys.stderr)
    sys.exit(1)

# Convert character ID to cellname
# Accepts character UTF-8 encodings

def get_cellname (ch):
    """Return name of cell used to store character data"""

    prefix = 'font_'

    if (ord(ch) < 0x100):
        cellname = '{:02X}'.format(ord(ch))
    elif (ord(ch) < 0x10000):
        cellname = '{:04X}'.format(ord(ch))
    elif (ord(ch) < 0x1000000):
        cellname = '{:06X}'.format(ord(ch))
    else:
        cellname = '{:X}'.format(ord(ch))

    return prefix + cellname

def write_text_generator(message, ofile):
    x = 0
    y = 0
    baselineskip = 400

    print('drc off', file=ofile)
    print('snap int', file=ofile)
    print('select top cell', file=ofile)
    print('box position 0 0', file=ofile)
    print('', file=ofile)

    # NOTE:  When a character is not found, substitute "?"

    for char in message:
        if char != '\n':
            filename = get_cellname(char)
            print('if {[catch {getcell ' + filename + ' child 0 0}]} {', file=ofile)
            print('   getcell font_3F child 0 0', file=ofile)
            print('}', file=ofile)
            print('pushstack', file=ofile)
            print('set bbox [property FIXED_BBOX]', file=ofile)
            print('set width [expr {[lindex $bbox 2] - [lindex $bbox 0]}]', file=ofile)
            print('popstack', file=ofile)
            print('box move e $width', file=ofile)
        else:
            x = 0
            y = y - baselineskip
            print('box position {} {}'.format(x,y), file=ofile)

    print('save ' + cellname, file=ofile)
    print('quit -noprompt', file=ofile)

##############################################################################
# Take message from stdin if not specified on the command line.

if not message:
    for line in sys.stdin:
        message = message + line

with open('gen_message.tcl', 'w') as ofile:
    write_text_generator(message, ofile)

    # Run magic with the text generator script as input.
    # NOTE:  Assumes that a .magicrc file exists at the target and that
    # it already includes the library in the search path.

    mproc = subprocess.run(['magic', '-dnull', '-noconsole', 'gen_message.tcl'],
		stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
		stderr = subprocess.PIPE, universal_newlines = True)
    if mproc.stdout:
        for line in mproc.stdout.splitlines():
            print(line)
    if mproc.stderr:
        print('Error message output from magic:')
        for line in mproc.stderr.splitlines():
            print(line)
    if mproc.returncode != 0:
        print('ERROR:  Magic exited with status ' + str(mproc.returncode))

# Delete the text generator script
if not keep:
    os.remove('gen_message.tcl')

sys.exit(mproc.returncode)
