#!/usr/bin/env python3
# Script to read a GDS file, modify the timestamp(s), and rewrite the GDS file.

import os
import sys
import datetime

def usage():
    print('change_gds_date.py <create_stamp> <mod_stamp> <path_to_gds_in> [<path_to_gds_out>]')

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

    if len(arguments) < 3 or len(arguments) > 4:
        print("Wrong number of arguments given to change_gds_date.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    createstamp = arguments[0]
    modstamp = arguments[1]
    source = arguments[2]

    # If modstamp is zero or negative, then set the modification timestamp
    # to be the same as the creation timestamp.
    try:
        if int(modstamp) <= 0:
            modstamp = createstamp
    except:
        pass

    # If only three arguments are provided, then overwrite the source file.
    if len(arguments) == 4:
        dest = arguments[3]
    else:
        dest = arguments[2]

    sourcedir = os.path.split(source)[0]
    gdsinfile = os.path.split(source)[1]

    destdir = os.path.split(dest)[0]
    gdsoutfile = os.path.split(dest)[1]

    with open(source, 'rb') as ifile:
        gdsdata = ifile.read()

    # Generate 12-byte modification timestamp data from date.
    try:
        modtime = datetime.datetime.fromtimestamp(int(modstamp))
    except:
        modtime = datetime.datetime.strptime(modstamp, "%m/%d/%Y %H:%M:%S")

    modyear = modtime.year - 1900

    year = modyear.to_bytes(2, byteorder='big')
    month = modtime.month.to_bytes(2, byteorder='big')
    day = modtime.day.to_bytes(2, byteorder='big')
    hour = modtime.hour.to_bytes(2, byteorder='big')
    minute = modtime.minute.to_bytes(2, byteorder='big')
    second = modtime.second.to_bytes(2, byteorder='big')

    gdsmodstamp = year + month + day + hour + minute + second

    # Generate 12-byte creation timestamp data from date.
    try:
        createtime = datetime.datetime.fromtimestamp(int(createstamp))
    except:
        createtime = datetime.datetime.strptime(createstamp, "%m/%d/%Y %H:%M:%S")

    createyear = createtime.year - 1900

    year = createyear.to_bytes(2, byteorder='big')
    month = createtime.month.to_bytes(2, byteorder='big')
    day = createtime.day.to_bytes(2, byteorder='big')
    hour = createtime.hour.to_bytes(2, byteorder='big')
    minute = createtime.minute.to_bytes(2, byteorder='big')
    second = createtime.second.to_bytes(2, byteorder='big')

    gdscreatestamp = year + month + day + hour + minute + second

    # To be done:  Allow the user to select which datestamps to change
    # (library or structure).  Otherwise, apply the same datestamps to both.

    recordtypes = ['beginstr', 'beginlib']
    recordfilter = [5, 1]

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

        if rectype in recordfilter:
            # Datatype should be 2
            if datatype != 2:
                print('Error:  Header data type is not 2-byte integer!')
            if reclen != 28:
                print('Error:  Header record length is not 28!')
            if debug:
                print('Record type = ' + str(rectype) + ' data type = ' + str(datatype) + ' length = ' + str(reclen))

            before = gdsdata[0:dataptr]
            after = gdsdata[dataptr + reclen:]

            # Assemble the new record
            newrecord = bheader + brectype + bdatatype + gdscreatestamp + gdsmodstamp
            # Reassemble the GDS data around the new record
            gdsdata = before + newrecord + after

        # Advance the pointer past the data
        dataptr += reclen

    with open(dest, 'wb') as ofile:
        ofile.write(gdsdata)

    exit(0)
