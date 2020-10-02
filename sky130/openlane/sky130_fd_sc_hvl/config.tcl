set current_folder [file dirname [file normalize [info script]]]
# Technology lib

#ifdef EF_FORMAT
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(STD_CELL_LIBRARY)/sky130_fd_sc_hvl__tt_025C_3v30.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(STD_CELL_LIBRARY)/sky130_fd_sc_hvl__ff_n40C_5v50.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(STD_CELL_LIBRARY)/sky130_fd_sc_hvl__ss_150C_1v65.lib"
#else (!EF_FORMAT)
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hvl__tt_025C_3v30.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hvl__ff_n40C_5v50.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_fd_sc_hvl__ss_150C_1v65.lib"
#endif (!EF_FORMAT)



set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)



# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithv"
set ::env(PLACE_SITE_WIDTH) 0.480
set ::env(PLACE_SITE_HEIGHT) 4.070

# welltap and endcap cells
#set ::env(FP_WELLTAP_CELL) ""
set ::env(FP_ENDCAP_CELL) "sky130_fd_sc_hvl__decap_4"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "sky130_fd_sc_hvl__inv_16"
#capacitance : 0.017653;
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
# update these
set ::env(SYNTH_CAP_LOAD) "35.49" ; # femtofarad __inv_8 pin A cap
set ::env(SYNTH_MIN_BUF_PORT) "sky130_fd_sc_hvl__buf_1 A X"
set ::env(SYNTH_TIEHI_PORT) "sky130_fd_sc_hvl__conb_1 HI"
set ::env(SYNTH_TIELO_PORT) "sky130_fd_sc_hvl__conb_1 LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) sky130_fd_sc_hvl__buf_16
set ::env(CELL_CLK_PORT) CLK

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "sky130_fd_sc_hvl__fill_"
set ::env(DECAP_CELL) "sky130_fd_sc_hvl__decap_"
set ::env(RE_BUFFER_CELL) "sky130_fd_sc_hvl__buf_1"


# Diode insertaion
set ::env(DIODE_CELL) "sky130_fd_sc_hvl__diode_2"
set ::env(DIODE_CELL_PIN) "DIODE"

set ::env(CELL_PAD) 8
set ::env(CELL_PAD_EXECLUDE) "sky130_fd_sc_hvl__tap* sky130_fd_sc_hvl__decap* sky130_fd_sc_hvl__fill*"

# Clk Buffers info CTS data
set ::env(ROOT_CLK_BUFFER) sky130_fd_sc_hvl__buf_16
set ::env(CLK_BUFFER) sky130_fd_sc_hvl__buf_4
set ::env(CLK_BUFFER_INPUT) A
set ::env(CLK_BUFFER_OUTPUT) X

set ::env(CTS_CLK_BUFFER_LIST) "sky130_fd_sc_hvl__buf_1 sky130_fd_sc_hvl__buf_2 sky130_fd_sc_hvl__buf_4 sky130_fd_sc_hvl__buf_8"
set ::env(CTS_MAX_CAP) 5.57100

set ::env(PDN_RAIL_WIDTH) 0.51
