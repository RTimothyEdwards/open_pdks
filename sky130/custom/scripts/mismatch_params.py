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

options = []
arguments = []
for item in sys.argv[1:]:
    if item.find('-', 0) == 0:
        options.append(item[1:])
    else:
        arguments.append(item)

variant = 'sky130A'
walkpath = variant + '/libs.tech/ngspice'

if len(options) > 0:
    for option in options:
        if option.startswith('variant'):
            variant = option.split('=')[1]
    walkpath = variant + '/libs.ref/sky130_fd_pr/spice'
elif len(arguments) > 0:
    walkpath = arguments[0]

mismatch_params = []

mmrex = re.compile(r'^\*[ \t]*mismatch[ \t]*\{')
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
                        # Make sure all "A = B" syntax closes up around the equal sign.
                        newline = re.sub(r'[ \t]*=[ \t]*', '=', line)
                        tokens = newline.split()
                        if 'vary' in tokens:
                            if ('dist=gauss' in tokens) or ('gauss' in tokens):
                                gtype = 'A'
                                std_dev = 1
                                mismatch_param = tokens[2]
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
                                repltext = '{}*' + gtype + 'GAUSS(0,{!s},1)'
                                replacement = repltext.format(mm_switch_param, std_dev)
                                mismatch_params.append((mismatch_param, replacement))
                            elif ('dist=lnorm' in tokens) or ('lnorm' in tokens):
                                mismatch_param = tokens[2]
                                std_dev = 1
                                for token in tokens[3:]:
                                    gparam = token.split('=')
                                    if len(gparam) == 2:
                                        if gparam[0] == 'std':
                                            std_dev = float(gparam[1])
                                replacement = '{}*EXP(AGAUSS(0,{!s},1))'.format(mm_switch_param, std_dev)
                                mismatch_params.append((mismatch_param, replacement))


            infile.close()

print('') 
print('Mismatch parameters found:')
for (mismatch_param, replacement) in mismatch_params:
     print(mismatch_param + ' : ' + replacement)
print('') 

#--------------------------------------------------------------------
# Create regexp for the alternative PSPICE "dev/gauss" syntax used in
# a number of places in the models.
#--------------------------------------------------------------------

gaussrex = re.compile(r'\'[ \t]+dev\/gauss=\'', re.IGNORECASE)

# Same as above, for parameters that are not already expressions.

gauss2rex = re.compile(r'=[ \t]*([^ \t]+)[ \t]+dev\/gauss=\'', re.IGNORECASE)

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

    state = 'before_mismatch'
    line_number = 0
    replaced_something = False

    for line in infile:
        line_number += 1
        newline = line

        gmatch = gaussrex.search(newline)
        if gmatch:
            newline = gaussrex.sub('+' + mm_switch_param + '*AGAUSS(0,1.0,1)*', newline)
            replaced_something = True
            print("  Line {}: Found PSPICE dev/gauss and replaced.".format(line_number))

        gmatch = gauss2rex.search(newline)
        if gmatch:
            newline = gauss2rex.sub(r"='\g<1>+" + mm_switch_param + '*AGAUSS(0,1.0,1)*', newline)
            replaced_something = True
            print("  Line {}: Found PSPICE dev/gauss and replaced.".format(line_number))

        if state == 'before_mismatch':
            outfile.write(newline)
            mmatch = mmrex.match(newline)
            if mmatch:
                state = 'in_mismatch'
        elif state == 'in_mismatch':
            outfile.write(newline)
            ematch = endrex.match(newline)
            if ematch:
                state = 'after_mismatch'
        elif state == 'after_mismatch':
            for (param, replacement) in mismatch_params:
                if param in newline:
                    newline = newline.replace(param, replacement)
                    replaced_something = True
                    print("  Line {}: Found mismatch parameter '{}' and replaced with '{}'.".format(line_number, param, replacement))
            outfile.write(newline)

    infile.close()
    outfile.close()
    if replaced_something:
        # print("Something was replaced in '{}', backed up original file"
        #	+ " and replaced with processed one.".format(infile_name))
        print("Something was replaced in '{}'.".format(infile_name))
        # os.rename(infile_name, infile_name + '.orig')
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

