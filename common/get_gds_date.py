#!/usr/bin/env python3
# Script to read a GDS file and print out the timestamp(s).

import os
import sys
import datetime

def usage():
    print('get_gds_date.py <path_to_gds_in> [-created | -modified]')

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to change_gds_date.py.")
        usage()
        sys.exit(0)

    optionlist = []
    arguments = []

    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)

    if len(arguments) != 1:
        print("Wrong number of arguments given to get_gds_date.py.")
        usage()
        sys.exit(0)

    created = True
    modified = True

    if '-debug' in optionlist:
        debug = True
    if '-created' in optionlist:
        modified = False
    if '-modified' in optionlist:
        created = False

    source = arguments[0]

    sourcedir = os.path.split(source)[0]
    gdsinfile = os.path.split(source)[1]

    with open(source, 'rb') as ifile:
        gdsdata = ifile.read()

    datalen = len(gdsdata)
    dataptr = 0
    while dataptr < datalen:
        # Read stream records up to any string, then search for search text.
        bheader = gdsdata[dataptr:dataptr + 2]
        reclen = int.from_bytes(bheader, 'big')
        if reclen == 0:
            print('Error: found zero-length record at position ' + str(dataptr))
            break

        rectype = gdsdata[dataptr + 2]
        datatype = gdsdata[dataptr + 3]

        brectype = rectype.to_bytes(1, byteorder='big')
        bdatatype = datatype.to_bytes(1, byteorder='big')

        if rectype == 1:		# 1 = beginlib
            # Datatype should be 2
            if datatype != 2:
                print('Error:  Header data type is not 2-byte integer!')
            if reclen != 28:
                print('Error:  Header record length is not 28!')
            if debug:
                print('Record type = ' + str(rectype) + ' data type = ' + str(datatype) + ' length = ' + str(reclen))

            if created:
                crec1 = gdsdata[dataptr + 4:dataptr + 6]
                crec2 = gdsdata[dataptr + 6:dataptr + 8]
                crec3 = gdsdata[dataptr + 8:dataptr + 10]
                crec4 = gdsdata[dataptr + 10:dataptr + 12]
                crec5 = gdsdata[dataptr + 12:dataptr + 14]
                crec6 = gdsdata[dataptr + 14:dataptr + 16]

                modyear = int.from_bytes(crec1, 'big')
                year = modyear + 1900
                month = int.from_bytes(crec2, 'big')
                day = int.from_bytes(crec3, 'big')
                hour = int.from_bytes(crec4, 'big')
                minute = int.from_bytes(crec5, 'big')
                second = int.from_bytes(crec6, 'big')

                print('Created date: {}-{}-{}-{}-{}-{}'.format(year, month, day, hour, minute, second))

            if modified:
                mrec1 = gdsdata[dataptr + 16:dataptr + 18]
                mrec2 = gdsdata[dataptr + 18:dataptr + 20]
                mrec3 = gdsdata[dataptr + 20:dataptr + 22]
                mrec4 = gdsdata[dataptr + 22:dataptr + 24]
                mrec5 = gdsdata[dataptr + 24:dataptr + 26]
                mrec6 = gdsdata[dataptr + 26:dataptr + 28]

                modyear = int.from_bytes(mrec1, 'big')
                year = modyear + 1900
                month = int.from_bytes(mrec2, 'big')
                day = int.from_bytes(mrec3, 'big')
                hour = int.from_bytes(mrec4, 'big')
                minute = int.from_bytes(mrec5, 'big')
                second = int.from_bytes(mrec6, 'big')

                print('Modified date: {}-{}-{}-{}-{}-{}'.format(year, month, day, hour, minute, second))
            break

        # Advance the pointer past the data
        dataptr += reclen

    exit(0)
