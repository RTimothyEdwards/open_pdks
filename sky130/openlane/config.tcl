# Process node
set ::env(PROCESS) 130
set ::env(DEF_UNITS_PER_MICRON) 1000

if { ![info exist ::env(STD_CELL_LIBRARY)] } {
	set ::env(STD_CELL_LIBRARY) sky130_fd_sc_hd
}
if { ![info exist ::env(STD_CELL_LIBRARY_OPT)] } {
	set ::env(STD_CELL_LIBRARY_OPT) sky130_fd_sc_hd
}

# Placement site for core cells
# This can be found in the technology lef
set ::env(VDD_PIN) "VPWR"
set ::env(GND_PIN) "VGND"

set ::env(VDD_PIN_VOLTAGE) "1.80"
set ::env(GND_PIN_VOLTAGE) "0.00"

set ::env(STD_CELL_POWER_PINS) "VPWR VPB"
set ::env(STD_CELL_GROUND_PINS) "VGND VNB"

# Technology LEF
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
# sky130_fd_io.v is not parsable by yosys, so it cannot be included it here just yet...
set ::env(GPIO_PADS_VERILOG) "\
	$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_io/verilog/sky130_ef_io.v
"

set ::env(GPIO_PADS_PREFIX) "sky130_fd_io sky130_ef_io"

# Optimization library
set ::env(TECH_LEF_OPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/techlef/$::env(STD_CELL_LIBRARY_OPT)__nom.tlef"
set ::env(CELLS_LEF_OPT) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/lef/*.lef"]
set ::env(GDS_FILES_OPT) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/gds/*.gds"]
set ::env(STD_CELL_LIBRARY_OPT_CDL)	"$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY_OPT)/cdl/$::env(STD_CELL_LIBRARY_OPT).cdl"

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
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/TECHNAME.magicrc"
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/TECHNAME.tech"

# Klayout setup
set ::env(KLAYOUT_TECH) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/$::env(PDK).lyt"
set ::env(KLAYOUT_PROPERTIES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/$::env(PDK).lyp"
set ::env(KLAYOUT_DEF_LAYER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/$::env(PDK).map"
set ::env(KLAYOUT_XOR_IGNORE_LAYERS) "81/14"
set ::env(KLAYOUT_DRC_OPTIONS) [dict create beol 1 feol 1 floating_metal 0 seal 1 offgrid 1] ; # based on KLAYOUT_DRC_RUNSET options
set ::env(KLAYOUT_DRC_RUNSET) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/drc/$::env(PDK)_mr.drc"
#set ::env(KLAYOUT_DRC_TECH) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/$::env(PDK).lydrc"

# netgen setup
set ::env(NETGEN_SETUP_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/netgen/TECHNAME_setup.tcl"
# CTS luts

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
if { [file exists "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).nom.calibre"] } {
	set ::env(RCX_RULES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).nom.calibre"
	set ::env(RCX_RULES_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).min.calibre"
	set ::env(RCX_RULES_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/rules.openrcx.$::env(PDK).max.calibre"
}

# Extra PDN configs
set ::env(FP_PDN_RAIL_LAYER) met1
set ::env(FP_PDN_VERTICAL_LAYER) met4
set ::env(FP_PDN_HORIZONTAL_LAYER) met5
set ::env(FP_PDN_RAIL_OFFSET) 0
set ::env(FP_PDN_VWIDTH) 1.6
set ::env(FP_PDN_HWIDTH) 1.6
set ::env(FP_PDN_VSPACING) 1.7
set ::env(FP_PDN_HSPACING) 1.7
set ::env(FP_PDN_VOFFSET) 16.32
set ::env(FP_PDN_VPITCH) 153.6
set ::env(FP_PDN_HOFFSET) 16.65
set ::env(FP_PDN_HPITCH) 153.18


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
set ::env(DATA_WIRE_RC_LAYER) "met2"
set ::env(CLOCK_WIRE_RC_LAYER) "met5"

# I/O Layer info
set ::env(FP_IO_HLAYER) "met3"
set ::env(FP_IO_VLAYER) "met2"

# Routing Layer Info
set ::env(GRT_LAYER_ADJUSTMENTS) "0.99,0,0,0,0,0"

set ::env(RT_MIN_LAYER) "met1"
set ::env(RT_MAX_LAYER) "met5"

set ::env(RT_CLOCK_MIN_LAYER) "met3"

# CVC
set ::env(CVC_SCRIPTS_DIR) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/cvc"

