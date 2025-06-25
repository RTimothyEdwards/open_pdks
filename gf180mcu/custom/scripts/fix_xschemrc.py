#!/usr/bin/env python3
#
# fix_xschemrc.py ---
#
# Special-purpose script that does the work of modifying a few items in
# the source xschemrc file to make it open_pdks-specific

import sys

if len(sys.argv) != 3:
    print('Usage:  fix_xschemrc.py <filename> <techname>')
    sys.exit(1)
else:
    file_name = sys.argv[1]
    tech_name = sys.argv[2]

with open(file_name, 'r') as ifile:
    xlines = ifile.read().splitlines()

# Replace lines which assume PDK is in the user directory above
outlines = []
skipnext = 0
for line in xlines:
    if skipnext == 0:
        if 'trying to find' in line:
            skipnext = 2
        elif '/models/ngspice' in line:
            # Path matches library source structure;  change to open_pdks structure
            line = line.replace('/models/', '/' + tech_name + '/libs.tech/')
        outlines.append(line)
    else:
        skipnext -= 1
        if skipnext == 0:
            outlines.append('  if {[file isdir /usr/share/pdk]} {set PDK_ROOT /usr/share/pdk')
            outlines.append('  } elseif {[file isdir /usr/local/share/pdk]} {set PDK_ROOT /usr/local/share/pdk')
            outlines.append('  } elseif {[file isdir $env(HOME)/share/pdk]} {set PDK_ROOT $env(HOME)/share/pdk')

# Append these lines:
outlines.append('')
outlines.append('# open_pdks-specific')
outlines.append('set XSCHEM_START_WINDOW ${PDK_ROOT}/' + tech_name + '/libs.tech/xschem/tests/0_top.sch')
outlines.append('append XSCHEM_LIBRARY_PATH :${PDK_ROOT}/' + tech_name + '/libs.tech/xschem/tests')
outlines.append('append XSCHEM_LIBRARY_PATH :${PDK_ROOT}/' + tech_name + '/libs.tech/xschem')
outlines.append('')
outlines.append('# allow a user-specific path add-on')
outlines.append('if { [info exists ::env(XSCHEM_USER_LIBRARY_PATH) ] } {')
outlines.append('    append XSCHEM_LIBRARY_PATH :$env(XSCHEM_USER_LIBRARY_PATH)')
outlines.append('}')

# Write back into the same file
with open(file_name, 'w') as ofile:
    for line in outlines:
        print(line, file=ofile)

print("Done!")
