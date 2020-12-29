$OPENLANE_ROOT/scripts/rectify_above.py -1.5 \
	sky130_ef_io__gpiov2_pad < ../../../../libs.ref/sky130_fd_io/lef/sky130_ef_io.lef |
	$OPENLANE_ROOT/scripts/obs_above.py -1.35 0.16 0.16 \
	sky130_ef_io__gpiov2_pad > sky130_ef_io.obs.gpiov2.lef.tmp

# $OPENLANE_ROOT/scripts/rectify_above.py 0 \
# 	sky130_ef_io__com_bus_slice_20um \
# 	sky130_ef_io__com_bus_slice_10um \
# 	sky130_ef_io__com_bus_slice_5um \
# 	sky130_ef_io__com_bus_slice_1um \
# 	sky130_ef_io__corner_pad < sky130_ef_io.obs.gpiov2.lef.tmp |
# 	$OPENLANE_ROOT/scripts/obs_above.py 0 0 0 \
# 	sky130_ef_io__com_bus_slice_20um \
# 	sky130_ef_io__com_bus_slice_10um \
# 	sky130_ef_io__com_bus_slice_5um \
# 	sky130_ef_io__com_bus_slice_1um \
# 	sky130_ef_io__corner_pad > sky130_ef_io.rect.obs.corner.lef.tmp

$OPENLANE_ROOT/scripts/rectify_above.py 0 \
	sky130_ef_io__vccd_hvc_pad \
	sky130_ef_io__vdda_hvc_pad \
	sky130_ef_io__vdda_hvc_clamped_pad \
	sky130_ef_io__vssa_hvc_pad \
	sky130_ef_io__vssa_hvc_clamped_pad \
	sky130_ef_io__vssd_hvc_pad \
	sky130_ef_io__vddio_hvc_pad \
	sky130_ef_io__vddio_hvc_clamped_pad \
	sky130_ef_io__vssio_hvc_pad \
	sky130_ef_io__vssio_hvc_clamped_pad \
	< sky130_ef_io.obs.gpiov2.lef.tmp |
	$OPENLANE_ROOT/scripts/obs_above.py 0 0 0 \
	sky130_ef_io__vccd_hvc_pad \
	sky130_ef_io__vdda_hvc_pad \
	sky130_ef_io__vdda_hvc_clamped_pad \
	sky130_ef_io__vssa_hvc_pad \
	sky130_ef_io__vssa_hvc_clamped_pad \
	sky130_ef_io__vssd_hvc_pad \
	sky130_ef_io__vddio_hvc_pad \
	sky130_ef_io__vddio_hvc_clamped_pad \
	sky130_ef_io__vssio_hvc_pad \
	sky130_ef_io__vssio_hvc_clamped_pad \
	> sky130_ef_io.rect.obs.hvc.lef.tmp

$OPENLANE_ROOT/scripts/rectify_above.py 1.4 \
	sky130_ef_io__vccd_lvc_pad \
	sky130_ef_io__vccd_lvc_clamped_pad \
	sky130_ef_io__vccd_lvc_clamped2_pad \
	sky130_ef_io__vdda_lvc_pad \
	sky130_ef_io__vssa_lvc_pad \
	sky130_ef_io__vssd_lvc_pad \
	sky130_ef_io__vssd_lvc_clamped_pad \
	sky130_ef_io__vssd_lvc_clamped2_pad \
	sky130_ef_io__vddio_lvc_pad \
	sky130_ef_io__vssio_lvc_pad < sky130_ef_io.rect.obs.hvc.lef.tmp |
	$OPENLANE_ROOT/scripts/obs_above.py 1.4 0 0 \
	sky130_ef_io__vccd_lvc_pad \
	sky130_ef_io__vccd_lvc_clamped_pad \
	sky130_ef_io__vccd_lvc_clamped2_pad \
	sky130_ef_io__vdda_lvc_pad \
	sky130_ef_io__vssa_lvc_pad \
	sky130_ef_io__vssd_lvc_pad \
	sky130_ef_io__vssd_lvc_clamped_pad \
	sky130_ef_io__vssd_lvc_clamped2_pad \
	sky130_ef_io__vddio_lvc_pad \
	sky130_ef_io__vssio_lvc_pad > sky130_ef_io.rect.obs.lvc.lef.tmp

# clean up
$OPENLANE_ROOT/scripts/remove_empty_pins.py < sky130_ef_io.rect.obs.lvc.lef.tmp |
	$OPENLANE_ROOT/scripts/remove_empty_ports.py > sky130_ef_io_core.lef

rm *.tmp
