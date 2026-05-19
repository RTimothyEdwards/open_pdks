set current_folder [file dirname [file normalize [info script]]]
# Technology lib

# MUX4 mapping
set ::env(SYNTH_MUX4_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/mux4_map.v"

# MUX2 mapping
set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithd"

# welltap and endcap cells
set ::env(WELLTAP_CELL) "$::env(STD_CELL_LIBRARY)__tapvpwrvgnd_1"
set ::env(ENDCAP_CELL) "$::env(STD_CELL_LIBRARY)__decap_3"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_2/Y"
#capacitance : 0.017653;
#set ::env(SYNTH_CLK_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__clkinv_2/Y"
# update these
set ::env(OUTPUT_CAP_LOAD) "33.442" ; # femtofarad __inv_16 pin A cap (https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hd/blob/main/cells/inv/sky130_fd_sc_hd__inv_16__tt_025C_1v80.lib.json)
set ::env(SYNTH_BUFFER_CELL) "$::env(STD_CELL_LIBRARY)__buf_2/A/X"
set ::env(SYNTH_TIEHI_CELL) "$::env(STD_CELL_LIBRARY)__conb_1/HI"
set ::env(SYNTH_TIELO_CELL) "$::env(STD_CELL_LIBRARY)__conb_1/LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) "$::env(STD_CELL_LIBRARY)__clkbuf_16"

# fill/decap cell insertion
set ::env(FILL_CELLS) "$::env(STD_CELL_LIBRARY)__fill_2 $::env(STD_CELL_LIBRARY)__fill_1"
set ::env(DECAP_CELLS) "$::env(STD_CELL_LIBRARY)__decap_3"

# diode insertion
set ::env(DIODE_CELL) "$::env(STD_CELL_LIBRARY)__diode_2/DIODE"

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}
set ::env(CELL_PAD_EXCLUDE) "$::env(STD_CELL_LIBRARY)__tap* $::env(STD_CELL_LIBRARY)__decap* $::env(STD_CELL_LIBRARY)__fill*"

# Clk Buffers info CTS data
set ::env(CTS_CLK_BUFFERS) "$::env(STD_CELL_LIBRARY)__clkbuf_8 $::env(STD_CELL_LIBRARY)__clkbuf_4 $::env(STD_CELL_LIBRARY)__clkbuf_2"

set ::env(MAX_TRANSITION_CONSTRAINT) 0.75
set ::env(MAX_FANOUT_CONSTRAINT) 10
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2

set ::env(PDN_RAIL_WIDTH) 0.48

set ::env(TRISTATE_CELLS) "$::env(STD_CELL_LIBRARY)__ebuf*"
