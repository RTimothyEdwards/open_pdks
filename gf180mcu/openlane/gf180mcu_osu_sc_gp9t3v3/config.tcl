set current_folder [file dirname [file normalize [info script]]]

# Standard cell library (override gf180mcu default)
set ::env(STD_CELL_LIBRARY) gf180mcu_osu_sc_gp9t3v3
set ::env(STD_CELL_LIBRARY_OPT) gf180mcu_osu_sc_gp9t3v3

set ::env(VDD_PIN_VOLTAGE) "3.30"

set ::env(STD_CELL_POWER_PINS) "VDD"
set ::env(STD_CELL_GROUND_PINS) "VSS"

# Lib Files (override gf180mcu defaults)
set ::env(LIB_SYNTH) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_3v30.lib"
set ::env(LIB_FASTEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_3v30.lib"
set ::env(LIB_SLOWEST) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lib/$::env(STD_CELL_LIBRARY)__tt_025C_3v30.lib"
set ::env(LIB_TYPICAL) $::env(LIB_SYNTH)

# Technology LEF (override gf180mcu defaults)
set ::env(TECH_LEF_MIN)  $::env(TECH_LEF)
set ::env(TECH_LEF_MAX)  $::env(TECH_LEF)

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "gf180mcu_osu_sc_gp9t3v3"
set ::env(PLACE_SITE_WIDTH) 0.10
set ::env(PLACE_SITE_HEIGHT) 6.35

# welltap and endcap cell
# set ::env(FP_WELLTAP_CELL) "$::env(STD_CELL_LIBRARY)__filltie"
# set ::env(FP_ENDCAP_CELL) "$::env(STD_CELL_LIBRARY)__endcap"
set ::env(FP_WELLTAP_CELL) ""
set ::env(FP_ENDCAP_CELL) ""

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_1"
set ::env(SYNTH_DRIVING_CELL_PIN) "Y"
set ::env(SYNTH_CLK_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__clkinv_4"
set ::env(SYNTH_CLK_DRIVING_CELL_PIN) "Y"

# update these
set ::env(OUTPUT_CAP_LOAD) "4.046" ; # femtofarad from pin A in liberty file
set ::env(SYNTH_MIN_BUF_PORT) "$::env(STD_CELL_LIBRARY)__buf_1 A Y"
set ::env(SYNTH_TIEHI_PORT) "$::env(STD_CELL_LIBRARY)__tieh Y"
set ::env(SYNTH_TIELO_PORT) "$::env(STD_CELL_LIBRARY)__tiel Y"

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "$::env(STD_CELL_LIBRARY)__fill_*"
set ::env(DECAP_CELL) "$::env(STD_CELL_LIBRARY)__decap_*"

# Diode Insertion
set ::env(DIODE_CELL) "$::env(STD_CELL_LIBRARY)__ant"
set ::env(DIODE_CELL_PIN) "A"
set ::env(DIODE_INSERTION_STRATEGY) {4}

# set ::env(CELL_PAD_EXCLUDE) "$::env(STD_CELL_LIBRARY)__filltie $::env(STD_CELL_LIBRARY)__fill_* $::env(STD_CELL_LIBRARY)__endcap"
set ::env(CELL_PAD_EXCLUDE) ""

# TritonCTS configurations
set ::env(CTS_ROOT_BUFFER) "$::env(STD_CELL_LIBRARY)__clkbuf_16"
set ::env(CTS_CLK_BUFFER_LIST) "$::env(STD_CELL_LIBRARY)__clkbuf_2 $::env(STD_CELL_LIBRARY)__clkbuf_4 $::env(STD_CELL_LIBRARY)__clkbuf_8"
set ::env(CTS_MAX_CAP) 0.5

set ::env(FP_PDN_RAIL_WIDTH) 0.6

# The library maximum transition is 8.9ns; setting it to lower value
set ::env(MAX_TRANSITION_CONSTRAINT) 3
set ::env(MAX_FANOUT_CONSTRAINT) 10
set ::env(MAX_CAPACITANCE_CONSTRAINT) 0.2

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}

set ::env(TRISTATE_CELL_PREFIX) "$::env(STD_CELL_LIBRARY)__tbuf"
