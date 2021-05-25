#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Parse the SPICE model files from sky130 and use the (commented out)
# statistics block to generate the correct monte carlo expressions
# in the parameters for process variation.
#--------------------------------------------------------------------

import os
import re
import sys

pr_switch_param = 'MC_PR_SWITCH'

walkpath = 'sky130A/libs.tech/ngspice'

if len(sys.argv) > 1:
    walkpath = sys.argv[1]

process_params = []

parmrex = re.compile('^\.param[ \t]+')
prrex = re.compile('^\*[ \t]*process[ \t]+\{')
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

            state = 'before_process'
            line_number = 0
            replaced_something = False

            for line in infile:
                line_number += 1

                if state == 'before_process':
                    pmatch = prrex.match(line)
                    if pmatch:
                        state = 'in_process'
                elif state == 'in_process':
                    ematch = endrex.match(line)
                    if ematch:
                        state = 'after_process'
                    else:
                        tokens = line.split()
                        if 'vary' in tokens:
                            if ('dist=gauss' in tokens) or ('gauss' in tokens):
                                process_param = tokens[2]
                                std_dev = float(tokens[-1].split('=')[-1])
                                replacement = ' + {}*AGAUSS(0,{!s},1)'.format(pr_switch_param, std_dev)
                                process_params.append((process_param, replacement))

            infile.close()

# Sort the process parameters so that names that are subsets of other
# names appear later in the list.

def getKey(item):
    return item[0]

process_params.sort(reverse=True, key=getKey)

print('') 
print('Process parameters found:')
for (process_param, addendum) in process_params:
     print(process_param + '  :' + addendum)
print('') 

#--------------------------------------------------------------------
# Step 2.  Make replacements
#--------------------------------------------------------------------

for infile_name in filelist:

    filepath = os.path.split(infile_name)[0]
    outfile_name = os.path.join(filepath, 'temp')

    infile = open(infile_name, 'r')
    outfile = open(outfile_name, 'w')

    state = 'before_process'
    line_number = 0
    replaced_something = False

    for line in infile:
        line_number += 1

        if state == 'before_process':
            pmatch = prrex.match(line)
            if pmatch:
                state = 'in_process'
                outfile.write(line)
            else:
                pmatch = parmrex.match(line)
                if pmatch:
                    newline = line
                    for (param, replacement) in process_params:
                        if ' ' + param + ' ' in newline:
                            newline = newline.strip('\n') + replacement + '\n'
                            print("  Line {}: Found process parameter '{}' and appended '{}'.".format(line_number, param, replacement))
                            replaced_something = True
                    outfile.write(newline)
                else:
                    outfile.write(line)
        elif state == 'in_process':
            outfile.write(line)
            ematch = endrex.match(line)
            if ematch:
                state = 'after_process'
        elif state == 'after_process':
            outfile.write(line)

    infile.close()
    outfile.close()
    if replaced_something:
        # print("Something was replaced in '{}', backed up original file"
        #	+ " and replaced with processed one.".format(infile_name))
        print("Something was replaced in '{}'".format(infile_name))
        # os.rename(infile_name, infile_name + '.orig')
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

