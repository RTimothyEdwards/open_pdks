set current_folder [file dirname [file normalize [info script]]]
# Technology lib
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/liberty/GF018hv5v_green_sc9_TT_1P80V_25C.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/liberty/GF018hv5v_green_sc9_FF_1P98V_M40C.db"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/liberty/GF018hv5v_green_sc9_SS_1P62V_125C.db"

set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

# to be removed as ABC scripts were updated to handle the mapping

# MUX4 mapping
# set ::env(SYNTH_MUX4_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux4_map.v"

# MUX2 mapping
# set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "GF018hv5v_green_sc9"
set ::env(PLACE_SITE_WIDTH) 0.56
set ::env(PLACE_SITE_HEIGHT) 5.04

# welltap and endcap cell
set ::env(FP_WELLTAP_CELL) "FILLTIE"
set ::env(FP_ENDCAP_CELL) "ENDCAP"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "INV_X1"
#capacitance : 0.017653;
set ::env(SYNTH_DRIVING_CELL_PIN) "ZN"

# update these
set ::env(SYNTH_CAP_LOAD) "72.91" ; # femtofarad from pin I in liberty file
set ::env(SYNTH_MIN_BUF_PORT) "BUF_X1 I Z"
set ::env(SYNTH_TIEHI_PORT) "TIEH Z"
set ::env(SYNTH_TIELO_PORT) "TIEL ZN"

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "FILL_*"
set ::env(DECAP_CELL) "FILLCAP_*" ; # There is also ENDCAP, which one should be used?

# To be removed
# set ::env(RE_BUFFER_CELL) "BUF_X4" ; # which buf should be used?

# Diode insertaion
# A fake diode has to be created, for now don't use any strategy that uses fake diode
set ::env(DIODE_CELL) "ANTENNA"
# set ::env(FAKEDIODE_CELL) "sky130_ef_sc_hd__fakediode_2" ; # What is this?
set ::env(DIODE_CELL_PIN) "I"

# Are we still using it? to be reviewed
set ::env(CELL_PAD) 2
set ::env(CELL_PAD_EXCLUDE) "FILLTIE_* FILLDECAP_* FILL_* ENDCAP_*"

# Clk Buffers info CTS data
# This is for simple_cts which is deprecated
# set ::env(CELL_CLK_PORT) CLK
# set ::env(ROOT_CLK_BUFFER) "CLKBUF_X20"
# set ::env(CLK_BUFFER) "CLKBUF_X4" ; # which size should be used?
# set ::env(CLK_BUFFER_INPUT) I
# set ::env(CLK_BUFFER_OUTPUT) Z

# TritonCTS configurations
set ::env(CTS_ROOT_BUFFER) "CLKBUF_X16"
set ::env(CTS_CLK_BUFFER_LIST) "CLKBUF_X2 CLKBUF_X4 CLKBUF_X8"
set ::env(CTS_MAX_CAP) 0.5

set ::env(FP_PDN_RAIL_WIDTH) 0.6

# The library maximum transition is 8.9ns; setting it to lower value
set ::env(DEFAULT_MAX_TRAN) 3

