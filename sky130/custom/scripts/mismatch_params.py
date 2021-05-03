#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Parse the SPICE model files from sky130 and use the (commented out)
# statistics block to generate the correct monte carlo expressions
# in the device models for mismatch.
#--------------------------------------------------------------------

import os
import re
import sys

mm_switch_param = 'MC_MM_SWITCH'

walkpath = 'sky130A/libs.ref/sky130_fd_pr/spice'

if len(sys.argv) > 1:
    walkpath = sys.argv[1]

mismatch_params = []

mmrex = re.compile('^\*[ \t]*mismatch[ \t]+\{')
endrex = re.compile('^\*[ \t]*\}')

filelist = []

#--------------------------------------------------------------------
# Step 1.  Gather variables
#--------------------------------------------------------------------

for dirpath, dirnames, filenames in os.walk(walkpath):
    for filename in filenames:
        if os.path.splitext(filename)[1] == '.spice':
            infile_name = os.path.join(dirpath, filename)
            filelist.append(infile_name)

            infile = open(infile_name, 'r')

            state = 'before_mismatch'
            line_number = 0
            replaced_something = False

            for line in infile:
                line_number += 1

                if state == 'before_mismatch':
                    mmatch = mmrex.match(line)
                    if mmatch:
                        state = 'in_mismatch'
                elif state == 'in_mismatch':
                    ematch = endrex.match(line)
                    if ematch:
                        state = 'after_mismatch'
                    else:
                        tokens = line.split()
                        if 'vary' in tokens:
                            if ('dist=gauss' in tokens) or ('gauss' in tokens):
                                mismatch_param = tokens[2]
                                std_dev = float(tokens[-1].split('=')[-1])
                                replacement = '{}*AGAUSS(0,{!s},1)'.format(mm_switch_param, std_dev)
                                mismatch_params.append((mismatch_param, replacement))

            infile.close()

print('') 
print('Mismatch parameters found:')
for (mismatch_param, replacement) in mismatch_params:
     print(mismatch_param + ' : ' + replacement)
print('') 

#--------------------------------------------------------------------
# Step 2.  Make replacements
#--------------------------------------------------------------------

for infile_name in filelist:

    filepath = os.path.split(infile_name)[0]
    outfile_name = os.path.join(filepath, 'temp')

    infile = open(infile_name, 'r')
    outfile = open(outfile_name, 'w')

    state = 'before_mismatch'
    line_number = 0
    replaced_something = False

    for line in infile:
        line_number += 1

        if state == 'before_mismatch':
            outfile.write(line)
            mmatch = mmrex.match(line)
            if mmatch:
                state = 'in_mismatch'
        elif state == 'in_mismatch':
            outfile.write(line)
            ematch = endrex.match(line)
            if ematch:
                state = 'after_mismatch'
        elif state == 'after_mismatch':
            newline = line
            for (param, replacement) in mismatch_params:
                if param in newline:
                    newline = newline.replace(param, replacement)
                    replaced_something = True
                    print("  Line {}: Found mismatch parameter '{}' and replaced with '{}'.".format(line_number, param, replacement))
            outfile.write(newline)

    infile.close()
    outfile.close()
    if replaced_something:
        print("Something was replaced in '{}', backed up original file and replaced with processed one.".format(infile_name))
        os.rename(infile_name, infile_name + '.orig')
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

