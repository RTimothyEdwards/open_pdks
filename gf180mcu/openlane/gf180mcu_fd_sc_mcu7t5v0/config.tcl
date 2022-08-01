set current_folder [file dirname [file normalize [info script]]]
# Technology lib
set TRACK_POSTFIX "7T5P0"
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/liberty/GF018hv5v_mcu_sc7_TT_1P8V_25C.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/liberty/GF018hv5v_mcu_sc7_FF_1P98V_M40C.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/liberty/GF018hv5v_mcu_sc7_SS_1P62V_125C.lib"

set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

# to be removed as ABC scripts were updated to handle the mapping

# MUX4 mapping
# set ::env(SYNTH_MUX4_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux4_map.v"

# MUX2 mapping
# set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "GF018hv5v_mcu_sc7"
set ::env(PLACE_SITE_WIDTH) 0.56
set ::env(PLACE_SITE_HEIGHT) 3.92

# welltap and endcap cell
set ::env(FP_WELLTAP_CELL) "FILLTIE_$TRACK_POSTFIX"
set ::env(FP_ENDCAP_CELL) "ENDCAP_$TRACK_POSTFIX"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "INV_X1_$TRACK_POSTFIX"
set ::env(SYNTH_DRIVING_CELL_PIN) "ZN"
set ::env(SYNTH_CLK_DRIVING_CELL) "INV_X4_$TRACK_POSTFIX"
set ::env(SYNTH_CLK_DRIVING_CELL_PIN) "ZN"

# update these
set ::env(SYNTH_CAP_LOAD) "72.91" ; # femtofarad from pin I in liberty file
set ::env(SYNTH_MIN_BUF_PORT) "BUF_X1_$TRACK_POSTFIX I Z"
set ::env(SYNTH_TIEHI_PORT) "TIEH_$TRACK_POSTFIX Z"
set ::env(SYNTH_TIELO_PORT) "TIEL_$TRACK_POSTFIX ZN"

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "FILL_*"
set ::env(DECAP_CELL) "FILLCAP_*" ; # There is also ENDCAP, which one should be used?

# To be removed
# set ::env(RE_BUFFER_CELL) "BUF_X4_$TRACK_POSTFIX" ; # which buf should be used?

# Diode Insertion
# A fake diode has to be created, for now don't use any strategy that uses fake diode
# set ::env(FAKEDIODE_CELL) ""
set ::env(DIODE_CELL) "ANTENNA_$TRACK_POSTFIX"
set ::env(DIODE_CELL_PIN) "I"
set ::env(DIODE_INSERTION_STRATEGY) {4}

# What should be put here?
# Are we still using it? to be reviewed
set ::env(CELL_PAD) 2
set ::env(CELL_PAD_EXCLUDE) "FILLTIE_* FILLDECAP_* FILL_* ENDCAP_*"

# Clk Buffers info CTS data
# This is for simple_cts which is deprecated
# set ::env(CELL_CLK_PORT) CLK
# set ::env(ROOT_CLK_BUFFER) "CLKBUF_X20_$TRACK_POSTFIX"
# set ::env(CLK_BUFFER) "CLKBUF_X4_$TRACK_POSTFIX" ; # which size should be used?
# set ::env(CLK_BUFFER_INPUT) I
# set ::env(CLK_BUFFER_OUTPUT) Z

# TritonCTS configurations
set ::env(CTS_ROOT_BUFFER) "CLKBUF_X16_$TRACK_POSTFIX"
set ::env(CTS_CLK_BUFFER_LIST) "CLKBUF_X2_$TRACK_POSTFIX CLKBUF_X4_$TRACK_POSTFIX CLKBUF_X8_$TRACK_POSTFIX"
set ::env(CTS_MAX_CAP) 0.5

set ::env(FP_PDN_RAIL_WIDTH) 0.6

# The library maximum transition is 8.9ns; setting it to lower value
set ::env(DEFAULT_MAX_TRAN) 3

