#!/usr/bin/env python3
#
# cace_datasheet_upload.py
#
# Send newly-created challenge datasheet and associated
# design files (testbench schematics and netlists) to
# the  marketplace server for storage.
#

import os
import json
import re
import sys
import requests
import subprocess

import file_compressor
import file_request_hash

"""
 standalone script.
 Makes rest calls to marketplace REST server to save datasheet
 and associated file(s).  Request hash is generated so the two
 requests can be associated on the server side.  This action
 has no other side effects.
"""

mktp_server_url = ""

# Make request to server sending json passed in.
def send_doc(doc):
    result = requests.post(mktp_server_url + '/cace/save_datasheet', json=doc)
    print('send_doc', result.status_code)

# Pure HTTP post here.  Add the file to files object and the hash/filename
# to the data params.
def send_file(hash, file, file_name):
    files = {'file': file.getvalue()}
    data = {'request-hash': hash, 'file-name': file_name}
    result = requests.post(mktp_server_url + '/cace/save_files', files=files, data=data)
    print('send_file', result.status_code)


if __name__ == '__main__':

    # Divide up command line into options and arguments
    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item)
        else:
            arguments.append(item)

    # There should be two arguments passed to the script.  One is
    # the path and filename of the datasheet JSON file, and the
    # other a path to the location of testbenches (netlists and/or
    # schematics).  If there is only one argument, then datasheet_filepath
    # is assumed to be in the same path as netlist_filepath.

    datasheet_filepath = []
    netlist_filepath = []

    for argval in arguments:
        if os.path.isfile(argval):
            datasheet_filepath = argval
        elif os.path.isdir(argval):
            netlist_filepath = argval
        elif os.path.splitext(argval)[1] == '':
            argname = argval + '.json'
            if os.path.isfile(argval):
                datasheet_filepath = argname

    if not datasheet_filepath:
        # Check for JSON file 'project.json' in the netlist filepath directory
        # or the directory above it.
        if netlist_filepath:
            argtry = netlist_filepath + '/project.json'
            if os.path.isfile(argtry):
                datasheet_filepath = argtry
            else:
                argtry = os.path.split(netlist_filepath)[0] + '/project.json'
                if os.path.isfile(argtry):
                    datasheet_filepath = argtry

        # Legacy behavior support
        if not os.path.isfile(datasheet_filepath):
            # Check for JSON file with same name as netlist filepath,
            # but with a .json extension, in the netlist filepath directory
            # or the directory above it.
            if netlist_filepath:
                argtry = netlist_filepath + '/' + os.path.basename(netlist_filepath) + '.json'
                if os.path.isfile(argtry):
                    datasheet_filepath = argtry
                else:
                    argtry = os.path.split(netlist_filepath)[0] + '/' + os.path.basename(netlist_filepath) + '.json'
                    if os.path.isfile(argtry):
                        datasheet_filepath = argtry

    if not datasheet_filepath:
        print('Error:  No datasheet JSON file specified.\n')
        sys.exit(1)

    if not os.path.isfile(datasheet_filepath):
        print('Error:  No datasheet JSON file ' + datasheet_filepath + ' found.\n')
        sys.exit(1)

    # Technically okay to have null netlist_filepath, but unlikely,
    # so flag a warning.

    if not netlist_filepath:
        print('Warning: No netlist filepath given.  No files will be '
		+ 'transmitted with the datasheet.\n')

    dsheet = {}
    with open(datasheet_filepath, 'r') as user_doc_file:
        docinfo = json.load(user_doc_file)
        dsheet = docinfo['data-sheet']
        try:
            name = dsheet['ip-name']
        except KeyError:
            datasheet_file = os.path.split(datasheet_filepath)[1]
            name = os.path.splitext(datasheet_file)[0]
            dsheet['ip-name'] = name

    # Behavior starting 4/27/2017:  the UID is required to be a
    # numeric value, but the datasheet upload is generally being
    # done as user admin from the remote CACE host, and admin has
    # no official UID number.  So always attach ID 9999 to datasheet
    # uploads.

    if 'UID' in docinfo:
        uid = docinfo['UID']
    else:
        uid = 9999
        docinfo['UID'] = uid

    # Get a request hash and add it to the JSON document
    rhash, timestamp = file_request_hash.get_hash(name)
    docinfo['request-hash'] = rhash

    # Put the current git system state into the target directory
    # prior to tarballing
    if os.path.isfile('.version'):
        with open('.version', 'r') as f:
            ef_version = f.read().rstrip()
        docinfo['ef-version'] = ef_version

    # Now send the datasheet
    if '-test' in options:
        print("Test:  running send_doc( <docinfo> )\n")
        print("       with docinfo['UID'] = " + uid + "\n")
    else:
        send_doc(docinfo)

    # Send the merged JSON file and the tarballed design file directory
    # to the marketplace server for storage.

    if netlist_filepath:
        # Use the version below to ignore the 'spi' directory.  However, it may
        # be the intention of the challenge creator to seed the challenge with
        # an example.  This is normally not the case.  So use '-include' option
        # to avoid excluding the 'spi' folder contents.
        if '-includeall' in options:
            print('Including netlist/schematic and simulation files in project folder.')
            tar = file_compressor.tar_directory_contents(netlist_filepath,
			exclude=['elec/\.java', 'elec/electric\.log', name + '\.log',
			'.*\.raw', 'ngspice/run/\.allwaves'])
        elif '-include' in options:
            print('Including netlist/schematic files in project folder.')
            tar = file_compressor.tar_directory_contents(netlist_filepath,
			exclude=['ngspice', 'elec/\.java', 'elec/electric\.log',
			name + '\.log'])
        else:
            print('Excluding netlist/schematic and simulation files in project folder.')
            tar = file_compressor.tar_directory_contents(netlist_filepath,
			exclude=['spi', 'ngspice', 'elec/\.java', 'mag', 'elec/electric\.log',
			'elec/' + name + '\.delib/' + name + '\.sch', name + '\.log'])
        tarballname = name + '.tar.gz'

        # Now send the netlist file tarball
        if '-test' in options:
            print('Test:  running send_file(' + rhash + ' <tarball> ' + tarballname + ')')
            print('Saving tarball locally as ' + tarballname)
            file_compressor.tar_directory_contents_to_file(netlist_filepath,
			tarballname, exclude=['spi', 'ngspice', 'elec/\.java', 'mag',
			'elec/electric\.log', 'elec/' + name + '\.delib/' + name + '\.sch',
			name + '\.log'])
        else:
            send_file(rhash, tar, tarballname)

