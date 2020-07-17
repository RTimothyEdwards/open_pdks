#!/usr/bin/env python3
#
# foundry_install.py
#
# This file generates the local directory structure and populates the
# directories with foundry vendor data.  The local directory (target)
# should be a staging area, not a place where files are kept permanently.
#
# Options:
#    -ef_format		Use efabless naming (libs.ref/techLEF),
#			otherwise use generic naming (libs.tech/lef)
#    -clean		Clear out and remove target directory before starting
#    -source <path>	Path to source data top level directory
#    -target <path>	Path to target (staging) top level directory
#
# All other options represent paths to vendor files.  They may all be
# wildcarded with "*", or with specific escapes like "%l" for library
# name or "%v" for version number (see below for a complete list of escape
# sequences).
#
# Note only one of "-spice" or "-cdl" need be specified.  Since the
# open source tools use ngspice, CDL files are converted to ngspice
# syntax when needed.
#
#	-techlef <path>	Path to technology LEF file
#	-doc <path>	Path to technology documentation
#	-lef <path>	Path to LEF file
#	-spice <path>	Path to SPICE netlists
#	-cdl <path>	Path to CDL netlists
#	-models <path>	Path to SPICE (primitive device) models
#	-liberty <path>	Path to Liberty timing files
#	-gds <path>	Path to GDS data
#	-verilog <path>	Path to verilog models
#
#	-library <type> <name> [<target>]	See below
#
# For the "-library" option, any number of libraries may be supported, and
# one "-library" option should be provided for each supported library.
# <type> is one of:  "digital", "primitive", or "general".  Analog and I/O
# libraries fall under the category "general", as they are all treated the
# same way.  <name> is the vendor name of the library.  [<target>] is the
# (optional) local name of the library.  If omitted, then the vendor name
# is used for the target (there is no particular reason to specify a
# different local name for a library).
#
# In special cases using options (see below), path may be "-", indicating
# that there are no source files, but only to run compilations or conversions
# on the files in the target directory.
#
# All options "-lef", "-spice", etc., can take the additional arguments
# 	up  <number>
#
# to indicate that the source hierarchy should be copied from <number>
# levels above the files.  For example, if liberty files are kept in
# multiple directories according to voltage level, then
#
# 	-liberty x/y/z/PVT_*/*.lib
#
# would install all .lib files directly into libs.ref/<libname>/liberty/*.lib
# (if "-ef_format" option specified, then: libs.ref/<libname>/liberty/*.lib)
# while
#
# 	-liberty x/y/z/PVT_*/*.lib up 1
#
# would install all .lib files into libs.ref/liberty/<libname>/PVT_*/*.lib
# (if "-ef_format" option specified, then: libs.ref/<libname>/liberty/PVT_*/*.lib)
#
# Please note that the INSTALL variable in the Makefile starts with "set -f"
# to suppress the OS from doing wildcard substitution;  otherwise the
# wildcards in the install options will get expanded by the OS before
# being passed to the install script.
#
# Other library-specific arguments are:
#
#	nospec	:  Remove timing specification before installing
#		    (used with verilog files;  needs to be extended to
#		    liberty files)
#	compile :  Create a single library from all components.  Used
#		    when a foundry library has inconveniently split
#		    an IP library (LEF, CDL, verilog, etc.) into
#		    individual files.
#	stub :	   Remove contents of subcircuits from CDL or SPICE
#		    netlist files.
#
#	priv :	   Mark the contents being installed as privleged, and
#		    put them in a separate root directory libs.priv
#		    where they can be given additional read/write
#		    restrictions.
#
#	exclude :  Followed by "=" and a comma-separated list of names.
#		    exclude these files/modules/subcircuits.  Names may
#		    also be wildcarded in "glob" format.
#
#	rename :   Followed by "=" and an alternative name.  For any
#		    file that is a single entry, change the name of
#		    the file in the target directory to this (To-do:
#		    take regexps for multiple files).  When used with
#		    "compile" or "compile-only", this refers to the
# 		    name of the target compiled file.
#
#	noconvert : Install only; do not attempt to convert to other
#		    formats (applies only to GDS, CDL, and LEF).
#
# NOTE:  This script can be called once for all libraries if all file
# types (gds, cdl, lef, etc.) happen to all work with the same wildcards.
# However, it is more likely that it will be called several times for the
# same PDK, once to install I/O cells, once to install digital, and so
# forth, as made possible by the wild-carding.

import re
import os
import sys
import glob
import stat
import shutil
import fnmatch
import subprocess

def usage():
    print("foundry_install.py [options...]")
    print("   -copy             Copy files from source to target (default)")
    print("   -ef_format        Use efabless naming conventions for local directories")
    print("")
    print("   -source <path>    Path to top of source directory tree")
    print("   -target <path>    Path to top of target directory tree")
    print("")
    print("   -techlef <path>   Path to technology LEF file")
    print("   -doc <path>       Path to technology documentation")
    print("   -lef <path>       Path to LEF file")
    print("   -spice <path>     Path to SPICE netlists")
    print("   -cdl <path>       Path to CDL netlists")
    print("   -models <path>    Path to SPICE (primitive device) models")
    print("   -lib <path>       Path to Liberty timing files")
    print("   -liberty <path>       Path to Liberty timing files")
    print("   -gds <path>       Path to GDS data")
    print("   -verilog <path>   Path to verilog models")
    print("   -library <type> <name> [<target>]	 See below")
    print("")
    print(" All <path> names may be wild-carded with '*' ('glob'-style wild-cards)")
    print("")
    print(" All options with <path> other than source and target may take the additional")
    print(" arguments 'up <number>', where <number> indicates the number of levels of")
    print(" hierarchy of the source path to include when copying to the target.")
    print("")
    print(" Library <type> may be one of:")
    print("    digital		Digital standard cell library")
    print("    primitive	Primitive device library")
    print("    general		All other library types (I/O, analog, etc.)")
    print("")
    print(" If <target> is unspecified then <name> is used for the target.")

# Return a list of files after glob-style substituting into pathname.  This
# mostly relies on glob.glob(), but uses the additional substitutions with
# escape strings:
#
#   %v :  Match a version number in the form "major[.minor[.rev]]"
#   %l :  substitute the library name
#   %% :  substitute the percent character verbatim

from distutils.version import LooseVersion

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def makeuserwritable(filepath):
    if os.path.exists(filepath):
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IWUSR)

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def substitute(pathname, library):
    if library:
        # Do %l substitution
        newpathname = re.sub('%l', library, pathname)
    else:
        newpathname = pathname

    if '%v' in newpathname:
        vglob = re.sub('%v.*', '*', newpathname)
        vlibs = glob.glob(vglob)
        try:
            vstr = vlibs[0][len(vglob)-1:]
        except IndexError:
            pass
        else:
            for vlib in vlibs[1:]:
                vtest = vlib[len(vglob)-1:]
                if LooseVersion(vtest) > LooseVersion(vstr):
                    vstr = vtest
            newpathname = re.sub('%v', vstr, newpathname)

    if '%%' in newpathname:
        newpathname = re.sub('%%', '%', newpathname)

    return newpathname

#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

def get_gds_properties(magfile):
    proprex = re.compile('^[ \t]*string[ \t]+(GDS_[^ \t]+)[ \t]+([^ \t]+)$')
    proplines = []
    if os.path.isfile(magfile):
        with open(magfile, 'r') as ifile:
            magtext = ifile.read().splitlines()
            for line in magtext:
                lmatch = proprex.match(line)
                if lmatch:
                    propline = lmatch.group(1) + ' ' + lmatch.group(2)
                    proplines.append(propline)
    return proplines

#----------------------------------------------------------------------------
# Read subcircuit ports from a CDL file, given a subcircuit name that should
# appear in the file as a subcircuit entry, and return a dictionary of ports
# and their indexes in the subcircuit line.
#----------------------------------------------------------------------------

def get_subckt_ports(cdlfile, subname):
    portdict = {}
    pidx = 1
    portrex = re.compile('^\.subckt[ \t]+([^ \t]+)[ \t]+(.*)$', flags=re.IGNORECASE)
    with open(cdlfile, 'r') as ifile:
        cdltext = ifile.read()
        cdllines = cdltext.replace('\n+', ' ').splitlines()
        for line in cdllines:
            lmatch = portrex.match(line)
            if lmatch:
                if lmatch.group(1).lower() == subname.lower():
                    ports = lmatch.group(2).split()
                    for port in ports:
                        portdict[port.lower()] = pidx
                        pidx += 1
                    break
    return portdict

#----------------------------------------------------------------------------
# Filter a verilog file to remove any backslash continuation lines, which
# iverilog does not parse.  If targetroot is a directory, then find and
# process all files in the path of targetroot.  If any file to be processed
# is unmodified (has no backslash continuation lines), then ignore it.  If
# any file is a symbolic link and gets modified, then remove the symbolic
# link before overwriting with the modified file.
#----------------------------------------------------------------------------

def vfilefilter(vfile):
    modified = False
    with open(vfile, 'r') as ifile:
        vtext = ifile.read()

    # Remove backslash-followed-by-newline and absorb initial whitespace.  It
    # is unclear what initial whitespace means in this context, as the use-
    # case that has been seen seems to work under the assumption that leading
    # whitespace is ignored up to the amount used by the last indentation.

    vlines = re.sub('\\\\\n[ \t]*', '', vtext)

    if vlines != vtext:
        # File contents have been modified, so if this file was a symbolic
        # link, then remove it.  Otherwise, overwrite the file with the
        # modified contents.
        if os.path.islink(vfile):
            os.unlink(vfile)
        with open(vfile, 'w') as ofile:
            ofile.write(vlines)

#----------------------------------------------------------------------------
# Run a filter on verilog files that cleans up known syntax issues.
# This is embedded in the foundry_install script and is not a custom
# filter largely because the issue is in the tool, not the PDK.
#----------------------------------------------------------------------------

def vfilter(targetroot):
    if os.path.isfile(targetroot):
        vfilefilter(targetroot)
    else:
        vlist = glob.glob(targetroot + '/*')
        for vfile in vlist:
            if os.path.isfile(vfile):
                vfilefilter(vfile)

#----------------------------------------------------------------------------
# For issues that are PDK-specific, a script can be written and put in
# the PDK's custom/scripts/ directory, and passed to the foundry_install
# script using the "filter" option.
#----------------------------------------------------------------------------

def tfilter(targetroot, filterscript, outfile=[]):
    filterroot = os.path.split(filterscript)[1]
    if os.path.isfile(targetroot):
        print('   Filtering file ' + targetroot + ' with ' + filterroot)
        sys.stdout.flush()
        if not outfile:
            outfile = targetroot
        else:
            # Make sure this file is writable (as the original may not be)
            makeuserwritable(outfile)

        fproc = subprocess.run([filterscript, targetroot, outfile],
			stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, universal_newlines = True)
        if fproc.stdout:
            for line in fproc.stdout.splitlines():
                print(line)
        if fproc.stderr:
            print('Error message output from filter script:')
            for line in fproc.stderr.splitlines():
                print(line)

    else:
        tlist = glob.glob(targetroot + '/*')
        for tfile in tlist:
            if os.path.isfile(tfile):
                print('   Filtering file ' + tfile + ' with ' + filterroot)
                sys.stdout.flush()
                fproc = subprocess.run([filterscript, tfile, tfile],
			stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, universal_newlines = True)
                if fproc.stdout:
                    for line in fproc.stdout.splitlines():
                        print(line)
                if fproc.stderr:
                    print('Error message output from filter script:')
                    for line in fproc.stderr.splitlines():
                        print(line)

#----------------------------------------------------------------------------
# Given a destination directory holding individual verilog files of a number
# of modules, create a single verilog library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-verilog" install.
#----------------------------------------------------------------------------

def create_verilog_library(destlibdir, destlib, do_compile_only, do_stub, excludelist):

    alllibname = destlibdir + '/' + destlib + '.v'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    print('Diagnostic:  Creating consolidated verilog library ' + destlib + '.v')
    vlist = glob.glob(destlibdir + '/*.v')
    if alllibname in vlist:
        vlist.remove(alllibname)

    # Create exclude list with glob-style matching using fnmatch
    if len(vlist) > 0:
        vlistnames = list(os.path.split(item)[1] for item in vlist)
        notvlist = []
        for exclude in excludelist:
            notvlist.extend(fnmatch.filter(vlistnames, exclude))

        # Apply exclude list
        if len(notvlist) > 0:
            for file in vlist[:]:
                if os.path.split(file)[1] in notvlist:
                    vlist.remove(file)

    if len(vlist) > 1:
        print('New file is:  ' + alllibname)
        with open(alllibname, 'w') as ofile:
            allmodules = []
            for vfile in vlist:
                with open(vfile, 'r') as ifile:
                    # print('Adding ' + vfile + ' to library.')
                    vtext = ifile.read()
                    modules = re.findall(r'[ \t\n]module[ \t]+([^ \t\n\(]+)', vtext)
                    mseen = list(item for item in modules if item in allmodules)
                    allmodules.extend(list(item for item in modules if item not in allmodules))
                    vfilter = remove_redundant_modules(vtext, allmodules, mseen)
                    # NOTE:  The following workaround resolves an issue with iverilog,
                    # which does not properly parse specify timing paths that are not in
                    # parentheses.  Easy to work around
                    vlines = re.sub(r'\)[ \t]*=[ \t]*([01]:[01]:[01])[ \t]*;', r') = ( \1 ) ;', vfilter)
                    print(vlines, file=ofile)
                print('\n//--------EOF---------\n', file=ofile)

        if do_compile_only == True:
            print('Compile-only:  Removing individual verilog files')
            for vfile in vlist:
                if os.path.isfile(vfile):
                    os.remove(vfile)
                elif os.path.islink(vfile):
                    os.unlink(vfile)
    else:
        print('Only one file (' + str(vlist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Remove redundant module entries from a verilog file.  "m2list" is a list of
# module names gleaned from all previously read files using re.findall().
# "mlist" is a list of all module names including those in "ntext".
# The reason for doing this is that some verilog files may includes modules used
# by all the files, and if included more than once, then iverilog complains.
#----------------------------------------------------------------------------

def remove_redundant_modules(ntext, mlist, m2list):
    updated = ntext
    for module in mlist:
        # Determine the number of times the module appears in the text
        if module in m2list:
            # This module seen before outside of ntext, so remove all occurrances in ntext
            new = re.sub(r'[ \t\n]+module[ \t]+' + module + '[ \t\n\(]+.*[ \t\n]endmodule', '\n', updated, flags=re.DOTALL)
            updated = new

        else:
            n = len(re.findall(r'[ \t\n]module[ \t]+' + module + '[ \t\n\(]+.*[ \t\n]endmodule', updated, flags=re.DOTALL))
            # This module defined more than once inside ntext, so remove all but one
            # Optimization:  Just keep original text if n < 2
            if n < 2:
                continue

            # Remove all but one
            updated = re.sub(r'[ \t\n]+module[ \t]+' + module + '[ \t\n]+.*[ \t\n]endmodule', '\n', n - 1, updated, flags=re.IGNORECASE | re.DOTALL)
    return updated

#----------------------------------------------------------------------------
# Given a destination directory holding individual LEF files of a number
# of cells, create a single LEF library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-lef" install.
#----------------------------------------------------------------------------

def create_lef_library(destlibdir, destlib, do_compile_only, excludelist):

    alllibname = destlibdir + '/' + destlib + '.lef'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    print('Diagnostic:  Creating consolidated LEF library ' + destlib + '.lef')
    llist = glob.glob(destlibdir + '/*.lef')
    if alllibname in llist:
        llist.remove(alllibname)

    # Create exclude list with glob-style matching using fnmatch
    if len(llist) > 0:
        llistnames = list(os.path.split(item)[1] for item in llist)
        notllist = []
        for exclude in excludelist:
            notllist.extend(fnmatch.filter(llistnames, exclude))

        # Apply exclude list
        if len(notllist) > 0:
            for file in llist[:]:
                if os.path.split(file)[1] in notllist:
                    llist.remove(file)

    if len(llist) > 1:
        print('New file is:  ' + alllibname)
        with open(alllibname, 'w') as ofile:
            headerdone = False
            for lfile in llist:
                with open(lfile, 'r') as ifile:
                    # print('Adding ' + lfile + ' to library.')
                    ltext = ifile.read()
                    llines = ltext.splitlines()
                    headerseen = False
                    for lline in llines:
                        if headerdone:
                            if not headerseen:
                                if not lline.startswith('MACRO'):
                                    continue
                                else:
                                    headerseen = True
                        print(lline, file=ofile)
                    headerdone = True
                print('#--------EOF---------\n', file=ofile)

        if do_compile_only == True:
            print('Compile-only:  Removing individual LEF files')
            for lfile in llist:
                if os.path.isfile(lfile):
                    os.remove(lfile)
            if newname:
                if os.path.isfile(newname):
                    os.remove(newname)
    else:
        print('Only one file (' + str(llist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Given a destination directory holding individual liberty files of a number
# of cells, create a single liberty library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-lib" install.
#----------------------------------------------------------------------------

# Warning:  This script is unfinished.  Needs to parse the library header
# in each cell and generate a new library header combining the contents of
# all cell headers.  Also:  The library name in the header needs to be
# changed to the full library name.  Also:  There is no mechanism for
# collecting all files belonging to a single process corner/temperature/
# voltage.

def create_lib_library(destlibdir, destlib, do_compile_only, excludelist):

    alllibname = destlibdir + '/' + destlib + '.lib'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    print('Diagnostic:  Creating consolidated liberty library ' + destlib + '.lib')

    # Create exclude list with glob-style matching using fnmatch
    if len(llist) > 0:
        llistnames = list(os.path.split(item)[1] for item in llist)
        notllist = []
        for exclude in excludelist:
            notllist.extend(fnmatch.filter(llistnames, exclude))

        # Apply exclude list
        if len(notllist) > 0:
            for file in llist[:]:
                if os.path.split(file)[1] in notllist:
                    llist.remove(file)

    if len(llist) > 1:
        print('New file is:  ' + alllibname)
        with open(alllibname, 'w') as ofile:
            headerdone = False
            for lfile in llist:
                with open(lfile, 'r') as ifile:
                    # print('Adding ' + lfile + ' to library.')
                    ltext = ifile.read()
                    llines = ltext.splitlines()
                    headerseen = False
                    for lline in llines:
                        if headerdone:
                            if not headerseen:
                                if not lline.split()[0] == 'cell':
                                    continue
                                else:
                                    headerseen = True
                        print(lline, file=ofile)
                    headerdone = True
                print('/*--------EOF---------*/\n', file=ofile)

        if do_compile_only == True:
            print('Compile-only:  Removing individual LEF files')
            for lfile in llist:
                if os.path.isfile(lfile):
                    os.remove(lfile)
            if newname:
                if os.path.isfile(newname):
                    os.remove(newname)
    else:
        print('Only one file (' + str(llist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Given a destination directory holding individual GDS files of a number
# of cells, create a single GDL library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-gds" install.
#----------------------------------------------------------------------------

def create_gds_library(destlibdir, destlib, startup_script, do_compile_only, excludelist):

    alllibname = destlibdir + '/' + destlib + '.gds'
    if os.path.isfile(alllibname):
        os.remove(alllibname)

    print('Diagnostic:  Creating consolidated GDS library ' + destlib + '.gds')
    glist = glob.glob(destlibdir + '/*.gds')
    glist.extend(glob.glob(destlibdir + '/*.gdsii'))
    glist.extend(glob.glob(destlibdir + '/*.gds2'))
    if alllibname in glist:
        glist.remove(alllibname)

    # Create exclude list with glob-style matching using fnmatch
    if len(glist) > 0:
        glistnames = list(os.path.split(item)[1] for item in glist)
        notglist = []
        for exclude in excludelist:
            notglist.extend(fnmatch.filter(glistnames, exclude))

        # Apply exclude list
        if len(notglist) > 0:
            for file in glist[:]:
                if os.path.split(file)[1] in notglist:
                    glist.remove(file)

    if len(glist) > 1:
        print('New file is:  ' + alllibname)

        if os.path.isfile(startup_script):
            # If the symbolic link exists, remove it.
            if os.path.isfile(destlibdir + '/.magicrc'):
                os.remove(destlibdir + '/.magicrc')
            os.symlink(startup_script, destlibdir + '/.magicrc')

        # A GDS library is binary and requires handling in Magic
        print('Creating magic generation script to generate GDS library.') 
        with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
            print('#!/usr/bin/env wish', file=ofile)
            print('#--------------------------------------------', file=ofile)
            print('# Script to generate .gds library from files   ', file=ofile)
            print('#--------------------------------------------', file=ofile)
            print('drc off', file=ofile)
            print('gds readonly true', file=ofile)
            print('gds flatten true', file=ofile)
            print('gds rescale false', file=ofile)
            print('tech unlock *', file=ofile)

            for gdsfile in glist:
                print('gds read ' + gdsfile, file=ofile)

            print('puts stdout "Creating cell ' + destlib + '"', file=ofile)
            print('load ' + destlib, file=ofile)
            print('puts stdout "Adding cells to library"', file=ofile)
            print('box values 0 0 0 0', file=ofile)
            for gdsfile in glist:
                gdsroot = os.path.split(gdsfile)[1]
                gdsname = os.path.splitext(gdsroot)[0]
                print('getcell ' + gdsname, file=ofile)
                # Could properly make space for the cell here. . . 
                print('box move e 200', file=ofile)
                                
            print('puts stdout "Writing GDS library ' + destlib + '"', file=ofile)
            print('gds library', file=ofile)
            print('gds write ' + destlib, file=ofile)
            print('puts stdout "Done."', file=ofile)
            print('quit -noprompt', file=ofile)

        # Run magic to read in the individual GDS files and
        # write out the consolidated GDS library

        print('Running magic to create GDS library.')
        sys.stdout.flush()

        mproc = subprocess.run(['magic', '-dnull', '-noconsole',
			destlibdir + '/generate_magic.tcl'],
			stdin = subprocess.DEVNULL,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, cwd = destlibdir,
			universal_newlines = True)

        if mproc.stdout:
            for line in mproc.stdout.splitlines():
                print(line)
        if mproc.stderr:
            print('Error message output from magic:')
            for line in mproc.stderr.splitlines():
                print(line)
        if mproc.returncode != 0:
            print('ERROR:  Magic exited with status ' + str(mproc.returncode))
        if do_compile_only == True:
            print('Compile-only:  Removing individual GDS files')
            for gfile in glist:
                if os.path.isfile(gfile):
                    os.remove(gfile)
            if newname:
                if os.path.isfile(newname):
                    os.remove(newname)
    else:
        print('Only one file (' + str(glist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Given a destination directory holding individual SPICE netlists of a number
# of cells, create a single SPICE library file named <alllibname> and place
# it in the same directory.  This is done for the option "compile" if specified
# for the "-spice" install.
#----------------------------------------------------------------------------

def create_spice_library(destlibdir, destlib, spiext, do_compile_only, do_stub, excludelist):

    fformat = 'CDL' if spiext == '.cdl' else 'SPICE'

    allstubname = destlibdir + '/stub' + spiext
    alllibname = destlibdir + '/' + destlib + spiext
    if do_stub:
        outputname = allstubname
    else:
        outputname = alllibname

    print('Diagnostic:  Creating consolidated ' + fformat + ' library ' + outputname)

    if os.path.isfile(outputname):
        os.remove(outputname)

    if fformat == 'CDL':
        slist = glob.glob(destlibdir + '/*.cdl')
    else:
        # Sadly, there is no consensus on what a SPICE file extension should be.
        slist = glob.glob(destlibdir + '/*.spc')
        slist.extend(glob.glob(destlibdir + '/*.spice'))
        slist.extend(glob.glob(destlibdir + '/*.spi'))
        slist.extend(glob.glob(destlibdir + '/*.ckt'))

    if alllibname in slist:
        slist.remove(alllibname)

    if allstubname in slist:
        slist.remove(allstubname)

    # Create exclude list with glob-style matching using fnmatch
    if len(slist) > 0:
        slistnames = list(os.path.split(item)[1] for item in slist)
        notslist = []
        for exclude in excludelist:
            notslist.extend(fnmatch.filter(slistnames, exclude))

        # Apply exclude list
        if len(notslist) > 0:
            for file in slist[:]:
                if os.path.split(file)[1] in notslist:
                    slist.remove(file)

    if len(slist) > 1:
        with open(outputname, 'w') as ofile:
            allsubckts = []
            for sfile in slist:
                with open(sfile, 'r') as ifile:
                    # print('Adding ' + sfile + ' to library.')
                    stext = ifile.read()
                    subckts = re.findall(r'\.subckt[ \t]+([^ \t\n]+)', stext, flags=re.IGNORECASE)
                    sseen = list(item for item in subckts if item in allsubckts)
                    allsubckts.extend(list(item for item in subckts if item not in allsubckts))
                    sfilter = remove_redundant_subckts(stext, allsubckts, sseen)
                    print(sfilter, file=ofile)
                print('\n******* EOF\n', file=ofile)

        if do_compile_only == True:
            print('Compile-only:  Removing individual SPICE files')
            for sfile in slist:
                if os.path.isfile(sfile):
                    os.remove(sfile)
                elif os.path.islink(sfile):
                    os.unlink(sfile)
    else:
        print('Only one file (' + str(slist) + ');  ignoring "compile" option.')

#----------------------------------------------------------------------------
# Remove redundant subcircuit entries from a SPICE or CDL netlist file.  "sseen"
# is a list of subcircuit names gleaned from all previously read files using
# re.findall(). "slist" is a list of subcircuits including those in "ntext".
# If a subcircuit is defined outside of "ntext", then remove all occurrences in
# "ntext".  Otherwise, if a subcircuit is defined more than once in "ntext",
# remove all but one copy.  The reason for doing this is that some netlists will
# include primitive device definitions used by all the standard cell subcircuits.
#
# It may be necessary to remove redundant .include statements and redundant .model
# and/or .option statements as well.
#----------------------------------------------------------------------------

def remove_redundant_subckts(ntext, slist, sseen):
    updated = ntext
    for subckt in slist:
        if subckt in sseen:
            # Remove all occurrences of subckt
            updated = re.sub(r'\n\.subckt[ \t]+' + subckt + '[ \t\n]+.*\n\.ends[ \t\n]+', '\n', updated, flags=re.IGNORECASE | re.DOTALL)

        else:
            # Determine the number of times the subcircuit appears in the text
            n = len(re.findall(r'\n\.subckt[ \t]+' + subckt + '[ \t\n]+.*\n\.ends[ \t\n]+', updated, flags=re.IGNORECASE | re.DOTALL))
            # Optimization:  Just keep original text if n < 2
            if n < 2:
                continue

            # Remove all but one
            updated = re.sub(r'\n\.subckt[ \t]+' + subckt + '[ \t\n]+.*\n\.ends[ \t\n]+', '\n', n - 1, updated, flags=re.IGNORECASE | re.DOTALL)
    return updated

#----------------------------------------------------------------------------
# This is the main entry point for the foundry install script.
#----------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("No options given to foundry_install.py.")
        usage()
        sys.exit(0)
    
    optionlist = []
    newopt = []

    sourcedir = None
    targetdir = None

    ef_format = False
    do_clean = False

    have_lef = False
    have_techlef = False
    have_lefanno = False
    have_gds = False
    have_spice = False
    have_cdl = False
    have_verilog = False
    have_lib = False

    # Break arguments into groups where the first word begins with "-".
    # All following words not beginning with "-" are appended to the
    # same list (optionlist).  Then each optionlist is processed.
    # Note that the first entry in optionlist has the '-' removed.

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            if newopt != []:
                optionlist.append(newopt)
                newopt = []
            newopt.append(option[1:])
        else:
            newopt.append(option)

    if newopt != []:
        optionlist.append(newopt)

    # Pull library names from optionlist
    libraries = []
    for option in optionlist[:]:
        if option[0] == 'library':
            optionlist.remove(option)
            libraries.append(option[1:]) 

    # Check for option "ef_format" or "std_format" or "clean"
    for option in optionlist[:]:
        if option[0] == 'ef_naming' or option[0] == 'ef_names' or option[0] == 'ef_format':
            optionlist.remove(option)
            ef_format = True
        elif option[0] == 'std_naming' or option[0] == 'std_names' or option[0] == 'std_format':
            optionlist.remove(option)
            ef_format = False
        elif option[0] == 'clean':
            do_clean = True

    # Check for options "source" and "target"
    for option in optionlist[:]:
        if option[0] == 'source':
            optionlist.remove(option)
            sourcedir = option[1]
        elif option[0] == 'target':
            optionlist.remove(option)
            targetdir = option[1]

    if not targetdir:
        print("No target directory specified.  Exiting.")
        sys.exit(1)

    # Take the target PDK name from the target path last component
    pdkname = os.path.split(targetdir)[1]

    # If targetdir (the staging area) exists, make sure it's empty.

    if os.path.isdir(targetdir):
        # Error if targetdir exists but is not writeable
        if not os.access(targetdir, os.W_OK):
            print("Target installation directory " + targetdir + " is not writable.")
            sys.exit(1)

        # Clear out the staging directory if specified
        if do_clean:
            shutil.rmtree(targetdir)
    elif os.path.exists(targetdir):
        print("Target installation directory " + targetdir + " is not a directory.")
        sys.exit(1)

    # Error if no source or dest specified unless "-clean" was specified
    if not sourcedir:
        if do_clean:
            print("Done removing staging area.")
            sys.exit(0)
        else:
            print("No source directory specified.  Exiting.")
            sys.exit(1)

    # Create the target directory
    os.makedirs(targetdir, exist_ok=True)

    #----------------------------------------------------------------
    # Installation part 1:  Install files into the staging directory
    #----------------------------------------------------------------

    # Diagnostic
    print("Installing in target (staging) directory " + targetdir)

    # Create the top-level directories

    os.makedirs(targetdir + '/libs.tech', exist_ok=True)
    os.makedirs(targetdir + '/libs.ref', exist_ok=True)

    # Path to magic techfile depends on ef_format

    if ef_format == True:
        mag_current = '/libs.tech/magic/current/'
    else:
        mag_current = '/libs.tech/magic/'

    # Check for magic version and set flag if it does not exist or if
    # it has the wrong version.
    have_mag_8_2 = False
    try:
        mproc = subprocess.run(['magic', '--version'],
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		universal_newlines = True)
        if mproc.stdout:
            mag_version = mproc.stdout.splitlines()[0]
            mag_version_info = mag_version.split('.')
            try:
                if int(mag_version_info[0]) > 8:
                    have_mag_8_2 = True
                elif int(mag_version_info[0]) == 8:
                    if int(mag_version_info[1]) >= 2:
                        have_mag_8_2 = True
                        print('Magic version 8.2 available on the system.')
            except ValueError:
                print('Error: "magic --version" did not return valid version number.')
    except FileNotFoundError:
        print('Error: Failed to find executable for magic in standard search path.')

    if not have_mag_8_2:
        print('WARNING:  Magic version 8.2 cannot be executed from the standard executable search path.')
        print('Please install or correct the search path.')
        print('Magic database files will not be created, and other missing file formats may not be generated.')

    # Populate any targets that do not specify a library, or where the library is
    # specified as "primitive".  

    # Populate the techLEF and SPICE models, if specified.  Also, this section can add
    # to any directory in libs.tech/ as given by the option;  e.g., "-ngspice" will
    # install into libs.tech/ngspice/.

    if libraries == [] or 'primitive' in libraries[0]:

        for option in optionlist[:]:

            # Legacy behavior is to put libs.tech models and techLEF files in
            # the same grouping as files for the primdev library (which go in
            # libs.ref).  Current behavior is to put all libs.tech files in
            # a grouping with no library, with unrestricted ability to write
            # into any subdirectory of libs.tech/.  Therefore, need to restrict
            # legacy use to just 'techlef' and 'models'.

            if len(libraries) > 0 and 'primitive' in libraries[0]:
                if option[0] != 'techlef' and option[0] != 'techLEF' and option[0] != 'models':
                    continue
  
            # Normally technology LEF files are associated with IP libraries.
            # However, if no library is specified or the library is 'primitive'
            # (legacy behavior), then put in the techLEF directory with no subdirectory.

            filter_scripts = []
            if option[0] == 'techlef' or option[0] == 'techLEF':
                for item in option:
                    if item.split('=')[0] == 'filter':
                        filter_scripts.append(item.split('=')[1])
                        break

                if ef_format:
                    techlefdir = targetdir + '/libs.ref/' + 'techLEF'
                else:
                    techlefdir = targetdir + '/libs.tech/lef'

                os.makedirs(techlefdir, exist_ok=True)
                # All techlef files should be copied, so use "glob" on the wildcards
                techlist = glob.glob(substitute(sourcedir + '/' + option[1], None))

                for lefname in techlist:
                    leffile = os.path.split(lefname)[1]
                    targname = techlefdir + '/' + leffile

                    if os.path.isfile(lefname):
                        shutil.copy(lefname, targname)
                    else:
                        shutil.copytree(lefname, targname)

                    for filter_script in filter_scripts:
                        # Apply filter script to all files in the target directory
                        tfilter(targname, filter_script)

                optionlist.remove(option)

            # All remaining options will refer to specific tools (e.g., -ngspice, -magic)
            # although generic names (.e.g, -models) are acceptable if the tools know
            # where to find the files.  Currently, most tools have their own formats
            # and standards for setup, and so generally each install directory will be
            # unique to one EDA tool.

            else:
                filter_scripts = []
                for item in option:
                    if item.split('=')[0] == 'filter':
                        filter_scripts.append(item.split('=')[1])
                        break

                print('Diagnostic:  installing ' + option[0] + '.')
                tooldir = targetdir + '/libs.tech/' + option[0]
                os.makedirs(tooldir, exist_ok=True)

                # All files should be linked or copied, so use "glob" on
                # the wildcards.  Copy each file and recursively copy each
                # directory.
                toollist = glob.glob(substitute(sourcedir + '/' + option[1], None))

                for toolname in toollist:
                    toolfile = os.path.split(toolname)[1]
                    targname = tooldir + '/' + toolfile

                    if os.path.isdir(toolname):
                        # Remove any existing directory, and its contents
                        if os.path.isdir(targname):
                            shutil.rmtree(targname)
                        os.makedirs(targname)
    
                        # Recursively find and copy or link the whole directory
                        # tree from this point.

                        alltoollist = glob.glob(toolname + '/**', recursive=True)
                        commonpart = os.path.commonpath(alltoollist)
                        for subtoolname in alltoollist:
                            if os.path.isdir(subtoolname):
                                continue
                            # Get the path part that is not common between toollist and
                            # alltoollist.
                            subpart = os.path.relpath(subtoolname, commonpart)
                            subtargname = targname + '/' + subpart
                            os.makedirs(os.path.split(subtargname)[0], exist_ok=True)

                            if os.path.isfile(subtoolname):
                                shutil.copy(subtoolname, subtargname)
                            else:
                                shutil.copytree(subtoolname, subtargname)

                            for filter_script in filter_scripts:
                                # Apply filter script to all files in the target directory
                                tfilter(subtargname, filter_script)

                    else:
                        # Remove any existing file
                        if os.path.isfile(targname):
                            os.remove(targname)
                        elif os.path.isdir(targname):
                            shutil.rmtree(targname)

                        if os.path.isfile(toolname):
                            shutil.copy(toolname, targname)
                        else:
                            shutil.copytree(toolname, targname)

                        for filter_script in filter_scripts:
                            # Apply filter script to all files in the target directory
                            tfilter(targname, filter_script)

                optionlist.remove(option)

    # Do an initial pass through all of the options and determine what is being
    # installed, so that we know in advance which file formats are missing and
    # need to be generated.

    for option in optionlist[:]:
        if option[0] == 'lef':
            have_lef = True
        if option[0] == 'techlef' or option[0] == 'techLEF':
            have_techlef = True
        elif option[0] == 'gds':
            have_gds = True
        elif option[0] == 'spice' or option[0] == 'spi':
            have_spice = True
        elif option[0] == 'cdl':
            have_cdl = True
        elif option[0] == 'verilog':
            have_verilog = True
        elif option[0] == 'lib' or option[0] == 'liberty':
            have_lib = True

    # The remaining options in optionlist should all be types like 'lef' or 'liberty'
    # and there should be a corresponding library list specified by '-library'

    for option in optionlist[:]:

        # Ignore if no library list---should have been taken care of above.
        if libraries == []:
            break

        # Diagnostic
        print("Install option: " + str(option[0]))

        # For ef_format:  always make techlef -> techLEF and spice -> spi

        if ef_format:
            if option[0] == 'techlef':
                option[0] = 'techLEF'
            elif option[0] == 'spice':
                option[0] = 'spi'

            destdir = targetdir + '/libs.ref/' + option[0]
            os.makedirs(destdir, exist_ok=True)

        # If the option is followed by the keyword "up" and a number, then
        # the source should be copied (or linked) from <number> levels up
        # in the hierarchy (see below).

        if 'up' in option:
            uparg = option.index('up') 
            try:
                hier_up = int(option[uparg + 1])
            except:
                print("Non-numeric option to 'up': " + option[uparg + 1])
                print("Ignoring 'up' option.")
                hier_up = 0
        else:
            hier_up = 0

        filter_scripts = []
        for item in option:
            if item.split('=')[0] == 'filter':
                filter_scripts.append(item.split('=')[1])
                break

        # Option 'stub' applies to netlists ('cdl' or 'spice') and generates
        # a file with only stub entries.
        do_stub = 'stub' in option

        # Option 'compile' is a standalone keyword ('comp' may be used).
        do_compile = 'compile' in option or 'comp' in option
        do_compile_only = 'compile-only' in option or 'comp-only' in option
 
        # Option 'nospecify' is a standalone keyword ('nospec' may be used).
        do_remove_spec = 'nospecify' in option or 'nospec' in option

        # Option 'exclude' has an argument
        try:
            excludelist = list(item.split('=')[1].split(',') for item in option if item.startswith('excl'))[0]
        except IndexError:
            excludelist = []
        else:
            print('Excluding files: ' + (',').join(excludelist))

        # Option 'rename' has an argument
        try:
            newname = list(item.split('=')[1] for item in option if item.startswith('rename'))[0]
        except IndexError:
            newname = None
        else:
            print('Renaming file to: ' + newname)

        # 'anno' may be specified for LEF, in which case the LEF is used only
        # to annotate GDS and is not itself installed;  this allows LEF to
        # be generated from Magic and avoids quirky use of obstruction layers.
        have_lefanno = True if 'annotate' in option or 'anno' in option else False
        if have_lefanno: 
            if option[0] != 'lef':
                print("Warning: 'annotate' option specified outside of -lef.  Ignoring.")
            else:
                # Mark as NOT having LEF since we want to use it only for annotation.
                have_lef = False

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]

            if ef_format:
                destlibdir = destdir + '/' + destlib
            else:
                destdir = targetdir + '/libs.ref/' + destlib + '/' + option[0]
                destlibdir = destdir

            os.makedirs(destlibdir, exist_ok=True)

            # Populate the library subdirectory
            # Parse the option and replace each '/*/' with the library name,
            # and check if it is a valid directory name.  Then glob the
            # resulting option name.  Warning:  This assumes that all
            # occurences of the text '/*/' match a library name.  It should
            # be possible to wild-card the directory name in such a way that
            # this is always true.

            testpath = substitute(sourcedir + '/' + option[1], library[1])
            liblist = glob.glob(testpath)

            # Create a file "sources.txt" (or append to it if it exists)
            # and add the source directory name so that the staging install
            # script can know where the files came from.

            with open(destlibdir + '/sources.txt', 'a') as ofile:
                print(testpath, file=ofile)

            # Create exclude list with glob-style matching using fnmatch
            if len(liblist) > 0:
                liblistnames = list(os.path.split(item)[1] for item in liblist)
                notliblist = []
                for exclude in excludelist:
                    notliblist.extend(fnmatch.filter(liblistnames, exclude))

                # Apply exclude list
                if len(notliblist) > 0:
                    for file in liblist[:]:
                        if os.path.split(file)[1] in notliblist:
                            liblist.remove(file)

                if len(excludelist) > 0 and len(notliblist) == 0:
                    print('Warning:  Nothing from the exclude list found in sources.')
                    print('excludelist = ' + str(excludelist))
                    print('destlibdir = ' + destlibdir)

            # Diagnostic
            print('Collecting files from ' + testpath)
            print('Files to install:')
            if len(liblist) < 10:
                for item in liblist:
                    print('   ' + item)
            else:
                for item in liblist[0:4]:
                    print('   ' + item)
                print('   .')
                print('   .')
                print('   .')
                for item in liblist[-6:-1]:
                    print('   ' + item)
                print('(' + str(len(liblist)) + ' files total)')

            for libname in liblist:
                # Note that there may be a hierarchy to the files in option[1],
                # say for liberty timing files under different conditions, so
                # make sure directories have been created as needed.

                libfile = os.path.split(libname)[1]
                libfilepath = os.path.split(libname)[0]
                destpathcomp = []
                for i in range(hier_up):
                    destpathcomp.append('/' + os.path.split(libfilepath)[1])
                    libfilepath = os.path.split(libfilepath)[0]
                destpathcomp.reverse()
                destpath = ''.join(destpathcomp)

                if newname:
                    if len(liblist) == 1:
                        destfile = newname
                    else:
                        if not do_compile and not do_compile_only:
                            print('Error:  rename specified but more than one file found!')
                        destfile = libfile
                else:
                    destfile = libfile

                targname = destlibdir + destpath + '/' + destfile

                # NOTE:  When using "up" with link_from, could just make
                # destpath itself a symbolic link;  this way is more flexible
                # but adds one symbolic link per file.

                if destpath != '':
                    if not os.path.isdir(destlibdir + destpath):
                        os.makedirs(destlibdir + destpath, exist_ok=True)

                # Remove any existing file
                if os.path.isfile(targname):
                    os.remove(targname)
                elif os.path.isdir(targname):
                    shutil.rmtree(targname)

                # NOTE:  Diagnostic, probably much too much output.
                print('   Install:' + libname + ' to ' + targname)
                if os.path.isfile(libname):
                    shutil.copy(libname, targname)
                else:
                    shutil.copytree(libname, targname)

                # File filtering options:  Two options 'stub' and 'nospec' are
                # handled by scripts in ../common/.  Custom filters can also be
                # specified.

                local_filter_scripts = filter_scripts[:]

                if option[0] == 'verilog':
                    # Internally handle syntactical issues with verilog and iverilog
                    vfilter(targname)

                    if do_remove_spec:
                        scriptdir = os.path.split(os.getcwd())[0] + '/common'
                        local_filter_scripts.append(scriptdir + '/remove_specify.py')

                elif option[0] == 'cdl' or option[0] == 'spi' or option[0] == 'spice':
                    if do_stub:
                        scriptdir = os.path.split(os.getcwd())[0] + '/common'
                        local_filter_scripts.append(scriptdir + '/makestub.py')

                for filter_script in local_filter_scripts:
                    # Apply filter script to all files in the target directory
                    tfilter(targname, filter_script)

            if do_compile == True or do_compile_only == True:
                # NOTE:  The purpose of "rename" is to put a destlib-named
                # library elsewhere so that it can be merged with another
                # library into a compiled <destlib>.<ext>

                compname = destlib
                    
                # To do:  Make this compatible with linking from another PDK.

                if option[0] == 'verilog':
                    # If there is not a single file with all verilog cells in it,
                    # then compile one, because one does not want to have to have
                    # an include line for every single cell used in a design.

                    create_verilog_library(destlibdir, compname, do_compile_only, do_stub, excludelist)

                elif option[0] == 'gds' and have_mag_8_2:
                    # If there is not a single file with all GDS cells in it,
                    # then compile one.

                    # Link to the PDK magic startup file from the target directory
                    startup_script = targetdir + mag_current + pdkname + '-F.magicrc'
                    if not os.path.isfile(startup_script):
                        startup_script = targetdir + mag_current + pdkname + '.magicrc'
                    create_gds_library(destlibdir, compname, startup_script, do_compile_only, excludelist)

                elif option[0] == 'liberty' or option[0] == 'lib':
                    # If there is not a single file with all liberty cells in it,
                    # then compile one, because one does not want to have to have
                    # an include line for every single cell used in a design.

                    create_lib_library(destlibdir, compname, do_compile_only, excludelist)

                elif option[0] == 'spice' or option[0] == 'spi':
                    # If there is not a single file with all SPICE subcircuits in it,
                    # then compile one, because one does not want to have to have
                    # an include line for every single cell used in a design.

                    spiext = '.spice' if not ef_format else '.spi'
                    create_spice_library(destlibdir, compname, spiext, do_compile_only, do_stub, excludelist)
                    if do_compile_only == True:
                        if newname:
                            if os.path.isfile(newname):
                                os.remove(newname)

                elif option[0] == 'cdl':
                    # If there is not a single file with all CDL subcircuits in it,
                    # then compile one, because one does not want to have to have
                    # an include line for every single cell used in a design.

                    create_spice_library(destlibdir, compname, '.cdl', do_compile_only, do_stub, excludelist)
                    if do_compile_only == True:
                        if newname:
                            if os.path.isfile(newname):
                                os.remove(newname)

                elif option[0] == 'lef':
                    # If there is not a single file with all LEF cells in it,
                    # then compile one, because one does not want to have to have
                    # an include line for every single cell used in a design.

                    create_lef_library(destlibdir, compname, do_compile_only, excludelist)

        # Find any libraries/options marked as "privileged" (or "private") and
        # move the files from libs.tech or libs.ref to libs.priv, leaving a
        # symbolic link in the original location.  Do this during the initial
        # install so that options following in the list can add files to the
        # non-privileged equivalent directory path.

        if 'priv' in option or 'privileged' in option or 'private' in option:

            # Diagnostic
            print("Install option: " + str(option[0]))

            if ef_format == True:
                os.makedirs(targetdir + '/libs.priv', exist_ok=True)

            for library in libraries:
                if len(library) == 3:
                    destlib = library[2]
                else:
                    destlib = library[1]

                if ef_format:
                    srclibdir = targetdir + '/libs.ref/' + option[0] + '/' + destlib
                    destlibdir = targetdir + '/libs.priv/' + option[0] + '/' + destlib
                else:
                    srclibdir = targetdir + '/libs.ref/' + destlib + '/' + option[0]
                    destlibdir = targetdir + '/libs.priv/' + destlib + '/' + option[0]

                if not os.path.exists(destlibdir):
                    os.makedirs(destlibdir)

                print('Moving files in ' + srclibdir + ' to privileged space.')
                filelist = os.listdir(srclibdir)
                for file in filelist:
                    srcfile = srclibdir + '/' + file
                    destfile = destlibdir + '/' + file
                    if os.path.isfile(destfile):
                        os.remove(destfile)
                    elif os.path.isdir(destfile):
                        shutil.rmtree(destfile)

                    if os.path.isfile(srcfile):
                        shutil.copy(srcfile, destfile)
                        os.remove(srcfile)
                    else:
                        shutil.copytree(srcfile, destfile)
                        shutil.rmtree(srcfile)

    print("Completed installation of vendor files.")

    #----------------------------------------------------------------
    # Installation part 2:  Generate derived file formats
    #----------------------------------------------------------------

    # Now for the harder part.  If GDS and/or LEF databases were specified,
    # then migrate them to magic (.mag files in layout/ or abstract/).

    ignorelist = []
    do_cdl_scaleu  = False
    no_cdl_convert = False
    no_gds_convert = False
    no_lef_convert = False
    cdl_compile_only = False

    cdl_exclude = []
    lef_exclude = []
    gds_exclude = []
    spice_exclude = []
    verilog_exclude = []

    cdl_reflib = '/libs.ref/'
    gds_reflib = '/libs.ref/'
    lef_reflib = '/libs.ref/'

    for option in optionlist[:]:
        if option[0] == 'cdl':
            # Option 'scaleu' is a standalone keyword
            do_cdl_scaleu = 'scaleu' in option

            # Option 'ignore' has arguments after '='
            for item in option:
                if item.split('=')[0] == 'ignore':
                    ignorelist = item.split('=')[1].split(',')

	# Option 'noconvert' is a standalone keyword.
        if 'noconvert' in option:
            if option[0] == 'cdl':
                no_cdl_convert = True
            elif option[0] == 'gds':
                no_gds_convert = True
            elif option[0] == 'lef':
                no_lef_convert = True

        # Option 'privileged' is a standalone keyword.
        if 'priv' in option or 'privileged' in option or 'private' in option:
            if option[0] == 'cdl':
                cdl_reflib = '/libs.priv/'
            elif option[0] == 'gds':
                gds_reflib = '/libs.priv/'
            elif option[0] == 'lef':
                lef_reflib = '/libs.priv/'

        # If CDL is marked 'compile-only' then CDL should only convert the
        # compiled file to SPICE if conversion is needed.
        if 'compile-only' in option:
            if option[0] == 'cdl':
                cdl_compile_only = True

        # Find exclude list for any option
        for item in option:
            if item.split('=')[0] == 'exclude':
                exclude_list = item.split('=')[1].split(',')
                if option[0] == 'cdl':
                    cdl_exclude = exclude_list
                elif option[0] == 'lef':
                    lef_exclude = exclude_list
                elif option[0] == 'gds':
                    gds_exclude = exclude_list
                elif option[0] == 'spi' or option[0] == 'spice':
                    spice_exclude = exclude_list
                elif option[0] == 'verilog':
                    verilog_exclude = exclude_list
 
    devlist = []
    pdklibrary = None

    if have_gds and not no_gds_convert:
        print("Migrating GDS files to layout.")

        if ef_format:
            destdir = targetdir + gds_reflib + 'mag'
            srcdir = targetdir + gds_reflib + 'gds'
            vdir = targetdir + '/libs.ref/' + 'verilog'
            cdir = targetdir + cdl_reflib + 'cdl'
            sdir = targetdir + cdl_reflib + 'spi'

            os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]

            if ef_format:
                destlibdir = destdir + '/' + destlib
                srclibdir = srcdir + '/' + destlib
                vlibdir = vdir + '/' + destlib
                clibdir = cdir + '/' + destlib
                slibdir = sdir + '/' + destlib
            else:
                destdir = targetdir + gds_reflib + destlib + '/mag'
                srcdir = targetdir + gds_reflib + destlib + '/gds'
                vdir = targetdir + '/libs.ref/' + destlib + '/verilog'
                cdir = targetdir + cdl_reflib + destlib + '/cdl'
                sdir = targetdir + cdl_reflib + destlib + '/spice'
                destlibdir = destdir
                srclibdir = srcdir
                vlibdir = vdir
                clibdir = cdir
                slibdir = sdir

            os.makedirs(destlibdir, exist_ok=True)

            # For primitive devices, check the PDK script and find the name
            # of the library and get a list of supported devices.

            if library[0] == 'primitive':
                pdkscript = targetdir + mag_current + pdkname + '.tcl'
                print('Searching for supported devices in PDK script ' + pdkscript + '.')

                if os.path.isfile(pdkscript):
                    librex = re.compile('^[ \t]*set[ \t]+PDKNAMESPACE[ \t]+([^ \t]+)$')
                    devrex = re.compile('^[ \t]*proc[ \t]+([^ :\t]+)::([^ \t_]+)_defaults')
                    fixrex = re.compile('^[ \t]*return[ \t]+\[([^ :\t]+)::fixed_draw[ \t]+([^ \t]+)[ \t]+')
                    devlist = []
                    fixedlist = []
                    with open(pdkscript, 'r') as ifile:
                        scripttext = ifile.read().splitlines()
                        for line in scripttext:
                            lmatch = librex.match(line)
                            if lmatch:
                                pdklibrary = lmatch.group(1)
                            dmatch = devrex.match(line)
                            if dmatch:
                                if dmatch.group(1) == pdklibrary:
                                    devlist.append(dmatch.group(2))
                            fmatch = fixrex.match(line)
                            if fmatch:
                                if fmatch.group(1) == pdklibrary:
                                    fixedlist.append(fmatch.group(2))

                # Diagnostic
                print("PDK library is " + str(pdklibrary))

            # Link to the PDK magic startup file from the target directory
            # If there is no -F version then look for one without -F (open source PDK)
            startup_script = targetdir + mag_current + pdkname + '-F.magicrc'
            if not os.path.isfile(startup_script):
                startup_script = targetdir + mag_current + pdkname + '.magicrc'

            if have_mag_8_2 and os.path.isfile(startup_script):
                # If the symbolic link exists, remove it.
                if os.path.isfile(destlibdir + '/.magicrc'):
                    os.remove(destlibdir + '/.magicrc')
                os.symlink(startup_script, destlibdir + '/.magicrc')
 
                # Find GDS file names in the source
                print('Getting GDS file list from ' + srclibdir + '.')
                gdsfilesraw = os.listdir(srclibdir)
                gdsfiles = []
                for gdsfile in gdsfilesraw:
                    gdsext = os.path.splitext(gdsfile)[1].lower()
                    if gdsext == '.gds' or gdsext == '.gdsii' or gdsext == '.gds2':
                        gdsfiles.append(gdsfile)

                # Create exclude list with glob-style matching using fnmatch
                if len(gdsfiles) > 0:
                    gdsnames = list(os.path.split(item)[1] for item in gdsfiles)
                    notgdsnames = []
                    for exclude in gds_exclude:
                        notgdsnames.extend(fnmatch.filter(gdsnames, exclude))

                    # Apply exclude list
                    if len(notgdsnames) > 0:
                        for file in gdsfiles[:]:
                            if os.path.split(file)[1] in notgdsnames:
                                gdsfiles.remove(file)

                # Generate a script called "generate_magic.tcl" and leave it in
                # the target directory.  Use it as input to magic to create the
                # .mag files from the database.

                print('Creating magic generation script to generate magic database files.') 

                with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
                    print('#!/usr/bin/env wish', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('# Script to generate .mag files from .gds    ', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('gds readonly true', file=ofile)
                    print('gds flatten true', file=ofile)
                    print('gds rescale false', file=ofile)
                    print('tech unlock *', file=ofile)

                    for gdsfile in gdsfiles:
                        # Note:  DO NOT use a relative path here.
                        print('gds read ' + srclibdir + '/' + gdsfile, file=ofile)

                    # Make sure properties include the Tcl generated cell
                    # information from the PDK script

                    if pdklibrary:
                        tclfixedlist = '{' + ' '.join(fixedlist) + '}'
                        print('set devlist ' + tclfixedlist, file=ofile)
                        print('set topcell [lindex [cellname list top] 0]',
				    file=ofile)

                        print('foreach cellname $devlist {', file=ofile)
                        print('    load $cellname', file=ofile)
                        print('    property gencell $cellname', file=ofile)
                        print('    property parameter m=1', file=ofile)
                        print('    property library ' + pdklibrary, file=ofile)
                        print('}', file=ofile)
                        print('load $topcell', file=ofile)

                    print('cellname delete \(UNNAMED\)', file=ofile)
                    print('writeall force', file=ofile)

                    leffiles = []
                    lefmacros = []
                    if have_lefanno:
                        # Find LEF file names in the source
                        if ef_format:
                            lefsrcdir = targetdir + lef_reflib + 'lefanno'
                            lefsrclibdir = lefsrcdir + '/' + destlib
                        else:
                            lefsrcdir = targetdir + lef_reflib + destlib + '/lefanno'
                            lefsrclibdir = lefsrcdir

                        leffiles = os.listdir(lefsrclibdir)
                        leffiles = list(item for item in leffiles if os.path.splitext(item)[1] == '.lef')
                        # Get list of abstract views to make from LEF macros
                        for leffile in leffiles:
                            with open(leffile, 'r') as ifile:
                                ltext = ifile.read()
                                llines = ltext.splitlines()
                                for lline in llines:
                                    ltok = re.split(' |\t|\(', lline)
                                    if ltok[0] == 'MACRO':
                                        lefmacros.append(ltok[1])

                        # Create exclude list with glob-style matching using fnmatch
                        if len(lefmacros) > 0:
                            lefnames = list(os.path.split(item)[1] for item in lefmacros)
                            notlefnames = []
                            for exclude in lef_exclude:
                                notlefnames.extend(fnmatch.filter(lefnames, exclude))

                            # Apply exclude list
                            if len(notlefnames) > 0:
                                for file in lefmacros[:]:
                                    if os.path.split(file)[1] in notlefnames:
                                        lefmacros.remove(file)

                    elif have_verilog and os.path.isdir(vlibdir):
                        # Get list of abstract views to make from verilog modules
                        vfiles = os.listdir(vlibdir)
                        vfiles = list(item for item in vfiles if os.path.splitext(item)[1] == '.v')
                        for vfile in vfiles:
                            with open(vlibdir + '/' + vfile, 'r') as ifile:
                                vtext = ifile.read()
                                vlines = vtext.splitlines()
                                for vline in vlines:
                                    vtok = re.split(' |\t|\(', vline)
                                    try:
                                        if vtok[0] == 'module':
                                            if vtok[1] not in lefmacros:
                                                lefmacros.append(vtok[1])
                                    except:
                                        pass

                        # Create exclude list with glob-style matching using fnmatch
                        if len(lefmacros) > 0:
                            lefnames = list(os.path.split(item)[1] for item in lefmacros)
                            notlefnames = []
                            for exclude in verilog_exclude:
                                notlefnames.extend(fnmatch.filter(lefnames, exclude))

                            # Apply exclude list
                            if len(notlefnames) > 0:
                                for file in lefmacros[:]:
                                    if os.path.split(file)[1] in notlefnames:
                                        lefmacros.remove(file)

                    elif have_cdl and os.path.isdir(clibdir):
                        # Get list of abstract views to make from CDL subcircuits
                        cfiles = os.listdir(clibdir)
                        cfiles = list(item for item in cfiles if os.path.splitext(item)[1] == '.cdl')
                        for cfile in cfiles:
                            with open(clibdir + '/' + cfile, 'r') as ifile:
                                ctext = ifile.read()
                                clines = ctext.splitlines()
                                for cline in clines:
                                    ctok = cline.split()
                                    try:
                                        if ctok[0].lower() == '.subckt':
                                            if ctok[1] not in lefmacros:
                                                lefmacros.append(ctok[1])
                                    except:
                                        pass

                        # Create exclude list with glob-style matching using fnmatch
                        if len(lefmacros) > 0:
                            lefnames = list(os.path.split(item)[1] for item in lefmacros)
                            notlefnames = []
                            for exclude in cdl_exclude:
                                notlefnames.extend(fnmatch.filter(lefnames, exclude))

                            # Apply exclude list
                            if len(notlefnames) > 0:
                                for file in lefmacros[:]:
                                    if os.path.split(file)[1] in notlefnames:
                                        lefmacros.remove(file)

                    elif have_spice and os.path.isdir(slibdir):
                        # Get list of abstract views to make from SPICE subcircuits
                        sfiles = os.listdir(slibdir)
                        sfiles = list(item for item in sfiles)
                        for sfile in sfiles:
                            with open(slibdir + '/' + sfile, 'r') as ifile:
                                stext = ifile.read()
                                slines = stext.splitlines()
                                for sline in slines:
                                    stok = sline.split()
                                    try:
                                        if stok[0].lower() == '.subckt':
                                            if stok[1] not in lefmacros:
                                                lefmacros.append(stok[1])
                                    except:
                                        pass

                        # Create exclude list with glob-style matching using fnmatch
                        if len(lefmacros) > 0:
                            lefnames = list(os.path.split(item)[1] for item in lefmacros)
                            notlefnames = []
                            for exclude in spice_exclude:
                                notlefnames.extend(fnmatch.filter(lefnames, exclude))

                            # Apply exclude list
                            if len(notlefnames) > 0:
                                for file in lefmacros[:]:
                                    if os.path.split(file)[1] in notlefnames:
                                        lefmacros.remove(file)

                    if not lefmacros:
                        print('No source for abstract views:  Abstract views not made.')
                    elif not have_lef:
                        # This library has a GDS database but no LEF database.  Use
                        # magic to create abstract views of the GDS cells.  If
                        # option "annotate" is given, then read the LEF file after
                        # loading the database file to annotate the cell with
                        # information from the LEF file.  This usually indicates
                        # that the LEF file has some weird definition of obstruction
                        # layers and we want to normalize them by using magic's LEF
                        # write procedure, but we still need the pin use and class
                        # information from the LEF file, and maybe the bounding box.

                        for leffile in leffiles:
                            if have_lefanno:
                                print('lef read ' + lefsrclibdir + '/' + leffile, file=ofile)
                        for lefmacro in lefmacros:
                            print('if {[cellname list exists ' + lefmacro + '] != 0} {', file=ofile)
                            print('   load ' + lefmacro, file=ofile)
                            print('   lef write ' + lefmacro + ' -hide', file=ofile)
                            print('}', file=ofile)
                    print('puts stdout "Done."', file=ofile)
                    print('quit -noprompt', file=ofile)

                print('Running magic to create magic database files.')
                sys.stdout.flush()

                # Run magic to read in the GDS file and write out magic databases.
                with open(destlibdir + '/generate_magic.tcl', 'r') as ifile:
                    mproc = subprocess.run(['magic', '-dnull', '-noconsole'],
				stdin = ifile, stdout = subprocess.PIPE,
				stderr = subprocess.PIPE, cwd = destlibdir,
				universal_newlines = True)
                    if mproc.stdout:
                        for line in mproc.stdout.splitlines():
                            print(line)
                    if mproc.stderr:
                        print('Error message output from magic:')
                        for line in mproc.stderr.splitlines():
                            print(line)
                    if mproc.returncode != 0:
                        print('ERROR:  Magic exited with status ' + str(mproc.returncode))

                if not have_lef:
                    print('No LEF file install;  need to generate LEF.')
                    # Remove the lefanno/ target and its contents.
                    if have_lefanno:
                        if ef_format:
                            lefannosrcdir = targetdir + lef_reflib + 'lefanno'
                        else:
                            lefannosrcdir = targetdir + lef_reflib + destlib + '/lefanno'
                        if os.path.isdir(lefannosrcdir):
                            shutil.rmtree(lefannosrcdir)

                    if ef_format:
                        destlefdir = targetdir + lef_reflib + 'lef'
                        destleflibdir = destlefdir + '/' + destlib
                    else:
                        destlefdir = targetdir + lef_reflib + destlib + '/lef'
                        destleflibdir = destlefdir

                    os.makedirs(destleflibdir, exist_ok=True)
                    leflist = os.listdir(destlibdir)
                    leflist = list(item for item in leflist if os.path.splitext(item)[1] == '.lef')

                    # All macros will go into one file
                    destleflib = destleflibdir + '/' + destlib + '.lef'
                    # Remove any existing library file from the target directory
                    if os.path.isfile(destleflib):
                        print('Removing existing library ' + destleflib)
                        os.remove(destleflib)

                    first = True
                    with open(destleflib, 'w') as ofile:
                        for leffile in leflist:
                            # Remove any existing single file from the target directory
                            if os.path.isfile(destleflibdir + '/' + leffile):
                                print('Removing ' + destleflibdir + '/' + leffile)
                                os.remove(destleflibdir + '/' + leffile)

                            # Append contents
                            sourcelef =  destlibdir + '/' + leffile
                            with open(sourcelef, 'r') as ifile:
                                leflines = ifile.read().splitlines()
                                if not first:
                                    # Remove header from all but the first file
                                    leflines = leflines[8:]
                                else:
                                    first = False

                            for line in leflines:
                                print(line, file=ofile)

                            # Remove file from the source directory
                            print('Removing source file ' + sourcelef)
                            os.remove(sourcelef)

                    # Set have_lef now that LEF files were made, so they
                    # can be used to generate the maglef/ databases.
                    have_lef = True

            elif not have_mag_8_2:
                print('The installer is not able to run magic.')
            else:
                print("Master PDK magic startup file not found.  Did you install")
                print("PDK tech files before PDK vendor files?")

    if have_lef and not no_lef_convert:
        print("Migrating LEF files to layout.")
        if ef_format:
            destdir = targetdir + '/libs.ref/' + 'maglef'
            srcdir = targetdir + lef_reflib + 'lef'
            magdir = targetdir + gds_reflib + 'mag'
            cdldir = targetdir + cdl_reflib + 'cdl'
            os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]

            if ef_format:
                destlibdir = destdir + '/' + destlib
                srclibdir = srcdir + '/' + destlib
                maglibdir = magdir + '/' + destlib
                cdllibdir = cdldir + '/' + destlib
            else:
                destdir = targetdir + '/libs.ref/' + destlib + '/maglef'
                srcdir = targetdir + lef_reflib + destlib + '/lef'
                magdir = targetdir + gds_reflib + destlib + '/mag'
                cdldir = targetdir + cdl_reflib + destlib + '/cdl'

                destlibdir = destdir
                srclibdir = srcdir
                maglibdir = magdir
                cdllibdir = cdldir

            os.makedirs(destlibdir, exist_ok=True)

            # Link to the PDK magic startup file from the target directory
            startup_script = targetdir + mag_current + pdkname + '-F.magicrc'
            if not os.path.isfile(startup_script):
                startup_script = targetdir + mag_current + pdkname + '.magicrc'

            if have_mag_8_2 and os.path.isfile(startup_script):
                # If the symbolic link exists, remove it.
                if os.path.isfile(destlibdir + '/.magicrc'):
                    os.remove(destlibdir + '/.magicrc')
                os.symlink(startup_script, destlibdir + '/.magicrc')
 
                # Find LEF file names in the source
                leffiles = os.listdir(srclibdir)
                leffiles = list(item for item in leffiles if os.path.splitext(item)[1].lower() == '.lef')

                # Get list of abstract views to make from LEF macros
                lefmacros = []
                err_no_macros = False
                for leffile in leffiles:
                    with open(srclibdir + '/' + leffile, 'r') as ifile:
                        ltext = ifile.read()
                        llines = ltext.splitlines()
                        for lline in llines:
                            ltok = re.split(' |\t|\(', lline)
                            if ltok[0] == 'MACRO':
                                lefmacros.append(ltok[1])

                # Create exclude list with glob-style matching using fnmatch
                if len(lefmacros) > 0:
                    lefnames = list(os.path.split(item)[1] for item in lefmacros)
                    notlefnames = []
                    for exclude in lef_exclude:
                        notlefnames.extend(fnmatch.filter(lefnames, exclude))

                    # Apply exclude list
                    if len(notlefnames) > 0:
                        for file in lefmacros[:]:
                            if os.path.split(file)[1] in notlefnames:
                                lefmacros.remove(file)

                if len(leffiles) == 0:
                    print('Warning:  No LEF files found in ' + srclibdir)
                    continue

                print('Generating conversion script to create magic databases from LEF')

                # Generate a script called "generate_magic.tcl" and leave it in
                # the target directory.  Use it as input to magic to create the
                # .mag files from the database.

                with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
                    print('#!/usr/bin/env wish', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('# Script to generate .mag files from .lef    ', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('tech unlock *', file=ofile)

                    # If there are devices in the LEF file that come from the
                    # PDK library, then copy this list into the script.

                    if pdklibrary:
                        shortdevlist = []
                        for macro in lefmacros:
                            if macro in devlist:
                                shortdevlist.append(macro)

                        tcldevlist = '{' + ' '.join(shortdevlist) + '}'
                        print('set devlist ' + tcldevlist, file=ofile)

                    for leffile in leffiles:
                        print('lef read ' + srclibdir + '/' + leffile, file=ofile)

                    for lefmacro in lefmacros:

                        # To be completed:  Parse SPICE file for port order, make
                        # sure ports are present and ordered.

                        if pdklibrary and lefmacro in shortdevlist:
                            print('set cellname ' + lefmacro, file=ofile)
                            print('if {[lsearch $devlist $cellname] >= 0} {',
					file=ofile)
                            print('    load $cellname', file=ofile)
                            print('    property gencell $cellname', file=ofile)
                            print('    property parameter m=1', file=ofile)
                            print('    property library ' + pdklibrary, file=ofile)
                            print('}', file=ofile)

                    # Load one of the LEF files so that the default (UNNAMED) cell
                    # is not loaded, then delete (UNNAMED) so it doesn't generate
                    # an error message.
                    if len(lefmacros) > 0:
                        print('load ' + lefmacros[0], file=ofile)
                        print('cellname delete \(UNNAMED\)', file=ofile)
                    else:
                        err_no_macros = True
                    print('writeall force', file=ofile)
                    print('puts stdout "Done."', file=ofile)
                    print('quit -noprompt', file=ofile)

                if err_no_macros == True:
                    print('Warning:  No LEF macros were defined.')

                print('Running magic to create magic databases from LEF')
                sys.stdout.flush()

                # Run magic to read in the LEF file and write out magic databases.
                with open(destlibdir + '/generate_magic.tcl', 'r') as ifile:
                    mproc = subprocess.run(['magic', '-dnull', '-noconsole'],
				stdin = ifile, stdout = subprocess.PIPE,
				stderr = subprocess.PIPE, cwd = destlibdir,
				universal_newlines = True)
                    if mproc.stdout:
                        for line in mproc.stdout.splitlines():
                            print(line)
                    if mproc.stderr:
                        print('Error message output from magic:')
                        for line in mproc.stderr.splitlines():
                            print(line)
                    if mproc.returncode != 0:
                        print('ERROR:  Magic exited with status ' + str(mproc.returncode))


                # Now list all the .mag files generated, and for each, read the
                # corresponding file from the mag/ directory, pull the GDS file
                # properties, and add those properties to the maglef view.  Also
                # read the CDL (or SPICE) netlist, read the ports, and rewrite
                # the port order in the mag and maglef file accordingly.

                # Diagnostic
                print('Annotating files in ' + destlibdir)
                sys.stdout.flush()
                magfiles = os.listdir(destlibdir)
                magfiles = list(item for item in magfiles if os.path.splitext(item)[1] == '.mag')
                for magroot in magfiles:
                    magname = os.path.splitext(magroot)[0]
                    magfile = maglibdir + '/' + magroot
                    magleffile = destlibdir + '/' + magroot
                    prop_lines = get_gds_properties(magfile)

                    # Make sure properties include the Tcl generated cell
                    # information from the PDK script

                    prop_gencell = []
                    if pdklibrary:
                        if magname in fixedlist:
                            prop_gencell.append('gencell ' + magname)
                            prop_gencell.append('library ' + pdklibrary)
                            prop_gencell.append('parameter m=1')

                    nprops = len(prop_lines) + len(prop_gencell)

                    cdlfile = cdllibdir + '/' + magname + '.cdl'
                    if os.path.exists(cdlfile):
                        cdlfiles = [cdlfile]
                    else:
                        # Assume there is at least one file with all cell subcircuits
                        # in it.
                        try:
                            cdlfiles = glob.glob(cdllibdir + '/*.cdl')
                        except:
                            pass
                    if len(cdlfiles) > 0:
                        for cdlfile in cdlfiles:
                            port_dict = get_subckt_ports(cdlfile, magname)
                            if port_dict != {}:
                                break
                    else:
                        port_dict = {}

                    if port_dict == {}:
                        print('No CDL file contains ' + destlib + ' device ' + magname)
                        cdlfile = None
                        # To be done:  If destlib is 'primitive', then look in
                        # SPICE models for port order.
                        if destlib == 'primitive':
                            print('Fix me:  Need to look in SPICE models!')

                    proprex = re.compile('<< properties >>')
                    endrex = re.compile('<< end >>')
                    rlabrex = re.compile('rlabel[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+([^ \t]+)')
                    flabrex = re.compile('flabel[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+([^ \t]+)')
                    portrex = re.compile('port[ \t]+([^ \t]+)[ \t]+(.*)')
                    gcellrex = re.compile('string gencell')
                    portnum = -1

                    with open(magleffile, 'r') as ifile:
                        magtext = ifile.read().splitlines()

                    with open(magleffile, 'w') as ofile:
                        has_props = False
                        is_gencell = False
                        for line in magtext:
                            tmatch = portrex.match(line)
                            if tmatch:
                                if portnum >= 0:
                                    line = 'port ' + str(portnum) + ' ' + tmatch.group(2)
                                else:
                                    line = 'port ' + tmatch.group(1) + ' ' + tmatch.group(2)
                            ematch = endrex.match(line)
                            if ematch and nprops > 0:
                                if not has_props:
                                    print('<< properties >>', file=ofile)
                                if not is_gencell:
                                    for prop in prop_gencell:
                                        print('string ' + prop, file=ofile)
                                for prop in prop_lines:
                                    print('string ' + prop, file=ofile)

                            print(line, file=ofile)
                            pmatch = proprex.match(line)
                            if pmatch:
                                has_props = True

                            gmatch = gcellrex.match(line)
                            if gmatch:
                                is_gencell = True

                            lmatch = flabrex.match(line)
                            if not lmatch:
                                lmatch = rlabrex.match(line)
                            if lmatch:
                                labname = lmatch.group(1).lower()
                                try:
                                    portnum = port_dict[labname]
                                except:
                                    portnum = -1

                    if os.path.exists(magfile):
                        with open(magfile, 'r') as ifile:
                            magtext = ifile.read().splitlines()

                        with open(magfile, 'w') as ofile:
                            for line in magtext:
                                tmatch = portrex.match(line)
                                if tmatch:
                                    if portnum >= 0:
                                        line = 'port ' + str(portnum) + ' ' + tmatch.group(2)
                                    else:
                                        line = 'port ' + tmatch.group(1) + ' ' + tmatch.group(2)
                                ematch = endrex.match(line)
                                print(line, file=ofile)
                                lmatch = flabrex.match(line)
                                if not lmatch:
                                    lmatch = rlabrex.match(line)
                                if lmatch:
                                    labname = lmatch.group(1).lower()
                                    try:
                                        portnum = port_dict[labname]
                                    except:
                                        portnum = -1
                    elif os.path.splitext(magfile)[1] == '.mag':
                        # NOTE:  Possibly this means the GDS cell has a different name.
                        print('Error: No file ' + magfile + '.  Why is it in maglef???')

            elif not have_mag_8_2:
                print('The installer is not able to run magic.')
            else:
                print("Master PDK magic startup file not found.  Did you install")
                print("PDK tech files before PDK vendor files?")

    # If SPICE or CDL databases were specified, then convert them to
    # a form that can be used by ngspice, using the cdl2spi.py script 

    if have_spice:
        if ef_format:
            if not os.path.isdir(targetdir + cdl_reflib + 'spi'):
                os.makedirs(targetdir + cdl_reflib + 'spi', exist_ok=True)

    elif have_cdl and not no_cdl_convert:
        if ef_format:
            if not os.path.isdir(targetdir + cdl_reflib + 'spi'):
                os.makedirs(targetdir + cdl_reflib + 'spi', exist_ok=True)

        print("Migrating CDL netlists to SPICE.")
        sys.stdout.flush()

        if ef_format:
            destdir = targetdir + cdl_reflib + 'spi'
            srcdir = targetdir + cdl_reflib + 'cdl'
            os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]

            if ef_format:
                destlibdir = destdir + '/' + destlib
                srclibdir = srcdir + '/' + destlib
            else:
                destdir = targetdir + cdl_reflib + destlib + '/spice'
                srcdir = targetdir + cdl_reflib + destlib + '/cdl'

                destlibdir = destdir
                srclibdir = srcdir

            os.makedirs(destlibdir, exist_ok=True)

            # Find CDL file names in the source
            # If CDL is marked compile-only then ONLY convert <distdir>.cdl
            if cdl_compile_only:
                alllibname = destlibdir + '/' + destlib + '.cdl'
                if not os.path.exists(alllibname):
                    cdl_compile_only = False
                else:
                    cdlfiles = [alllibname]

            if not cdl_compile_only:
                cdlfiles = os.listdir(srclibdir)
                cdlfiles = list(item for item in cdlfiles if os.path.splitext(item)[1].lower() == '.cdl')

            # The directory with scripts should be in ../common with respect
            # to the Makefile that determines the cwd.
            scriptdir = os.path.split(os.getcwd())[0] + '/common'

            # Run cdl2spi.py script to read in the CDL file and write out SPICE
            for cdlfile in cdlfiles:
                if ef_format:
                    spiname = os.path.splitext(cdlfile)[0] + '.spi'
                else:
                    spiname = os.path.splitext(cdlfile)[0] + '.spice'
                procopts = [scriptdir + '/cdl2spi.py', srclibdir + '/' + cdlfile, destlibdir + '/' + spiname]
                if do_cdl_scaleu:
                    procopts.append('-dscale=u')
                for item in ignorelist:
                    procopts.append('-ignore=' + item)

                print('Running (in ' + destlibdir + '): ' + ' '.join(procopts))
                pproc = subprocess.run(procopts,
			stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, cwd = destlibdir,
			universal_newlines = True)
                if pproc.stdout:
                    for line in pproc.stdout.splitlines():
                        print(line)
                if pproc.stderr:
                    print('Error message output from cdl2spi.py:')
                    for line in pproc.stderr.splitlines():
                        print(line)

    elif have_gds and not no_gds_convert:
        # If neither SPICE nor CDL formats is available in the source, then
        # read GDS;  if the result has no ports, then read the corresponding
        # LEF library to get port information.  Then write out a SPICE netlist
        # for the whole library.  NOTE:  If there is no CDL or SPICE source,
        # then the port numbering is arbitrary, and becomes whatever the
        # output of this script makes it.

        if ef_format:
            destdir = targetdir + cdl_reflib + 'spi'
            srcdir = targetdir + gds_reflib + 'gds'
            lefdir = targetdir + lef_reflib + 'lef'
            os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]

            if ef_format:
                destlibdir = destdir + '/' + destlib
                srclibdir = srcdir + '/' + destlib
                leflibdir = lefdir + '/' + destlib
            else:
                destdir = targetdir + cdl_reflib + destlib + '/spice'
                srcdir = targetdir + gds_reflib + destlib + '/gds'
                lefdir = targetdir + lef_reflib + destlib + '/lef'

                destlibdir = destdir
                srclibdir = srcdir
                leflibdir = lefdir

            os.makedirs(destlibdir, exist_ok=True)

            # Link to the PDK magic startup file from the target directory
            startup_script = targetdir + mag_current + pdkname + '-F.magicrc'
            if not os.path.isfile(startup_script):
                startup_script = targetdir + mag_current + pdkname + '.magicrc'
            if os.path.isfile(startup_script):
                # If the symbolic link exists, remove it.
                if os.path.isfile(destlibdir + '/.magicrc'):
                    os.remove(destlibdir + '/.magicrc')
                os.symlink(startup_script, destlibdir + '/.magicrc')

            # Get the consolidated GDS library file, or a list of all GDS files
            # if there is no single consolidated library

            allgdslibname = srclibdir + '/' + destlib + '.gds'
            if not os.path.isfile(allgdslibname):
                glist = glob.glob(srclibdir + '/*.gds')
                glist.extend(glob.glob(srclibdir + '/*.gdsii'))
                glist.extend(glob.glob(srclibdir + '/*.gds2'))

            allleflibname = leflibdir + '/' + destlib + '.lef'
            if not os.path.isfile(allleflibname):
                llist = glob.glob(leflibdir + '/*.lef')

            print('Creating magic generation script to generate SPICE library.') 
            with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
                print('#!/usr/bin/env wish', file=ofile)
                print('#---------------------------------------------', file=ofile)
                print('# Script to generate SPICE library from GDS   ', file=ofile)
                print('#---------------------------------------------', file=ofile)
                print('drc off', file=ofile)
                print('gds readonly true', file=ofile)
                print('gds flatten true', file=ofile)
                print('gds rescale false', file=ofile)
                print('tech unlock *', file=ofile)

                if not os.path.isfile(allgdslibname):
                    for gdsfile in glist:
                        print('gds read ' + gdsfile, file=ofile)
                else:
                    print('gds read ' + allgdslibname, file=ofile)

                if not os.path.isfile(allleflibname):
                    # Annotate the cells with information from the LEF files
                    for leffile in llist:
                        print('lef read ' + leffile, file=ofile)
                else:
                    print('lef read ' + allleflibname, file=ofile)

                # Load first file and remove the (UNNAMED) cell
                if not os.path.isfile(allgdslibname):
                    print('load ' + os.path.splitext(glist[0])[0], file=ofile)
                else:
                    gdslibroot = os.path.split(allgdslibname)[1]
                    print('load ' + os.path.splitext(gdslibroot)[0], file=ofile)
                print('cellname delete \(UNNAMED\)', file=ofile)

                print('ext2spice lvs', file=ofile)

                # NOTE:  Leaving "subcircuit top" as "auto" (default) can cause
                # cells like decap that have no I/O to be output without a subcircuit
                # wrapper.  Also note that if this happens, it is an indication that
                # power supplies have not been labeled as ports, which is harder to
                # handle and should be fixed in the source.
                print('ext2spice subcircuit top on', file=ofile)

                print('ext2spice cthresh 0.1', file=ofile)

                if os.path.isfile(allgdslibname):
                    print('select top cell', file=ofile)
                    print('set glist [cellname list children]', file=ofile)
                    print('foreach cell $glist {', file=ofile)
                else:
                    print('foreach cell [cellname list top] {', file=ofile)

                print('    load $cell', file=ofile)
                print('    puts stdout "Extracting cell $cell"', file=ofile)
                print('    extract all', file=ofile)
                print('    ext2spice', file=ofile)
                print('}', file=ofile)
                print('puts stdout "Done."', file=ofile)
                print('quit -noprompt', file=ofile)

            # Run magic to read in the individual GDS files and
            # write out the consolidated GDS library

            print('Running magic to create GDS library.')
            sys.stdout.flush()

            mproc = subprocess.run(['magic', '-dnull', '-noconsole',
				destlibdir + '/generate_magic.tcl'],
				stdin = subprocess.DEVNULL,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE, cwd = destlibdir,
				universal_newlines = True)
            if mproc.stdout:
                for line in mproc.stdout.splitlines():
                    print(line)
            if mproc.stderr:
                print('Error message output from magic:')
                for line in mproc.stderr.splitlines():
                    print(line)
            if mproc.returncode != 0:
                print('ERROR:  Magic exited with status ' + str(mproc.returncode))

            # Remove intermediate extraction files
            extfiles = glob.glob(destlibdir + '/*.ext')
            for extfile in extfiles:
                os.remove(extfile)

            # If the GDS file was a consolidated file of all cells, then
            # create a similar SPICE library of all cells.

            if os.path.isfile(allgdslibname):
                spiext = '.spice' if not ef_format else '.spi'
                create_spice_library(destlibdir, destlib, spiext, do_compile_only, do_stub, excludelist)

    sys.exit(0)
