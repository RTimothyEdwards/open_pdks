#!/bin/sh
#
# generate_lef_views.sh ---
#
# Read all of the cell names from "topcells.txt" and generate LEF views
# from them.  Then write those files to the ../lef directory.
#
allcells=`cat topcells.txt`

magic -dnull -noconsole -rcfile /usr/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc << EOF
drc off
crashbackups stop
set cells $allcells
foreach cell \$cells {
   load \$cell
   lef write -hide
}
quit -noprompt
EOF

mv *.lef ../lef/

exit 0
