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

# Sort the process parameters so that names that are subsets of other
# names appear later in the list.

def getKey(item):
    return item[0]

pr_switch_param = 'MC_PR_SWITCH'

options = []
arguments = []
for item in sys.argv[1:]:
    if item.find('-', 0) == 0:
        options.append(item[1:])
    else:
        arguments.append(item)

variant = 'sky130A'
walkpath = variant + '/libs.ref/sky130_fd_pr/spice'

if len(options) > 0:
    for option in options:
        if option.startswith('variant'):
            variant = option.split('=')[1]
    walkpath = variant + '/libs.ref/sky130_fd_pr/spice'
elif len(arguments) > 0:
    walkpath = arguments[0]

process_params = []

parmrex = re.compile(r'^\.param[ \t]+')
prrex = re.compile(r'^\*[ \t]*process[ \t]*\{')
endrex = re.compile(r'^\*[ \t]*\}')

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
                        # Make sure all "A = B" syntax closes up around the equal sign.
                        newline = re.sub(r'[ \t]*=[ \t]*', '=', line)
                        tokens = newline.split()
                        if 'vary' in tokens:
                            if ('dist=gauss' in tokens) or ('gauss' in tokens):
                                gtype = 'A'
                                process_param = tokens[2]
                                for token in tokens[3:]:
                                    gparam = token.split('=')
                                    if len(gparam) == 2:
                                        if gparam[0] == 'std':
                                            std_dev = float(gparam[1])
                                        elif gparam[0] == 'percent' and gparam[1] == 'yes':
                                            gtype = ''
                                if gtype == '':
                                    # Convert percentage to a fraction
                                    std_dev = std_dev / 100
                                repltext = ' + {}*' + gtype + 'GAUSS(0,{!s},1)'
                                replacement = repltext.format(pr_switch_param, std_dev)
                                process_params.append((process_param, replacement))
                            elif ('dist=lnorm' in tokens) or ('lnorm' in tokens):
                                process_param = tokens[2]
                                for token in tokens[3:]:
                                    gparam = token.split('=')
                                    if len(gparam) == 2:
                                        if gparam[0] == 'std':
                                            std_dev = float(gparam[1])
                                replacement = ' + {}*EXP(AGAUSS(0,{!s},1))'.format(pr_switch_param, std_dev)
                                process_params.append((process_param, replacement))


            infile.close()

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
    filename = os.path.split(infile_name)[1]
    fileroot = os.path.splitext(filename)[0]
    outfile_name = os.path.join(filepath, fileroot + '_temp')

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

