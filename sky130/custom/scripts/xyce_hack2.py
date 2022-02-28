#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Workaround for the problem that xyce does not ignore ACM model
# parameters passed to bsim3 models, and throws an error.  These
# parameters have no known effect on simulation and therefore
# should be removed.
#--------------------------------------------------------------------

import os
import re
import sys
import tempfile

plist = ["ldif", "hdif", "rd", "rs", "rsc", "rdc", "nqsmod"]
regexps = []
for parm in plist:
    regexps.append(re.compile('^\+[ \t]*' + parm + '[ \t]*=[ \t]*0.0', re.IGNORECASE))

if len(sys.argv) <= 1:
    print('Usage: xyce_hack2.py <path_to_file>')
    sys.exit(1)

else:
    infile_name = sys.argv[1]

    filepath = os.path.split(infile_name)[0]
    filename = os.path.split(infile_name)[1]
    fileroot = os.path.splitext(filename)[0]

    infile = open(infile_name, 'r')
    handle, outfile_name = tempfile.mkstemp()
    outfile = os.fdopen(handle, 'w')

    line_number = 0
    replaced_something = False
    for line in infile:
        line_number += 1

        for rex in regexps:
            rmatch = rex.match(line)
            if rmatch:
                # If a match is found, comment out the line.
                replaced_something = True
                break

        if rmatch:
            newline = re.sub('^\+', '* +', line)
        else:
            newline = line

        outfile.write(newline)

    infile.close()
    outfile.close()
    if replaced_something:
        print("Something was replaced in '{}'".format(infile_name))
        os.rename(outfile_name, infile_name)
    else:
        print("Nothing was replaced in '{}'.".format(infile_name))
        os.remove(outfile_name)

