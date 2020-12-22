#!/bin/env python3
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
# To do: Rework from electric to xschem and support both EF_STYLE = 0
# and 1 styles of directory structures from open_pdks.
#---------------------------------------------------------------------

import os
import re
import sys
import subprocess

# Routines to generate netlist from schematic if needed

def check_schematic_out_of_date(spipath, schempath, schematic_name):
    # Check if a netlist (spipath) is out-of-date relative to the schematics
    # (schempath).  Need to read the netlist and check all of the subcells.
    need_capture = False
    if not os.path.isfile(spipath):
        return True
    if os.path.isfile(schempath):
        spi_statbuf = os.stat(spipath)
        sch_statbuf = os.stat(schempath)
        if spi_statbuf.st_mtime < sch_statbuf.st_mtime:
            # netlist exists but is out-of-date
            need_capture = True
        else:
            # only found that the top-level-schematic is older than the
            # netlist.  Now need to read the netlist, find all subcircuits,
            # and check those dates, too.
            schemdir = os.path.split(schempath)[0]
            subrex = re.compile('^[^\*]*[ \t]*.subckt[ \t]+([^ \t]+).*$', re.IGNORECASE)
            with open(spipath, 'r') as ifile:
                duttext = ifile.read()
 
            dutlines = duttext.replace('\n+', ' ').splitlines()
            for line in dutlines:
                lmatch = subrex.match(line)
                if lmatch:
                    subname = lmatch.group(1)
                    # NOTE: Electric uses library:cell internally to track libraries,
                    # and maps the ":" to "__" in the netlist.  Not entirely certain that
                    # the double-underscore uniquely identifies the library:cell. . .
                    librex = re.compile('(.*)__(.*)', re.IGNORECASE)
                    lmatch = librex.match(subname)
                    if lmatch:
                        elecpath = os.path.split(os.path.split(schempath)[0])[0]
                        libname = lmatch.group(1)
                        subschem = elecpath + '/' + libname + '.delib/' + lmatch.group(2) + '.sch'
                    else:
                        libname = {}
                        subschem = schemdir + '/' + subname + '.sch'
                    # subcircuits that cannot be found in the current directory are
                    # assumed to be library components and therefore never out-of-date.
                    if os.path.exists(subschem):
                        sub_statbuf = os.stat(subschem)
                        if spi_statbuf.st_mtime < sub_statbuf.st_mtime:
                            # netlist exists but is out-of-date
                            need_capture = True
                            break
                    # mapping of characters to what's allowed in SPICE makes finding
                    # the associated schematic file a bit difficult.  Requires wild-card
                    # searching.
                    elif libname:
                        restr = lmatch.group(2) + '.sch'
                        restr = restr.replace('.', '\.')
                        restr = restr.replace('_', '.')
                        schrex = re.compile(restr, re.IGNORECASE)
                        libpath = elecpath + '/' + libname + '.delib'
                        if os.path.exists(libpath):
                            liblist = os.listdir(libpath)
                            for file in liblist:
                                lmatch = schrex.match(file)
                                if lmatch:
                                    subschem = libpath + '/' + file
                                    sub_statbuf = os.stat(subschem)
                                    if spi_statbuf.st_mtime < sch_statbuf.st_mtime:
                                        # netlist exists but is out-of-date
                                        need_capture = True
                                    break
    return need_capture

def generate_schematic_netlist(schem_path, schem_src, project_path, schematic_name):
    # Does schematic netlist exist and is it current?
    if check_schematic_out_of_date(schem_path, schem_src, schematic_name):
        # elec2spi will not run unless /spi/stub directory is present
        if not os.path.exists(project_path + '/spi'):
            os.makedirs(project_path + '/spi')
        if not os.path.exists(project_path + '/spi/stub'):
            os.makedirs(project_path + '/spi/stub')

        # elec2spi will run, but not correctly, if the .java directory is not present
        if not os.path.exists(project_path + '/elec/.java'):
            # Same behavior as project manager. . . copy from skeleton directory
            pdkdir = os.path.join(project_path, '.ef-config/techdir')
            dotjava = os.path.join(pdkdir, 'libs.tech/deskel/dotjava')
            if not os.path.exists(dotjava):
                dotjava = '/ef/efabless/deskel/dotjava'

            if os.path.exists(dotjava):
                try:
                    shutil.copytree(dotjava, project_path + '/elec/.java', symlinks = True)
                except IOError as e:
                    print('Error copying files: ' + str(e))

        print('Generating schematic netlist.')
        eproc = subprocess.Popen(['/ef/efabless/bin/elec2spi',
			'-o', schem_path, '-LP', '-TS', '-NTI', schematic_name + '.delib',
			schematic_name + '.sch'], stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT, cwd = project_path + '/elec/')
        elecout = eproc.communicate()[0]
        outlines = elecout.splitlines()
        for line in outlines:
            print(line)
        if eproc.returncode != 0:
            print('Bad result from elec2spi -o ' + schem_path + ' -LP -TS -NTI ' + schematic_name + '.delib ' + schematic_name + '.sch')
            print('Failure to generate new schematic netlist.')
            return False
    return True

def generate_layout_start(library):
    # Write out a TCL script to generate the layout
    ofile = open('create_script.tcl', 'w')

    # Write a couple of simplifying procedures
    print('#!/usr/bin/env wish', file=ofile)
    print('#-------------------------------------', file=ofile)
    print('# Script to create layout from netlist', file=ofile)
    print('# Source this in magic.', file=ofile)
    print('#-----------------------------------------', file=ofile)
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

def generate_layout_add(ofile, subname, subpins, complist, library):
    parmrex = re.compile('([^=]+)=([^=]+)', re.IGNORECASE)
    exprrex = re.compile('\'([^\']+)\'', re.IGNORECASE)
    librex  = re.compile('(.*)__(.*)', re.IGNORECASE)

    print('load ' + subname, file=ofile)
    print('box 0um 0um 0um 0um', file=ofile)
    print('', file=ofile)

    # Generate all of the pins as labels
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
        params = {}
        tokens = comp.split()
        # Diagnostic
        # print("Adding component " + tokens[0])
        instname = tokens[0]
        mult = 1
        for token in tokens[1:]:
            rmatch = parmrex.match(token)
            if rmatch:
                parmname = rmatch.group(1).upper()
                parmval = rmatch.group(2)
                params[parmname] = parmval
                if parmname.upper() == 'M':
                    try:
                        mult = int(parmval)
                    except ValueError:
                        # This takes care of multiplier expressions, as long
                        # as they don't reference parameter names themselves.
                        mult = eval(eval(parmval))
            else:
                # Last one that isn't a parameter will be kept
                devtype = token

        # If devtype is a cellname in the form "<lib>__<cell>" then check if <cell> is
        # in the user's /ip/ directory.  If so, recast devtype to just <cell>.
        ematch = librex.match(devtype)
        if ematch:
            cellname = ematch.group(2)
            if os.path.exists(os.path.expanduser('~/design/ip/' + cellname)):
                devtype = cellname

        # devtype is assumed to be in library.  If not, it will throw an error and
        # attempt to use 'getcell' on devtype.  NOTE:  Current usage is to not pass
        # a library to netlist_to_layout.py but to rely on the PDK Tcl script to
        # define variable PDKNAMESPACE, which is the namespace to use for low-level
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
        for item in params:
            outparts.append(str(item).lower())
            outparts.append(params[item])

        outstring = ' '.join(outparts)
        print('if {[catch {' + outstring + '}]} {', file=ofile)
        print('   get_and_move_inst ' + devtype + ' ' + instname
			+ ' ' + str(mult), file=ofile)
        print('} else {', file=ofile)
        print('   move_forward ' + instname, file=ofile)
        print('}', file=ofile)
        print('', file=ofile)
    print('save ' + subname, file=ofile)
                
def generate_layout_end(ofile):
    print('resumeall', file=ofile)
    print('refresh', file=ofile)
    print('writeall force', file=ofile)
    print('quit', file=ofile)
    ofile.close()

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
            library = arguments[1]
        else:
            library = None
    else:
        raise SyntaxError('Usage: ' + sys.argv[0] + ' netlist_file [library] [-options]\n')

    debug = False
    for item in options:
        result = item.split('=')
        if result[0] == '-help':
            print('Usage: ' + sys.argv[0] + ' netlist_file [-options]\n')
        elif result[0] == '-debug':
            debug = True
        else:
            raise SyntaxError('Bad option ' + item + ', options are -help\n')

    # Check if netlist exists or needs updating.
    netpath = os.path.split(inputfile)[0]
    netfile = os.path.split(inputfile)[1]
    netname = os.path.splitext(netfile)[0]
    projectpath = os.path.split(netpath)[0]
    projectname = os.path.split(projectpath)[1]

    elec_path = projectpath + '/elec/' + projectname + '.delib'
    schem_src = elec_path + '/' + projectname + '.sch'

    if not generate_schematic_netlist(inputfile, schem_src, projectpath, netname):
        raise SyntaxError('File ' + inputfile + ':  Failure to generate netlist.')

    # Read SPICE netlist

    with open(inputfile, 'r') as ifile:
        spicetext = ifile.read()
        
    subrex = re.compile('.subckt[ \t]+(.*)$', re.IGNORECASE)
    # All devices are going to be subcircuits
    xrex = re.compile('[xmcrbdi]([^ \t]+)[ \t](.*)$', re.IGNORECASE)
    namerex = re.compile('([^= \t]+)[ \t]+(.*)$', re.IGNORECASE)
    endsrex = re.compile('^[ \t]*\.ends', re.IGNORECASE)

    # Contatenate continuation lines
    spicelines = spicetext.replace('\n+', ' ').splitlines()

    insub = False
    subname = ''
    subpins = ''
    complist = []
    ofile = generate_layout_start(library)
    for line in spicelines:
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
                    raise SyntaxError('File ' + inputfile + ':  Failure to parse line ' + line)
                    break
        else:
            lmatch = endsrex.match(line)
            if lmatch:
                insub = False
                generate_layout_add(ofile, subname, subpins, complist, library)
                subname = None
                subpins = None
                complist = []
            else:
                xmatch = xrex.match(line)
                if xmatch:
                    complist.append(line)

    generate_layout_end(ofile)
