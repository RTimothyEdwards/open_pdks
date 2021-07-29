#!/usr/bin/python

# foundry_nodes.py ---
#
# This script runs in cloudV and discovers the set of foundry-
# node names that are on the system and which support digital
# synthesis.  It returns the list of discovered nodes in JSON
# data format (output to stdout).
#
# Note that as this runs on the cloudV server, it is written
# in python 2.7 syntax

from __future__ import print_function

import os
import re
import sys
import json
import glob

def print_usage():
     print('Usage: foundry_nodes.py [all|<tag>]')

if __name__ == '__main__':
    arguments = []
    for item in sys.argv[1:]:
        arguments.append(item)

    dolist = 'active'
    if len(arguments) == 1:
        dolist = arguments[0]
    elif len(arguments) != 0:
        print_usage()
        sys.exit(0)

    # Search the /ef/ tree and find all foundry name (root name of the
    # directory above the foundry node name).  If nothing is found,
    # assume that this is the project name.  If the project name
    # is already set, then generate an error.

    proclist = []

    for procnode in glob.glob('/ef/tech/*/*/.ef-config/nodeinfo.json'):
        try:
            with open(procnode, 'r') as ifile:
                process = json.load(ifile)
        except:
            pass
        else:
            nodename = process['node']
            rootpath = os.path.split(procnode)[0]
            techroot = os.path.realpath(rootpath + '/techdir')
            qflowlist = glob.glob(techroot + '/libs.tech/qflow/' + nodename + '*.sh')

            
            if 'status' in process:
                status = process['status']
            else:
                # Default behavior is that nodes with "LEGACY" in the name
                # are inactive, and all others are active.
                if 'LEGACY' in nodename:
                    status = 'legacy'
                else:
                    status = 'active'

            # Do not record process nodes that do not match the status-match
            # argument (unless the argument is "all").
            if dolist != 'all':
                if status != dolist:
                    continue

            # Try to find available standard cell sets if they are not marked
            # as an entry in the nodeinfo.json file.  If they are an entry in nodeinfo.json,
            # check if it is just a list of names.  If so, look up each name entry and
            # expand it into a dictionary.  If it is already a dictionary, then just copy
            # it to the output.
            validcells = []
            if 'stdcells' in process:
                for name in process['stdcells'][:]:
                    if type(name) is not dict:
                        process['stdcells'].remove(name)
                        validcells.append(name)

            stdcells = []
            for qflowdefs in qflowlist:
                stdcellname = os.path.split(qflowdefs)[1]
                validname = os.path.splitext(stdcellname)[0]
                if validcells == [] or validname in validcells:

                    stdcelldef = {}
                    stdcelldef['name'] = validname

                    # Read the qflow .sh file for the name of the preferred liberty format
                    # file and the name of the verilog file.  Pull the path name from the
                    # verilog file since there may be other supporting files that need to
                    # be read from that path.

                    # Diagnostic
                    # print("Reading file " + qflowdefs, file=sys.stderr)
                    with open(qflowdefs, 'r') as ifile:
                        nodevars = ifile.read().splitlines()

                    try:
                        libline = next(item for item in nodevars if 'libertyfile' in item and item.strip()[0] != '#')
                        lfile = libline.split('=')[1].strip()
                        lfile = lfile.split()[0]
                        stdcelldef['libertyfile'] = lfile
                    except:
                        pass

                    try:
                        vlgline = next(item for item in nodevars if 'verilogfile' in item and item.strip()[0] != '#')
                        vfile = vlgline.split('=')[1].strip()
                        vfile = vfile.split()[0]
                        if os.path.exists(vfile):
                            stdcelldef['verilogpath'] = os.path.split(vfile)[0]
                        else:
                            print("Warning:  bad verilogfile path " + vfile, file=sys.stderr)
                    except:
                        pass
    
                    stdcells.append(stdcelldef)

            process['stdcells'] = stdcells
            proclist.append(process)

    if len(proclist) > 0:
        json.dump(proclist, sys.stdout, indent=4)
    else:
        print("Error, no process nodes found!", file=sys.stderr)

