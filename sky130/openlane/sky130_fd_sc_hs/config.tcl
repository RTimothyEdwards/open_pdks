set current_folder [file dirname [file normalize [info script]]]
# Technology lib

set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/TECHNAME/libs.ref/sky130_fd_sc_hs/lib/sky130_fd_sc_hs__tt_025C_1v80.lib"
set ::env(LIB_MAX) "$::env(PDK_ROOT)/TECHNAME/libs.ref/sky130_fd_sc_hs/lib/sky130_fd_sc_hs__ff_n40C_1v95.lib"
set ::env(LIB_MIN) "$::env(PDK_ROOT)/TECHNAME/libs.ref/sky130_fd_sc_hs/lib/sky130_fd_sc_hs__ss_100C_1v60.lib"

set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

#tracks info
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/TECHNAME/libs.tech/openlane/sky130_fd_sc_hs/tracks.info"


# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unit"
set ::env(PLACE_SITE_WIDTH) 0.480
set ::env(PLACE_SITE_HEIGHT) 3.330


# welltap and endcap cells
set ::env(FP_WELLTAP_CELL) "sky130_fd_sc_hs__tapvpwrvgnd_1"
set ::env(FP_ENDCAP_CELL) "sky130_fd_sc_hs__decap_4"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "sky130_fd_sc_hs__inv_8"
#capacitance : 0.02104;
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
# update these
set ::env(SYNTH_CAP_LOAD) "21.04" ; # femtofarad _inv_8 pin A cap
set ::env(SYNTH_MIN_BUF_PORT) "sky130_fd_sc_hs__buf_2 A X"
set ::env(SYNTH_TIEHI_PORT) "sky130_fd_sc_hs__conb_1 HI"
set ::env(SYNTH_TIELO_PORT) "sky130_fd_sc_hs__conb_1 LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) sky130_fd_sc_hs__clkbuf_16
set ::env(CELL_CLK_PORT) CLK

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "sky130_fd_sc_hs__fill_"
set ::env(DECAP_CELL) "sky130_fd_sc_hs__decap_"

# Diode insertaion
set ::env(DIODE_CELL) "sky130_fd_sc_hs__diode_2"
set ::env(DIODE_CELL_PIN) "DIODE"

set ::env(CELL_PAD) 8
set ::env(CELL_PAD_EXECLUDE) "sky130_fd_sc_hs__tap* sky130_fd_sc_hs__decap* sky130_fd_sc_hs__fill*"

set ::env(ROOT_CLK_BUFFER) sky130_fd_sc_hs__clkbuf_16
set ::env(CLK_BUFFER) sky130_fd_sc_hs__clkbuf_4
set ::env(CLK_BUFFER_INPUT) A
set ::env(CLK_BUFFER_OUTPUT) X
