$OPENLANE_ROOT/scripts/rectify_above.py 1.635 sky130_fd_io__top_xres4v2 < ../../../../libs.ref/sky130_fd_io/lef/sky130_fd_io.lef |
	$OPENLANE_ROOT/scripts/obs_above.py 1.635 0 0 sky130_fd_io__top_xres4v2 > sky130_fd_io_core.lef.tmp

# clean up
$OPENLANE_ROOT/scripts/remove_empty_pins.py < sky130_fd_io_core.lef.tmp |
	$OPENLANE_ROOT/scripts/remove_empty_ports.py > sky130_fd_io_core.lef

rm *.tmp
