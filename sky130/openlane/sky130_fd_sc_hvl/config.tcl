set current_folder [file dirname [file normalize [info script]]]
# Technology lib

#ifdef EF_FORMAT
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(PDK_VARIANT)/sky130_fd_sc_hvl__tt_025C_3v30.lib"
set ::env(LIB_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(PDK_VARIANT)/sky130_fd_sc_hvl__ff_n40C_5v50.lib"
set ::env(LIB_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lib/$::env(PDK_VARIANT)/sky130_fd_sc_hvl__ss_150C_1v65.lib"
#else (!EF_FORMAT)
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PDK_VARIANT)/lib/sky130_fd_sc_hvl__tt_025C_3v30.lib"
set ::env(LIB_MAX) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PDK_VARIANT)/lib/sky130_fd_sc_hvl__ff_n40C_5v50.lib"
set ::env(LIB_MIN) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PDK_VARIANT)/lib/sky130_fd_sc_hvl__ss_150C_1v65.lib"
#endif (!EF_FORMAT)



set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

# Tracks info
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(PDK_VARIANT)/tracks.info"


# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithv"
set ::env(PLACE_SITE_WIDTH) 0.480
set ::env(PLACE_SITE_HEIGHT) 4.070

# welltap and endcap cells
#set ::env(FP_WELLTAP_CELL) ""
set ::env(FP_ENDCAP_CELL) "sky130_fd_sc_hvl__decap_4"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "sky130_fd_sc_hvl_inv_16"
#capacitance : 0.017653;
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
# update these
set ::env(SYNTH_CAP_LOAD) "70.77" ; # femtofarad __inv_8 pin A cap
set ::env(SYNTH_MIN_BUF_PORT) "sky130_fd_sc_hvl__buf_1 A X"
set ::env(SYNTH_TIEHI_PORT) "sky130_fd_sc_hvl__conb_1 HI"
set ::env(SYNTH_TIELO_PORT) "sky130_fd_sc_hvl__conb_1 LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) ""
#set ::env(CELL_CLK_PORT) CLK

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
set ::env(CLOCK_TREE_SYNTH) 0

