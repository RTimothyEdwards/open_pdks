#!/usr/bin/env python3
#--------------------------------------------------------
# make_icon_from_soft.py --
#
# Create an electric icon (manually) from information taken from
# a verilog module.
#-----------------------------------------------------------------

import os
import re
import sys
import json
import datetime
import subprocess

def create_symbol(projectpath, verilogfile, project, destfile=None, debug=False, dolist=False):
    if not os.path.exists(projectpath):
        print('No path to project ' + projectpath)
        return 1

    if not os.path.isfile(verilogfile):
        print('No path to verilog file ' + verilogfile)
        return 1

    if not os.path.exists(projectpath + '/elec'):
        print('No electric subdirectory /elec/ in project.')
        return 1

    if not destfile:

        delibdir = projectpath + '/elec/' + project + '.delib'
        if not os.path.isdir(delibdir):
            print('No electric library ' + project + '.delib in project.')
            return 1

        if os.path.isfile(delibdir + '/' + project + '.ic'):
            print('Symbol file ' + project + '.ic exists already.')
            print('Please remove it if you want to overwrite it.')
            return 1

        # By default, put the icon file in the project's electric library
        destfile = projectpath + '/elec/' + project + '.delib/' + project + '.ic'
        desthdr = projectpath + '/elec/' + project + '.delib/header'

    else:
        if os.path.isfile(destfile):
            print('Symbol file ' + project + '.ic exists already.')
            print('Please remove it if you want to overwrite it.')
            return 1

        destdir = os.path.split(destfile)[0]
        desthdr = destdir + '/header'
        if not os.path.isdir(destdir):
            os.makedirs(destdir)

    # Original verilog source can be very complicated to parse.  Run through
    # qflow's vlog2Verilog tool to get a much simplified header, which also
    # preprocesses the verilog, handles parameters, etc.

    vdir = os.path.split(verilogfile)[0]
    vtempfile = vdir + '/vtemp.out'
    p = subprocess.run(['/usr/local/share/qflow/bin/vlog2Verilog',
			'-p', '-o', vtempfile, verilogfile], stdout = subprocess.PIPE)

    if not os.path.exists(vtempfile):
        print('Error:  Failed to create preprocessed verilog from ' + verilogfile)
        return 1

    # Okay, ready to go.  Now read the verilog source file and get the list
    # of pins.

    commstr1 = '/\*.*\*/'
    commstr2 = '//[^\n]*\n'
    c1rex = re.compile(commstr1)
    c2rex = re.compile(commstr2)

    # Find and isolate the module and its pin list.
    modstr = 'module[ \t]+' + project + '[ \t]*\(([^\)]+)\)[ \t\n]*;'
    modrex = re.compile(modstr)

    # End parsing on any of these tokens
    endrex = re.compile('[ \t]*(initial|function|task|always)')

    inpins = []
    outpins = []
    iopins = []
    invecs = []
    outvecs = []
    iovecs = []

    with open(vtempfile, 'r') as ifile:
        vlines = ifile.read()

        # Remove comments
        vlines2 = c2rex.sub('\n', c1rex.sub('', vlines))

        # Find and isolate the module pin list
        modpinslines = modrex.findall(vlines2)

        modpinsstart = modrex.search(vlines2)
        if modpinsstart:
            startc = modpinsstart.span()[0]
        else:
            startc = 0
        modpinsend = endrex.search(vlines2[startc:])
        if modpinsend:
            endc = modpinsend.span()[0]
        else:
            endc = len(vlines2)

        vlines2 = vlines2[startc:endc]

        # Find the module (there should be only one) and get pins if in the
        # format with input / output declarations in the module heading.

        pinlist = []
        if len(modpinslines) > 0:
            modpins = modpinslines[0]
            pinlist = re.sub('[\t\n]', '', modpins).split(',')

        # If each pinlist entry is only one word, then look for following
        # lines "input", "output", etc., and compile them into a similar
        # list.  Then parse each list entry.

        knownreal = {}
        knownpower = {}
        knownground = {}
            
        if len(pinlist) > 0 and len(pinlist[0].split()) == 1:

            invecrex  = re.compile('\n[ \t]*input[ \t]*\[[ \t]*([0-9]+)[ \t]*:[ \t]*([0-9]+)[ \t]*\][ \t]*([^;]+);')
            insigrex  = re.compile('\n[ \t]*input[ \t]+([^\[;]+);')
            outvecrex = re.compile('\n[ \t]*output[ \t]*\[[ \t]*([0-9]+)[ \t]*:[ \t]*([0-9]+)[ \t]*\][ \t]*([^;]+);')
            outsigrex = re.compile('\n[ \t]*output[ \t]+([^;\[]+);')
            iovecrex  = re.compile('\n[ \t]*inout[ \t]*\[[ \t]*([0-9]+)[ \t]*:[ \t]*([0-9]+)[ \t]*\][ \t]*([^;]+);')
            iosigrex  = re.compile('\n[ \t]*inout [ \t]+([^;\[]+);')

            # Find input, output, and inout lines
            for test in insigrex.findall(vlines2):
                pinname = list(item.strip() for item in test.split(','))
                inpins.extend(pinname)
            for test in outsigrex.findall(vlines2):
                pinname = list(item.strip() for item in test.split(','))
                outpins.extend(pinname)
            for test in iosigrex.findall(vlines2):
                pinname = list(item.strip() for item in test.split(','))
                iopins.extend(pinname)
            for test in invecrex.finditer(vlines2):
                tpin = test.group(3).split(',')
                for pin in tpin:
                    pinname = pin.strip() + '[' + test.group(1) + ':' + test.group(2) + ']'
                    invecs.append(pinname)
            for test in outvecrex.finditer(vlines2):
                tpin = test.group(3).split(',')
                for pin in tpin:
                    pinname = pin.strip() + '[' + test.group(1) + ':' + test.group(2) + ']'
                    outvecs.append(pinname)
            for test in iovecrex.finditer(vlines2):
                tpin = test.group(3).split(',')
                for pin in tpin:
                    pinname = pin.strip() + '[' + test.group(1) + ':' + test.group(2) + ']'
                    iovecs.append(pinname)
          
            # Apply syntax checks (to do:  check for "real" above)
            powerrec = re.compile('VDD|VCC', re.IGNORECASE)
            groundrec = re.compile('VSS|GND|GROUND', re.IGNORECASE)
            for pinname in inpins + outpins + iopins + invecs + outvecs + iovecs: 
                pmatch = powerrec.match(pinname)
                gmatch = groundrec.match(pinname)
                if pmatch:
                    knownpower[pinname] = True
                if gmatch:
                    knownground[pinname] = True
        else:

            # Get pin lists from module pin list.  These are simpler to
            # parse, since they have to be enumerated one by one.

            invecrex  = re.compile('[ \t]*input[ \t]*\[[ \t]*([0-9]+)[ \t]*:[ \t]*([0-9]+)[ \t]*\][ \t]*(.+)')
            insigrex  = re.compile('[ \t]*input[ \t]+([a-zA-Z_][^ \t]+)')
            outvecrex = re.compile('[ \t]*output[ \t]*\[[ \t]*([0-9]+)[ \t]*:[ \t]*([0-9]+)[ \t]*\][ \t]*(.+)')
            outsigrex = re.compile('[ \t]*output[ \t]+([a-zA-Z_][^ \t]+)')
            iovecrex  = re.compile('[ \t]*inout[ \t]*\[[ \t]*([0-9]+)[ \t]*:[ \t]*([0-9]+)[ \t]*\][ \t]*(.+)')
            iosigrex  = re.compile('[ \t]*inout[ \t]+([a-zA-Z_][^ \t]+)')
            realrec = re.compile('[ \t]+real[ \t]+')
            logicrec = re.compile('[ \t]+logic[ \t]+')
            wirerec = re.compile('[ \t]+wire[ \t]+')
            powerrec = re.compile('VDD|VCC', re.IGNORECASE)
            groundrec = re.compile('VSS|GND|GROUND', re.IGNORECASE)

            for pin in pinlist:
                # Pull out any reference to "real", "logic", or "wire" to get pin name
                ppin = realrec.sub(' ', logicrec.sub(' ', wirerec.sub(' ', pin.strip())))
                pinname = None

                # Make syntax checks
                rmatch = realrec.match(pin)
                pmatch = powerrec.match(pin)
                gmatch = groundrec.match(pin)

                imatch = insigrex.match(ppin)
                if imatch:
                   pinname = imatch.group(1)
                   inpins.append(pinname)
                omatch = outsigrex.match(ppin)
                if omatch:
                   pinname = omatch.group(1)
                   outpins.append(pinname)
                bmatch = iosigrex.match(ppin)
                if bmatch:
                   pinname = bmatch.group(1)
                   iopins.append(pinname)
                ivmatch = invecrex.match(ppin)
                if ivmatch:
                   pinname = ivmatch.group(3) + '[' + ivmatch.group(1) + ':' + ivmatch.group(2) + ']'
                   invecs.append(pinname)
                ovmatch = outvecrex.match(ppin)
                if ovmatch:
                   pinname = ovmatch.group(3) + '[' + ovmatch.group(1) + ':' + ovmatch.group(2) + ']'
                   outvecs.append(pinname)
                bvmatch = iovecrex.match(ppin)
                if bvmatch:
                   pinname = bvmatch.group(3) + '[' + bvmatch.group(1) + ':' + bvmatch.group(2) + ']'
                   iovecs.append(pinname)

                # Apply syntax checks
                if pinname:
                    if rmatch:
                        knownreal[pinname] = True
                    if pmatch and rmatch:
                        knownpower[pinname] = True
                    if gmatch and rmatch:
                        knownground[pinname] = True

    if (os.path.exists(vtempfile)):
        os.remove(vtempfile)

    if len(inpins) + len(outpins) + len(iopins) + len(invecs) + len(outvecs) + len(iovecs) == 0:
        print('Failure to parse pin list for module ' + project + ' out of verilog source.')
        return 1

    if debug:
        print("Input pins of module " + project + ":")
        for pin in inpins:
            print(pin)
        print("Output pins of module " + project + ":")
        for pin in outpins:
            print(pin)
        print("Bidirectional pins of module " + project + ":")
        for pin in iopins:
            print(pin)
    
    # If "dolist" is True, then create a list of pin records in the style used by
    # project.json, and return the list.

    if dolist == True:
        pinlist = []
        for pin in inpins:
            pinrec = {}
            pinrec["name"] = pin
            pinrec["description"] = "(add description here)"
            if pin in knownreal:
                pinrec["type"] = 'signal'
            else:
                pinrec["type"] = 'digital'
            pinrec["Vmin"] = "-0.5"
            pinrec["Vmax"] = "VDD + 0.3"
            pinrec["dir"] = "input"
            pinlist.append(pinrec)
        for pin in outpins:
            pinrec = {}
            pinrec["name"] = pin
            pinrec["description"] = "(add description here)"
            if pin in knownreal:
                pinrec["type"] = 'signal'
            else:
                pinrec["type"] = 'digital'
            pinrec["Vmin"] = "-0.5"
            pinrec["Vmax"] = "VDD + 0.3"
            pinrec["dir"] = "output"
            pinlist.append(pinrec)
        for pin in iopins:
            pinrec = {}
            pinrec["name"] = pin
            pinrec["description"] = "(add description here)"
            if pin in knownpower:
                pinrec["type"] = 'power'
                pinrec["Vmin"] = "3.6"
                pinrec["Vmax"] = "3.0"
            elif pin in knownground:
                pinrec["type"] = 'ground'
                pinrec["Vmin"] = "0"
                pinrec["Vmax"] = "0"
            elif pin in knownreal:
                pinrec["type"] = 'signal'
                pinrec["Vmin"] = "-0.5"
                pinrec["Vmax"] = "VDD + 0.3"
            else:
                pinrec["type"] = 'digital'
                pinrec["Vmin"] = "-0.5"
                pinrec["Vmax"] = "VDD + 0.3"
            pinrec["dir"] = "inout"
            pinlist.append(pinrec)
        for pin in invecs:
            pinrec = {}
            pinrec["name"] = pin
            pinrec["description"] = "(add description here)"
            if pin in knownreal:
                pinrec["type"] = 'signal'
            else:
                pinrec["type"] = 'digital'
            pinrec["dir"] = "input"
            pinrec["Vmin"] = "-0.5"
            pinrec["Vmax"] = "VDD + 0.3"
            pinlist.append(pinrec)
        for pin in outvecs:
            pinrec = {}
            pinrec["name"] = pin
            pinrec["description"] = "(add description here)"
            if pin in knownreal:
                pinrec["type"] = 'signal'
            else:
                pinrec["type"] = 'digital'
            pinrec["dir"] = "output"
            pinrec["Vmin"] = "-0.5"
            pinrec["Vmax"] = "VDD + 0.3"
            pinlist.append(pinrec)
        for pin in iovecs:
            pinrec = {}
            pinrec["name"] = pin
            pinrec["description"] = "(add description here)"
            if pin in knownpower:
                pinrec["type"] = 'power'
                pinrec["Vmin"] = "3.6"
                pinrec["Vmax"] = "3.0"
            elif pin in knownground:
                pinrec["type"] = 'ground'
                pinrec["Vmin"] = "0"
                pinrec["Vmax"] = "0"
            elif pin in knownreal:
                pinrec["type"] = 'signal'
                pinrec["Vmin"] = "-0.5"
                pinrec["Vmax"] = "VDD + 0.3"
            else:
                pinrec["type"] = 'digital'
                pinrec["Vmin"] = "-0.5"
                pinrec["Vmax"] = "VDD + 0.3"
            pinrec["dir"] = "inout"
            pinlist.append(pinrec)
    
        return pinlist

    # Okay, we've got all the pins, now build the symbol.

    leftpins = len(inpins) + len(invecs)
    rightpins = len(outpins) + len(outvecs)
    # Arbitrarily, bidirectional pins are put on bottom and vectors on top.
    toppins = len(iovecs)
    botpins = len(iopins)

    height = 2 + max(leftpins, rightpins) * 10
    width = 82 + max(toppins, botpins) * 10

    # Enforce minimum height (minimum width enforced above)
    if height < 40:
        height = 40

    # Run electric -v to get version string
    p = subprocess.run(['electric', '-v'], stdout = subprocess.PIPE)
    vstring = p.stdout.decode('utf-8').rstrip()

    # Get timestamp
    timestamp = str(int(datetime.datetime.now().strftime("%s")) * 1000)

    with open(destfile, 'w') as ofile:
        print('H' + project + '|' + vstring, file=ofile)
        print('', file=ofile)
        print('# Cell ' + project + ';1{ic}', file=ofile)
        print('C' + project + ';1{ic}||artwork|' + timestamp + '|' + timestamp + '|E', file=ofile)
        print('Ngeneric:Facet-Center|art@0||0|0||||AV', file=ofile)
        print('NBox|art@1||0|0|' + str(width) + '|' + str(height) + '||', file=ofile)
        pnum = 0

        # Title
        print('Ngeneric:Invisible-Pin|pin@' + str(pnum) + '||0|5|||||ART_message(BD5G5;)S' + project, file=ofile)

        pnum += 1
        # Fill in left side pins
        px = -(width / 2)
        py = -(height / 2) + 5
        for pin in inpins:
            print('Nschematic:Wire_Pin|pin@' + str(pnum) + '||' + str(px - 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px - 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            py += 10
        for pin in invecs:
            print('Nschematic:Bus_Pin|pin@' + str(pnum) + '||' + str(px - 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px - 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            py += 10

        # Fill in right side pins
        px = (width / 2)
        py = -(height / 2) + 5
        for pin in outpins:
            print('Nschematic:Wire_Pin|pin@' + str(pnum) + '||' + str(px + 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px + 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            py += 10
        for pin in outvecs:
            print('Nschematic:Bus_Pin|pin@' + str(pnum) + '||' + str(px + 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px + 10) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            py += 10

        # Fill in bottom side pins
        py = -(height / 2)
        px = -(width / 2) + 45
        for pin in iopins:
            print('Nschematic:Wire_Pin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py - 10) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py - 10) + '|1|1||', file=ofile)
            pnum += 1
            px += 10

        # Fill in top side pins
        py = (height / 2)
        px = -(width / 2) + 45
        for pin in iovecs:
            print('Nschematic:Bus_Pin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py + 10) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|1|1||', file=ofile)
            pnum += 1
            print('NPin|pin@' + str(pnum) + '||' + str(px) + '|' + str(py + 10) + '|1|1||', file=ofile)
            pnum += 1
            px += 10

        # Start back at pin 1 and retain the same order when drawing wires
        pnum = 1
        nnum = 0

        px = -(width / 2)
        py = -(height / 2) + 5
        for pin in inpins:
            pnum += 1
            print('ASolid|net@' + str(nnum) + '|||FS0|pin@' + str(pnum) + '||' + str(px - 10) + '|' + str(py) + '|pin@' + str(pnum + 1) + '||' + str(px) + '|' + str(py), file=ofile)
            pnum += 2
            nnum += 1
            py += 10

        for pin in invecs:
            pnum += 1
            print('ASolid|net@' + str(nnum) + '|||FS0|pin@' + str(pnum) + '||' + str(px - 10) + '|' + str(py) + '|pin@' + str(pnum + 1) + '||' + str(px) + '|' + str(py), file=ofile)
            pnum += 2
            nnum += 1
            py += 10

        px = (width / 2)
        py = -(height / 2) + 5
        for pin in outpins:
            pnum += 1
            print('ASolid|net@' + str(nnum) + '|||FS0|pin@' + str(pnum) + '||' + str(px + 10) + '|' + str(py) + '|pin@' + str(pnum + 1) + '||' + str(px) + '|' + str(py), file=ofile)
            pnum += 2
            nnum += 1
            py += 10

        for pin in outvecs:
            pnum += 1
            print('ASolid|net@' + str(nnum) + '|||FS0|pin@' + str(pnum) + '||' + str(px + 10) + '|' + str(py) + '|pin@' + str(pnum + 1) + '||' + str(px) + '|' + str(py), file=ofile)
            pnum += 2
            nnum += 1
            py += 10

        py = -(height / 2)
        px = -(width / 2) + 45 
        for pin in iopins:
            pnum += 1
            print('ASolid|net@' + str(nnum) + '|||FS0|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|pin@' + str(pnum + 1) + '||' + str(px) + '|' + str(py - 10), file=ofile)
            pnum += 2
            nnum += 1
            px += 10

        py = (height / 2)
        px = -(width / 2) + 45
        for pin in iovecs:
            pnum += 1
            print('ASolid|net@' + str(nnum) + '|||FS0|pin@' + str(pnum) + '||' + str(px) + '|' + str(py) + '|pin@' + str(pnum + 1) + '||' + str(px) + '|' + str(py + 10), file=ofile)
            pnum += 2
            nnum += 1
            px += 10

        # Add the exports (which are the only nontrivial elements)
        pnum = 1
        for pin in inpins:
            print('E' + pin + '||D6G4;X12.0;Y0.0;|pin@' + str(pnum) + '||I', file=ofile)
            pnum += 3
        for pin in invecs:
            print('E' + pin + '||D6G4;X12.0;Y0.0;|pin@' + str(pnum) + '||I', file=ofile)
            pnum += 3
        for pin in outpins:
            print('E' + pin + '||D4G4;X-12.0;Y0.0;|pin@' + str(pnum) + '||O', file=ofile)
            pnum += 3
        for pin in outvecs:
            print('E' + pin + '||D4G4;X-12.0;Y0.0;|pin@' + str(pnum) + '||O', file=ofile)
            pnum += 3
        for pin in iopins:
            print('E' + pin + '||D6G4;RX0.0;Y12.0;|pin@' + str(pnum) + '||B', file=ofile)
            pnum += 3
        for pin in iovecs:
            print('E' + pin + '||D6G4;RRRX0.0;Y-12.0;|pin@' + str(pnum) + '||B', file=ofile)
            pnum += 3

        # X marks the spot, or at least the end.
        print('X', file=ofile)

    if not os.path.isfile(desthdr):
        with open(desthdr, 'w') as ofile:
            print('# header information:', file=ofile)
            print('H' + project + '|' + vstring, file=ofile)
            print('', file=ofile)
            print('# Views:', file=ofile)
            print('Vicon|ic', file=ofile)
            print('', file=ofile)
            print('# Tools:', file=ofile)
            print('Ouser|DefaultTechnology()Sschematic', file=ofile)
            print('Osimulation|VerilogUseAssign()BT', file=ofile)
            print('C____SEARCH_FOR_CELL_FILES____', file=ofile)

    return 0

def usage():
    print("make_icon_from_soft.py <project_path> [<verilog_source>] [<output_file>]")
    print("")
    print("   where <project_path> is the path to a standard efabless project, and")
    print("   <verilog_source> is the path to a verilog source file.")
    print("")
    print("   The module name must be the same as the project's ip-name.")
    print("")
    print("   <verilog_source> is assumed to be in verilog/source/<ip-name>.v by")
    print("   default if not otherwise specified.")
    print("")
    print("   If <output_file> is not specified, output goes in the project's")
    print("   electric library.")
    print("")

if __name__ == '__main__':
    arguments = []
    options = []

    for item in sys.argv[1:]:
        if item[0] == '-':
            options.append(item.strip('-'))
        else:
            arguments.append(item)

    debug = True if 'debug' in options else False

    numarg = len(arguments)
    if numarg > 3 or numarg == 0:
        usage()
        sys.exit(0)

    projectpath = arguments[0]

    projdirname = os.path.split(projectpath)[1]
    jsonfile = projectpath + '/project.json'
    if not os.path.isfile(jsonfile):
        # Legacy behavior is to have the JSON file name the same as the directory name.
        jsonfile = projectpath + '/' + projdirname + '.json'
        if not os.path.isfile(jsonfile):
            print('Error:  No project JSON file found for project ' + projdirname)
            sys.exit(1)

    project = None
    with open(jsonfile, 'r') as ifile:
        datatop = json.load(ifile)
        dsheet = datatop['data-sheet']
        project = dsheet['ip-name']

    if not project:
        print('Error:  No project IP name in project JSON file.')
        sys.exit(1)

    if numarg > 1:
        verilogfile = arguments[1]
    else:
        verilogfile = projectpath + '/verilog/source/' + project + '.v'
        if not os.path.exists(verilogfile):
            print('Error:  No verilog file ' + verilogfile + ' found.')
            print('Please specify full path as 2nd argument.')
            sys.exit(1)

    if numarg > 2:
        destfile = arguments[2]
    else:
        destfile = projectpath + '/elec/' + project + '.delib/' + project + '.ic'
        if os.path.exists(destfile):
            print('Error:  Icon file ' + destfile + ' already exists.')
            print('Please delete any unwanted original before running this script.')
            sys.exit(1)

    result = create_symbol(projectpath, verilogfile, project, destfile, debug)
    sys.exit(result)
