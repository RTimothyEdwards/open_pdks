# Process node
set ::env(PROCESS) 180
set ::env(DEF_UNITS_PER_MICRON) 2000

set ::env(VDD_PIN) "VDD"
set ::env(GND_PIN) "VSS"
set ::env(VDD_PIN_VOLTAGE) "5.00"
set ::env(GND_PIN_VOLTAGE) "0.00"

set ::env(STD_CELL_POWER_PINS) "VDD VNW"
set ::env(STD_CELL_GROUND_PINS) "VSS VPW"

if { ![info exist ::env(STD_CELL_LIBRARY)] } {
    set ::env(STD_CELL_LIBRARY) gf180mcu_fd_sc_mcu7t5v0
}

if { ![info exist ::env(PAD_CELL_LIBRARY)] } {
    set ::env(PAD_CELL_LIBRARY) gf180mcu_fd_io
}


# Technology lib
set ::env(LIB) [dict create]
dict set ::env(LIB) *_tt_025C_5v00 "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_5v00.lib\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__tt_025C_5v00.lib]\
"
dict set ::env(LIB) *_ff_n40C_5v50 "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_5v50.lib\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__ff_n40C_5v50.lib]\
"
dict set ::env(LIB) *_ss_125C_4v50 "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_125C_4v50.lib\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__ss_125C_4v50.lib]\
"

# Corners
set ::env(STA_CORNERS) "\
nom_tt_025C_5v00 \
nom_ss_125C_4v50 \
nom_ff_n40C_5v50 \
min_tt_025C_5v00 \
min_ss_125C_4v50 \
min_ff_n40C_5v50 \
max_tt_025C_5v00 \
max_ss_125C_4v50 \
max_ff_n40C_5v50 \
"

set ::env(DEFAULT_CORNER) "nom_tt_025C_5v00"

set ::env(TIMING_VIOLATION_CORNERS) "*tt*"

# Technology LEF
set ::env(TECH_LEFS) [dict create]
dict set ::env(TECH_LEFS) nom_* [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/*__nom.tlef"]
dict set ::env(TECH_LEFS) min_* [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/*__min.tlef"]
dict set ::env(TECH_LEFS) max_* [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/*__max.tlef"]

# Standard cells
set ::env(CELL_LEFS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lef/*.lef"]
set ::env(CELL_GDS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/gds/*.gds"]
set ::env(CELL_VERILOG_MODELS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/verilog/$::env(STD_CELL_LIBRARY).v"
set ::env(CELL_SPICE_MODELS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/spice/$::env(STD_CELL_LIBRARY).spice"
set ::env(CELL_CDLS)	"$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/cdl/$::env(STD_CELL_LIBRARY).cdl"

# Pad cells
set ::env(PAD_LEFS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lef/*.lef"]
# Unfortunately, the foundry library must be read in before the ef or ws library (ghost cell)
set ::env(PAD_GDS) "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/gds/gf180mcu_fd_io.gds\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/gds/gf180mcu_ef_io.gds\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/gds/gf180mcu_ws_io.gds\
"
set ::env(PAD_VERILOG_MODELS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/verilog/*__blackbox.v"]
set ::env(PAD_SPICE_MODELS) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/spice/*.spice"]
set ::env(PAD_CDLS) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/cdl/$::env(PAD_CELL_LIBRARY).cdl"

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
set ::env(SYNTH_EXCLUDED_CELL_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/synth_exclude.cells"

# Default DRC Exclude List
set ::env(PNR_EXCLUDED_CELL_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/pnr_exclude.cells"

# Open-RCX Rules File
set ::env(RCX_RULES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rcx_rules.info"

# Floorplanning

# I/O Layer info
set ::env(FP_IO_HLAYER) "Metal3"
set ::env(FP_IO_VLAYER) "Metal2"

# PDN Macro blockages list
set ::env(MACRO_BLOCKAGES_LAYER) "Metal1 Metal2 Metal3 Metal4 Metal5"

## Tap Cell Dist
set ::env(FP_TAPCELL_DIST) 20

# Extra PDN configs
set ::env(FP_PDN_RAIL_LAYER) "Metal1"
set ::env(FP_PDN_RAIL_OFFSET) 0

set ::env(FP_PDN_VERTICAL_LAYER) "Metal4"
set ::env(FP_PDN_HORIZONTAL_LAYER) "Metal5"

set ::env(FP_PDN_VWIDTH) 1.6
set ::env(FP_PDN_HWIDTH) 1.6
set ::env(FP_PDN_VSPACING) 1.7
set ::env(FP_PDN_HSPACING) 1.7
set ::env(FP_PDN_VOFFSET) 16.32
set ::env(FP_PDN_VPITCH) 153.6
set ::env(FP_PDN_HOFFSET) 16.65
set ::env(FP_PDN_HPITCH) 153.18

## Core Ring PDN defaults
set ::env(FP_PDN_CORE_RING_VWIDTH) 1.6
set ::env(FP_PDN_CORE_RING_HWIDTH) 1.6
set ::env(FP_PDN_CORE_RING_VSPACING) 1.7
set ::env(FP_PDN_CORE_RING_HSPACING) 1.7
set ::env(FP_PDN_CORE_RING_VOFFSET) 6
set ::env(FP_PDN_CORE_RING_HOFFSET) 6

# Timing
set ::env(RCX_RULES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).nom"
set ::env(RCX_RULES_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).min"
set ::env(RCX_RULES_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/rules.openrcx.$::env(PDK).max"

# Routing
set ::env(METAL_LAYER_NAMES) "Metal1 Metal2 Metal3 Metal4 Metal5"
set ::env(RT_MIN_LAYER) "Metal2" ;# stdcells heavily use Metal1 - setting it to Metal1 will cause congestions
set ::env(RT_MAX_LAYER) "Metal5"
set ::env(DRT_MIN_LAYER) "Metal1"
set ::env(GRT_LAYER_ADJUSTMENTS) "0,0,0,0,0"

## Tracks info
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/tracks.info"

# Signoff
## Magic
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/$::env(PDK).magicrc"
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/$::env(PDK).tech"

## Klayout
set ::env(KLAYOUT_TECH) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/gf180mcu.lyt"
set ::env(KLAYOUT_PROPERTIES) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/gf180mcu.lyp"
set ::env(KLAYOUT_DEF_LAYER_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/gf180mcu.map"

set ::env(KLAYOUT_DRC_RUNSET) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/drc/gf180mcu.drc"
set ::env(KLAYOUT_DRC_OPTIONS) [dict create]
dict set ::env(KLAYOUT_DRC_OPTIONS) feol true
dict set ::env(KLAYOUT_DRC_OPTIONS) beol true
dict set ::env(KLAYOUT_DRC_OPTIONS) dummy true
dict set ::env(KLAYOUT_DRC_OPTIONS) dummy_no_sub_prev true
dict set ::env(KLAYOUT_DRC_OPTIONS) offgrid true
dict set ::env(KLAYOUT_DRC_OPTIONS) conn_drc true
dict set ::env(KLAYOUT_DRC_OPTIONS) wedge true
dict set ::env(KLAYOUT_DRC_OPTIONS) run_mode "deep"

set ::env(KLAYOUT_DENSITY_RUNSET) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/drc/rule_decks/density.drc"
set ::env(KLAYOUT_DENSITY_OPTIONS) [dict create]
dict set ::env(KLAYOUT_DENSITY_OPTIONS) run_mode "tiling"

set ::env(KLAYOUT_ANTENNA_RUNSET) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/drc/rule_decks/antenna.drc"
set ::env(KLAYOUT_ANTENNA_OPTIONS) [dict create]
dict set ::env(KLAYOUT_ANTENNA_OPTIONS) run_mode "deep"

set ::env(KLAYOUT_FILLER_SCRIPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/drc/filler_generation/fill_all.rb"
set ::env(KLAYOUT_FILLER_OPTIONS) [dict create]

set ::env(KLAYOUT_LVS_SCRIPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/lvs/gf180mcu.lvs"
set ::env(KLAYOUT_LVS_OPTIONS) [dict create run_mode deep]

## Netgen
set ::env(NETGEN_SETUP_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/netgen/$::env(PDK)_setup.tcl"

# Used for parasitics estimation, IR drop analysis, etc
set ::env(LAYERS_RC) [dict create]

# RC fit from OpenROAD
# https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/flow/platforms/gf180/setRC.tcl
dict set ::env(LAYERS_RC) "*" Metal2 res 3.85861E-04
dict set ::env(LAYERS_RC) "*" Metal2 cap 1.35357E-04
dict set ::env(LAYERS_RC) "*" Metal3 res 2.06673E-04
dict set ::env(LAYERS_RC) "*" Metal3 cap 1.46141E-04
dict set ::env(LAYERS_RC) "*" Metal4 res 1.68609E-04
dict set ::env(LAYERS_RC) "*" Metal4 cap 1.50688E-04
dict set ::env(LAYERS_RC) "*" Metal5 res 7.92778E-05
dict set ::env(LAYERS_RC) "*" Metal5 cap 1.55595E-04

set ::env(VIAS_R) [dict create]

# Best case (and used for nom)
dict set ::env(VIAS_R) "*" Via1 res 4.23
dict set ::env(VIAS_R) "*" Via2 res 4.23
dict set ::env(VIAS_R) "*" Via3 res 4.23
dict set ::env(VIAS_R) "*" Via4 res 4.23

# Worst case (last one wins)
dict set ::env(VIAS_R) "max_*" Via1 res 16.845
dict set ::env(VIAS_R) "max_*" Via2 res 16.845
dict set ::env(VIAS_R) "max_*" Via3 res 16.845
dict set ::env(VIAS_R) "max_*" Via4 res 16.845

set ::env(SIGNAL_WIRE_RC_LAYERS) "Metal2 Metal3 Metal4"
set ::env(CLOCK_WIRE_RC_LAYERS) "Metal2 Metal3 Metal4"

# Base SDC

# in ns
set ::env(CLOCK_UNCERTAINTY_CONSTRAINT) 0.25
set ::env(CLOCK_TRANSITION_CONSTRAINT) 0.15

# Percentage
set ::env(TIME_DERATING_CONSTRAINT) 5
set ::env(IO_DELAY_CONSTRAINT) 20
