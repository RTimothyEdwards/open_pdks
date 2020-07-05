#!/usr/bin/env python3
#
# foundry_install.py
#
# This file generates the local directory structure and populates the
# directories with foundry vendor data.
#
# Options:
#    -link_from <type>	Make symbolic links to vendor files from target
#			Types are: "none", "source", or a PDK name.
#			Default "none" (copy all files from source)
#    -ef_names		Use efabless naming (libs.ref/techLEF),
#			otherwise use generic naming (libs.tech/lef)
#
#    -source <path>	Path to source data top level directory
#    -target <path>	Path to target top level directory
#
#
# All other options represent paths to vendor files.  They may all be
# wildcarded with "*" to represent, e.g., version number directories,
# or names of supported libraries.  Where wildcards exist, if there is
# more than one directory in the path, the value represented by "*"
# will first be checked against library names.  If no library name is
# found, then the wildcard value will be assumed to be numeric and
# separated by either "." or "_" to represent major/minor/sub/...
# revision numbers (alphanumeric).
#
# Note only one of "-spice" or "-cdl" need be specified.  Since the
# open source tools use ngspice, CDL files are converted to ngspice
# syntax when needed.
#
#	-techlef <path>	Path to technology LEF file
#	-doc <path>	Path to technology documentation
#	-lef <path>	Path to LEF file
#	-lefanno <path>	Path to LEF file (for annotation only)
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
# All options "-lef", "-spice", etc., can take the additional arguments
# 	up  <number>
#
# to indicate that the source hierarchy should be copied from <number>
# levels above the files.  For example, if liberty files are kept in
# multiple directories according to voltage level, then
#
# 	-liberty x/y/z/PVT_*/*.lib
#
# would install all .lib files directly into libs.ref/lef/<libname>/*.lib
# while
#
# 	-liberty x/y/z/PVT_*/*.lib up 1
#
# would install all .lib files into libs.ref/lef/PVT_*/<libname>/*.lib
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
import shutil
import subprocess

def usage():
    print("foundry_install.py [options...]")
    print("   -link_from <name> Make symbolic links from target to <name>")
    print("                     where <name> can be 'source' or a PDK name.")
    print("                     Default behavior is to copy all files.")
    print("   -copy             Copy files from source to target (default)")
    print("   -ef_names         Use efabless naming conventions for local directories")
    print("")
    print("   -source <path>    Path to top of source directory tree")
    print("   -target <path>    Path to top of target directory tree")
    print("")
    print("   -techlef <path>   Path to technology LEF file")
    print("   -doc <path>       Path to technology documentation")
    print("   -lef <path>       Path to LEF file")
    print("   -lefanno <path>   Path to LEF file (for annotation only)")
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

# Read subcircuit ports from a CDL file, given a subcircuit name that should
# appear in the file as a subcircuit entry, and return a dictionary of ports
# and their indexes in the subcircuit line.

def get_subckt_ports(cdlfile, subname):
    portdict = {}
    pidx = 1
    portrex = re.compile('^\.subckt[ \t]+([^ \t]+)[ \t]+(.*)$', re.IGNORECASE)
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

# Filter a verilog file to remove any backslash continuation lines, which
# iverilog does not parse.  If targetroot is a directory, then find and
# process all files in the path of targetroot.  If any file to be processed
# is unmodified (has no backslash continuation lines), then ignore it.  If
# any file is a symbolic link and gets modified, then remove the symbolic
# link before overwriting with the modified file.
#
# If 'do_remove_spec' is True, then remove timing information from the file,
# which is everything between the keywords "specify" and "endspecify".

def vfilefilter(vfile, do_remove_spec):
    modified = False
    with open(vfile, 'r') as ifile:
        vtext = ifile.read()

    # Remove backslash-followed-by-newline and absorb initial whitespace.  It
    # is unclear what initial whitespace means in this context, as the use-
    # case that has been seen seems to work under the assumption that leading
    # whitespace is ignored up to the amount used by the last indentation.

    vlines = re.sub('\\\\\n[ \t]*', '', vtext)

    if do_remove_spec:
        specrex = re.compile('\n[ \t]*specify[ \t\n]+')
        endspecrex = re.compile('\n[ \t]*endspecify')
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
        if os.path.islink(vfile):
            os.unlink(vfile)
        with open(vfile, 'w') as ofile:
            ofile.write(vlines)

# Run a filter on verilog files that cleans up known syntax issues.
# This is embedded in the foundry_install script and is not a custom
# filter largely because the issues are in the tool, not the PDK.

def vfilter(targetroot, do_remove_spec):
    if os.path.isfile(targetroot):
        vfilefilter(targetroot, do_remove_spec)
    else:
        vlist = glob.glob(targetroot + '/*')
        for vfile in vlist:
            if os.path.isfile(vfile):
                vfilefilter(vfile, do_remove_spec)

# For issues that are PDK-specific, a script can be written and put in
# the PDK's custom/scripts/ directory, and passed to the foundry_install
# script using the "filter" option.

def tfilter(targetroot, filterscript):
    if os.path.isfile(targetroot):
        print('   Filtering file ' + targetroot)
        subprocess.run([filterscript, targetroot, targetroot],
			stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, universal_newlines = True)
    else:
        tlist = glob.glob(targetroot + '/*')
        for tfile in tlist:
            if os.path.isfile(tfile):
                print('   Filtering file ' + tfile)
                subprocess.run([filterscript, tfile, tfile],
			stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, universal_newlines = True)

# This is the main entry point for the foundry install script.

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("No options given to foundry_install.py.")
        usage()
        sys.exit(0)
    
    optionlist = []
    newopt = []

    sourcedir = None
    targetdir = None
    link_from = None

    ef_names = False

    have_lef = False
    have_lefanno = False
    have_gds = False
    have_spice = False
    have_cdl = False
    ignorelist = []

    do_install = True

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

    # Check for option "ef_names" or "std_names"
    for option in optionlist[:]:
        if option[0] == 'ef_naming' or option[0] == 'ef_names':
            optionlist.remove(option)
            ef_names = True
        elif option[0] == 'std_naming' or option[0] == 'std_names':
            optionlist.remove(option)
            ef_names = False
        elif option[0] == 'uninstall':
            optionlist.remove(option)
            do_install = False

    # Check for options "link_from", "source", and "target"
    link_name = None
    for option in optionlist[:]:
        if option[0] == 'link_from':
            optionlist.remove(option)
            if option[1].lower() == 'none':
                link_from = None
            elif option[1].lower() == 'source':
                link_from = 'source'
            else:
                link_from = option[1]
                link_name = os.path.split(link_from)[1]
        elif option[0] == 'source':
            optionlist.remove(option)
            sourcedir = option[1]
        elif option[0] == 'target':
            optionlist.remove(option)
            targetdir = option[1]

    # Error if no source or dest specified
    if not sourcedir:
        print("No source directory specified.  Exiting.")
        sys.exit(1)

    if not targetdir:
        print("No target directory specified.  Exiting.")
        sys.exit(1)

    # If link source is a PDK name, if it has no path, then pull the
    # path from the target name.

    if link_from:
        if link_from != 'source':
            if link_from.find('/', 0) < 0:
                target_root = os.path.split(targetdir)[0]
                link_from = target_root + '/' + link_from
                link_name = link_from
        else:
            # If linking from source, convert the source path to an
            # absolute pathname.
            sourcedir = os.path.abspath(sourcedir)

    # Take the target PDK name from the target path last component
    pdkname = os.path.split(targetdir)[1]

    # checkdir is the DIST target directory for the PDK pointed
    # to by link_name.  Files must be found there before creating
    # symbolic links to the (not yet existing) final install location.

    if link_name:
        checkdir = os.path.split(targetdir)[0] + '/' + link_name
    else:
        checkdir = ''

    # Diagnostic
    if do_install:
        print("Installing in target directory " + targetdir)

    # Create the top-level directories

    os.makedirs(targetdir, exist_ok=True)
    os.makedirs(targetdir + '/libs.ref', exist_ok=True)
    os.makedirs(targetdir + '/libs.tech', exist_ok=True)

    # Path to magic techfile depends on ef_names

    if ef_names == True:
        mag_current = '/libs.tech/magic/current/'
    else:
        mag_current = '/libs.tech/magic/'

    # Populate the techLEF and SPICE models, if specified.

    for option in optionlist[:]:
        if option[0] == 'techlef':
            filter_script = None
            for item in option:
                if item.split('=')[0] == 'filter':
                    filter_script = item.split('=')[1]
                    break

            if ef_names == True:
                techlefdir = targetdir + '/libs.ref/techLEF'
                checklefdir = checkdir + '/libs.ref/techLEF'
                if link_from:
                    linklefdir = link_from + '/libs.ref/techLEF'
                else:
                    linklefdir = ''
            else:
                techlefdir = targetdir + '/libs.tech/lef'
                checklefdir = checkdir + '/libs.tech/lef'
                if link_from:
                    linklefdir = link_from + '/libs.tech/lef'
                else:
                    linklefdir = ''
            os.makedirs(techlefdir, exist_ok=True)
            # All techlef files should be linked or copied, so use "glob"
            # on the wildcards
            techlist = glob.glob(sourcedir + '/' + option[1])

            for lefname in techlist:
                leffile = os.path.split(lefname)[1]
                targname = techlefdir + '/' + leffile
                checklefname = checklefdir + '/' + leffile
                linklefname = linklefdir + '/' + leffile
                # Remove any existing file(s)
                if os.path.isfile(targname):
                    os.remove(targname)
                elif os.path.islink(targname):
                    os.unlink(targname)
                elif os.path.isdir(targname):
                    shutil.rmtree(targname)

                if do_install:
                    if not link_from:
                        if os.path.isfile(lefname):
                            shutil.copy(lefname, targname)
                        else:
                            shutil.copytree(lefname, targname)
                    elif link_from == 'source':
                        os.symlink(lefname, targname)
                    else:
                        if os.path.exists(checklefname):
                            os.symlink(linklefname, targname)
                        elif os.path.isfile(lefname):
                            shutil.copy(lefname, targname)
                        else:
                            shutil.copytree(lefname, targname)

                    if filter_script:
                        # Apply filter script to all files in the target directory
                        tfilter(targname, filter_script)
            optionlist.remove(option)

        elif option[0] == 'models':
            filter_script = None
            for item in option:
                if item.split('=')[0] == 'filter':
                    filter_script = item.split('=')[1]
                    break

            print('Diagnostic:  installing models.')
            modelsdir = targetdir + '/libs.tech/models'
            checkmoddir = checkdir + '/libs.tech/models'
            if link_from:
                linkmoddir = link_from + '/libs.tech/models'
            else:
                linkmoddir = ''

            os.makedirs(modelsdir, exist_ok=True)

            # All model files should be linked or copied, so use "glob"
            # on the wildcards.  Copy each file and recursively copy each
            # directory.
            modellist = glob.glob(sourcedir + '/' + option[1])

            for modname in modellist:
                modfile = os.path.split(modname)[1]
                targname = modelsdir + '/' + modfile
                checkmodname = checkmoddir + '/' + modfile
                linkmodname = linkmoddir + '/' + modfile

                if os.path.isdir(modname):
                    # Remove any existing directory, and its contents
                    if os.path.isdir(targname):
                        shutil.rmtree(targname)
                    os.makedirs(targname)

                    # Recursively find and copy or link the whole directory
                    # tree from this point.

                    allmodlist = glob.glob(modname + '/**', recursive=True)
                    commonpart = os.path.commonpath(allmodlist)
                    for submodname in allmodlist:
                        if os.path.isdir(submodname):
                            continue
                        # Get the path part that is not common between modlist and
                        # allmodlist.
                        subpart = os.path.relpath(submodname, commonpart)
                        subtargname = targname + '/' + subpart
                        os.makedirs(os.path.split(subtargname)[0], exist_ok=True)
                        if do_install:
                            if not link_from:
                                if os.path.isfile(submodname):
                                    shutil.copy(submodname, subtargname)
                                else:
                                    shutil.copytree(submodname, subtargname)
                            elif link_from == 'source':
                                os.symlink(submodname, subtargname)
                            else:
                                if os.path.exists(checkmodname):
                                    os.symlink(linkmodname, subtargname)
                                elif os.path.isfile(submodname):
                                    shutil.copy(submodname, subtargname)
                                else:
                                    shutil.copytree(submodname, subtargname)
                        
                            if filter_script:
                                # Apply filter script to all files in the target directory
                                tfilter(targname, filter_script)

                else:
                    # Remove any existing file
                    if os.path.isfile(targname):
                        os.remove(targname)
                    elif os.path.islink(targname):
                        os.unlink(targname)
                    elif os.path.isdir(targname):
                        shutil.rmtree(targname)

                    if do_install:
                        if not link_from:
                            if os.path.isfile(modname):
                                shutil.copy(modname, targname)
                            else:
                                shutil.copytree(modname, targname)
                        elif link_from == 'source':
                            os.symlink(modname, targname)
                        else:
                            if os.path.isfile(checkmodname):
                                os.symlink(linkmodname, targname)
                            elif os.path.isfile(modname):
                                shutil.copy(modname, targname)
                            else:
                                shutil.copytree(modname, targname)

                        if filter_script:
                            # Apply filter script to all files in the target directory
                            tfilter(targname, filter_script)

            optionlist.remove(option)

    # The remaining options in optionlist should all be types like 'lef' or 'liberty'
    for option in optionlist[:]:
        # Diagnostic
        if do_install:
            print("Installing option: " + str(option[0]))
        destdir = targetdir + '/libs.ref/' + option[0]
        checklibdir = checkdir + '/libs.ref/' + option[0]
        if link_from:
            destlinkdir = link_from + '/libs.ref/' + option[0]
        else:
            destlinkdir = ''
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

        filter_script = None
        for item in option:
            if item.split('=')[0] == 'filter':
                filter_script = item.split('=')[1]
                break

        # Option 'compile' is a standalone keyword ('comp' may be used).
        do_compile = 'compile' in option or 'comp' in option
 
        # Option 'nospecify' is a standalone keyword ('nospec' may be used).
        do_remove_spec = 'nospecify' in option or 'nospec' in option

        # Check off things we need to do migration to magic database and
        # abstact files.
        if option[0] == 'lef':
            have_lef = True
        elif option[0] == 'gds':
            have_gds = True
        elif option[0] == 'lefanno':
            have_lefanno = True
        elif option[0] == 'spice':
            have_spice = True
        elif option[0] == 'cdl':
            have_cdl = True

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]
            destlibdir = destdir + '/' + destlib
            destlinklibdir = destlinkdir + '/' + destlib
            checksrclibdir = checklibdir + '/' + destlib
            os.makedirs(destlibdir, exist_ok=True)

            # Populate the library subdirectory
            # Parse the option and replace each '/*/' with the library name,
            # and check if it is a valid directory name.  Then glob the
            # resulting option name.  Warning:  This assumes that all
            # occurences of the text '/*/' match a library name.  It should
            # be possible to wild-card the directory name in such a way that
            # this is always true.

            testopt = re.sub('\/\*\/', '/' + library[1] + '/', option[1])

            liblist = glob.glob(sourcedir + '/' + testopt)

            # Diagnostic
            print('Collecting files from ' + str(sourcedir + '/' + testopt))
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

                targname = destlibdir + destpath + '/' + libfile

                # NOTE:  When using "up" with link_from, could just make
                # destpath itself a symbolic link;  this way is more flexible
                # but adds one symbolic link per file.

                if destpath != '':
                    if not os.path.isdir(destlibdir + destpath):
                        os.makedirs(destlibdir + destpath, exist_ok=True)

                # Both linklibname and checklibname need to contain any hierarchy
                # implied by the "up" option.

                linklibname = destlinklibdir + destpath + '/' + libfile
                checklibname = checksrclibdir + destpath + '/' + libfile

                # Remove any existing file
                if os.path.isfile(targname):
                    os.remove(targname)
                elif os.path.islink(targname):
                    os.unlink(targname)
                elif os.path.isdir(targname):
                    shutil.rmtree(targname)

                if do_install:
                    if not link_from:
                        if os.path.isfile(libname):
                            shutil.copy(libname, targname)
                        else:
                            shutil.copytree(libname, targname)
                    elif link_from == 'source':
                        os.symlink(libname, targname)
                    else:
                        if os.path.exists(checklibname):
                            os.symlink(linklibname, targname)
                        elif os.path.isfile(libname):
                            shutil.copy(libname, targname)
                        else:
                            shutil.copytree(libname, targname)

                    if option[0] == 'verilog':
                        # Special handling of verilog files to make them
                        # syntactically acceptable to iverilog.
                        # NOTE:  Perhaps this should be recast as a custom filter?
                        vfilter(targname, do_remove_spec)

                    if filter_script:
                        # Apply filter script to all files in the target directory
                        tfilter(targname, filter_script)

            if do_compile == True:
                # To do:  Extend this option to include formats other than verilog.
                # Also to do:  Make this compatible with linking from another PDK.

                if option[0] == 'verilog':
                    # If there is not a single file with all verilog cells in it,
                    # then compile one, because one does not want to have to have
                    # an include line for every single cell used in a design.

                    alllibname = destlibdir + '/' + destlib + '.v'

                    print('Diagnostic:  Creating consolidated verilog library ' + destlib + '.v')
                    vlist = glob.glob(destlibdir + '/*.v')
                    if alllibname in vlist:
                        vlist.remove(alllibname)

                    if len(vlist) > 1:
                        print('New file is:  ' + alllibname)
                        with open(alllibname, 'w') as ofile:
                            for vfile in vlist:
                                with open(vfile, 'r') as ifile:
                                    # print('Adding ' + vfile + ' to library.')
                                    vtext = ifile.read()
                                    # NOTE:  The following workaround resolves an
                                    # issue with iverilog, which does not properly
                                    # parse specify timing paths that are not in
                                    # parentheses.  Easy to work around
                                    vlines = re.sub(r'\)[ \t]*=[ \t]*([01]:[01]:[01])[ \t]*;', r') = ( \1 ) ;', vtext)
                                    print(vlines, file=ofile)
                                print('\n//--------EOF---------\n', file=ofile)
                    else:
                        print('Only one file (' + str(vlist) + ');  ignoring "compile" option.')

    print("Completed installation of vendor files.")

    # Now for the harder part.  If GDS and/or LEF databases were specified,
    # then migrate them to magic (.mag files in layout/ or abstract/).

    ignore = []
    do_cdl_scaleu = False
    for option in optionlist[:]:
        if option[0] == 'cdl':
            # Option 'scaleu' is a standalone keyword
            do_cdl_scaleu = 'scaleu' in option

            # Option 'ignore' has arguments after '='
            for item in option:
                if item.split('=')[0] == 'ignore':
                    ignorelist = item.split('=')[1].split(',')
 
    devlist = []
    pdklibrary = None

    if have_gds:
        print("Migrating GDS files to layout.")
        destdir = targetdir + '/libs.ref/mag'
        srcdir = targetdir + '/libs.ref/gds'
        os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]
            destlibdir = destdir + '/' + destlib
            srclibdir = srcdir + '/' + destlib
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

            if os.path.isfile(startup_script):
                # If the symbolic link exists, remove it.
                if os.path.isfile(destlibdir + '/.magicrc'):
                    os.remove(destlibdir + '/.magicrc')
                os.symlink(startup_script, destlibdir + '/.magicrc')
 
                # Find GDS file names in the source
                print('Getting GDS file list from ' + srclibdir + '.')
                gdsfiles = os.listdir(srclibdir)

                # Generate a script called "generate_magic.tcl" and leave it in
                # the target directory.  Use it as input to magic to create the
                # .mag files from the database.

                print('Creating magic generation script.') 
                with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
                    print('#!/usr/bin/env wish', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('# Script to generate .mag files from .gds    ', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('gds readonly true', file=ofile)
                    print('gds flatten true', file=ofile)
                    # print('gds rescale false', file=ofile)
                    print('tech unlock *', file=ofile)

                    for gdsfile in gdsfiles:
                        # Note:  DO NOT use a relative path here.
                        # print('gds read ../../gds/' + destlib + '/' + gdsfile, file=ofile)
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

                    print('writeall force', file=ofile)

                    if have_lefanno:
                        # Find LEF file names in the source
                        lefsrcdir = targetdir + '/libs.ref/lefanno'
                        lefsrclibdir = lefsrcdir + '/' + destlib
                        leffiles = list(item for item in os.listdir(lefsrclibdir) if os.path.splitext(item)[1] == '.lef')

                    if not have_lef:
                        # This library has a GDS database but no LEF database.  Use
                        # magic to create abstract views of the GDS cells.  If
                        # option "-lefanno" is given, then read the LEF file after
                        # loading the database file to annotate the cell with
                        # information from the LEF file.  This usually indicates
                        # that the LEF file has some weird definition of obstruction
                        # layers and we want to normalize them by using magic's LEF
                        # write procedure, but we still need the pin use and class
                        # information from the LEF file, and maybe the bounding box.

                        print('set maglist [glob *.mag]', file=ofile)
                        print('foreach name $maglist {', file=ofile)
                        print('   load [file root $name]', file=ofile)
                        if have_lefanno:
                            print('}', file=ofile)
                            for leffile in leffiles:
                                print('lef read ' + lefsrclibdir + '/' + leffile, file=ofile)
                            print('foreach name $maglist {', file=ofile)
                            print('   load [file root $name]', file=ofile)
                        print('   lef write [file root $name]', file=ofile)
                        print('}', file=ofile)
                    print('quit -noprompt', file=ofile)

                # Run magic to read in the GDS file and write out magic databases.
                with open(destlibdir + '/generate_magic.tcl', 'r') as ifile:
                    subprocess.run(['magic', '-dnull', '-noconsole'],
				stdin = ifile, stdout = subprocess.PIPE,
				stderr = subprocess.PIPE, cwd = destlibdir,
				universal_newlines = True)

                if not have_lef:
                    # Remove the lefanno/ target and its contents.
                    if have_lefanno:
                        lefannosrcdir = targetdir + '/libs.ref/lefanno'
                        if os.path.isdir(lefannosrcdir):
                            shutil.rmtree(lefannosrcdir)

                    destlefdir = targetdir + '/libs.ref/lef'
                    destleflibdir = destlefdir + '/' + destlib
                    os.makedirs(destleflibdir, exist_ok=True)
                    leflist = list(item for item in os.listdir(destlibdir) if os.path.splitext(item)[1] == '.lef')

                    # All macros will go into one file
                    destleflib = destleflibdir + '/' + destlib + '.lef'
                    # Remove any existing library file from the target directory
                    if os.path.isfile(destleflib):
                        os.remove(destleflib)

                    first = True
                    with open(destleflib, 'w') as ofile:
                        for leffile in leflist:
                            # Remove any existing single file from the target directory
                            if os.path.isfile(destleflibdir + '/' + leffile):
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
                            os.remove(sourcelef)

                    have_lef = True

                # Remove the startup script and generation script
                os.remove(destlibdir + '/.magicrc')
                os.remove(destlibdir + '/generate_magic.tcl')
            else:
                print("Master PDK magic startup file not found.  Did you install")
                print("PDK tech files before PDK vendor files?")

    if have_lef:
        print("Migrating LEF files to layout.")
        destdir = targetdir + '/libs.ref/maglef'
        srcdir = targetdir + '/libs.ref/lef'
        magdir = targetdir + '/libs.ref/mag'
        cdldir = targetdir + '/libs.ref/cdl'
        os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]
            destlibdir = destdir + '/' + destlib
            srclibdir = srcdir + '/' + destlib
            maglibdir = magdir + '/' + destlib
            cdllibdir = cdldir + '/' + destlib
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
 
                # Find LEF file names in the source
                leffiles = os.listdir(srclibdir)

                # Generate a script called "generate_magic.tcl" and leave it in
                # the target directory.  Use it as input to magic to create the
                # .mag files from the database.

                with open(destlibdir + '/generate_magic.tcl', 'w') as ofile:
                    print('#!/usr/bin/env wish', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('# Script to generate .mag files from .lef    ', file=ofile)
                    print('#--------------------------------------------', file=ofile)
                    print('tech unlock *', file=ofile)

                    if pdklibrary:
                        tcldevlist = '{' + ' '.join(devlist) + '}'
                        print('set devlist ' + tcldevlist, file=ofile)

                    for leffile in leffiles:

                        # Okay to use a relative path here.
                        # print('lef read ' + srclibdir + '/' + leffile', file=ofile)
                        print('lef read ../../lef/' + destlib + '/' + leffile, file=ofile)

                        # To be completed:  Parse SPICE file for port order, make
                        # sure ports are present and ordered.

                        if pdklibrary:
                            print('set cellname [file root ' + leffile + ']', file=ofile)
                            print('if {[lsearch $devlist $cellname] >= 0} {',
					file=ofile)
                            print('    load $cellname', file=ofile)
                            print('    property gencell $cellname', file=ofile)
                            print('    property parameter m=1', file=ofile)
                            print('    property library ' + pdklibrary, file=ofile)
                            print('}', file=ofile)

                    print('writeall force', file=ofile)
                    print('quit -noprompt', file=ofile)

                # Run magic to read in the LEF file and write out magic databases.
                with open(destlibdir + '/generate_magic.tcl', 'r') as ifile:
                    subprocess.run(['magic', '-dnull', '-noconsole'],
				stdin = ifile, stdout = subprocess.PIPE,
				stderr = subprocess.PIPE, cwd = destlibdir,
				universal_newlines = True)

                # Now list all the .mag files generated, and for each, read the
                # corresponding file from the mag/ directory, pull the GDS file
                # properties, and add those properties to the maglef view.  Also
                # read the CDL (or SPICE) netlist, read the ports, and rewrite
                # the port order in the mag and maglef file accordingly.

                # Diagnostic
                print('Annotating files in ' + destlibdir)
                magfiles = os.listdir(destlibdir)
                for magroot in magfiles:
                    magname = os.path.splitext(magroot)[0]
                    magfile = maglibdir + '/' + magroot
                    magleffile = destlibdir + '/' + magroot
                    prop_lines = get_gds_properties(magfile)

                    # Make sure properties include the Tcl generated cell
                    # information from the PDK script

                    if pdklibrary:
                        if magname in fixedlist:
                            prop_lines.append('string gencell ' + magname)
                            prop_lines.append('string library ' + pdklibrary)
                            prop_lines.append('string parameter m=1')

                    cdlfile = cdllibdir + '/' + magname + '.cdl'
                    if not os.path.exists(cdlfile):
                        # Assume there is one file with all cell subcircuits in it.
                        try:
                            cdlfile = glob.glob(cdllibdir + '/*.cdl')[0]
                        except:
                            print('No CDL file for ' + destlib + ' device ' + magname)
                            cdlfile = None
                            # To be done:  If destlib is 'primitive', then look in
                            # SPICE models for port order.
                            if destlib == 'primitive':
                                print('Fix me:  Need to look in SPICE models!')
                    if cdlfile:
                        port_dict = get_subckt_ports(cdlfile, magname)
                    else:
                        port_dict = {}

                    proprex = re.compile('<< properties >>')
                    endrex = re.compile('<< end >>')
                    rlabrex = re.compile('rlabel[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+([^ \t]+)')
                    flabrex = re.compile('flabel[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+([^ \t]+)')
                    portrex = re.compile('port[ \t]+([^ \t])+[ \t]+(.*)')
                    portnum = -1

                    with open(magleffile, 'r') as ifile:
                        magtext = ifile.read().splitlines()

                    with open(magleffile, 'w') as ofile:
                        for line in magtext:
                            tmatch = portrex.match(line)
                            if tmatch:
                                if portnum >= 0:
                                    line = 'port ' + str(portnum) + ' ' + tmatch.group(2)
                                else:
                                    line = 'port ' + tmatch.group(1) + ' ' + tmatch.group(2)
                            ematch = endrex.match(line)
                            if ematch and len(prop_lines) > 0:
                                print('<< properties >>', file=ofile)
                                for prop in prop_lines:
                                    print('string ' + prop, file=ofile)

                            print(line, file=ofile)
                            pmatch = proprex.match(line)
                            if pmatch:
                                for prop in prop_lines:
                                    print('string ' + prop, file=ofile)
                                prop_lines = []

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
                        # NOTE:  Probably this means the GDS cell has a different name.
                        print('Error: No file ' + magfile + '.  Why is it in maglef???')

                # Remove the startup script and generation script
                os.remove(destlibdir + '/.magicrc')
                os.remove(destlibdir + '/generate_magic.tcl')
            else:
                print("Master PDK magic startup file not found.  Did you install")
                print("PDK tech files before PDK vendor files?")

    # If SPICE or CDL databases were specified, then convert them to
    # a form that can be used by ngspice, using the cdl2spi.py script 

    if have_spice:
        if not os.path.isdir(targetdir + '/libs.ref/spi'):
            os.makedirs(targetdir + '/libs.ref/spi', exist_ok=True)

    elif have_cdl:
        if not os.path.isdir(targetdir + '/libs.ref/spi'):
            os.makedirs(targetdir + '/libs.ref/spi', exist_ok=True)

        print("Migrating CDL netlists to SPICE.")
        destdir = targetdir + '/libs.ref/spi'
        srcdir = targetdir + '/libs.ref/cdl'
        os.makedirs(destdir, exist_ok=True)

        # For each library, create the library subdirectory
        for library in libraries:
            if len(library) == 3:
                destlib = library[2]
            else:
                destlib = library[1]
            destlibdir = destdir + '/' + destlib
            srclibdir = srcdir + '/' + destlib
            os.makedirs(destlibdir, exist_ok=True)

            # Find CDL file names in the source
            cdlfiles = os.listdir(srclibdir)

            # The directory with scripts should be in ../common with respect
            # to the Makefile that determines the cwd.
            scriptdir = os.path.split(os.getcwd())[0] + '/common/'

            # Run cdl2spi.py script to read in the CDL file and write out SPICE
            for cdlfile in cdlfiles:
                spiname = os.path.splitext(cdlfile)[0] + '.spi'
                procopts = [scriptdir + 'cdl2spi.py', srclibdir + '/' + cdlfile, destlibdir + '/' + spiname]
                if do_cdl_scaleu:
                    procopts.append('-dscale=u')
                for item in ignorelist:
                    procopts.append('-ignore=' + item)
                print('Running (in ' + destlibdir + '): ' + ' '.join(procopts))
                subprocess.run(procopts,
			stdin = subprocess.DEVNULL, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE, cwd = destlibdir,
			universal_newlines = True)

    sys.exit(0)
