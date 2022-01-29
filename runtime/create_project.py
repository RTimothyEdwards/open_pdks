#!/usr/bin/env python3
#-----------------------------------------------------------------------
# create_project.py
#-----------------------------------------------------------------------
#
# Create a project in the form preferred by open_pdks.
#
#---------------------------------------------------------------------
# Written by Tim Edwards
# March 15, 2021
# Version 1.0
#---------------------------------------------------------------------

import os
import re
import sys
import json
import yaml

def usage():
    print('Usage:')
    print('	create_project.py <project_name> [<pdk_name>] [-options]')
    print('')
    print('Arguments:')
    print('	<project_name> is the name of the project and the top-level directory')
    print('	<pdk_name> is the name of the PDK')
    print('')
    print('     <pdk_name> can be a full path to the PDK')
    print('     <project_name> can be a full path to the project, otherwise use cwd.')
    print('')
    print('Options:')
    print('	-help	Print this help text.')

# Main procedure

if __name__ == '__main__':

    # Parse command line for options and arguments
    optionlist = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            optionlist.append(item)
        else:
            arguments.append(item)

    if len(arguments) > 0:
        projectname = arguments[0]
        if len(arguments) > 1:
            pdkname = arguments[1]
        else:
            pdkname = None
    else:
        usage()
        sys.exit(0)

    if pdkname:
        if pdkname.startswith('/'):
            pdkpath = pdkname
            pdkname = os.path.split(pdkpath)[1]
        else:
            pdkpath = os.path.join('PREFIX', 'pdk', pdkname)
    else:
        try:
            pdkpath = os.getenv()['PDK_PATH']
        except:
            try:
                pdkpath = os.getenv()['PDKPATH']
            except:
                print('If PDK name is not specified, then PDKPATH must be set.')
                sys.exit(1)

    if not os.path.isdir(pdkpath):
        print('Path to PDK ' + pdkpath + ' does not exist or is not readable.')
        sys.exit(1)

    for item in optionlist:
        result = item.split('=')
        if result[0] == '-help':
            usage()
            sys.exit(0)
        else:
            usage()
            sys.exit(1)

    if projectname.startswith('/'):
        projectpair = os.path.split(projectname)
        projectparent = projectpair[0]
        projectname = projectpair[1]
    else:
        projectparent = os.getcwd()

    if not os.path.isdir(projectparent):
        print('Path to project ' + projectpath + ' does not exist or is not readable.')
        sys.exit(1)

    projectpath = os.path.join(projectparent, projectname)

    # Check that files to be linked to exist in the PDK
    if not os.path.isfile(pdkpath + '/libs.tech/magic/' + pdkname + '.magicrc'):
        print(pdkname + '.magicrc not found;  not installing.')
        domagic = False
    else:
        domagic = True

    if not os.path.isfile(pdkpath + '/libs.tech/netgen/' + pdkname + '_setup.tcl'):
        print(pdkname + '_setup.tcl for netgen not found;  not installing.')
        donetgen = False
    else:
        donetgen = True

    if not os.path.isfile(pdkpath + '/libs.tech/xschem/xschemrc'):
        print('xschemrc for xschem not found;  not installing.')
        doxschem = False
    else:
        doxschem = True

    if not os.path.isfile(pdkpath + '/libs.tech/ngspice/spinit'):
        print('spinit for ngspice not found;  not installing.')
        dongspice = False
    else:
        dongspice = True

    if not os.path.isdir(pdkpath + '/.ef-config') and not os.path.isdir(pdkpath + '/.config'):
        print('PDK does not contain .config or .ef-config directory, cannot create project.')
        sys.exit(1)

    if domagic or donetgen or doxschem or dongspice:
        print('Creating project ' + projectname)
        os.makedirs(projectpath)
    else:
        print('No setup files were found . . .  bailing.')
        sys.exit(1)

    if os.path.isdir(pdkpath + '/.ef-config'):
        os.makedirs(projectpath + '/.ef-config')
        os.symlink(pdkpath, projectpath + '/.ef-config/techdir')
    elif os.path.isdir(pdkpath + '/.config'):
        os.makedirs(projectpath + '/.config')
        os.symlink(pdkpath, projectpath + '/.config/techdir')


    if domagic:
        magpath = os.path.join(projectpath, 'mag')
        os.makedirs(magpath)
        os.symlink(pdkpath + '/libs.tech/magic/' + pdkname + '.magicrc',
		magpath + '/.magicrc')

    if doxschem:
        xschempath = os.path.join(projectpath, 'xschem')
        os.makedirs(xschempath)
        os.symlink(pdkpath + '/libs.tech/xschem/xschemrc',
		xschempath + '/xschemrc')

    if donetgen:
        netgenpath = os.path.join(projectpath, 'netgen')
        os.makedirs(netgenpath)
        os.symlink(pdkpath + '/libs.tech/netgen/' + pdkname + '_setup.tcl',
		netgenpath + '/setup.tcl')

    if dongspice:
        ngspicepath = os.path.join(projectpath, 'ngspice')
        os.makedirs(ngspicepath)
        os.symlink(pdkpath + '/libs.tech/ngspice/spinit',
		ngspicepath + '/.spiceinit')

    data = {}
    project={}
    project['description'] = "(Add project description here)"

    infofile = pdkpath + '/.config/nodeinfo.json'
    if os.path.exists(infofile):
        with open(infofile, 'r') as ifile:
            nodeinfo = json.load(ifile)
        if 'foundry' in nodeinfo:
            project['foundry'] = nodeinfo['foundry']

    project['process']=pdkname
    project['project_name'] = projectname
    data['project']=project

    with open(projectpath + '/info.yaml', 'w') as ofile:
        print('---', file=ofile)
        yaml.dump(data, ofile)

    print('Done!')
    sys.exit(0)
