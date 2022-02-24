#!/usr/bin/env python3
#
#--------------------------------------------------------------------
# Workaround for the problem that xyce does not like having "vt"
# as a subcircuit parameter name, because it is a xyce reserved
# name.  Change the parameter name in the one file that uses it.
# This script is not robust, and depends on the fact that the
# one file that declares "vt" does not have any corner model files,
# and the characters "vt" do not appear in any other context.
#--------------------------------------------------------------------

import os
import re
import sys
import tempfile

if len(sys.argv) <= 1:
    print('Usage: xyce_hack.py <path_to_file>')
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

        if 'vt' in line:
            newline = re.sub('vt', 'local_vt', line)
            replaced_something = True
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

