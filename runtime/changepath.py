#!/usr/bin/env python3
#
# changepath.py:  Look up all .mag files in maglef paths from the root
# PDK directory given as the first argument, and replace them with the
# path that is given as the second argument.
#
# The purpose of this script is to prepare a technology for relocation.
# This script may be expanded to take care of all relocation issues.
# For now, only the property "GDS_FILE" in each .mag file is modified.
#
# Usage, e.g.:
#
# changepath.py /home/tim/pdk/sky130A/libs.ref/sky130_fd_sc_hd/mag /usr/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/mag
#
# NOTE:  This file is deprecated as moving GDS_FILE properties from
# library to library is taken care of by the open_pdks installer, and
# portability is largely taken care of through use of the $PDK_PATH
# variable in the prefix of the GDS_FILE name.

import os
import re
import sys
import glob

def usage():
    print("changepath.py <orig_path_to_dir> <target_path_to_dir>")
    return 0

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 2:
        print("Wrong number of arguments given to changepath.py.")
        usage()
        sys.exit(0)

    source = arguments[0]
    target = arguments[1]

    gdssource = source.replace('/mag/', '/gds/')
    gdssource = gdssource.replace('/maglef/', '/gds/')
    gdstarget = target.replace('/mag/', '/gds/')
    gdstarget = gdstarget.replace('/maglef/', '/gds/')

    magpath = source + '/*.mag'
    sourcefiles = glob.glob(magpath)

    if len(sourcefiles) == 0:
        print("Warning:  No files were found in the path " + magpath + ".")

    for file in sourcefiles:
        # print("Converting file " + file)
        with open(file, 'r') as ifile:
            magtext = ifile.read().splitlines() 

        proprex = re.compile('string[ \t]+GDS_FILE[ \t]+([^ \t]+)')
        with open(file, 'w') as ofile:
            for line in magtext:
                pmatch = proprex.match(line)
                if pmatch:
                    filepath = pmatch.group(1)
                    if filepath.startswith(gdssource):
                        print('string GDS_FILE ' + filepath.replace(gdssource, gdstarget), file=ofile)
                    else:
                        print(line, file=ofile)
                else:
                    print(line, file=ofile)

