#!/usr/bin/env python3
#
# cleanup_unref.py:  Look up all .mag files in the indicated path, and
# parse all files for "use" lines and make a list of all the cells being
# used.  Next, check all files to determine which ones are parameterized
# PDK cells (those that have "string gencell" in the properties section).
# Finally, remove all the files which represent parametersized PDK cells
# that are not used anywhere by any other layout file.
#
# The purpose of this script is to reduce the number of cells scattered
# about the filesystem that come from parameterized cells being modified
# in place.  Eventually, magic will be upgraded to have a way to indicate
# just the cell name and parameters in the .mag file so that all parameterized
# cells can be generated on-the-fly and do not need to be saved in .mag files.
# 
# Note that this routine assumes that all files are local to a single project
# directory and are not being used by layout in some other directory.  So use
# with caution.
#
# Usage, e.g.:
#
# cleanup_unref.py <path_to_layout>

import os
import re
import sys
import glob

def usage():
    print("cleanup_unref.py [-remove] <path_to_layout>")
    return 0

if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    testmode = True
    debugmode = False

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 1:
        print("Wrong number of arguments given to cleanup_unref.py.")
        usage()
        sys.exit(0)

    if '-remove' in optionlist or '-delete' in optionlist:
        testmode = False
    if '-debug' in optionlist:
        debugmode = True

    filepath = arguments[0]

    magpath = filepath + '/*.mag'
    sourcefiles = glob.glob(magpath)

    if len(sourcefiles) == 0:
        print("Warning:  No files were found in the path " + filepath + ".")

    usedfiles = []
    pdkfiles = []

    for file in sourcefiles:
        if debugmode:
            print("Checking file " + file)
        fileroot = os.path.split(file)[1]
        cellname = os.path.splitext(fileroot)[0]

        proprex = re.compile('^string[ \t]+gencell[ \t]+([^ \t]+)')
        userex = re.compile('^use[ \t]+([^ \t]+)')

        with open(file, 'r') as ifile:
            magtext = ifile.read().splitlines() 
            for line in magtext:
                pmatch = proprex.match(line)
                if pmatch:
                    pdkfiles.append(cellname)
                umatch = userex.match(line)
                if umatch:
                    cellname = umatch.group(1)
                    if cellname not in usedfiles:
                        usedfiles.append(cellname)

    unusedfiles = list(item for item in pdkfiles if item not in usedfiles)

    if debugmode:
        print('')
        print('Parameterized cells found:')
        for cellname in sorted(pdkfiles):
            print(cellname)

        print('')
        print('Used cells found:')
        for cellname in sorted(usedfiles):
            print(cellname)
    
    if testmode:
        # Just report on files that are unused
        print('')
        print('Parameterized cells not used by any layout:')
        for cellname in sorted(unusedfiles):
            print(cellname)
    else:
        # Remove files that are unused
        for cellname in sorted(unusedfiles):
            file = filepath + '/' + cellname + '.mag'
            os.remove(file)
            print('Removed unused parameterized cell ' + cellname)

    print('')
    print('Done!')
