#!/usr/bin/env python3
#
# rename_project.py ---  Perform all tasks required for renaming a project.
#
# In the context of this script, "renaming" a project means changing the
# 'ip-name' entry in the JSON file and all that that implies.  To create a
# new project with an existing ip-name is essentially a trivial process of
# renaming the parent directory.
#
# Note that when a catalog entry is generated in the marketplace, the entry's
# default name is taken from the parent directory name, not the ip-name.  The
# resulting entry name is irrelevant to most everything except how and where
# the IP is listed in the catalog.  The read-only IP version has the name of
# the ip-name.  Implies it is important that ip-name does not collide with
# the ip-name of anything else in the marketplace catalog (but this is not
# currently enforced).
#
# Modified 12/20/2018: New protocol is that the .json file is always called
# 'project.json' and does not take the name of the parent directory.  This
# makes projects more portable.
#
import shutil
import json
import stat
import sys
import os
import re

"""
    This module converts an entire project from one ip-name to another, making
    sure that all filenames and file contents are updated.
"""

def copy_meta_with_ownership(src, dst, follow_symlinks=False):
    # Copy file metadata using copystat() and preserve ownership through stat calls.
    file_stat = os.stat(src)
    owner = file_stat[stat.ST_UID]
    group = file_stat[stat.ST_GID]
    shutil.copystat(src, dst)
    os.chown(dst, owner, group, follow_symlinks=follow_symlinks)

def rename_json(project_path, json_file, new_name, orig_name = ''):
    # Make sure we have the full absolute path to the project
    fullpath = os.path.abspath(project_path)
    # Project directory name is the last component of the full path
    dirname = os.path.split(fullpath)[1]
    # Get contents of the file, then recast the ip-name and rewrite it.
    with open(json_file, 'r') as ifile:
        datatop = json.load(ifile)

    # Find ip-name and replace it
    if 'data-sheet' in datatop:
        dsheet = datatop['data-sheet']
        if 'ip-name' in dsheet:
            ipname = dsheet['ip-name']
            if ipname == orig_name:
                dsheet['ip-name'] = new_name
            elif orig_name == '':
                dsheet['ip-name'] = new_name
            else:
                print('Error: original name ' + orig_name + ' specified in command line,')
                print('but ip-name is ' + ipname + ' in the datasheet.')
                return ipname

    # Change name of file.  This must match the name of the directory whether
    # or not the directory name matches the IP name.
    # (New protocol from Dec. 2018:  JSON file is now always named 'project.json')

    opath = os.path.split(json_file)[0]
    # oname = opath + '/' + dirname + '.json'
    oname = opath + '/project.json'
    
    with open(oname, 'w') as ofile:
        json.dump(datatop, ofile, indent = 4)

    # Remove original file.  Avoid destroying the file if rename_project happens
    # to be called with the same name for old and new.
    if (json_file != oname):
        copy_meta_with_ownership(json_file, oname)
        os.remove(json_file)

    # Return the original IP name
    return ipname

def rename_netlist(netlist_path, orig_name, new_name):
    # All netlists can be regenerated on the fly, so remove any that are
    # from orig_name
    if not os.path.exists(netlist_path):
        return

    filelist = os.listdir(netlist_path)
    for file in filelist:
       rootname = os.path.splitext(file)[0]
       fullpath = netlist_path + '/' + file
       if rootname == orig_name:
           if os.path.isdir(fullpath):
               rename_netlist(fullpath, orig_name, new_name);
           else:
               print('Removing netlist file ' + file)
               os.remove(fullpath)

def rename_magic(magic_path, orig_name, new_name):
    # remove old files that will get regenerated:  comp.out, comp.json, any *.log
    # move any file beginnng with orig_name to the same file with new_name
    filelist = os.listdir(magic_path)

    # All netlists can be regenerated on the fly, so remove any that are
    # from orig_name
    for file in filelist:
       rootname, fext = os.path.splitext(file)

       if file == 'comp.out' or file == 'comp.json':
           os.remove(magic_path + '/' + file)
       elif rootname == orig_name:
           if fext == '.spc' or fext == '.spice':
               print('Removing netlist file ' + file)
               os.remove(magic_path + '/' + file)
           elif fext == '.ext' or fext == '.lef':
               os.remove(magic_path + '/' + file)
           else:
               shutil.move(magic_path + '/' + file, magic_path + '/' + new_name + fext)

       elif fext == '.log':
           os.remove(magic_path + '/' + file)

def rename_verilog(verilog_path, orig_name, new_name):
    filelist = os.listdir(verilog_path)

    # The root module name can remain as the original (may not match orig_name
    # anyway), but the verilog file containing it gets renamed.
    # To be done:  Any file (e.g., simulation testbenches, makefiles) referencing
    # the file must be modified to match.  These may be in subdirectories, so
    # walk the filesystem from verilog_path.

    for file in filelist:
       rootname, fext = os.path.splitext(file)
       if rootname == orig_name:
           if fext == '.v' or fext == '.sv':
               shutil.move(verilog_path + '/' + file, verilog_path + '/' + new_name + fext)

def rename_electric(electric_path, orig_name, new_name):
    # <project_name>.delib gets renamed

    filelist = os.listdir(electric_path)
    for file in filelist:
        rootname, fext = os.path.splitext(file)
        if rootname == orig_name:
            shutil.move(electric_path + '/' + file, electric_path + '/' + new_name + fext)

    delib_path = electric_path + '/' + new_name + '.delib'
    if os.path.exists(delib_path):
        filelist = os.listdir(delib_path)
        for file in filelist:
            if os.path.isdir(file):
                continue
            rootname, fext = os.path.splitext(file)
            if rootname == orig_name:
                # Read and do name substitution where orig_name occurs
                # in 'H', 'C', and 'L' statements.  The top-level should not appear in
                # an 'I' (instance) statement.
                with open(delib_path + '/' + file, 'r') as ifile:
                    contents = ifile.read()
                    contents = re.sub('H' + orig_name + '\|', 'H' + new_name + '|', contents)
                    contents = re.sub('C' + orig_name + ';', 'C' + new_name + ';', contents)
                    contents = re.sub('L' + orig_name + '\|' + orig_name, 'L' + new_name + '|' + new_name, contents)
		
                oname = new_name + fext
                with open(delib_path + '/' + oname, 'w') as ofile:
                    ofile.write(contents)

                # Copy ownership and permissions from the old file
                # Remove the original file
                copy_meta_with_ownership(delib_path + '/' + file, delib_path + '/' + oname)
                os.remove(delib_path + '/' + file)

            elif rootname == 'header':
                # Read and do name substitution where orig_name occurs in 'H' statements.
                with open(delib_path + '/' + file, 'r') as ifile:
                    contents = ifile.read()
                    contents = re.sub('H' + orig_name + '\|', 'H' + new_name + '|', contents)
		
                with open(delib_path + '/' + file + '.tmp', 'w') as ofile:
                    ofile.write(contents)

                copy_meta_with_ownership(delib_path + '/' + file, delib_path + '/' + file + '.tmp')
                os.remove(delib_path + '/' + file)
                shutil.move(delib_path + '/' + file + '.tmp', delib_path + '/' + file)

# Top level routine (call this one)

def rename_project_all(project_path, new_name, orig_name=''):
    # project_path is the original full path to the project in the user's design space.
    #
    # new_name is the new name to give to the project.  It is assumed to have been
    # already checked for uniqueness against existing names

    # Original name is determined from the 'ip-name' field in the JSON file
    # unless it is specified as a separate argument.

    proj_name = os.path.split(project_path)[1]
    json_path = project_path + '/project.json'  

    # The JSON file is assumed to have the name "project.json" always.
    # However, if the project directory just got named, or if the project pre-dates
    # December 2018, then that may not be true.  If json_path does not exist, look
    # for any JSON file containing a data-sheet entry.

    if not os.path.exists(json_path):
        json_path = ''
        filelist = os.listdir(project_path)
        for file in filelist:
            if os.path.splitext(file)[1] == '.json':
                with open(project_path + '/' + file) as ifile:
                    datatop = json.load(ifile)
                    if 'data-sheet' in datatop:
                        json_path = project_path + '/' + file
                        break

    if os.path.exists(json_path):
        if (orig_name == ''):
            orig_name = rename_json(project_path, json_path, new_name)
        else:
            test_name = rename_json(project_path, json_path, new_name, orig_name)
            if test_name != orig_name:
                # Refusing to make a change because the orig_name didn't match ip-name
                return
    else:
        if (orig_name == ''):
            orig_name = proj_name

    if orig_name == new_name:
        print('Warning:  project old and new names are the same;  nothing to change.', file=sys.stderr)
        return

    # Each subroutine renames a specific group of files.
    electric_path = project_path + '/elec'
    if os.path.exists(electric_path):
        rename_electric(electric_path, orig_name, new_name)

    magic_path = project_path + '/mag'
    if os.path.exists(magic_path):
        rename_magic(magic_path, orig_name, new_name)

    verilog_path = project_path + '/verilog'
    if os.path.exists(verilog_path):
        rename_verilog(verilog_path, orig_name, new_name)

    # Maglef is deprecated in anything but readonly IP and PDKs, but
    # handle for backwards compatibility.
    maglef_path = project_path + '/maglef'
    if os.path.exists(maglef_path):
        rename_magic(maglef_path, orig_name, new_name)

    netlist_path = project_path + '/spi'
    if os.path.exists(netlist_path):
        rename_netlist(netlist_path, orig_name, new_name)
        rename_netlist(netlist_path + '/pex', orig_name, new_name)
        rename_netlist(netlist_path + '/cdl', orig_name, new_name)
        rename_netlist(netlist_path + '/lvs', orig_name, new_name)

    # To be done:  handle qflow directory if it exists.

    print('Renamed project ' + orig_name + ' to ' + new_name + '; done.')

# If called as main, run rename_project_all.

if __name__ == '__main__':

    # Divide up command line into options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # Need two arguments:  path to directory, and new project name.

    if len(arguments) < 2:
        print("Usage:  rename_project.py <project_path> <new_name> [<orig_name>]")
    elif len(arguments) >= 2:
        project_path = arguments[0]
        new_name = arguments[1]

        if len(arguments) == 3:
            orig_name = arguments[2]
            rename_project_all(project_path, new_name, orig_name)
        else:
            rename_project_all(project_path, new_name)

