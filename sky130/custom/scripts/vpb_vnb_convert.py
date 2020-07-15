#!/usr/bin/env python3
#
# Convert VNB and VPB layers in a LEF file from "li1" or "met1" to
# "pwell" and "nwell" masterslice layers, as they should be. 
#

import os
import sys
import re

if len(sys.argv) < 3:
    print("Usage: vpb_vnb_convert.py <lef_file_in> <lef_file_out>")
    sys.exit(1)

lef_file_in = sys.argv[1]
lef_file_out = sys.argv[2]

print("Input:  " + lef_file_in)
print("Output:  " + lef_file_out)

with open(lef_file_in, 'r') as ifile:
    leflines = ifile.read().splitlines()

layrex = re.compile('[ \t]*LAYER[ \t]+([^ \t]+)[ \t]+;')
pinrex = re.compile('[ \t]*PIN[ \t]+([^ \t\n]+)')
endrex = re.compile('[ \t]*END[ \t]+([^ \t\n]+)')
subrex = re.compile('([ \t]*LAYER[ \t]+)([^ \t]+)([ \t]+;)')

vpbpin = False
vnbpin = False

linesout = []

for line in leflines:
    lineout = line

    lmatch = layrex.match(line)
    pmatch = pinrex.match(line)
    ematch = endrex.match(line)

    if pmatch:
        pinname = pmatch.group(1)

        if pinname == 'VNB':
            vnbpin = True
        elif pinname == 'VPB':
            vpbpin = True

    elif ematch:
        pinname = ''
        vnbpin = False
        vpbpin = False

    elif lmatch:
        if vpbpin:
           lineout = subrex.sub(r'\1nwell\3', line)
        elif vnbpin:
           lineout = subrex.sub(r'\1pwell\3', line)
    
    linesout.append(lineout)

with open(lef_file_out, 'w') as ofile:
    for line in linesout:
        print(line, file=ofile)
