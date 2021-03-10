#!/usr/bin/env python3
#-----------------------------------------------------------------------
# netlist_to_layout.py
#-----------------------------------------------------------------------
#
# Generate a magic layout from a SPICE netlist, running magic in batch
# mode and calling up the PDK selections non-interactively for each
# component in the netlist.
#
#---------------------------------------------------------------------
# Written by Tim Edwards
# efabless, inc.
# November 17, 2016
# Updated December 17, 2016
# Version 1.0
# Imported December 22, 2020 to open_pdks
# Updated February 10, 2021 for use running on netlist alone
#---------------------------------------------------------------------

import os
import re
import sys
import subprocess

def generate_layout_start(library, ofile=sys.stdout):
    global debugmode
    if debugmode:
        print('Writing layout generating script.')

    # Write a couple of simplifying procedures
    print('#!/usr/bin/env wish', file=ofile)
    print('#-------------------------------------', file=ofile)
    print('# Script to create layout from netlist', file=ofile)
    print('# Source this in magic.', file=ofile)
    print('#-----------------------------------------', file=ofile)
    print('drc off', file=ofile)
    print('proc move_forward {instname} {', file=ofile)
    print('    select cell $instname', file=ofile)
    print('    set anum [lindex [array -list count] 1]', file=ofile)
    print('    set xpitch [lindex [array -list pitch] 0]', file=ofile)
    print('    set bbox [box values]', file=ofile)
    print('    set posx [lindex $bbox 0]', file=ofile)
    print('    set posy [lindex $bbox 1]', file=ofile)
    print('    set width [expr [lindex $bbox 2] - $posx]', file=ofile)
    print('    set posx [expr $posx + $width + $xpitch * $anum]', file=ofile)
    print('    box position ${posx}i ${posy}i', file=ofile)
    print('    return [lindex $bbox 3]', file=ofile)
    print('}', file=ofile)
    print('', file=ofile)
    print('proc get_and_move_inst {cellname instname anum} {', file=ofile)
    print('    set newinst [getcell $cellname]', file=ofile)
    print('    select cell $newinst', file=ofile)
    print('    if {$newinst == ""} {return}', file=ofile)
    print('    identify $instname', file=ofile)
    print('    if {$anum > 1} {array 1 $anum}', file=ofile)
    print('    set bbox [box values]', file=ofile)
    print('    set posx [lindex $bbox 2]', file=ofile)
    print('    set posy [lindex $bbox 1]', file=ofile)
    print('    box position ${posx}i ${posy}i', file=ofile)
    print('    return [lindex $bbox 3]', file=ofile)
    print('}', file=ofile)
    print('', file=ofile)
    print('proc add_pin {pinname portnum} {', file=ofile)
    print('    box size 1um 1um', file=ofile)
    print('    paint m1', file=ofile)
    print('    label $pinname FreeSans 16 0 0 0 c m1', file=ofile)
    print('    port make $portnum', file=ofile)
    print('    box move s 2um', file=ofile)
    print('}', file=ofile)
    print('', file=ofile)
    if not library:
        print('namespace import ${PDKNAMESPACE}::*', file=ofile)
    print('suspendall', file=ofile)
    return ofile
 
def generate_layout_add(subname, subpins, complist, library, ofile=sys.stdout):
    global debugmode
    if debugmode:
        if subpins:
            print('   Generating layout for subcircuit ' + subname + '.')
        else:
            print('   Generating layout for top level circuit ' + subname + '.')

    gparmrex = re.compile('([^= \t]+)=([^=]+)')
    sparmrex = re.compile('([^= \t]+)=([^= \t]+)[ \t]*(.*)')
    expr1rex = re.compile('([^= \t]+)=\'([^\']+)\'[ \t]*(.*)')
    expr2rex = re.compile('([^= \t]+)=\{([^\}]+)\}[ \t]*(.*)')
    tokrex = re.compile('([^ \t]+)[ \t]*(.*)')

    if subname:
        print('load ' + subname + ' -quiet', file=ofile)

    print('box 0um 0um 0um 0um', file=ofile)
    print('', file=ofile)

    # Generate all of the pins as labels
    if subpins:
        pinlist = subpins.split()
        i = 0
        for pin in pinlist:
            # Escape [ and ] in pin name
            pin_esc = pin.replace('[', '\[').replace(']', '\]')
            # To be done:  watch for key=value parameters
            print('add_pin ' + pin_esc + ' ' + str(i), file=ofile)
            i += 1

    # Set initial position for importing cells
    print('box size 0 0', file=ofile)
    print('set posx 0', file=ofile)
    print('set posy [expr {round(3 / [cif scale out])}]', file=ofile)
    print('box position ${posx}i ${posy}i', file=ofile)

    for comp in complist:
        pinlist = []
        paramlist = []

        # Parse into pins, device name, and parameters.  Make sure parameters
        # incorporate quoted expressions as {} or ''.
        rest = comp
        while rest and rest != '':
            gmatch = gparmrex.match(rest)
            if gmatch:
                break
            else:
                tmatch = tokrex.match(rest)
                if tmatch:
                    token = tmatch.group(1)
                    pinlist.append(token)
                    rest = tmatch.group(2)
                else:
                    rest = ''
        
        while rest and rest != '':
            ematch = expr1rex.match(rest)
            if ematch:
                pname = ematch.group(1)
                value = ematch.group(2)
                paramlist.append((pname, '{' + value + '}'))
                rest = ematch.group(3)
            else:
                ematch = expr2rex.match(rest)
                if ematch:
                    pname = ematch.group(1)
                    value = ematch.group(2)
                    paramlist.append((pname, '{' + value + '}'))
                    rest = ematch.group(3)
                else:
                    smatch = sparmrex.match(rest)
                    if smatch:
                        pname = smatch.group(1)
                        value = smatch.group(2)
                        paramlist.append((pname, value))
                        rest = smatch.group(3)
                    else:
                        print('Error parsing line "' + comp + '"')
                        print('at:  "' + rest + '"')
                        rest = ''

        if len(pinlist) < 2:
            print('Error:  No device type found in line "' + comp + '"')
            print('Tokens found are: ' + ', '.join(pinlist))
            continue

        instname = pinlist[0]
        devtype = pinlist[-1]
        pinlist = pinlist[0:-1]

        # Diagnostic
        if debugmode:
            print('      Adding component ' + devtype + ' instance ' + instname)

        mult = 1
        for param in paramlist:
            parmname = param[0]
            parmval = param[1]
            if parmname.upper() == 'M':
                try:
                    mult = int(parmval)
                except ValueError:
                    # This takes care of multiplier expressions, as long
                    # as they don't reference parameter names themselves.
                    mult = eval(eval(parmval))

        # devtype is assumed to be in library.  If not, it will attempt to use
        # 'getcell' on devtype.  NOTE:  Current usage is to not pass a library
        # to netlist_to_layout.py but to rely on the PDK Tcl script to define
        # variable PDKNAMESPACE, which is the namespace to use for low-level
        # components, and may not be the same name as the technology node.
        if library:
            libdev = library + '::' + devtype
        else:
            libdev = '${PDKNAMESPACE}::' + devtype
        outparts = []
        outparts.append('magic::gencell ' + libdev + ' ' + instname)

        #  Output all parameters.  Parameters not used by the toolkit are ignored
        # by the toolkit.
        outparts.append('-spice')
        for param in paramlist:
            outparts.append(str(param[0]).lower())
            outparts.append(param[1])

        outstring = ' '.join(outparts)
        print('if {[catch {' + outstring + '}]} {', file=ofile)
        print('   get_and_move_inst ' + devtype + ' ' + instname
			+ ' ' + str(mult), file=ofile)
        print('} else {', file=ofile)
        print('   move_forward ' + instname, file=ofile)
        print('}', file=ofile)
        print('', file=ofile)
    print('save ' + subname, file=ofile)
                
def generate_layout_end(ofile=sys.stdout):
    global debugmode

    print('resumeall', file=ofile)
    print('writeall force', file=ofile)
    print('quit -noprompt', file=ofile)

def parse_layout(topname, lines, library, ofile):
    global debugmode

    subrex = re.compile('.subckt[ \t]+(.*)$', re.IGNORECASE)
    devrex = re.compile('[xmcrbdivq]([^ \t]+)[ \t](.*)$', re.IGNORECASE)
    namerex = re.compile('([^= \t]+)[ \t]+(.*)$', re.IGNORECASE)
    endsrex = re.compile('^[ \t]*\.ends', re.IGNORECASE)

    insub = False
    subname = ''
    subpins = ''
    complist = []
    toplist = []

    for line in lines:
        if not insub:
            lmatch = subrex.match(line)
            if lmatch:
                rest = lmatch.group(1)
                smatch = namerex.match(rest)
                if smatch:
                    subname = smatch.group(1)
                    subpins = smatch.group(2)
                    insub = True
                else:
                    print('File ' + inputfile + ':  Failure to parse line ' + line)
            else:
                dmatch = devrex.match(line)
                if dmatch:
                    toplist.append(line)
        else:
            lmatch = endsrex.match(line)
            if lmatch:
                insub = False
                generate_layout_add(subname, subpins, complist, library, ofile)
                subname = None
                subpins = None
                complist = []
            else:
                dmatch = devrex.match(line)
                if dmatch:
                    complist.append(line)

    # Add any top-level components
    if toplist:
        generate_layout_add(topname, None, toplist, library, ofile)

def usage():
    print('Usage:')
    print('	netlist_to_layout.py <filename> [<namespace>] [-options]')
    print('')
    print('Arguments:')
    print('	<filename> is the path to the SPICE netlist to import to magic')
    print('	<namespace> is the namespace of the PDK')
    print('')
    print('Options:')
    print('	-keep	Keep the working script after completion.')
    print('	-debug	Provide verbose output while generating script.')
    print('	-help	Print this help text.')

# Main procedure

if __name__ == '__main__':
    global debugmode

    # Parse command line for options and arguments
    optionlist = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            optionlist.append(item)
        else:
            arguments.append(item)

    if len(arguments) > 0:
        inputfile = arguments[0]
        if len(arguments) > 1:
            library = arguments[1]
        else:
            library = None
    else:
        usage()
        sys.exit(0)

    debugmode = False
    keepmode = False

    for item in optionlist:
        result = item.split('=')
        if result[0] == '-help':
            usage()
            sys.exit(0)
        elif result[0] == '-debug':
            debugmode = True
        elif result[0] == '-keep':
            keepmode = True
        else:
            usage()
            sys.exit(1)

    netpath = os.path.split(inputfile)[0]
    if netpath == '':
        netpath = os.getcwd()

    if os.path.splitext(inputfile)[1] == '.sch':
        print('Sorry, automatic conversion of schematic to netlist not yet supported.')
        sys.exit(1)

    netroot = os.path.split(netpath)[0]
    magpath = os.path.join(netroot, 'mag')
    if not os.path.isdir(magpath):
        print('Error:  Layout path "' + magpath + '" does not exist or is not readable.')
        sys.exit(1)

    # NOTE:  There should be some attempt to find the installed PDK magicrc file
    # if there is no mag/ directory.
    rcfile = '.magicrc'
    rcfilepath = os.path.join(magpath, rcfile)
    if not os.path.isfile(rcfilepath):
        print('Error:  No startup script file "' + rcfilepath + '"')
        sys.exit(1)

    # Read SPICE netlist
    with open(inputfile, 'r') as ifile:
        if debugmode:
            print('Reading file ' + inputfile)
        spicetext = ifile.read()
        
    # Contatenate continuation lines
    spicelines = spicetext.replace('\n+', ' ').splitlines()

    filename = os.path.split(inputfile)[1]
    topname = os.path.splitext(filename)[0]

    scriptfile = 'generate_layout.tcl'
    scriptpath = os.path.join(magpath, scriptfile)

    with open(scriptpath, 'w') as ofile:
        generate_layout_start(library, ofile)
        parse_layout(topname, spicelines, library, ofile)
        generate_layout_end(ofile)

    myenv = os.environ.copy()
    myenv['MAGTYPE'] = 'mag'

    # Run the layout generator
    mproc = subprocess.run(['magic', '-dnull', '-noconsole', '-rcfile',
		rcfile, scriptfile],
		stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
		stderr = subprocess.PIPE, cwd = magpath,
		env = myenv, universal_newlines = True)
    if mproc.stdout:
        for line in mproc.stdout.splitlines():
            print(line)
    if mproc.stderr:
        print('Error message output from magic:')
        for line in mproc.stderr.splitlines():
            print(line)
    if mproc.returncode != 0:
        print('ERROR:  Magic exited with status ' + str(mproc.returncode))

    # Clean up
    if not keepmode:
        os.remove(scriptpath)

    sys.exit(0)
