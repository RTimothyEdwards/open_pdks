set current_folder [file dirname [file normalize [info script]]]
# Technology lib

set ::env(VDD_PIN_VOLTAGE) "3.30"
set ::env(GND_PIN_VOLTAGE) "0.00"

# Corners
set ::env(STA_CORNERS) "\
    nom_tt_025C_3v30 \
    nom_ss_150C_1v65 \
    nom_ff_n40C_5v50 \
    min_tt_025C_3v30 \
    min_ss_150C_1v65 \
    min_ff_n40C_5v50 \
    max_tt_025C_3v30 \
    max_ss_150C_1v65 \
    max_ff_n40C_5v50 \
"

set ::env(DEFAULT_CORNER) "nom_tt_025C_3v30"

# Technology lib
set ::env(CELL_LIBS) [dict create]
dict set ::env(CELL_LIBS) "*_tt_025C_3v30" "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_3v30.lib\
"
dict set ::env(CELL_LIBS) "*_ff_n40C_5v50" "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_5v50.lib\
"
dict set ::env(CELL_LIBS) "*_ss_150C_1v65" "\
    $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_150C_1v65.lib\
"

# MUX4 mapping
set ::env(SYNTH_MUX4_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/mux4_map.v"

# MUX2 mapping
set ::env(SYNTH_MUX_MAP) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/librelane/$::env(STD_CELL_LIBRARY)/mux2_map.v"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithv"

# welltap and endcap cells
#set ::env(WELLTAP_CELL) ""
set ::env(ENDCAP_CELL) "sky130_fd_sc_hvl__decap_4"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "sky130_fd_sc_hvl__inv_2/Y"
#capacitance : 0.017653;
# update these
set ::env(OUTPUT_CAP_LOAD) "70.77" ; # femtofarad __inv_16 pin A cap (https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hvl/blob/main/cells/inv/sky130_fd_sc_hvl__inv_16__tt_025C_3v30.lib.json)
set ::env(SYNTH_BUFFER_CELL) "sky130_fd_sc_hvl__buf_1/A/X"
set ::env(SYNTH_TIEHI_CELL) "sky130_fd_sc_hvl__conb_1/HI"
set ::env(SYNTH_TIELO_CELL) "sky130_fd_sc_hvl__conb_1/LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) sky130_fd_sc_hvl__buf_16

# fill/decap cell insertion
set ::env(FILL_CELLS) "sky130_fd_sc_hvl__fill*"
set ::env(DECAP_CELLS) "sky130_fd_sc_hvl__decap*"

# diode insertion
set ::env(DIODE_CELL) "sky130_fd_sc_hvl__diode_2/DIODE"

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}
set ::env(CELL_PAD_EXCLUDE) "sky130_fd_sc_hvl__tap* sky130_fd_sc_hvl__decap* sky130_fd_sc_hvl__fill*"

# Clk Buffers info CTS data
set ::env(CTS_CLK_BUFFERS) "sky130_fd_sc_hvl__buf_8 sky130_fd_sc_hvl__buf_4 sky130_fd_sc_hvl__buf_2"
set ::env(MAX_TRANSITION_CONSTRAINT) 0.75
set ::env(MAX_FANOUT_CONSTRAINT) 10
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2
set ::env(PDN_RAIL_WIDTH) 0.51
