#!/usr/bin/env python3
#
# Copyright 2020 OpenCircuitDesign
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
staging_install.py [options...]

This file copies the staging area created by foundry_install.py
into the target directory area, changing paths to match the target,
and creating symbolic links where requested and allowed.

Options:
  -staging <path>    Path to staging top level directory that the files
                     will be installed from.

  -finalpath <path>  Final install path in system file system.

                     Normally, '$(prefix)/pdks/<unique pdk name>'.

                     If -writeto is not given, this will be the top level
                     directory location the files are installed too.

  -writeto <path>    Actual file system location to write the files too.
                     The result can then be packaged and distributed.

                     For usage with things like package managers and other
                     administrator installation tooling.  The resulting
                     files still need to be installed at '-finalpath' on the
                     final system.

                     Think 'DESTDIR', see
                     https://www.gnu.org/prep/standards/html_node/DESTDIR.html

  -source <path>     Path to original source top level directory, if
                     link_from is "source".  This option may be called
                     multiple times if there are multiple sources.

  -variable <name>   Specify a variable name that is used for the
                     target path.  This variable name must be enforced
                     in setup scripts like .magicrc

Less common options:
  -link_from <type>  Make symbolic links to vendor files from target.

                     Types are: "none", "source", or a PDK name.

                     Default "none" (copy all files from source)

  -ef_format         Use efabless naming (libs.ref/techLEF),
                     otherwise use generic naming (libs.tech/lef)

  -verbose           Output more information about the install process.

If <target> is unspecified then <name> is used for the target.
"""

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
try:
    from setuptools.distutils.dir_util import copy_tree
except:
    from distutils.dir_util import copy_tree

def makeuserwritable(filepath):
    if os.path.exists(filepath):
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IWUSR)

# Filter files to replace all strings matching "stagingdir" with "finaldir" for
# every file in "tooldir".  If "tooldir" contains subdirectories, then recursively
# apply the replacement filter to all files in the subdirectories.  Do not follow
# symbolic links.

def filter_recursive(tooldir, stagingdir, finaldir):
    # Add any non-ASCII file types here
    bintypes = ['.gds', '.gds2', '.gdsii', '.png', '.swp']

    # Also do substitutions on strings containing the stagingdir parent
    # directory (replace with the finaldir parent directory).
    stagingparent = os.path.split(stagingdir)[0]
    localparent = os.path.split(finaldir)[0]

    if not os.path.exists(tooldir):
        return 0
    elif os.path.islink(tooldir):
        return 0

    toolfiles = os.listdir(tooldir)
    total = 0

    for file in toolfiles:
        # Do not attempt to do text substitutions on a binary file!
        if os.path.splitext(file)[1] in bintypes:
            continue

        filepath = tooldir + '/' + file
        if os.path.islink(filepath):
            continue
        elif os.path.isdir(filepath):
            total += filter_recursive(filepath, stagingdir, finaldir)
        else:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as ifile:
                try:
                    flines = ifile.readlines()
                except UnicodeDecodeError:
                    print('Failure to read file ' + filepath + '; non-ASCII content.')
                    continue

            # Make sure this file is writable (as the original may not be)
            makeuserwritable(filepath)

            modified = False
            with open(filepath, 'wb') as ofile:
                for line in flines:
                    newline = line.replace(stagingdir, finaldir)
                    newline = newline.replace(stagingparent, localparent)
                    ofile.write(newline.encode('utf-8'))
                    if newline != line:
                        modified = True

            if modified:
                total += 1
    return total

# To avoid problems with various library functions that copy hierarchical
# directory trees, remove all the files from the target that are going to
# be replaced by the contents of staging.  This avoids problems with
# symbolic links and such.

def remove_target(stagingdir, targetdir, verbose=False):

    slist = os.listdir(stagingdir)
    tlist = os.listdir(targetdir)

    for sfile in slist:
        if sfile in tlist:
            tpath = targetdir + '/' + sfile
            if os.path.islink(tpath):
                if verbose:
                    print("Removing link", tpath)
                os.unlink(tpath)
            elif os.path.isdir(tpath):
                remove_target(
                    stagingdir + '/' + sfile,
                    targetdir + '/' + sfile,
                    verbose)
            else:
                if verbose:
                    print("Removing", tpath)
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
        print(__doc__)
        sys.exit(0)

    optionlist = []
    newopt = []

    debug = False

    stagingdir = None
    link_from = None
    variable = None

    writedir = None  # Directory to write the files to.
    finaldir = None  # Directory files will end up installed to.

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
        elif option[0] == 'debug':
            optionlist.remove(option)
            debug = True

    # Check for options "link_from", "staging", "writeto", and "finalpath"
    # "target" and "local" are also parsed for backwards compatibility
    # although the names were misleading.

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
        elif option[0] == 'writeto' or option[0] == 'target':
            optionlist.remove(option)
            writedir = option[1]
        elif option[0] == 'finalpath' or option[0] == 'local':
            optionlist.remove(option)
            finaldir = option[1]
        elif option[0] == 'variable':
            optionlist.remove(option)
            variable = option[1]

    # Error if no staging or dest specified
    if not stagingdir:
        print("No staging directory specified.  Exiting.")
        sys.exit(1)

    if not finaldir:
        print("No final install directory specified.  Exiting.")
        sys.exit(1)

    # If finaldir is not specified, then it is the same as the parent
    # of the target (local installation assumed)
    if not writedir:
        writedir = finaldir
    else:
        writedir = writedir + finaldir

    # Take the target PDK name from the target path last component
    pdkname = os.path.split(writedir)[1]

    # If link source is a PDK name, if it has no path, then pull the
    # path from the target name.

    if link_from:
        if link_from != 'source':
            if link_from.find('/', 0) < 0:
                link_name = link_from
                link_from = os.path.split(finaldir)[0] + '/' + link_name
        else:
            # If linking from source, convert the source path to an
            # absolute pathname.
            stagingdir = os.path.abspath(stagingdir)

        # If link_from is the same as finaldir, then set link_from to None
        if link_from == finaldir:
            link_from = None

    # checkdir is the DIST target directory for the PDK pointed
    # to by link_name.  Files must be found there before creating
    # symbolic links to the (not yet existing) final install location.

    if link_name:
        checkdir = os.path.split(writedir)[0] + '/' + link_name
    else:
        checkdir = ''

    # Diagnostic
    if do_install:
        print("Installing in target directory " + writedir)
    else:
        print("Uninstalling from target directory " + writedir)
        print("(Method not yet implemented)")

    # Create the top-level directories

    os.makedirs(writedir, exist_ok=True)
    os.makedirs(writedir + '/libs.tech', exist_ok=True)
    os.makedirs(writedir + '/libs.ref', exist_ok=True)
    if os.path.isdir(stagingdir + '/libs.priv'):
        os.makedirs(writedir + '/libs.priv', exist_ok=True)
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

    if not os.path.isdir(writedir):
        try:
            os.makedirs(writedir, exist_ok=True)
        except:
            print('Fatal error:  Cannot make target directory ' + writedir + '!')
            exit(1)

    # Remove any files from the target directory that are going to be replaced
    print('Removing files from target')
    remove_target(stagingdir, writedir)

    print('Copying staging files to target')
    # print('Diagnostic:  copy_tree ' + stagingdir + ' ' + writedir)
    copy_tree(stagingdir, writedir, preserve_symlinks=True, verbose=debug)
    print('Done.')

    # Magic and qflow setup files have references to the staging area that have
    # been used by the vendor install;  these need to be changed to the target
    # directory.

    print('Changing local path references from ' + stagingdir + ' to ' + finaldir)
    print('Part 1:  Tools')

    # If there are any tool directories that should *not* be checked, then add
    # them to the list below.
    noneedcheck = []
    techdirs = ['/libs.tech/']
    if has_priv:
        techdirs.append('/libs.priv/')

    for techdir in techdirs:
        tools = os.listdir(writedir + techdir)
        for tool in tools:
            tooldir = writedir + techdir + tool

            # There are few enough tool setup files that they can just all be
            # filtered directly.  This code only looks in the directory 'tooldir'.
            # If there are files is subdirectories of 'tooldir' that require
            # substitution, then this code needs to be revisited.

            # Note that due to the low overhead of tool setup files, there is
            # no attempt to check for possible symlinks to link_from if link_from
            # is a base PDK.

            total = filter_recursive(tooldir, stagingdir, finaldir)
            if total > 0:
                substr = 'substitutions' if total > 1 else 'substitution'
                print('      ' + tool + ' (' + str(total) + ' ' + substr + ')')

    # If "link_from" is another PDK, then check all files against the files in
    # the other PDK, and replace the file with a symbolic link if the file contents
    # match (Note:  This is done only for ngspice model files;  other tool files are
    # generally small and deemed unnecessary to make symbolic links).

    if link_from not in ['source', None]:
        thispdk = os.path.split(writedir)[1]

        # Only create links for PDKs other than the one we are making links to.
        if thispdk != link_from:
            print('Replacing files with symbolic links to ' + link_from + ' where possible.')
            for techdir in techdirs:
                tools = os.listdir(writedir + techdir)
                for tool in tools:
                    if tool in noneedcheck:
                        continue
                    tooldir = writedir + techdir + tool
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
    # directory name to finaldir.  If "-variable" is specified in the options,
    # the replace the staging path with the variable name, not finaldir.

    if variable:
        localname = '$' + variable
    else:
        localname = finaldir

    needcheck = ['mag', 'maglef']
    refdirs = ['/libs.ref/']
    if has_priv:
        refdirs.append('/libs.priv/')

    if ef_format:
        print('Part 2:  Formats')
        for refdir in refdirs:
            for filetype in needcheck:
                print('   ' + filetype)
                filedir = writedir + refdir + filetype
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
            libraries = os.listdir(writedir + refdir)
            for library in libraries:
                print('   ' + library)
                for filetype in needcheck:
                    filedir = writedir + refdir + library + '/' + filetype
                    total = filter_recursive(filedir, stagingdir, localname)
                    if total > 0:
                        substr = 'substitutions' if total > 1 else 'substitution'
                        print('      ' + filetype + ' (' + str(total) + ' ' + substr + ')')

    # If "link_from" is "source", then check all files against the source
    # directory, and replace the file with a symbolic link if the file
    # contents match.  The "foundry_install.py" script should have added a
    # file "sources.txt" with the name of the source directories for each
    # install directory.

    if link_from == 'source':
        print('Replacing files with symbolic links to source where possible.')
        for refdir in refdirs:
            if ef_format:
                filedirs = os.listdir(writedir + refdir)
                for filedir in filedirs:
                    print('   ' + filedir)
                    dirpath = writedir + refdir + filedir
                    if os.path.isdir(dirpath):
                        libraries = os.listdir(dirpath)
                        for library in libraries:
                            libdir = writedir + refdir + filedir + '/' + library
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
                libraries = os.listdir(writedir + refdir)
                for library in libraries:
                    print('   ' + library)
                    filedirs = os.listdir(writedir + refdir + library)
                    for filedir in filedirs:
                        libdir = writedir + refdir + library + '/' + filedir
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
        thispdk = os.path.split(writedir)[1]

        # Only create links for PDKs other than the one we are making links to.
        if thispdk != link_from:

            print('Replacing files with symbolic links to ' + link_from + ' where possible.')

            for refdir in refdirs:
                if ef_format:
                    filedirs = os.listdir(writedir + refdir)
                    for filedir in filedirs:
                        print('   ' + filedir)
                        dirpath = writedir + refdir + filedir
                        if os.path.isdir(dirpath):
                            libraries = os.listdir(dirpath)
                            for library in libraries:
                                libdir = writedir + refdir + filedir + '/' + library
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
                    libraries = os.listdir(writedir + refdir)
                    for library in libraries:
                        print('   ' + library)
                        filedirs = os.listdir(writedir + refdir + library)
                        for filedir in filedirs:
                            libdir = writedir + refdir + library + '/' + filedir
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
            filedirs = os.listdir(writedir + refdir)
            for filedir in filedirs:
                if os.path.islink(filedir):
                    continue
                elif os.path.isdir(filedir):
                    libraries = os.listdir(writedir + refdir + filedir)
                    for library in libraries:
                        libdir = writedir + refdir + filedir + '/' + library
                        libfiles = os.listdir(libdir)
                        for libfile in libfiles:
                            filepath = libdir + '/' + libfile
                            if os.path.islink(filepath):
                                realpath = os.path.realpath(filepath)
                                if realpath.startswith(stagingdir):
                                    if libfile == '.magicrc':
                                        if debug:
                                            print('Removing unused .magicrc file from' +
							filepath)
                                        os.remove(filepath)
                            elif libfile == 'sources.txt':
                                os.remove(filepath)
                            elif libfile == 'generate_magic.tcl':
                                os.remove(filepath)
                            elif os.path.splitext(libfile)[1] == '.ext':
                                os.remove(filepath)
                            elif os.path.splitext(libfile)[1] == '.swp':
                                os.remove(filepath)
                            elif os.path.splitext(libfile)[1] == '.orig':
                                os.remove(filepath)
        else:
            libraries = os.listdir(writedir + refdir)
            for library in libraries:
                filedirs = os.listdir(writedir + refdir + library)
                for filedir in filedirs:
                    filepath = writedir + refdir + library + '/' + filedir
                    if os.path.islink(filepath):
                        continue
                    elif os.path.isdir(filepath):
                        libfiles = os.listdir(filepath)
                        for libfile in libfiles:
                            libfilepath = filepath + '/' + libfile
                            if os.path.islink(libfilepath):
                                # NOTE:  This could be used to move symbolic links
                                # from staging to destination.  At the moment there
                                # are none except the .magicrc file, which doesn't
                                # belong in the destination path.
                                realpath = os.path.realpath(libfilepath)
                                if realpath.startswith(stagingdir):
                                    if libfile == '.magicrc':
                                        if debug:
                                            print('Removing unused .magicrc file ' +
							'from ' + libfilepath)
                                        os.remove(libfilepath)
                            elif libfile == 'sources.txt':
                                os.remove(libfilepath)
                            elif libfile == 'generate_magic.tcl':
                                os.remove(libfilepath)
                            elif os.path.splitext(libfile)[1] == '.ext':
                                os.remove(libfilepath)
                            elif os.path.splitext(libfile)[1] == '.orig':
                                os.remove(libfilepath)

    print('Done with PDK migration.')
    sys.exit(0)
