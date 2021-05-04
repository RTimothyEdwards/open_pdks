#!/usr/bin/env python3
# Copyright 2020 R. Timothy Edwards
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
#-------------------------------------------------------------------------
# run_standard_drc.py ---  A script to run magic in batch mode and apply
# full DRC checks on a layout.  This inclues full DRC but excludes
# antenna and density checks, for which there are separate scripts.
#
# Usage:
#
#   run_standard_drc.py <layout_name>
#
# Results:
#
#   generates a file "<layout_name>_drc.txt" containing a human-readable
#   list of the DRC errors.
# 	
#-------------------------------------------------------------------------

import subprocess
import shutil
import glob
import sys
import os
import re

# Work in progress

def run_full_drc(layout_name, output_file):
    is_gds = False

    # Remove any extension from layout_name
    layout_root = layout_name
    layout_name = os.path.splitext(layout_root)[0]
    layout_ext = os.path.splitext(layout_root)[1]

    if layout_ext != '.mag':
        # Assume this is GDS
        # Is the layout file in the current directory, or a full
        # path, or is this a project directory?

        is_gds = True
        if layout_name[0] == '/':
            gdspath = os.path.split(layout_name)[0]
            layout_name = os.path.split(layout_name)[1]

        else:
            if not os.path.isfile(layout_root):
                if not os.path.isfile('gds/' + layout_root):
                    print('Error:  Cannot find GDS file ' + layout_root)
                    return
                else:
                    gdspath = os.getcwd() + '/gds'
            else:
                gdspath = os.getcwd()

        if os.path.isdir('mag/'):
            magpath = os.getcwd() + '/mag'
        else:
            magpath = os.getcwd()

    else:
        # File is a .mag layout
        # Is the layout file in the current directory, or a full
        # path, or is this a project directory?

        if layout_name[0] == '/':
            magpath = os.path.split(layout_name)[0]
            layout_name = os.path.split(layout_name)[1]

        else:
            if not os.path.isfile(layout_name + '.mag'):
                if not os.path.isfile('mag/' + layout_name + '.mag'):
                    print('Error:  Cannot find file ' + layout_name + '.mag')
                    return
                else:
                    magpath = os.getcwd() + '/mag'
            else:
                magpath = os.getcwd()

    if output_file == '':
        output_file = layout_name + '_drc.txt'

    # Check for presence of a .magicrc file, or else check for environment
    # variable PDKPATH, or PDK_PATH

    myenv = os.environ.copy()
    myenv['MAGTYPE'] = 'mag'

    if os.path.isfile(magpath + '/.magicrc'):
       rcfile = magpath + '/.magicrc'
    elif os.path.isfile(os.getcwd() + '/.magicrc'):
       rcfile = os.getcwd() + '/.magicrc'
    else:
        if 'PDKPATH' in myenv:
            rcpathroot = myenv['PDKPATH'] + '/libs.tech/magic'
            rcfile = glob.glob(rcpathroot + '/*.magicrc')[0]
        elif 'PDK_PATH' in myenv:
            rcpathroot = myenv['PDKPATH'] + '/libs.tech/magic'
            rcfile = glob.glob(rcpathroot + '/*.magicrc')[0]
        else:
            print('Error: Cannot get magic rcfile for the technology!')
            return

    # Generate the DRC Tcl script

    # If magpath is writeable, then continue.  If not, then if the
    # current working directory is writeable, use it.
    if not os.access(magpath, os.W_OK):
        if os.access(os.getcwd(), os.W_OK):
            scriptpath = os.getcwd()
            # The output .txt file won't be writeable, either.
            output_file = os.path.join(scriptpath, os.path.split(output_file)[1])
        else:
            print('Error:  Neither the path of the layout or the current directory is writeable.')
            return
    else:
        scriptpath = magpath

    print('Evaluating full DRC results for layout ' + layout_name)
    magic_script = scriptpath + "/run_magic_drc_%s.tcl" % os.path.basename(layout_name)
    with open(magic_script, 'w') as ofile:
        print('# run_magic_drc.tcl ---', file=ofile)
        print('#    batch script for running DRC', file=ofile)
        print('', file=ofile)
        print('crashbackups stop', file=ofile)
        print('drc euclidean on', file=ofile)
        print('drc style drc(full)', file=ofile)
        print('drc on', file=ofile)
        print('snap internal', file=ofile)
        if is_gds:
            print('gds flatglob *__example_*', file=ofile)
            print('gds flatten true', file=ofile)
            print('gds read ' + gdspath + '/' + layout_name, file=ofile)
            print('load ' + layout_name, file=ofile)
        else:
            print('load ' + layout_name + ' -dereference', file=ofile)
        print('select top cell', file=ofile)
        print('expand', file=ofile)
        print('drc catchup', file=ofile)
        print('set allerrors [drc listall why]', file=ofile)
        print('set oscale [cif scale out]', file=ofile)
        print('set ofile [open ' + output_file + ' w]', file=ofile)
        print('puts $ofile "DRC errors for cell ' + layout_name + '"', file=ofile)
        print('puts $ofile "--------------------------------------------"', file=ofile)
        print('foreach {whytext rectlist} $allerrors {', file=ofile)
        print('   puts $ofile ""', file=ofile)
        print('   puts $ofile $whytext', file=ofile)
        print('   foreach rect $rectlist {', file=ofile)
        print('       set llx [format "%.3f" [expr $oscale * [lindex $rect 0]]]',
				file=ofile)
        print('       set lly [format "%.3f" [expr $oscale * [lindex $rect 1]]]',
				file=ofile)
        print('       set urx [format "%.3f" [expr $oscale * [lindex $rect 2]]]',
				file=ofile)
        print('       set ury [format "%.3f" [expr $oscale * [lindex $rect 3]]]',
				file=ofile)
        print('       puts $ofile "$llx $lly $urx $ury"', file=ofile)
        print('   }', file=ofile)
        print('}', file=ofile)
        print('close $ofile', file=ofile)

    # Run the DRC Tcl script

    print('Running: magic -dnull -noconsole -rcfile ' + rcfile + ' ' + magic_script)
    print('Running in directory: ' + magpath)
    mproc = subprocess.run(['magic', '-dnull', '-noconsole', '-rcfile',
		rcfile, magic_script],
		env = myenv, cwd = magpath,
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

    print('Done!')

# If called as main, run all DRC tests

if __name__ == '__main__':

    # Divide up command line into options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # Need one argument:  path to layout
    # If two arguments, then 2nd argument is the output file.

    if len(arguments) > 0 and len(arguments) < 3:
        layout_root = arguments[0]

    if len(arguments) == 1:
        out_filename = ""
    elif len(arguments) > 2:
        out_filename = arguments[1]

    if len(arguments) > 0 and len(arguments) < 3:
        run_full_drc(layout_root, out_filename)
    else:
        print("Usage:  run_standard_drc.py <layout_name> [<output_file>] [options]")
        print("Options:")
        print("   (none)")
    

