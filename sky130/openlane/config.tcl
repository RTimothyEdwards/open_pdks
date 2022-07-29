# Process node
set ::env(PROCESS) 130
set ::env(DEF_UNITS_PER_MICRON) 1000

# Placement site for core cells
# This can be found in the technology lef

set ::env(VDD_PIN) "VPWR"
set ::env(GND_PIN) "VGND"

set ::env(STD_CELL_POWER_PINS) "VPWR VPB"
set ::env(STD_CELL_GROUND_PINS) "VGND VNB"

# Technology LEF
#ifdef EF_FORMAT
set ::env(TECH_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/techLEF/$::env(STD_CELL_LIBRARY)/$::env(STD_CELL_LIBRARY)__nom.tlef"
set ::env(TECH_LEF_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/techLEF/$::env(STD_CELL_LIBRARY)/$::env(STD_CELL_LIBRARY)__min.tlef"
set ::env(TECH_LEF_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/techLEF/$::env(STD_CELL_LIBRARY)/$::env(STD_CELL_LIBRARY)__max.tlef"
set ::env(CELLS_LEF) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/$::env(STD_CELL_LIBRARY)/*.lef"]
set ::env(GDS_FILES) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/gds/$::env(STD_CELL_LIBRARY)/*.gds"]
set ::env(STD_CELL_LIBRARY_CDL)	"$::env(PDK_ROOT)/$::env(PDK)/libs.ref/cdl/$::env(STD_CELL_LIBRARY)/$::env(STD_CELL_LIBRARY).cdl"

set ::env(GPIO_PADS_LEF) "\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/sky130_fd_io/sky130_fd_io.lef\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/sky130_fd_io/sky130_ef_io.lef\
"
# sky130_fd_io.v is not parsable by yosys, so it cannot be included it here yet...
set ::env(GPIO_PADS_VERILOG) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/verilog/sky130_fd_io/sky130_ef_io.v"
set ::env(GPIO_PADS_VERILOG) "\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/verilog/sky130_fd_io/sky130_ef_io.v\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/verilog/sky130_fd_io/sky130_ef_io__gpiov2_pad_wrapped.v\
"

# Optimization library
set ::env(TECH_LEF_OPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/techLEF/$::env(STD_CELL_LIBRARY_OPT)/$::env(STD_CELL_LIBRARY_OPT)__nom.tlef"
set ::env(CELLS_LEF_OPT) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/$::env(STD_CELL_LIBRARY_OPT)/*.lef"]
set ::env(GDS_FILES_OPT) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/gds/$::env(STD_CELL_LIBRARY_OPT)/*.gds"]
set ::env(STD_CELL_LIBRARY_OPT_CDL)	"$::env(PDK_ROOT)/$::env(PDK)/libs.ref/cdl/$::env(STD_CELL_LIBRARY_OPT)/$::env(STD_CELL_LIBRARY_OPT).cdl"

#else (!EF_FORMAT)
set ::env(TECH_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY)__nom.tlef"
set ::env(TECH_LEF_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY)__min.tlef"
set ::env(TECH_LEF_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY)__max.tlef"
set ::env(CELLS_LEF) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lef/*.lef"]
set ::env(GDS_FILES) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/gds/*.gds"]
set ::env(STD_CELL_LIBRARY_CDL)	"$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/cdl/$::env(STD_CELL_LIBRARY).cdl"

set ::env(GPIO_PADS_LEF) "\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_io/lef/sky130_fd_io.lef\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_io/lef/sky130_ef_io.lef\
"

set ::env(GPIO_PADS_VERILOG) "\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_io/verilog/sky130_ef_io.v\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_io/verilog/sky130_ef_io__gpiov2_pad_wrapped.v\
"

# Optimization library
set ::env(TECH_LEF_OPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/techlef/$::env(STD_CELL_LIBRARY_OPT)__nom.tlef"
set ::env(CELLS_LEF_OPT) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/lef/*.lef"]
set ::env(GDS_FILES_OPT) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/gds/*.gds"]
set ::env(STD_CELL_LIBRARY_OPT_CDL)	"$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/cdl/$::env(STD_CELL_LIBRARY_OPT).cdl"

#endif (!EF_FORMAT)

# Optimization library slowest corner
set tmp $::env(STD_CELL_LIBRARY)
set ::env(STD_CELL_LIBRARY) $::env(STD_CELL_LIBRARY_OPT)
source "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY_OPT)/config.tcl"
set ::env(LIB_SLOWEST_OPT) $::env(LIB_SLOWEST)
set ::env(STD_CELL_LIBRARY) $tmp
source "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/config.tcl"

set ::env(GPIO_PADS_LEF_CORE_SIDE) "\
	$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/custom_cells/lef/sky130_fd_io_core.lef\
	$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/custom_cells/lef/sky130_ef_io_core.lef\
"

# magic setup
#ifdef EF_FORMAT
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/current/TECHNAME.magicrc"
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/current/TECHNAME.tech"
#else (!EF_FORMAT)
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/TECHNAME.magicrc"
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/TECHNAME.tech"
#endif (!EF_FORMAT)

# Klayout setup
set ::env(KLAYOUT_TECH) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/$::env(PDK).lyt"
set ::env(KLAYOUT_PROPERTIES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/$::env(PDK).lyp"
set ::env(KLAYOUT_DRC_TECH_SCRIPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/drc/$::env(PDK)_mr.drc"
#set ::env(KLAYOUT_DRC_TECH) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/$::env(PDK).lydrc"

# netgen setup
set ::env(NETGEN_SETUP_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/netgen/TECHNAME_setup.tcl"
# CTS luts
set ::env(CTS_TECH_DIR) "N/A"

set ::env(CTS_SQR_CAP) 0.258e-3
set ::env(CTS_SQR_RES) 0.125
set ::env(FP_TAPCELL_DIST) 13

# Tracks info
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/tracks.info"

# Latch mapping
set ::env(SYNTH_LATCH_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/latch_map.v"

# Tri-state buffer mapping
set ::env(TRISTATE_BUFFER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/tribuff_map.v"

# Full adder mapping
set ::env(FULL_ADDER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/fa_map.v"

# Ripple carry adder mapping
set ::env(RIPPLE_CARRY_ADDER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/rca_map.v"

# Carry select adder mapping
set ::env(CARRY_SELECT_ADDER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/csa_map.v"

# Default No Synth List
set ::env(NO_SYNTH_CELL_LIST) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/no_synth.cells"

# Default DRC Exclude List
set ::env(DRC_EXCLUDE_CELL_LIST) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/drc_exclude.cells"

# DRC Exclude List for Optimization library
set ::env(DRC_EXCLUDE_CELL_LIST_OPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY_OPT)/drc_exclude.cells"

# Open-RCX Rules File
set ::env(RCX_RULES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).nom.spef_extractor"
set ::env(RCX_RULES_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).min.spef_extractor"
set ::env(RCX_RULES_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).max.spef_extractor"

# Extra PDN configs
set ::env(FP_PDN_RAILS_LAYER) met1
set ::env(FP_PDN_LOWER_LAYER) met4
set ::env(FP_PDN_UPPER_LAYER) met5
set ::env(FP_PDN_RAIL_OFFSET) 0
set ::env(FP_PDN_VWIDTH) 1.6
set ::env(FP_PDN_HWIDTH) 1.6
set ::env(FP_PDN_VSPACING) 1.7
set ::env(FP_PDN_HSPACING) 1.7

# Core Ring PDN defaults
set ::env(FP_PDN_CORE_RING_VWIDTH) 1.6
set ::env(FP_PDN_CORE_RING_HWIDTH) 1.6
set ::env(FP_PDN_CORE_RING_VSPACING) 1.7
set ::env(FP_PDN_CORE_RING_HSPACING) 1.7
set ::env(FP_PDN_CORE_RING_VOFFSET) 6
set ::env(FP_PDN_CORE_RING_HOFFSET) 6

# PDN Macro blockages list
set ::env(MACRO_BLOCKAGES_LAYER) "li1 met1 met2 met3 met4"

# Used for parasitics estimation, IR drop analysis, etc
set ::env(WIRE_RC_LAYER) "met1"
set ::env(DATA_WIRE_RC_LAYER) "met2"
set ::env(CLOCK_WIRE_RC_LAYER) "met5"

# I/O Layer info
set ::env(FP_IO_HLAYER) "met3"
set ::env(FP_IO_VLAYER) "met2"

# Routing Layer Info
set ::env(GLB_RT_LAYER_ADJUSTMENTS) "0.99,0,0,0,0,0"

set ::env(RT_MIN_LAYER) "met1"
set ::env(RT_MAX_LAYER) "met5"

# CVC
set ::env(CVC_SCRIPTS_DIR) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/cvc"