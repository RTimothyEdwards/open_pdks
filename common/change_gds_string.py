#!/usr/bin/env python3
# Script to read a GDS file, modify the given string, and rewrite the GDS file.
# The string may be a substring;  the GDS file will be parsed completely for
# library name, structure name, instance name, and other strings, and the
# replacement made everywhere it occurs, finding the bounds of the entire
# string around the search text, and adjusting the record bounds accordingly.

import os
import sys

def usage():
    print('change_gds_string.py <old_string> <new_string> <path_to_gds_in> [<path_to_gds_out>]')

if __name__ == '__main__':
    debug = False

    if len(sys.argv) == 1:
        print("No options given to change_gds_string.py.")
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
        print("Wrong number of arguments given to change_gds_string.py.")
        usage()
        sys.exit(0)

    if '-debug' in optionlist:
        debug = True

    oldstring = arguments[0]
    newstring = arguments[1]
    source = arguments[2]

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

    # To be done:  Allow the user to select a specific record type or types
    # in which to restrict the string substitution.  If no restrictions are
    # specified, then substitue in library name, structure name, and strings.

    recordtypes = ['libname', 'strname', 'sname', 'string']
    recordfilter = [2, 6, 18, 25]
    bsearch = bytes(oldstring, 'ascii')
    brep = bytes(newstring, 'ascii')

    datalen = len(gdsdata)
    if debug:
        print('Original data length = ' + str(datalen))
    dataptr = 0
    while dataptr < datalen:
        # Read stream records up to any string, then search for search text.
        bheader = gdsdata[dataptr:dataptr + 2]
        reclen = int.from_bytes(bheader, 'big')
        newlen = reclen
        if newlen == 0:
            print('Error: found zero-length record at position ' + str(dataptr))
            break

        rectype = gdsdata[dataptr + 2]
        datatype = gdsdata[dataptr + 3]

        if rectype in recordfilter:
            # Datatype 6 is STRING
            if datatype == 6:
                if debug:
                    print('Record type = ' + str(rectype) + ' data type = ' + str(datatype) + ' length = ' + str(reclen))

                bstring = gdsdata[dataptr + 4: dataptr + reclen]
                repstring = bstring.replace(bsearch, brep)
                if repstring != bstring:
                    before = gdsdata[0:dataptr]
                    after = gdsdata[dataptr + reclen:]
                    newlen = len(repstring) + 4
                    # Record sizes must be even
                    if newlen % 2 != 0:
                        # Was original string padded with null byte?  If so,
                        # remove the null byte and reduce newlen.  Otherwise,
                        # add a null byte and increase newlen.
                        if bstring[-1] == 0:
                            repstring = repstring[0:-1]
                            newlen -= 1
                        else:
                            repstring += b'\x00'
                            newlen += 1
                            
                    bnewlen = newlen.to_bytes(2, byteorder='big')
                    brectype = rectype.to_bytes(1, byteorder='big')
                    bdatatype = datatype.to_bytes(1, byteorder='big')

                    # Assemble the new record
                    newrecord = bnewlen + brectype + bdatatype + repstring
                    # Reassemble the GDS data around the new record
                    gdsdata = before + newrecord[0:newlen] + after
                    # Adjust the data end location
                    datalen += (newlen - reclen)

                    if debug:
                        print('Replaced ' + str(bstring) + ' with ' + str(repstring)) 

        # Advance the pointer past the data
        dataptr += newlen

    with open(dest, 'wb') as ofile:
        ofile.write(gdsdata)

    exit(0)
