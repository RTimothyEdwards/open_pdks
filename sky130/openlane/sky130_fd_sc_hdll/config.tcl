set current_folder [file dirname [file normalize [info script]]]
# Technology lib

#ifdef EF_FORMAT
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(STD_CELL_LIBRARY)/sky130_fd_sc_hdll__tt_025C_1v80.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(STD_CELL_LIBRARY)/sky130_fd_sc_hdll__ff_n40C_1v95.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(STD_CELL_LIBRARY)/sky130_fd_sc_hdll__ss_100C_1v60.lib"
#else (!EF_FORMAT)
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hdll__tt_025C_1v80.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hdll__ff_n40C_1v95.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hdll__ss_100C_1v60.lib"
#endif (!EF_FORMAT)

set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

# MUX2 mapping
set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithd"
set ::env(PLACE_SITE_WIDTH) 0.460
set ::env(PLACE_SITE_HEIGHT) 2.720

# welltap and endcap cells
set ::env(FP_WELLTAP_CELL) "sky130_fd_sc_hdll__tapvpwrvgnd_1"
set ::env(FP_ENDCAP_CELL) "sky130_fd_sc_hdll__decap_3"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "sky130_fd_sc_hdll__inv_2"
#capacitance : 0.017653;
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
# update these
set ::env(OUTPUT_CAP_LOAD) "33.468" ; # femtofarad _inv_16 pin A cap (https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hdll/blob/main/cells/inv/sky130_fd_sc_hdll__inv_16__tt_025C_1v80.lib.json)
set ::env(SYNTH_MIN_BUF_PORT) "sky130_fd_sc_hdll__buf_2 A X"
set ::env(SYNTH_TIEHI_PORT) "sky130_fd_sc_hdll__conb_1 HI"
set ::env(SYNTH_TIELO_PORT) "sky130_fd_sc_hdll__conb_1 LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) sky130_fd_sc_hdll__clkbuf_16
set ::env(CELL_CLK_PORT) CLK

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "sky130_fd_sc_hdll__fill*"
set ::env(DECAP_CELL) "sky130_fd_sc_hdll__decap_"
set ::env(RE_BUFFER_CELL) "sky130_fd_sc_hdll__buf_4"

# Diode insertaion
set ::env(DIODE_CELL) "sky130_fd_sc_hdll__diode_2"
set ::env(FAKEDIODE_CELL) "sky130_fd_sc_hdll__fakediode_2"
set ::env(DIODE_CELL_PIN) "DIODE"

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}
set ::env(CELL_PAD_EXCLUDE) "$::env(STD_CELL_LIBRARY)__tap* $::env(STD_CELL_LIBRARY)__decap* $::env(STD_CELL_LIBRARY)__fill*"

# Clk Buffers info CTS data
set ::env(ROOT_CLK_BUFFER) $::env(STD_CELL_LIBRARY)__clkbuf_16
set ::env(CTS_CLK_BUFFER_LIST) "sky130_fd_sc_hdll__clkbuf_8 sky130_fd_sc_hdll__clkbuf_4 sky130_fd_sc_hdll__clkbuf_2"
set ::env(FP_PDN_RAIL_WIDTH) 0.48
# Determined from https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hdll/blob/0694bd23893de20f5233ef024acf6cca1e750ac6/cells/clkbuf/sky130_fd_sc_hdll__clkbuf_16__tt_025C_1v80.lib.json
set ::env(CTS_MAX_CAP) 1.03547
set ::env(MAX_TRANSITION_CONSTRAINT) 0.75
set ::env(MAX_FANOUT_CONSTRAINT) 10
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2

set ::env(TRISTATE_CELL_PREFIX) "$::env(STD_CELL_LIBRARY)__ebuf"
