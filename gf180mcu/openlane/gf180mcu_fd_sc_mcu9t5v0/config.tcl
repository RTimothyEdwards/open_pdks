set current_folder [file dirname [file normalize [info script]]]

# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "GF018hv5v_green_sc9"
set ::env(PLACE_SITE_WIDTH) 0.56
set ::env(PLACE_SITE_HEIGHT) 3.92

# welltap and endcap cell
set ::env(FP_WELLTAP_CELL) "$::env(STD_CELL_LIBRARY)__filltie"
set ::env(FP_ENDCAP_CELL) "$::env(STD_CELL_LIBRARY)__endcap"

# defaults (can be overridden by designs):
set ::env(SYNTH_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_1"
set ::env(SYNTH_DRIVING_CELL_PIN) "ZN"
set ::env(SYNTH_CLK_DRIVING_CELL) "$::env(STD_CELL_LIBRARY)__inv_4"
set ::env(SYNTH_CLK_DRIVING_CELL_PIN) "ZN"

# update these
set ::env(OUTPUT_CAP_LOAD) "72.91" ; # femtofarad from pin I in liberty file
set ::env(SYNTH_MIN_BUF_PORT) "$::env(STD_CELL_LIBRARY)__buf_1 I Z"
set ::env(SYNTH_TIEHI_PORT) "$::env(STD_CELL_LIBRARY)__tieh Z"
set ::env(SYNTH_TIELO_PORT) "$::env(STD_CELL_LIBRARY)__tiel ZN"

# Placement defaults
set ::env(PL_LIB) $::env(LIB_TYPICAL)

# Fillcell insertion
set ::env(FILL_CELL) "$::env(STD_CELL_LIBRARY)__fill_*"
set ::env(DECAP_CELL) "$::env(STD_CELL_LIBRARY)__fillcap_*"

# Diode Insertion
# A fake diode has to be created, for now don't use any strategy that uses fake diode
# set ::env(FAKEDIODE_CELL) ""
set ::env(DIODE_CELL) "$::env(STD_CELL_LIBRARY)__antenna"
set ::env(DIODE_CELL_PIN) "I"
set ::env(DIODE_INSERTION_STRATEGY) {4}

set ::env(CELL_PAD_EXCLUDE) "$::env(STD_CELL_LIBRARY)__filltie $::env(STD_CELL_LIBRARY)__fill_* $::env(STD_CELL_LIBRARY)__endcap"

# TritonCTS configurations
set ::env(CTS_ROOT_BUFFER) "$::env(STD_CELL_LIBRARY)__clkbuf_16"
set ::env(CTS_CLK_BUFFER_LIST) "$::env(STD_CELL_LIBRARY)__clkbuf_2 $::env(STD_CELL_LIBRARY)__clkbuf_4 $::env(STD_CELL_LIBRARY)__clkbuf_8"
set ::env(CTS_MAX_CAP) 0.5

set ::env(FP_PDN_RAIL_WIDTH) 0.6

# The library maximum transition is 8.9ns; setting it to lower value
set ::env(MAX_TRANSITION_CONSTRAINT) 3
set ::env(MAX_FANOUT_CONSTRAINT) 10

set ::env(GPL_CELL_PADDING) {0}
set ::env(DPL_CELL_PADDING) {0}

set ::env(TRISTATE_CELL_PREFIX) "$::env(STD_CELL_LIBRARY)__bufz"
