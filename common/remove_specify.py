#!/usr/bin/env python3
#
# Remove timing information from a verilog file, which is everything between
# the keywords "specify" and "endspecify".
#
# Filter a verilog file to remove any backslash continuation lines, which
# iverilog does not parse.  If targetroot is a directory, then find and
# process all files in the path of targetroot.  If any file to be processed
# is unmodified (has no backslash continuation lines), then ignore it.  If
# any file is a symbolic link and gets modified, then remove the symbolic
# link before overwriting with the modified file.
#

import stat
import sys
import os
import re

def makeuserwritable(filepath):
    if os.path.exists(filepath):
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IWUSR)

def remove_specify(vfile, outfile):
    modified = False
    with open(vfile, 'r') as ifile:
        vtext = ifile.read()

    if outfile == None:
        outfile = vfile

    # Remove backslash-followed-by-newline and absorb initial whitespace.  It
    # is unclear what initial whitespace means in this context, as the use-
    # case that has been seen seems to work under the assumption that leading
    # whitespace is ignored up to the amount used by the last indentation.

    vlines = re.sub(r'\\\\\n[ \t]*', '', vtext)

    specrex = re.compile(r'\n[ \t]*specify[ \t\n]+')
    endspecrex = re.compile(r'\n[ \t]*endspecify')
    smatch = specrex.search(vlines)
    while smatch:
        specstart = smatch.start()
        specpos = smatch.end()
        ematch = endspecrex.search(vlines[specpos:])
        specend = ematch.end()
        vtemp = vlines[0:specstart + 1] + vlines[specpos + specend + 1:]
        vlines = vtemp
        smatch = specrex.search(vlines)

    if vlines != vtext:
        # File contents have been modified, so if this file was a symbolic
        # link, then remove it.  Otherwise, overwrite the file with the
        # modified contents.
        if outfile == vfile:
            if os.path.islink(vfile):
                os.unlink(vfile)
        if os.path.exists(outfile):
            makeuserwritable(outfile)
        with open(outfile, 'w') as ofile:
            ofile.write(vlines)

    elif outfile != vfile:
        if os.path.exists(outfile):
            makeuserwritable(outfile)
        with open(outfile, 'w') as ofile:
            ofile.write(vlines)

# If called as main, run remove_specify

if __name__ == '__main__':

    # Divide up command line into options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # Need one argument:  path to verilog netlist
    # If two arguments, then 2nd argument is the output file.

    if len(arguments) == 2:
        netlist_path = arguments[0]
        output_path = arguments[1]
        remove_specify(netlist_path, output_path)
    elif len(arguments) != 1:
        print("Usage:  remove_spcify.py <file_path> [<output_path>]")
    elif len(arguments) == 1:
        netlist_path = arguments[0]
        remove_specify(netlist_path, None)

