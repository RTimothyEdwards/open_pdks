set current_folder [file dirname [file normalize [info script]]]

# Pad IO sites
set ::env(PAD_SITE_NAME) "GF_IO_Site"
set ::env(PAD_CORNER_SITE_NAME) "GF_COR_Site"

# Create fake pad sites
# Note: This is needed if site definition are not in LEF
set ::env(PAD_FAKE_SITES) [dict create]
dict set ::env(PAD_FAKE_SITES) "GF_IO_Site" "0.1, 355"
dict set ::env(PAD_FAKE_SITES) "GF_COR_Site" "355, 355"

# Technology lib
set ::env(PAD_LIBS) [dict create]
dict set ::env(PAD_LIBS) *_tt_025C_5v00 "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__tt_025C_5v00.lib]\
"
dict set ::env(PAD_LIBS) *_ff_n40C_5v50 "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__ff_n40C_5v50.lib]\
"
dict set ::env(PAD_LIBS) *_ss_125C_4v50 "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__ss_125C_4v50.lib]\
"

# These corners are for 3.3V SCL libraries
dict set ::env(PAD_LIBS) *_tt_025C_3v30 "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__tt_025C_3v30.lib]\
"
dict set ::env(PAD_LIBS) *_ff_n40C_3v60 "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/*__ff_n40C_3v63.lib]\
"

# Pad cells
set ::env(PAD_CORNER) "$::env(PAD_CELL_LIBRARY)__cor"
set ::env(PAD_FILLERS) "\
    $::env(PAD_CELL_LIBRARY)__fill10\
    $::env(PAD_CELL_LIBRARY)__fill5\
    $::env(PAD_CELL_LIBRARY)__fill1\
    $::env(PAD_CELL_LIBRARY)__fillnc\
"

# Pad io terminals (if needed)
set ::env(PAD_PLACE_IO_TERMINALS) "\
    $::env(PAD_CELL_LIBRARY)__asig_5p0/ASIG5V\
    $::env(PAD_CELL_LIBRARY)__bi_24t/PAD\
    $::env(PAD_CELL_LIBRARY)__bi_t/PAD\
    $::env(PAD_CELL_LIBRARY)__in_c/PAD\
    $::env(PAD_CELL_LIBRARY)__in_s/PAD\
    $::env(PAD_CELL_LIBRARY)__dvss/DVSS\
    $::env(PAD_CELL_LIBRARY)__dvdd/DVDD\
"

# Pad sites to edge offset
set ::env(PAD_EDGE_SPACING) "26"
