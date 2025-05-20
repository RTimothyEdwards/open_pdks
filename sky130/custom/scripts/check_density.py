#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2020 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0

#
# check_density.py ---
#
#    Run density checks on a design (from GDS, after running fill generation).
#

import sys
import os
import re
import glob
import select
import subprocess

def usage():
    print("Usage:")
    print("check_density.py [<layout_file_name>] [-keep]")
    print("")
    print("where:")
    print("   <layout_file_name> is the path to the .gds or .mag file to be checked.")
    print("")
    print("  If '-keep' is specified, then keep the check script.")
    print("  If '-debug' is specified, then print diagnostic information.")
    return 0

if __name__ == '__main__':

    optionlist = []
    arguments = []

    debugmode = False
    keepmode = False

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 1:
        print("Wrong number of arguments given to check_density.py.")
        usage()
        sys.exit(0)
        
    # Process options

    if '-debug' in optionlist:
        debugmode = True
        print('Running in debug mode.')
    if '-keep' in optionlist:
        keepmode = True
        if debugmode:
            print('Keeping all files after running.')
    elif debugmode:
        print('Temporary files will be removed after running.')

    # Find layout from command-line argument

    user_project_path = arguments[0]

    if os.path.split(user_project_path)[0] == '':
        layoutpath = os.getcwd()
    else:
        layoutpath = os.getcwd() + '/' + os.path.split(user_project_path)[0]

    # Use split() not os.path.splitext() to capture double-dot extensions
    # like "layout.gds.gz".

    project = user_project_path.split(os.extsep, 1)

    if len(project) == 1:
        # No file extension given;  figure it out
        layoutfiles = glob.glob(layoutpath + '/' + user_project_path + '.*')
        if len(layoutfiles) == 1:
            proj_extension = '.' + layoutfiles[0].split(os.extsep, 1)[1]
            user_project_path = layoutfiles[0]
        elif len(layoutfiles) == 0:
            if debugmode:
                print('No matching files found for ' + layoutpath + '/' + user_project_path + '.*')
            print('Error:  Project is not a magic database or GDS file!')
            sys.exit(1)
        else:
            print('Error:  Project name is ambiguous!')
            sys.exit(1)
    else:
        proj_extension = '.' + project[1]

    is_mag = False
    is_gds = False

    if proj_extension == '.mag' or proj_extension == '.mag.gz':
        is_mag = True
    elif proj_extension == '.gds' or proj_extension == '.gds.gz':
        is_gds = True
    else:
        if debugmode:
            print('Unknown extension ' + proj_extension + ' in filename.')
        print('Error:  Project is not a magic database or GDS file!')
        sys.exit(1)

    if not os.path.isfile(user_project_path):
        print('Error:  Project "' + user_project_path + '" does not exist or is not readable.')
        sys.exit(1)

    # The path where the fill generation script resides should be the same
    # path where the magic startup script resides, for the same PDK
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    
    # Search for a magic startup script.  Order of precedence:
    #  1. PDK_ROOT environment variable
    #  2. Local .magicrc
    #  3. The location of this script

    if os.environ.get('PDK'):
        pdk_name = os.environ.get('PDK')
    else:
        pdk_name = 'sky130A'

    if os.environ.get('PDK_ROOT'):
        rcfile_path = os.environ.get('PDK_ROOT') + '/' + pdk_name + '/libs.tech/magic/' + pdk_name + '.magicrc'
    elif os.path.isfile(layoutpath + '/.magicrc'):
        rcfile_path = layoutpath + '/.magicrc'
    elif os.path.isfile(scriptpath + '/' + pdk_name + '.magicrc'):
        rcfile_path = scriptpath + '/' + pdk_name + '.magicrc'
    else:
        print('Unknown path to magic startup script.  Please set $PDK_ROOT')
        sys.exit(1)

    project_file = os.path.split(user_project_path)[1]
    project = project_file.split(os.extsep, 1)[0]
    
    # Create the Tcl script to run in magic to check local density across
    # stepped regions.

    with open(layoutpath + '/check_density.tcl', 'w') as ofile:
        print('#!/bin/env wish', file=ofile)
        print('crashbackups stop', file=ofile)
        print('drc off', file=ofile)
        print('snap internal', file=ofile)

        print('set starttime [orig_clock format [orig_clock seconds] -format "%D %T"]', file=ofile)
        print('puts stdout "Started reading GDS: $starttime"', file=ofile)
        print('', file=ofile)
        print('flush stdout', file=ofile)
        print('update idletasks', file=ofile)

        if is_gds:
            # Read GDS file
            print('gds readonly true', file=ofile)
            print('gds rescale false', file=ofile)
            print('gds read ' + project_file, file=ofile)
            print('', file=ofile)

        # NOTE:  This assumes that the name of the GDS file is the name of the
        # topmost cell (which should be passed as an option)
        print('load ' + project, file=ofile)
        print('', file=ofile)

        print('set midtime [orig_clock format [orig_clock seconds] -format "%D %T"]', file=ofile)
        print('puts stdout "Starting density checks: $midtime"', file=ofile)
        print('', file=ofile)
        print('flush stdout', file=ofile)
        print('update idletasks', file=ofile)

        # Get step box dimensions (700um for size and 70um for step)
        print('box values 0 0 0 0', file=ofile)
        # print('box size 700um 700um', file=ofile)
        # print('set stepbox [box values]', file=ofile)
        # print('set stepwidth [lindex $stepbox 2]', file=ofile)
        # print('set stepheight [lindex $stepbox 3]', file=ofile)

        print('box size 70um 70um', file=ofile)
        print('set stepbox [box values]', file=ofile)
        print('set stepsizex [lindex $stepbox 2]', file=ofile)
        print('set stepsizey [lindex $stepbox 3]', file=ofile)

        print('select top cell', file=ofile)
        print('expand', file=ofile)
        # Override with FIXED_BBOX, if it is defined
        print('set fullbox [property FIXED_BBOX]', file=ofile)
        print('if {$fullbox == ""} {', file=ofile)
        print('    set fullbox [box values]', file=ofile)
        print('}', file=ofile)
        print('set xmax [lindex $fullbox 2]', file=ofile)
        print('set xmin [lindex $fullbox 0]', file=ofile)
        print('set fullwidth [expr {$xmax - $xmin}]', file=ofile)
        print('set xtiles [expr {int(ceil(($fullwidth + 0.0) / $stepsizex))}]', file=ofile)
        print('set ymax [lindex $fullbox 3]', file=ofile)
        print('set ymin [lindex $fullbox 1]', file=ofile)
        print('set fullheight [expr {$ymax - $ymin}]', file=ofile)
        print('set ytiles [expr {int(ceil(($fullheight + 0.0) / $stepsizey))}]', file=ofile)
        print('box size $stepsizex $stepsizey', file=ofile)
        print('set xbase [lindex $fullbox 0]', file=ofile)
        print('set ybase [lindex $fullbox 1]', file=ofile)
        print('', file=ofile)

        print('puts stdout "XTILES: $xtiles"', file=ofile)
        print('puts stdout "YTILES: $ytiles"', file=ofile)
        print('', file=ofile)

        # Need to know what fraction of a full tile is the last row and column
        print('set xfrac [expr {1.0 - ($xtiles * $stepsizex - $fullwidth + 0.0) / $stepsizex}]', file=ofile)
        print('set yfrac [expr {1.0 - ($ytiles * $stepsizey - $fullheight + 0.0) / $stepsizey}]', file=ofile)

        # If the last row/column fraction is zero, then set to 1 (might never happen?)
        print('if {$xfrac == 0.0} {set xfrac 1.0}', file=ofile)
        print('if {$yfrac == 0.0} {set yfrac 1.0}', file=ofile)

        print('puts stdout "XFRAC: $xfrac"', file=ofile)
        print('puts stdout "YFRAC: $yfrac"', file=ofile)

        print('cif ostyle density', file=ofile)

        # Process density at steps.  For efficiency, this is done in 70x70 um
        # areas, dumped to a file, and then aggregated into the 700x700 areas.

        print('for {set y 0} {$y < $ytiles} {incr y} {', file=ofile)
        print('    for {set x 0} {$x < $xtiles} {incr x} {', file=ofile)
        print('        set xlo [expr $xbase + $x * $stepsizex]', file=ofile)
        print('        set ylo [expr $ybase + $y * $stepsizey]', file=ofile)
        print('        set xhi [expr $xlo + $stepsizex]', file=ofile)
        print('        set yhi [expr $ylo + $stepsizey]', file=ofile)
        print('        box values $xlo $ylo $xhi $yhi', file=ofile)

        # Flatten this area
        print('        flatten -dobbox -nolabels tile', file=ofile)
        print('        load tile', file=ofile)
        print('        select top cell', file=ofile)

        # Run density check for each layer
        print('        puts stdout "Density results for tile x=$x y=$y"', file=ofile)

        print('        set fdens  [cif list cover fom_all]', file=ofile)
        print('        set pdens  [cif list cover poly_all]', file=ofile)
        print('        set ldens  [cif list cover li_all]', file=ofile)
        print('        set m1dens [cif list cover m1_all]', file=ofile)
        print('        set m2dens [cif list cover m2_all]', file=ofile)
        print('        set m3dens [cif list cover m3_all]', file=ofile)
        print('        set m4dens [cif list cover m4_all]', file=ofile)
        print('        set m5dens [cif list cover m5_all]', file=ofile)
        print('        puts stdout "FOM: $fdens"', file=ofile)
        print('        puts stdout "POLY: $pdens"', file=ofile)
        print('        puts stdout "LI1: $ldens"', file=ofile)
        print('        puts stdout "MET1: $m1dens"', file=ofile)
        print('        puts stdout "MET2: $m2dens"', file=ofile)
        print('        puts stdout "MET3: $m3dens"', file=ofile)
        print('        puts stdout "MET4: $m4dens"', file=ofile)
        print('        puts stdout "MET5: $m5dens"', file=ofile)
        print('        flush stdout', file=ofile)
        print('        update idletasks', file=ofile)

        print('        load ' + project, file=ofile)
        print('        cellname delete tile', file=ofile)

        print('    }', file=ofile)
        print('}', file=ofile)

        print('set endtime [orig_clock format [orig_clock seconds] -format "%D %T"]', file=ofile)
        print('puts stdout "Ended: $endtime"', file=ofile)
        print('quit -noprompt', file=ofile)
        print('', file=ofile)


    myenv = os.environ.copy()
    myenv['MAGTYPE'] = 'mag'

    print('Running density checks on file ' + user_project_path, flush=True)
    
    magic_run_opts = [
		'magic',
		'-dnull',
		'-noconsole',
		'-rcfile', rcfile_path,
		layoutpath + '/check_density.tcl']

    mproc = subprocess.Popen(magic_run_opts,
		stdin = subprocess.DEVNULL,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		cwd = layoutpath,
		env = myenv,
		universal_newlines = True)

    # Use signal to poll the process and generate any output as it arrives

    dlines = []

    while mproc:
        status = mproc.poll()
        if status != None:
            try:
                output = mproc.communicate(timeout=1)
            except ValueError:
                print('Magic forced stop, status ' + str(status))
                sys.exit(1)
            else:
                outlines = output[0]
                errlines = output[1]
                for line in outlines.splitlines():
                    dlines.append(line)
                    print(line)
                for line in errlines.splitlines():
                    print(line)
                print('Magic exited with status ' + str(status))
                if int(status) != 0:
                    sys.exit(int(status))
                else:
                    break
        else:
            n = 0
            while True:
                n += 1
                if n > 100:
                    n = 0
                    status = mproc.poll()
                    if status != None:
                        break
                sresult = select.select([mproc.stdout, mproc.stderr], [], [], 0)[0]
                if mproc.stdout in sresult:
                    outstring = mproc.stdout.readline().strip()
                    dlines.append(outstring)
                    print(outstring)
                elif mproc.stderr in sresult:
                    outstring = mproc.stderr.readline().strip()
                    print(outstring)
                else:
                    break

    fomfill  = []
    polyfill = []
    lifill   = []
    met1fill = []
    met2fill = []
    met3fill = []
    met4fill = []
    met5fill = []
    xtiles = 0
    ytiles = 0
    xfrac = 0.0
    yfrac = 0.0

    for line in dlines:
        dpair = line.split(':')
        if debugmode:
            print('Magic output line: ' + line)
        if len(dpair) == 2:
            layer = dpair[0]
            try:
                density = float(dpair[1].strip())
            except:
                continue
            if layer == 'FOM':
                fomfill.append(density)
            elif layer == 'POLY':
                polyfill.append(density)
            elif layer == 'LI1':
                lifill.append(density)
            elif layer == 'MET1':
                met1fill.append(density)
            elif layer == 'MET2':
                met2fill.append(density)
            elif layer == 'MET3':
                met3fill.append(density)
            elif layer == 'MET4':
                met4fill.append(density)
            elif layer == 'MET5':
                met5fill.append(density)
            elif layer == 'XTILES':
                xtiles = int(dpair[1].strip())
            elif layer == 'YTILES':
                ytiles = int(dpair[1].strip())
            elif layer == 'XFRAC':
                xfrac = float(dpair[1].strip())
            elif layer == 'YFRAC':
                yfrac = float(dpair[1].strip())

    if ytiles == 0 or xtiles == 0:
        print('Failed to read XTILES or YTILES from output.')
        sys.exit(1)

    if xtiles < 10 or ytiles < 10:
        print('Layout is < 700um x 700um;  cannot run density checks.')
        sys.exit(1)

    total_tiles = (ytiles - 9) * (xtiles - 9)

    print('')
    print('Stepped area density results (total tiles = ' + str(total_tiles) + '):')

    # Full areas are 10 x 10 tiles = 100.  But the right and top sides are
    # not full tiles, so the full area must be prorated.

    print('Side adjustment = ' + '{:.3f}'.format(xfrac))
    print('Top adjustment = ' + '{:.3f}'.format(yfrac))

    if debugmode:
        with open('tile_densities.txt', 'w') as dfile:
            print(str(fomfill), file=dfile)
            print(str(polyfill), file=dfile)
            print(str(lifill), file=dfile)
            print(str(met1fill), file=dfile)
            print(str(met2fill), file=dfile)
            print(str(met3fill), file=dfile)
            print(str(met4fill), file=dfile)
            print(str(met5fill), file=dfile)

    print('')
    print('FOM Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            fomaccum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                fomaccum += sum(fomfill[base : base + 9])
                fomaccum += fomfill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            fomaccum += sum(fomfill[base : base + 9]) * locyfrac
            fomaccum += fomfill[base + 9] * locxfrac * locyfrac
                    
            fomaccum /= atotal
            fomstr = "{:.3f}".format(fomaccum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + fomstr)
            if fomaccum < 0.33:
                print('***Error:  FOM Density < 33%')
            elif fomaccum > 0.57:
                print('***Error:  FOM Density > 57%')

    print('')
    print('POLY Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            polyaccum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                polyaccum += sum(polyfill[base : base + 9])
                polyaccum += polyfill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            polyaccum += sum(polyfill[base : base + 9]) * locyfrac
            polyaccum += polyfill[base + 9] * locxfrac * locyfrac
                    
            polyaccum /= atotal
            polystr = "{:.3f}".format(polyaccum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + polystr)

    print('')
    print('LI Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            liaccum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                liaccum += sum(lifill[base : base + 9])
                liaccum += lifill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            liaccum += sum(lifill[base : base + 9]) * locyfrac
            liaccum += lifill[base + 9] * locxfrac * locyfrac
                    
            liaccum /= atotal
            listr = "{:.3f}".format(liaccum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + listr)
            if liaccum < 0.35:
                print('***Error:  LI Density < 35%')
            elif liaccum > 0.60:
                print('***Error:  LI Density > 60%')

    print('')
    print('MET1 Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            met1accum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                met1accum += sum(met1fill[base : base + 9])
                met1accum += met1fill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            met1accum += sum(met1fill[base : base + 9]) * locyfrac
            met1accum += met1fill[base + 9] * locxfrac * locyfrac
                    
            met1accum /= atotal
            met1str = "{:.3f}".format(met1accum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + met1str)
            if met1accum < 0.35:
                print('***Error:  MET1 Density < 35%')
            elif met1accum > 0.60:
                print('***Error:  MET1 Density > 60%')

    print('')
    print('MET2 Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            met2accum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                met2accum += sum(met2fill[base : base + 9])
                met2accum += met2fill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            met2accum += sum(met2fill[base : base + 9]) * locyfrac
            met2accum += met2fill[base + 9] * locxfrac * locyfrac
                    
            met2accum /= atotal
            met2str = "{:.3f}".format(met2accum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + met2str)
            if met2accum < 0.35:
                print('***Error:  MET2 Density < 35%')
            elif met2accum > 0.60:
                print('***Error:  MET2 Density > 60%')

    print('')
    print('MET3 Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            met3accum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                met3accum += sum(met3fill[base : base + 9])
                met3accum += met3fill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            met3accum += sum(met3fill[base : base + 9]) * locyfrac
            met3accum += met3fill[base + 9] * locxfrac * locyfrac
                    
            met3accum /= atotal
            met3str = "{:.3f}".format(met3accum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + met3str)
            if met3accum < 0.35:
                print('***Error:  MET3 Density < 35%')
            elif met3accum > 0.60:
                print('***Error:  MET3 Density > 60%')

    print('')
    print('MET4 Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0

        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            met4accum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                met4accum += sum(met4fill[base : base + 9])
                met4accum += met4fill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            met4accum += sum(met4fill[base : base + 9]) * locyfrac
            met4accum += met4fill[base + 9] * locxfrac * locyfrac
                    
            met4accum /= atotal
            met4str = "{:.3f}".format(met4accum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + met4str)
            if met4accum < 0.35:
                print('***Error:  MET4 Density < 35%')
            elif met4accum > 0.60:
                print('***Error:  MET4 Density > 60%')

    print('')
    print('MET5 Density:')
    for y in range(0, ytiles - 9):
        if y == ytiles - 10:
            locyfrac = yfrac
        else:
            locyfrac = 1.0
        for x in range(0, xtiles - 9):
            if x == xtiles - 10:
                locxfrac = xfrac
            else:
                locxfrac = 1.0

            met5accum = 0
            atotal = 81.0 + 9.0 * locxfrac + 9.0 * locyfrac + locxfrac * locyfrac

            for w in range(y, y + 9):
                base = xtiles * w + x
                met5accum += sum(met5fill[base : base + 9])
                met5accum += met5fill[base + 9] * locxfrac
            base = xtiles * (y + 9) + x
            met5accum += sum(met5fill[base : base + 9]) * locyfrac
            met5accum += met5fill[base + 9] * locxfrac * locyfrac
                    
            met5accum /= atotal
            met5str = "{:.3f}".format(met5accum)
            print('Tile (' + str(x) + ', ' + str(y) + '):   ' + met5str)
            if met5accum < 0.45:
                print('***Error:  MET5 Density < 45%')
            elif met5accum > 0.76:
                print('***Error:  MET5 Density > 76%')

    print('')
    print('Whole-chip (global) density results:')

    atotal = ((xtiles - 1.0) * (ytiles - 1.0)) + ((ytiles - 1.0) * xfrac) + ((xtiles - 1.0) * yfrac) + (xfrac * yfrac)

    fomaccum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        fomaccum += sum(fomfill[base:base + xtiles - 1])
        fomaccum += fomfill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    fomaccum += sum(fomfill[base:base + xtiles - 1]) * yfrac
    fomaccum += fomfill[base + xtiles - 1] * xfrac * yfrac

    fomaccum /= atotal
    fomstr = "{:.3f}".format(fomaccum)
    print('')
    print('FOM Density: ' + fomstr)
    if fomaccum < 0.33:
        print('***Error:  FOM Density < 33%')
    elif fomaccum > 0.57:
        print('***Error:  FOM Density > 57%')

    polyaccum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        polyaccum += sum(polyfill[base:base + xtiles - 1])
        polyaccum += polyfill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    polyaccum += sum(polyfill[base:base + xtiles - 1]) * yfrac
    polyaccum += polyfill[base + xtiles - 1] * xfrac * yfrac

    polyaccum /= atotal
    polystr = "{:.3f}".format(polyaccum)
    print('')
    print('POLY Density: ' + polystr)

    liaccum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        liaccum += sum(lifill[base:base + xtiles - 1])
        liaccum += lifill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    liaccum += sum(lifill[base:base + xtiles - 1]) * yfrac
    liaccum += lifill[base + xtiles - 1] * xfrac * yfrac

    liaccum /= atotal
    listr = "{:.3f}".format(liaccum)
    print('')
    print('LI Density: ' + listr)
    if liaccum < 0.35:
        print('***Error:  LI Density < 35%')
    elif liaccum > 0.60:
        print('***Error:  LI Density > 60%')

    met1accum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        met1accum += sum(met1fill[base:base + xtiles - 1])
        met1accum += met1fill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    met1accum += sum(met1fill[base:base + xtiles - 1]) * yfrac
    met1accum += met1fill[base + xtiles - 1] * xfrac * yfrac

    met1accum /= atotal
    met1str = "{:.3f}".format(met1accum)
    print('')
    print('MET1 Density: ' + met1str)
    if met1accum < 0.35:
        print('***Error:  MET1 Density < 35%')
    elif met1accum > 0.60:
        print('***Error:  MET1 Density > 60%')

    met2accum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        met2accum += sum(met2fill[base:base + xtiles - 1])
        met2accum += met2fill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    met2accum += sum(met2fill[base:base + xtiles - 1]) * yfrac
    met2accum += met2fill[base + xtiles - 1] * xfrac * yfrac

    met2accum /= atotal
    met2str = "{:.3f}".format(met2accum)
    print('')
    print('MET2 Density: ' + met2str)
    if met2accum < 0.35:
        print('***Error:  MET2 Density < 35%')
    elif met2accum > 0.60:
        print('***Error:  MET2 Density > 60%')

    met3accum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        met3accum += sum(met3fill[base:base + xtiles - 1])
        met3accum += met3fill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    met3accum += sum(met3fill[base:base + xtiles - 1]) * yfrac
    met3accum += met3fill[base + xtiles - 1] * xfrac * yfrac

    met3accum /= atotal
    met3str = "{:.3f}".format(met3accum)
    print('')
    print('MET3 Density: ' + met3str)
    if met3accum < 0.35:
        print('***Error:  MET3 Density < 35%')
    elif met3accum > 0.60:
        print('***Error:  MET3 Density > 60%')

    met4accum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        met4accum += sum(met4fill[base:base + xtiles - 1])
        met4accum += met4fill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    met4accum += sum(met4fill[base:base + xtiles - 1]) * yfrac
    met4accum += met4fill[base + xtiles - 1] * xfrac * yfrac

    met4accum /= atotal
    met4str = "{:.3f}".format(met4accum)
    print('')
    print('MET4 Density: ' + met4str)
    if met4accum < 0.35:
        print('***Error:  MET4 Density < 35%')
    elif met4accum > 0.60:
        print('***Error:  MET4 Density > 60%')

    met5accum = 0
    for y in range(0, ytiles - 1):
        base = xtiles * y
        met5accum += sum(met5fill[base:base + xtiles - 1])
        met5accum += met5fill[base + xtiles - 1] * xfrac
    base = xtiles * (ytiles - 1)
    met5accum += sum(met5fill[base:base + xtiles - 1]) * yfrac
    met5accum += met5fill[base + xtiles - 1] * xfrac * yfrac

    met5accum /= atotal
    met5str = "{:.3f}".format(met5accum)
    print('')
    print('MET5 Density: ' + met5str)
    if met5accum < 0.45:
        print('***Error:  MET5 Density < 45%')
    elif met5accum > 0.76:
        print('***Error:  MET5 Density > 76%')

    if not keepmode:
        if os.path.isfile(layoutpath + '/check_density.tcl'):
            os.remove(layoutpath + '/check_density.tcl')

    print('')
    print('Done!')
    sys.exit(0)

