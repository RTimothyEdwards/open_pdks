set current_folder [file dirname [file normalize [info script]]]

# Corners
set ::env(STA_CORNERS) "\
    min_ff_100C_1v95 nom_ff_100C_1v95 max_ff_100C_1v95 \
    min_ff_125C_3v15 nom_ff_125C_3v15 max_ff_125C_3v15 \
    min_ff_140C_1v95 nom_ff_140C_1v95 max_ff_140C_1v95 \
    min_ff_150C_2v05 nom_ff_150C_2v05 max_ff_150C_2v05 \
    min_ff_n40C_1v56 nom_ff_n40C_1v56 max_ff_n40C_1v56 \
    min_ff_n40C_1v76 nom_ff_n40C_1v76 max_ff_n40C_1v76 \
    min_ff_n40C_1v95 nom_ff_n40C_1v95 max_ff_n40C_1v95 \
    min_ff_n40C_2v05 nom_ff_n40C_2v05 max_ff_n40C_2v05 \
    min_ss_100C_1v60 nom_ss_100C_1v60 max_ss_100C_1v60 \
    min_ss_140C_1v65 nom_ss_140C_1v65 max_ss_140C_1v65 \
    min_ss_150C_1v65 nom_ss_150C_1v65 max_ss_150C_1v65 \
    min_ss_n40C_1v55 nom_ss_n40C_1v55 max_ss_n40C_1v55 \
    min_ss_n40C_1v60 nom_ss_n40C_1v60 max_ss_n40C_1v60 \
    min_ss_n40C_1v65 nom_ss_n40C_1v65 max_ss_n40C_1v65 \
"

# there is no typical choice for a default corner
set ::env(DEFAULT_CORNER) "nom_ff_n40C_1v56"

# Technology lib
set ::env(CELL_LIBS) [dict create]
dict set ::env(CELL_LIBS) "*_ff_100C_1v95" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_100C_1v95.lib"
dict set ::env(CELL_LIBS) "*_ff_125C_3v15" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_125C_3v15.lib"
dict set ::env(CELL_LIBS) "*_ff_140C_1v95" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_140C_1v95.lib"
dict set ::env(CELL_LIBS) "*_ff_150C_2v05" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_150C_2v05.lib"
dict set ::env(CELL_LIBS) "*_ff_n40C_1v56" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_1v56.lib"
dict set ::env(CELL_LIBS) "*_ff_n40C_1v76" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_1v76.lib"
dict set ::env(CELL_LIBS) "*_ff_n40C_1v95" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_1v95.lib"
dict set ::env(CELL_LIBS) "*_ff_n40C_2v05" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ff_n40C_2v05.lib"
dict set ::env(CELL_LIBS) "*_ss_100C_1v60" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_100C_1v60.lib"
dict set ::env(CELL_LIBS) "*_ss_140C_1v65" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_140C_1v65.lib"
dict set ::env(CELL_LIBS) "*_ss_150C_1v65" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_150C_1v65.lib"
dict set ::env(CELL_LIBS) "*_ss_n40C_1v55" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_n40C_1v55.lib"
dict set ::env(CELL_LIBS) "*_ss_n40C_1v60" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_n40C_1v60.lib"
dict set ::env(CELL_LIBS) "*_ss_n40C_1v65" "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__ss_n40C_1v65.lib"

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unit"

# welltap and endcap cells
set ::env(WELLTAP_CELL) "$::env(STD_CELL_LIBRARY)__tapvpwrvgnd_1"
set ::env(ENDCAP_CELL) "$::env(STD_CELL_LIBRARY)__decap_3"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_2/Y"
# capacitance : 0.0062400000; # sky130_fd_sc_lp__ff_100C_1v95.lib.part3
# capacitance : 0.0036200000; # sky130_fd_sc_lp__ff_125C_3v15.lib.part2
# capacitance : 0.0063000000; # sky130_fd_sc_lp__ff_140C_1v95.lib.part3
# capacitance : 0.0063800000; # sky130_fd_sc_lp__ff_150C_2v05.lib.part2
# capacitance : 0.0056400000; # sky130_fd_sc_lp__ff_n40C_1v56.lib.part3
# capacitance : 0.0058800000; # sky130_fd_sc_lp__ff_n40C_1v76.lib.part3
# capacitance : 0.0060100000; # sky130_fd_sc_lp__ff_n40C_1v95.lib.part3
# capacitance : 0.0060600000; # sky130_fd_sc_lp__ff_n40C_2v05.lib.part2
# capacitance : 0.0063600000; # sky130_fd_sc_lp__ss_100C_1v60.lib.part2
# capacitance : 0.0062800000; # sky130_fd_sc_lp__ss_140C_1v65.lib.part2
# capacitance : 0.0064900000; # sky130_fd_sc_lp__ss_150C_1v65.lib.part2
# capacitance : 0.0059500000; # sky130_fd_sc_lp__ss_n40C_1v55.lib.part2
# capacitance : 0.0060000000; # sky130_fd_sc_lp__ss_n40C_1v60.lib.part2
# capacitance : 0.0059900000; # sky130_fd_sc_lp__ss_n40C_1v65.lib.part2
set ::env(SYNTH_CLK_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__clkinv_2/Y"
# update these
#set ::env(OUTPUT_CAP_LOAD) "50.400" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_100C_1v95.lib.part3)
#set ::env(OUTPUT_CAP_LOAD) "53.570" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_125C_3v15.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "50.810" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_140C_1v95.lib.part3)
#set ::env(OUTPUT_CAP_LOAD) "51.190" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_150C_2v05.lib.part2)
set ::env(OUTPUT_CAP_LOAD) "44.660" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_n40C_1v56.lib.part3)
#set ::env(OUTPUT_CAP_LOAD) "47.200" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_n40C_1v76.lib.part3)
#set ::env(OUTPUT_CAP_LOAD) "48.400" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_n40C_1v95.lib.part3)
#set ::env(OUTPUT_CAP_LOAD) "48.920" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ff_n40C_2v05.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "51.720" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ss_100C_1v60.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "52.850" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ss_140C_1v65.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "53.990" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ss_150C_1v65.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "47.270" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ss_n40C_1v55.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "48.370" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ss_n40C_1v60.lib.part2)
#set ::env(OUTPUT_CAP_LOAD) "48.780" ; # femtofarad __inv_16 pin A cap (sky130_fd_sc_lp__ss_n40C_1v65.lib.part2)

set ::env(SYNTH_BUFFER_CELL) "$::env(STD_CELL_LIBRARY)__buf_2/A/X"
set ::env(SYNTH_TIEHI_CELL) "$::env(STD_CELL_LIBRARY)__conb_0/HI"
set ::env(SYNTH_TIELO_CELL) "$::env(STD_CELL_LIBRARY)__conb_0/LO"

# cts defaults
set ::env(CTS_ROOT_BUFFER) "$::env(STD_CELL_LIBRARY)__clkbuf_16"

# fill/decap cell insertion
set ::env(FILL_CELLS) "$::env(STD_CELL_LIBRARY)__fill*"
set ::env(DECAP_CELLS) "$::env(STD_CELL_LIBRARY)__decap*"

# diode insertion
set ::env(DIODE_CELL) "$::env(STD_CELL_LIBRARY)__diode_0/DIODE"

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}
set ::env(CELL_PAD_EXCLUDE) "$::env(STD_CELL_LIBRARY)__tap* $::env(STD_CELL_LIBRARY)__decap* $::env(STD_CELL_LIBRARY)__fill*"

# Clk Buffers info CTS data
set ::env(CTS_CLK_BUFFERS) "$::env(STD_CELL_LIBRARY)__clkbuf_*"

set ::env(MAX_TRANSITION_CONSTRAINT) 0.75
set ::env(MAX_FANOUT_CONSTRAINT) 10
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2

set ::env(PDN_RAIL_WIDTH) 0.48

set ::env(TRISTATE_CELLS) "$::env(STD_CELL_LIBRARY)__ebuf* $::env(STD_CELL_LIBRARY)__einv*"
