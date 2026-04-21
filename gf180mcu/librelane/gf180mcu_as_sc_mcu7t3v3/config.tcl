set current_folder [file dirname [file normalize [info script]]]
# Technology lib

set ::env(LIB) [dict create]
dict set ::env(LIB) *_tt_025C_3v30 "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_3v30.lib\
"
dict set ::env(LIB) *_ff_n40C_3v60 "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_3v60.lib\
"
#dict set ::env(LIB) *_ss_125C_4v50 "\
#    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_125C_4v50.lib\
#    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__ss_125C_4v50.lib]\
#"

set ::env(STA_CORNERS) "\
    nom_tt_025C_3v30 \
    min_tt_025C_3v30 \
    max_tt_025C_3v30 \
    nom_ff_n40C_3v60 \
    min_ff_n40C_3v60 \
    max_ff_n40C_3v60 \
"
set ::env(DEFAULT_CORNER) "nom_tt_025C_3v30"

# MUX2 mapping
set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithd"
set ::env(PLACE_SITE_WIDTH) 0.56
set ::env(PLACE_SITE_HEIGHT) 3.92

# welltap and endcap cell
set ::env(FP_WELLTAP_CELL) "$::env(STD_CELL_LIBRARY)__tap_2"
set ::env(FP_ENDCAP_CELL) "$::env(STD_CELL_LIBRARY)__tap_2"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_2"
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
set ::env(SYNTH_CLK_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_4"
set ::env(SYNTH_CLK_DRIVING_CELL_PIN) "Y"

# update these
set ::env(OUTPUT_CAP_LOAD) "72.91" ; # femtofarad from pin I in liberty file
set ::env(SYNTH_MIN_BUF_PORT) "$::env(STD_CELL_LIBRARY)__buff_2 A Y"
set ::env(SYNTH_TIEHI_PORT) "$::env(STD_CELL_LIBRARY)__tieh_4 ONE"
set ::env(SYNTH_TIELO_PORT) "$::env(STD_CELL_LIBRARY)__tiel_4 ZERO"

# Placement defaults
#set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "$::env(STD_CELL_LIBRARY)__fill_*"
set ::env(DECAP_CELL) "$::env(STD_CELL_LIBRARY)__fillcap_*"

# Diode Insertion
# A fake diode has to be created, for now don't use any strategy that uses fake diode
# set ::env(FAKEDIODE_CELL) ""
set ::env(DIODE_CELL) "$::env(STD_CELL_LIBRARY)__diode_2"
set ::env(DIODE_CELL_PIN) "DIODE"
set ::env(DIODE_INSERTION_STRATEGY) {4}

set ::env(CELL_PAD_EXCLUDE) "$::env(STD_CELL_LIBRARY)__tap_2 $::env(STD_CELL_LIBRARY)__fill_*"

# TritonCTS configurations
set ::env(CTS_ROOT_BUFFER) "$::env(STD_CELL_LIBRARY)__clkbuff_12"
set ::env(CTS_CLK_BUFFER_LIST) "$::env(STD_CELL_LIBRARY)__clkbuff_4 $::env(STD_CELL_LIBRARY)__clkbuff_8 $::env(STD_CELL_LIBRARY)__clkbuff_12"
set ::env(CTS_MAX_CAP) 0.5

set ::env(FP_PDN_RAIL_WIDTH) 0.6

set ::env(MAX_TRANSITION_CONSTRAINT) 1.5
set ::env(MAX_FANOUT_CONSTRAINT) 9
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}

set ::env(TRISTATE_CELL_PREFIX) "$::env(STD_CELL_LIBRARY)__invz"
