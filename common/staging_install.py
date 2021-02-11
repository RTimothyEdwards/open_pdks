#!/usr/bin/env python3
#
# staging_install.py
#
# This file copies the staging area created by foundry_install.py
# into the target directory area, changing paths to match the target,
# and creating symbolic links where requested and allowed.
#
# Options:
#    -link_from <type>	Make symbolic links to vendor files from target
#			Types are: "none", "source", or a PDK name.
#			Default "none" (copy all files from source)
#    -ef_format		Use efabless naming (libs.ref/techLEF),
#			otherwise use generic naming (libs.tech/lef)
#
#    -staging <path>	Path to staging top level directory
#    -target <path>	Path to target top level directory
#    -local <path>	For distributed installs, this is the local
#			path to target top level directory.
#    -source <path>     Path to original source top level directory,
#                       if link_from is "source".  This option may
#                       be called multiple times if there are multiple
#                       sources.
#    -variable <name>	Specify a variable name that is used for the
#			target path.  This variable name must be enforced
#			in setup scripts like .magicrc

import re
import os
import sys
import glob
import stat
import shutil
import filecmp
import subprocess

# NOTE:  This version of copy_tree from distutils works like shutil.copytree()
# in Python 3.8 and up ONLY using "dirs_exist_ok=True".
from distutils.dir_util import copy_tree

def usage():
    print("staging_install.py [options...]")
    print("   -link_from <name> Make symbolic links from target to <name>")
    print("                     where <name> can be 'source' or a PDK name.")
    print("                     Default behavior is to copy all files.")
    print("   -copy             Copy files from source to target (default)")
    print("   -ef_format        Use efabless naming conventions for local directories")
    print("")
    print("   -staging <path>   Path to top of staging directory tree")
    print("   -target <path>    Path to top of target directory tree")
    print("   -local <path>	Local path to top of target directory tree for distributed install")
    print("")
    print(" If <target> is unspecified then <name> is used for the target.")

def makeuserwritable(filepath):
    if os.path.exists(filepath):
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IWUSR)

# Filter files to replace all strings matching "stagingdir" with "localdir" for
# every file in "tooldir".  If "tooldir" contains subdirectories, then recursively
# apply the replacement filter to all files in the subdirectories.  Do not follow
# symbolic links.

def filter_recursive(tooldir, stagingdir, localdir):
    # Add any non-ASCII file types here
    bintypes = ['.gds', '.gds2', '.gdsii', '.png']

    if not os.path.exists(tooldir):
        return 0
    elif os.path.islink(tooldir):
        return 0

    toolfiles = os.listdir(tooldir)
    total = 0

    # Add any non-ASCII 
    binexts = ['.png']

    for file in toolfiles:
        # Do not attempt to do text substitutions on a binary file!
        if os.path.splitext(file)[1] in bintypes:
            continue

        filepath = tooldir + '/' + file
        if os.path.islink(filepath):
            continue
        elif os.path.isdir(filepath):
            total += filter_recursive(filepath, stagingdir, localdir)
        else:
            with open(filepath, 'r') as ifile:
                try:
                    flines = ifile.read().splitlines()
                except UnicodeDecodeError:
                    print('Failure to read file ' + filepath + '; non-ASCII content.')
                    continue

            # Make sure this file is writable (as the original may not be)
            makeuserwritable(filepath)

            modified = False
            with open(filepath, 'w') as ofile:
                for line in flines:
                    newline = line.replace(stagingdir, localdir)
                    print(newline, file=ofile) 
                    if newline != line:
                        modified = True

            if modified:
                total += 1
    return total
        
# To avoid problems with various library functions that copy hierarchical
# directory trees, remove all the files from the target that are going to
# be replaced by the contents of staging.  This avoids problems with
# symbolic links and such.

def remove_target(stagingdir, targetdir):

    slist = os.listdir(stagingdir)
    tlist = os.listdir(targetdir)

    for sfile in slist:
        if sfile in tlist:
            tpath = targetdir + '/' + sfile
            if os.path.islink(tpath):
                os.unlink(tpath)
            elif os.path.isdir(tpath):
                remove_target(stagingdir + '/' + sfile, targetdir + '/' + sfile)
            else:
                os.remove(tpath)

# Create a list of source files/directories from the contents of source.txt

def make_source_list(sources):
    sourcelist = []
    for source in sources:
        sourcelist.extend(glob.glob(source))
    return sourcelist

# Replace all files in list "libfiles" with symbolic links to files in
# "sourcelist", where the files are found to be the same.  If the entry
# in "libfiles" is a directory and the same directory is found in "sourcelist",
# then repeat recursively on the subdirectory.
#
# Because the installation may be distributed, there may be a difference
# between where the files to be linked to currently are (checklist)
# and where they will eventually be located (sourcelist).

def replace_with_symlinks(libfiles, sourcelist):
    # List of files that never get installed
    exclude = ['generate_magic.tcl', '.magicrc', 'sources.txt']
    total = 0
    for libfile in libfiles:
        if os.path.islink(libfile):
            continue
        else:
            try:
                sourcefile = next(item for item in sourcelist if os.path.split(item)[1] == os.path.split(libfile)[1])
            except:
                pass
            else:
                if os.path.isdir(libfile):
                    newlibfiles = glob.glob(libfile + '/*')
                    newsourcelist = glob.glob(sourcefile + '/*')
                    total += replace_with_symlinks(newlibfiles, newsourcelist)
                elif filecmp.cmp(libfile, sourcefile):
                    if not os.path.split(libfile)[1] in exclude:
                        os.remove(libfile)
                        # Use absolute path for the source file
                        sourcepath = os.path.abspath(sourcefile)
                        os.symlink(sourcepath, libfile)
                        total += 1
    return total

# Similar to the routine above, replace files in "libdir" with symbolic
# links to the files in "srclibdir", where the files are found to be the
# same.  The difference from the routine above is that "srclibdir" is
# another installed PDK, and so the directory hierarchy is expected to
# match that of "libdir" exactly, so the process of finding matches is
# a bit more straightforward.
#
# Because the installation may be distributed, there may be a difference
# between where the files to be linked to currently are (checklibdir)
# and where they will eventually be located (srclibdir).

def replace_all_with_symlinks(libdir, srclibdir, checklibdir):
    total = 0
    try:
        libfiles = os.listdir(libdir)
    except FileNotFoundError:
        print('Cannot list directory ' + libdir)
        print('Called: replace_all_with_symlinks(' + libdir + ', ' + srclibdir + ', ' + checklibdir + ')')
        return total

    try:
        checkfiles = os.listdir(checklibdir)
    except FileNotFoundError:
        print('Cannot list check directory ' + checklibdir)
        print('Called: replace_all_with_symlinks(' + libdir + ', ' + srclibdir + ', ' + checklibdir + ')')
        return total

    for libfile in libfiles:
        if libfile in checkfiles:
            libpath = libdir + '/' + libfile
            checkpath = checklibdir + '/' + libfile
            srcpath = srclibdir + '/' + libfile

            if os.path.isdir(libpath):
                if os.path.isdir(checkpath):
                    total += replace_all_with_symlinks(libpath, srcpath, checkpath)
            else:
                try:
                    if filecmp.cmp(libpath, checkpath):
                        os.remove(libpath)
                        os.symlink(srcpath, libpath)
                        total += 1
                except FileNotFoundError:
                    print('Failed file compare with libpath=' + libpath + ', checkpath=' + checkpath)

    return total

#----------------------------------------------------------------
# This is the main entry point for the staging install script.
#----------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("No options given to staging_install.py.")
        usage()
        sys.exit(0)
    
    optionlist = []
    newopt = []

    stagingdir = None
    targetdir = None
    link_from = None
    localdir = None
    variable = None

    ef_format = False
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

    # Check for option "ef_format" or "std_format"
    for option in optionlist[:]:
        if option[0] == 'ef_naming' or option[0] == 'ef_names' or option[0] == 'ef_format':
            optionlist.remove(option)
            ef_format = True
        elif option[0] == 'std_naming' or option[0] == 'std_names' or option[0] == 'std_format':
            optionlist.remove(option)
            ef_format = False
        elif option[0] == 'uninstall':
            optionlist.remove(option)
            do_install = False

    # Check for options "link_from", "staging", "target", and "local"

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
        elif option[0] == 'staging' or option[0] == 'source':
            optionlist.remove(option)
            stagingdir = option[1]
        elif option[0] == 'target':
            optionlist.remove(option)
            targetdir = option[1]
        elif option[0] == 'local':
            optionlist.remove(option)
            localdir = option[1]
        elif option[0] == 'variable':
            optionlist.remove(option)
            variable = option[1]

    # Error if no staging or dest specified
    if not stagingdir:
        print("No staging directory specified.  Exiting.")
        sys.exit(1)

    if not targetdir:
        print("No target directory specified.  Exiting.")
        sys.exit(1)

    # If localdir is not specified, then it is the same as the parent
    # of the target (local installation assumed)
    if not localdir:
        localdir = targetdir

    # Take the target PDK name from the target path last component
    pdkname = os.path.split(targetdir)[1]

    # If link source is a PDK name, if it has no path, then pull the
    # path from the target name.

    if link_from:
        if link_from != 'source':
            if link_from.find('/', 0) < 0:
                link_name = link_from
                link_from = os.path.split(localdir)[0] + '/' + link_name
        else:
            # If linking from source, convert the source path to an
            # absolute pathname.
            stagingdir = os.path.abspath(stagingdir)

        # If link_from is the same as localdir, then set link_from to None
        if link_from == localdir:
            link_from = None

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
    else:
        print("Uninstalling from target directory " + targetdir)
        print("(Method not yet implemented)")

    # Create the top-level directories

    os.makedirs(targetdir, exist_ok=True)
    os.makedirs(targetdir + '/libs.tech', exist_ok=True)
    os.makedirs(targetdir + '/libs.ref', exist_ok=True)
    if os.path.isdir(stagingdir + '/libs.priv'):
        os.makedirs(targetdir + '/libs.priv', exist_ok=True)
        has_priv = True
    else:
        has_priv = False

    # Path to magic techfile depends on ef_format

    if ef_format == True:
        mag_current = '/libs.tech/magic/current/'
    else:
        mag_current = '/libs.tech/magic/'

    # First install everything by direct copy.  Keep the staging files
    # as they will be used to reference the target area to know which
    # files need to be checked and/or modified.

    if not os.path.isdir(targetdir):
        try:
            os.makedirs(targetdir, exist_ok=True)
        except:
            print('Fatal error:  Cannot make target directory ' + targetdir + '!')
            exit(1)

    # Remove any files from the target directory that are going to be replaced
    print('Removing files from target')
    remove_target(stagingdir, targetdir)

    print('Copying staging files to target')
    # print('Diagnostic:  copy_tree ' + stagingdir + ' ' + targetdir)
    copy_tree(stagingdir, targetdir, preserve_symlinks=True)
    print('Done.')

    # Magic and qflow setup files have references to the staging area that have
    # been used by the vendor install;  these need to be changed to the target
    # directory.

    print('Changing local path references from ' + stagingdir + ' to ' + localdir)
    print('Part 1:  Tools')

    needcheck = ['ngspice']
    techdirs = ['/libs.tech/']
    if has_priv:
        techdirs.append('/libs.priv/')

    for techdir in techdirs:
        tools = os.listdir(targetdir + techdir)
        for tool in tools:
            tooldir = targetdir + techdir + tool

            # There are few enough tool setup files that they can just all be
            # filtered directly.  This code only looks in the directory 'tooldir'.
            # If there are files is subdirectories of 'tooldir' that require
            # substitution, then this code needs to be revisited.

            # Note that due to the low overhead of tool setup files, there is
            # no attempt to check for possible symlinks to link_from if link_from
            # is a base PDK.

            total = filter_recursive(tooldir, stagingdir, localdir)
            if total > 0:
                substr = 'substitutions' if total > 1 else 'substitution'
                print('      ' + tool + ' (' + str(total) + ' ' + substr + ')')

    # If "link_from" is another PDK, then check all files against the files in
    # the other PDK, and replace the file with a symbolic link if the file contents
    # match (Note:  This is done only for ngspice model files;  other tool files are
    # generally small and deemed unnecessary to make symbolic links).

    if link_from not in ['source', None]:
        thispdk = os.path.split(targetdir)[1]

        # Only create links for PDKs other than the one we are making links to.
        if thispdk != link_from:
            print('Replacing files with symbolic links to ' + link_from + ' where possible.')
            for techdir in techdirs:
                for tool in needcheck:
                    tooldir = targetdir + techdir + tool
                    srctooldir = link_from + techdir + tool
                    if checkdir != '':
                        checktooldir = checkdir + techdir + tool
                    else:
                        checktooldir = srctooldir
                    if os.path.exists(tooldir):
                        total = replace_all_with_symlinks(tooldir, srctooldir, checktooldir)
                        if total > 0:
                            symstr = 'symlinks' if total > 1 else 'symlink'
                            print('      ' + tool + ' (' + str(total) + ' ' + symstr + ')')

    # In .mag files in mag/ and maglef/, also need to change the staging
    # directory name to localdir.  If "-variable" is specified in the options,
    # the replace the staging path with the variable name, not localdir.

    if variable:
        localname = '$' + variable
    else:
        localname = localdir

    needcheck = ['mag', 'maglef']
    refdirs = ['/libs.ref/']
    if has_priv:
        refdirs.append('/libs.priv/')

    if ef_format:
        print('Part 2:  Formats')
        for refdir in refdirs:
            for filetype in needcheck:
                print('   ' + filetype)
                filedir = targetdir + refdir + filetype
                if os.path.isdir(filedir):
                    libraries = os.listdir(filedir)
                    for library in libraries:
                        libdir = filedir + '/' + library
                        total = filter_recursive(libdir, stagingdir, localname)
                        if total > 0:
                            substr = 'substitutions' if total > 1 else 'substitution'
                            print('      ' + library + ' (' + str(total) + ' ' + substr + ')')
    else:
        print('Part 2:  Libraries')
        for refdir in refdirs:
            libraries = os.listdir(targetdir + refdir)
            for library in libraries:
                print('   ' + library)
                for filetype in needcheck:
                    filedir = targetdir + refdir + library + '/' + filetype
                    total = filter_recursive(filedir, stagingdir, localname)
                    if total > 0:
                        substr = 'substitutions' if total > 1 else 'substitution'
                        print('      ' + filetype + ' (' + str(total) + ' ' + substr + ')')
        
    # If "link_from" is "source", then check all files against the source
    # directory, and replace the file with a symbolic link if the file
    # contents match.  The "foundry_install.py" script should have added a
    # file "sources.txt" with the name of the source directories for each
    # install directory.

    if link_from not in ['source', None]:
        print('Replacing files with symbolic links to source where possible.')
        for refdir in refdirs:
            if ef_format:
                filedirs = os.listdir(targetdir + refdir)
                for filedir in filedirs:
                    print('   ' + filedir)
                    dirpath = targetdir + refdir + filedir
                    if os.path.isdir(dirpath):
                        libraries = os.listdir(dirpath)
                        for library in libraries:
                            libdir = targetdir + refdir + filedir + '/' + library
                            libfiles = os.listdir(libdir)
                            if 'sources.txt' in libfiles:
                                libfiles = glob.glob(libdir + '/*')
                                libfiles.remove(libdir + '/sources.txt')
                                with open(libdir + '/sources.txt') as ifile:
                                    sources = ifile.read().splitlines()
                                sourcelist = make_source_list(sources)
                                total = replace_with_symlinks(libfiles, sourcelist)
                                if total > 0:
                                    symstr = 'symlinks' if total > 1 else 'symlink'
                                    print('      ' + library + ' (' + str(total) + ' ' + symstr + ')')
            else:
                libraries = os.listdir(targetdir + refdir)
                for library in libraries:
                    print('   ' + library)
                    filedirs = os.listdir(targetdir + refdir + library)
                    for filedir in filedirs:
                        libdir = targetdir + refdir + library + '/' + filedir
                        if os.path.isdir(libdir):
                            libfiles = os.listdir(libdir)
                            if 'sources.txt' in libfiles:
                                # List again, but with full paths.
                                libfiles = glob.glob(libdir + '/*')
                                libfiles.remove(libdir + '/sources.txt')
                                with open(libdir + '/sources.txt') as ifile:
                                    sources = ifile.read().splitlines()
                                sourcelist = make_source_list(sources)
                                total = replace_with_symlinks(libfiles, sourcelist)
                                if total > 0:
                                    symstr = 'symlinks' if total > 1 else 'symlink'
                                    print('      ' + filedir + ' (' + str(total) + ' ' + symstr + ')')

    # Otherwise, if "link_from" is another PDK, then check all files against
    # the files in the other PDK, and replace the file with a symbolic link
    # if the file contents match.

    elif link_from:
        thispdk = os.path.split(targetdir)[1]

        # Only create links for PDKs other than the one we are making links to.
        if thispdk != link_from:

            print('Replacing files with symbolic links to ' + link_from + ' where possible.')

            for refdir in refdirs:
                if ef_format:
                    filedirs = os.listdir(targetdir + refdir)
                    for filedir in filedirs:
                        print('   ' + filedir)
                        dirpath = targetdir + refdir + filedir
                        if os.path.isdir(dirpath):
                            libraries = os.listdir(dirpath)
                            for library in libraries:
                                libdir = targetdir + refdir + filedir + '/' + library
                                srclibdir = link_from + refdir + filedir + '/' + library
                                if checkdir != '':
                                    checklibdir = checkdir + refdir + filedir + '/' + library
                                else:
                                    checklibdir = srclibdir
                                if os.path.exists(libdir):
                                    total = replace_all_with_symlinks(libdir, srclibdir, checklibdir)
                                    if total > 0:
                                        symstr = 'symlinks' if total > 1 else 'symlink'
                                        print('      ' + library + ' (' + str(total) + ' ' + symstr + ')')
                else:
                    libraries = os.listdir(targetdir + refdir)
                    for library in libraries:
                        print('   ' + library)
                        filedirs = os.listdir(targetdir + refdir + library)
                        for filedir in filedirs:
                            libdir = targetdir + refdir + library + '/' + filedir
                            srclibdir = link_from + refdir + library + '/' + filedir
                            if checkdir != '':
                                checklibdir = checkdir + refdir + library + '/' + filedir
                            else:
                                checklibdir = srclibdir
                            if os.path.exists(libdir):
                                total = replace_all_with_symlinks(libdir, srclibdir, checklibdir)
                                if total > 0:
                                    symstr = 'symlinks' if total > 1 else 'symlink'
                                    print('      ' + filedir + ' (' + str(total) + ' ' + symstr + ')')

    # Remove temporary files:  Magic generation scripts, sources.txt
    # file, and magic extract files.

    print('Removing temporary files from destination.')

    for refdir in refdirs:
        if ef_format:
            filedirs = os.listdir(targetdir + refdir)
            for filedir in filedirs:
                if os.path.islink(filedir):
                    continue
                elif os.path.isdir(filedir):
                    libraries = os.listdir(targetdir + refdir + filedir)
                    for library in libraries:
                        libdir = targetdir + refdir + filedir + '/' + library
                        libfiles = os.listdir(libdir)
                        for libfile in libfiles:
                            filepath = libdir + '/' + libfile
                            if os.path.islink(filepath):
                                continue
                            elif libfile == 'sources.txt':
                                os.remove(filepath)
                            elif libfile == 'generate_magic.tcl':
                                os.remove(filepath)
                            elif os.path.splitext(libfile)[1] == '.ext':
                                os.remove(filepath)
        else:
            libraries = os.listdir(targetdir + refdir)
            for library in libraries:
                filedirs = os.listdir(targetdir + refdir + library)
                for filedir in filedirs:
                    filepath = targetdir + refdir + library + '/' + filedir
                    if os.path.islink(filepath):
                        continue
                    elif os.path.isdir(filepath):
                        libfiles = os.listdir(filepath)
                        for libfile in libfiles:
                            libfilepath = filepath + '/' + libfile
                            if os.path.islink(libfilepath):
                                continue
                            elif libfile == 'sources.txt':
                                os.remove(libfilepath)
                            elif libfile == 'generate_magic.tcl':
                                os.remove(libfilepath)
                            elif os.path.splitext(libfile)[1] == '.ext':
                                os.remove(libfilepath)
        
    print('Done with PDK migration.')
    sys.exit(0)
