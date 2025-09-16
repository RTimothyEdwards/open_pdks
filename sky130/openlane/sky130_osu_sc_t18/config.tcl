set current_folder [file dirname [file normalize [info script]]]
# Technology lib

set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_osu_sc_TT_1P8_25C.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_osu_sc_FF_1P8_25C.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/sky130_osu_sc_SS_1P8_25C.lib"

set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

# Placement site for core cells
# This can be found in the technology lef (SITE)
set ::env(PLACE_SITE) "s8_osu130"
set ::env(PLACE_SITE_WIDTH) 0.11
set ::env(PLACE_SITE_HEIGHT) 7.2

# welltap and endcap cells
# Does not exist in OSU cells.  Taps are included in each cell.
# set ::env(FP_WELLTAP_CELL) "sky130_osu_sc_t18__tapvpwrvgnd_1"
# set ::env(FP_ENDCAP_CELL) "sky130_osu_sc_t18__decap_3"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "INVX8"
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
# capacitance : 0.037357;
# update these
set ::env(OUTPUT_CAP_LOAD) "37.357" ; # femtofarad INVX8 pin A cap
set ::env(SYNTH_MIN_BUF_PORT) "BUFX1 A Y"
set ::env(SYNTH_TIEHI_PORT) "TIEHI Y"
set ::env(SYNTH_TIELO_PORT) "TIELO Y"

# Power pins
set ::env(VDD_PIN) "vdd"
set ::env(GND_PIN) "gnd"

# cts defaults
set ::env(CTS_ROOT_BUFFER) CLKBUFX1
set ::env(CELL_CLK_PORT) CK

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion - do decap cell
set ::env(FILL_CELL) "FILLX"
set ::env(DECAP_CELL) ""
set ::env(RE_BUFFER_CELL) "BUFX4"


# Diode insertion
set ::env(DIODE_CELL) "ANTFILL"
#set ::env(FAKEDIODE_CELL) "sky130_osu_sc_t18__fakediode_2"
set ::env(DIODE_CELL_PIN) "A"

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}
set ::env(CELL_PAD_EXCLUDE) "FILLX*"

# Clk Buffers info CTS data
set ::env(ROOT_CLK_BUFFER) CLKBUFX1
set ::env(CTS_CLK_BUFFER_LIST) "CLKBUFX1"
# TODO...
set ::env(CTS_MAX_CAP) 1.53169

set ::env(FP_PDN_RAIL_WIDTH) 0.48
