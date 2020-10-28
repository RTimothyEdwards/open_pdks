# Tcl script input to magic to generate seal ring GDS
tech load sky130seal_ring -noprompt
drc off
load advSeal_6um_gen
select top cell
expand
cif *hier write disable
cif *array write disable
gds write advSeal_6um_gen
quit
