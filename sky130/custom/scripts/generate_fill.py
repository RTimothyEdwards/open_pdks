#!/bin/env python3
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
# generate_fill.py ---
#
#    Run the fill generation on a layout top level.
#

import sys
import os
import re
import subprocess

def usage():
    print("Usage:")
    print("generate_fill.py <layout_name> [-keep] [-test]")
    print("")
    print("where:")
    print("    <layout_name> is the path to the .mag file to be filled.")
    print("")
    print("  If '-keep' is specified, then keep the generation script.")
    print("  If '-test' is specified, then create but do not run the generation script.")
    return 0

if __name__ == '__main__':

    optionlist = []
    arguments = []

    debugmode = False
    keepmode = False
    testmode = False

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 1:
        print("Wrong number of arguments given to generate_fill.py.")
        usage()
        sys.exit(1)

    user_project_path = arguments[0]

    magpath = os.path.split(user_project_path)[0]
    if magpath == '':
        magpath = os.getcwd()

    if os.path.splitext(user_project_path)[1] != '.mag':
        if os.path.splitext(user_project_path)[1] == '':
            user_project_path += '.mag'
        else:
            print('Error:  Project is not a magic database .mag file!')
            sys.exit(1)

    if not os.path.isfile(user_project_path):
        print('Error:  Project "' + user_project_path + '" does not exist or is not readable.')
        sys.exit(1)

    if '-debug' in optionlist:
        debugmode = True
    if '-keep' in optionlist:
        keepmode = True
    if '-test' in optionlist:
        testmode = True

    rcfile = magpath + '/.magicrc'
    if not os.path.isfile(rcfile):
        rcfile = None

    project = os.path.splitext(os.path.split(user_project_path)[1])[0]

    topdir = os.path.split(magpath)[0]
    gdsdir = topdir + '/gds'
    hasgdsdir = True if os.path.isdir(gdsdir) else False

    with open(magpath + '/generate_fill.tcl', 'w') as ofile:
        print('#!/bin/env wish', file=ofile)
        print('drc off', file=ofile)
        print('tech unlock *', file=ofile)
        print('snap internal', file=ofile)
        print('box values 0 0 0 0', file=ofile)
        print('box size 700um 700um', file=ofile)
        print('set stepbox [box values]', file=ofile)
        print('set stepwidth [lindex $stepbox 2]', file=ofile)
        print('set stepheight [lindex $stepbox 3]', file=ofile)
        print('', file=ofile)
        print('set starttime [orig_clock format [orig_clock seconds] -format "%D %T"]', file=ofile)
        print('puts stdout "Started: $starttime"', file=ofile)
        print('', file=ofile)
        print('load ' + project + ' -dereference', file=ofile)
        print('select top cell', file=ofile)
        print('expand', file=ofile)
        print('cif ostyle wafflefill(tiled)', file=ofile)
        print('', file=ofile)
        print('set fullbox [box values]', file=ofile)
        print('set xmax [lindex $fullbox 2]', file=ofile)
        print('set xmin [lindex $fullbox 0]', file=ofile)
        print('set fullwidth [expr {$xmax - $xmin}]', file=ofile)
        print('set xtiles [expr {int(ceil(($fullwidth + 0.0) / $stepwidth))}]', file=ofile)
        print('set ymax [lindex $fullbox 3]', file=ofile)
        print('set ymin [lindex $fullbox 1]', file=ofile)
        print('set fullheight [expr {$ymax - $ymin}]', file=ofile)
        print('set ytiles [expr {int(ceil(($fullheight + 0.0) / $stepheight))}]', file=ofile)
        print('box size $stepwidth $stepheight', file=ofile)
        print('set xbase [lindex $fullbox 0]', file=ofile)
        print('set ybase [lindex $fullbox 1]', file=ofile)
        print('', file=ofile)

        # Break layout into tiles and process each separately
        print('for {set y 0} {$y < $ytiles} {incr y} {', file=ofile)
        print('    for {set x 0} {$x < $xtiles} {incr x} {', file=ofile)
        print('        set xlo [expr $xbase + $x * $stepwidth]', file=ofile)
        print('        set ylo [expr $ybase + $y * $stepheight]', file=ofile)
        print('        set xhi [expr $xlo + $stepwidth]', file=ofile)
        print('        set yhi [expr $ylo + $stepheight]', file=ofile)
        print('        if {$xhi > $fullwidth} {set xhi $fullwidth}', file=ofile)
        print('        if {$yhi > $fullheight} {set yhi $fullheight}', file=ofile)
        print('        box values $xlo $ylo $xhi $yhi', file=ofile)
        # The flattened area must be larger than the fill tile by >1.5um
        print('        box grow c 1.6um', file=ofile)

        # Flatten into a cell with a new name
        print('        puts stdout "Flattening layout of tile x=$x y=$y. . . "', file=ofile)
        print('        flush stdout', file=ofile)
        print('        update idletasks', file=ofile)
        print('        flatten -dobox -nolabels ' + project + '_fill_pattern_${x}_$y', file=ofile)
        print('        load ' + project + '_fill_pattern_${x}_$y', file=ofile)

        # Remove any GDS_FILE reference (there should not be any?)
        print('        property GDS_FILE ""', file=ofile)
        # Set boundary using comment layer, to the size of the step box
	# This corresponds to the "topbox" rule in the wafflefill(tiled) style
        print('        select top cell', file=ofile)
        print('        erase comment', file=ofile)
        print('        box values $xlo $ylo $xhi $yhi', file=ofile)
        print('        paint comment', file=ofile)
        print('        puts stdout "Writing GDS. . . "', file=ofile)
        print('        flush stdout', file=ofile)
        print('        update idletasks', file=ofile)
        print('        gds write ' + project + '_fill_pattern_${x}_$y.gds', file=ofile)

        # Reload project top
        print('        load ' + project, file=ofile)

        # Remove last generated cell to save memory
        print('        cellname delete ' + project + '_fill_pattern_${x}_$y', file=ofile)

        print('    }', file=ofile)
        print('}', file=ofile)

        # Now create simple "fake" views of all the tiles.
        print('gds readonly true', file=ofile)
        print('gds rescale false', file=ofile)
        print('for {set y 0} {$y < $ytiles} {incr y} {', file=ofile)
        print('    for {set x 0} {$x < $xtiles} {incr x} {', file=ofile)
        print('        set xlo [expr $xbase + $x * $stepwidth]', file=ofile)
        print('        set ylo [expr $ybase + $y * $stepheight]', file=ofile)
        print('        set xhi [expr $xlo + $stepwidth]', file=ofile)
        print('        set yhi [expr $ylo + $stepheight]', file=ofile)
        print('        load ' + project + '_fill_pattern_${x}_$y -quiet', file=ofile)
        print('        box values $xlo $ylo $xhi $yhi', file=ofile)
        print('        paint comment', file=ofile)
        print('        property FIXED_BBOX "$xlo $ylo $xhi $yhi"', file=ofile)
        print('        property GDS_FILE ' + project + '_fill_pattern_${x}_${y}.gds', file=ofile)
        print('        property GDS_START 0', file=ofile)
        print('    }', file=ofile)
        print('}', file=ofile)

        # Now tile everything back together
        print('load ' + project + '_fill_pattern -quiet', file=ofile)
        print('for {set y 0} {$y < $ytiles} {incr y} {', file=ofile)
        print('    for {set x 0} {$x < $xtiles} {incr x} {', file=ofile)
        print('        box values 0 0 0 0', file=ofile)
        print('        getcell ' + project + '_fill_pattern_${x}_$y child 0 0', file=ofile)
        print('    }', file=ofile)
        print('}', file=ofile)

        # And write final GDS
        print('puts stdout "Writing final GDS"', file=ofile)

        print('cif *hier write disable', file=ofile)
        print('cif *array write disable', file=ofile)
        if hasgdsdir:
            print('gds write ../gds/' + project + '_fill_pattern.gds', file=ofile)
        else:
            print('gds write ' + project + '_fill_pattern.gds', file=ofile)
        print('set endtime [orig_clock format [orig_clock seconds] -format "%D %T"]', file=ofile)
        print('puts stdout "Ended: $endtime"', file=ofile)
        print('quit -noprompt', file=ofile)
    myenv = os.environ.copy()
    myenv['MAGTYPE'] = 'mag'

    if not testmode:
        # Diagnostic
        # print('This script will generate file ' + project + '_fill_pattern.gds')
        print('This script will generate files ' + project + '_fill_pattern_x_y.gds')
        print('Now generating fill patterns.  This may take. . . quite. . . a while.', flush=True)
        mproc = subprocess.run(['magic', '-dnull', '-noconsole',
		'-rcfile', rcfile, magpath + '/generate_fill.tcl'],
		stdin = subprocess.DEVNULL,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		cwd = magpath,
		env = myenv,
		universal_newlines = True)
        if mproc.stdout:
            for line in mproc.stdout.splitlines():
                print(line)
        if mproc.stderr:
            print('Error message output from magic:')
            for line in mproc.stderr.splitlines():
                print(line)
            if mproc.returncode != 0:
                print('ERROR:  Magic exited with status ' + str(mproc.returncode))

    if not keepmode:
        # Remove fill generation script
        os.remove(magpath + '/generate_fill.tcl')
        # Remove all individual fill tiles, leaving only the composite GDS.
        filelist = os.listdir(magpath)
        for file in filelist:
            if os.path.splitext(magpath + '/' + file)[1] == '.gds':
                if file.startswith(project + '_fill_pattern_'):
                    os.remove(magpath + '/' + file)

    print('Done!')
    exit(0)
