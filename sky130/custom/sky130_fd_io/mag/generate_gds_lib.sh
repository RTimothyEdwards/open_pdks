#!/bin/sh
#
# generate_gds_lib.sh ---
#
# Generate the GDS according to the instructions in README.
#

magic -dnull -noconsole -rcfile /usr/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc << EOF
drc off
crashbackups stop
load sky130_ef_io
cif *hier write disable
gds library true
gds addendum true
gds write sky130_ef_io
EOF

exit 0
