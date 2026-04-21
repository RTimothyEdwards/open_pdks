# Process node
set ::env(PROCESS) 130
set ::env(DEF_UNITS_PER_MICRON) 1000

if { ![info exist ::env(STD_CELL_LIBRARY)] } {
	set ::env(STD_CELL_LIBRARY) sky130_fd_sc_hd
}

if { ![info exist ::env(PAD_CELL_LIBRARY)] } {
	set ::env(PAD_CELL_LIBRARY) sky130_ef_io
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
set ::env(TECH_LEFS) [dict create]
dict set ::env(TECH_LEFS) "nom_*" [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY)__nom.tlef"]
dict set ::env(TECH_LEFS) "min_*" [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY)__min.tlef"]
dict set ::env(TECH_LEFS) "max_*" [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY)__max.tlef"]

# Corners
set ::env(STA_CORNERS) "\
    nom_tt_025C_1v80 \
    nom_ss_100C_1v60 \
    nom_ff_n40C_1v95 \
    min_tt_025C_1v80 \
    min_ss_100C_1v60 \
    min_ff_n40C_1v95 \
    max_tt_025C_1v80 \
    max_ss_100C_1v60 \
    max_ff_n40C_1v95 \
"

set ::env(DEFAULT_CORNER) "nom_tt_025C_1v80"

# Check all timing corners
set ::env(TIMING_VIOLATION_CORNERS) "*"

# Technology lib
set ::env(CELL_LIBS) [dict create]
dict set ::env(CELL_LIBS) "*_tt_025C_1v80" "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_1v80.lib\
"
dict set ::env(CELL_LIBS) "*_ff_n40C_1v95" "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_1v95.lib\
"
dict set ::env(CELL_LIBS) "*_ss_100C_1v60" "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_100C_1v60.lib\
"

# Standard cells
set ::env(CELL_LEFS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lef/*.lef"]
set ::env(CELL_GDS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/gds/*.gds"]
set ::env(CELL_VERILOG_MODELS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/verilog/$::env(STD_CELL_LIBRARY).v"
set ::env(CELL_SPICE_MODELS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/spice/*.spice"]
set ::env(CELL_CDLS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/cdl/$::env(STD_CELL_LIBRARY).cdl"

# Pad cells
set ::env(PAD_LEFS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lef/*.lef"]
set ::env(PAD_GDS) "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/gds/sky130_fd_io.gds \
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/gds/sky130_ef_io.gds \
"
set ::env(PAD_VERILOG_MODELS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/verilog/$::env(PAD_CELL_LIBRARY)__blackbox_pp.v"
set ::env(PAD_SPICE_MODELS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/spice/$::env(PAD_CELL_LIBRARY).spice"
set ::env(PAD_CDLS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/cdl/*.cdl"]

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
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/tracks.info"

# Latch mapping
set ::env(SYNTH_LATCH_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/latch_map.v"

# Tri-state buffer mapping
set ::env(TRISTATE_BUFFER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/tribuff_map.v"

# Full adder mapping
set ::env(FULL_ADDER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/fa_map.v"

# Ripple carry adder mapping
set ::env(RIPPLE_CARRY_ADDER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/rca_map.v"

# Carry select adder mapping
set ::env(CARRY_SELECT_ADDER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/csa_map.v"

# Default No Synth List
set ::env(NO_SYNTH_CELL_LIST) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/no_synth.cells"

# Default DRC Exclude List
set ::env(DRC_EXCLUDE_CELL_LIST) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/drc_exclude.cells"

# Open-RCX Rules File
set ::env(RCX_RULES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).nom.spef_extractor"
set ::env(RCX_RULES_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).min.spef_extractor"
set ::env(RCX_RULES_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).max.spef_extractor"
if { [file exists "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).nom.calibre"] } {
	set ::env(RCX_RULES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).nom.calibre"
	set ::env(RCX_RULES_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).min.calibre"
	set ::env(RCX_RULES_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).max.calibre"
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
set ::env(CVC_SCRIPTS_DIR) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/cvc"

