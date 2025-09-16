set current_folder [file dirname [file normalize [info script]]]
# Technology lib

set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hvl__tt_025C_3v30.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hvl__ff_n40C_5v50.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hvl__ss_150C_1v65.lib"

set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

set ::env(VDD_PIN_VOLTAGE) "3.30"
set ::env(GND_PIN_VOLTAGE) "0.00"

# MUX4 mapping
set ::env(SYNTH_MUX4_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux4_map.v"

# MUX2 mapping
set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithv"
set ::env(PLACE_SITE_WIDTH) 0.480
set ::env(PLACE_SITE_HEIGHT) 4.070

# welltap and endcap cells
#set ::env(FP_WELLTAP_CELL) ""
set ::env(FP_ENDCAP_CELL) "sky130_fd_sc_hvl__decap_4"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "sky130_fd_sc_hvl__inv_2"
#capacitance : 0.017653;
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
# update these
set ::env(OUTPUT_CAP_LOAD) "70.77" ; # femtofarad __inv_16 pin A cap (https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hvl/blob/main/cells/inv/sky130_fd_sc_hvl__inv_16__tt_025C_3v30.lib.json)
set ::env(SYNTH_MIN_BUF_PORT) "sky130_fd_sc_hvl__buf_1 A X"
set ::env(SYNTH_TIEHI_PORT) "sky130_fd_sc_hvl__conb_1 HI"
set ::env(SYNTH_TIELO_PORT) "sky130_fd_sc_hvl__conb_1 LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) sky130_fd_sc_hvl__buf_16
set ::env(CELL_CLK_PORT) CLK

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "sky130_fd_sc_hvl__fill*"
set ::env(DECAP_CELL) "sky130_fd_sc_hvl__decap*"
set ::env(RE_BUFFER_CELL) "sky130_fd_sc_hvl__buf_1"

# Diode insertaion
set ::env(DIODE_CELL) "sky130_fd_sc_hvl__diode_2"
set ::env(DIODE_CELL_PIN) "DIODE"

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}
set ::env(CELL_PAD_EXCLUDE) "sky130_fd_sc_hvl__tap* sky130_fd_sc_hvl__decap* sky130_fd_sc_hvl__fill*"

# Clk Buffers info CTS data
set ::env(ROOT_CLK_BUFFER) sky130_fd_sc_hvl__buf_16
set ::env(CTS_CLK_BUFFER_LIST) "sky130_fd_sc_hvl__buf_8 sky130_fd_sc_hvl__buf_4 sky130_fd_sc_hvl__buf_2"
set ::env(CTS_MAX_CAP) 5.57100
set ::env(MAX_TRANSITION_CONSTRAINT) 0.75
set ::env(MAX_FANOUT_CONSTRAINT) 10
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2
set ::env(FP_PDN_RAIL_WIDTH) 0.51
