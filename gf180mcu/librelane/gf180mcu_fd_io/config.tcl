set current_folder [file dirname [file normalize [info script]]]

# Pad IO sites
set ::env(PAD_SITE_NAME) "GF_IO_Site"
set ::env(PAD_CORNER_SITE_NAME) "GF_COR_Site"

# Create fake pad sites
# Note: This is needed if site definition are not in LEF
set ::env(PAD_FAKE_SITES) [dict create]
dict set ::env(PAD_FAKE_SITES) "GF_IO_Site" "0.1, 355"
dict set ::env(PAD_FAKE_SITES) "GF_COR_Site" "355, 355"

# Pad cells
set ::env(PAD_CORNER) "$::env(PAD_CELL_LIBRARY)__cor"
set ::env(PAD_FILLERS) "\
    $::env(PAD_CELL_LIBRARY)__fill10\
    $::env(PAD_CELL_LIBRARY)__fill5\
    $::env(PAD_CELL_LIBRARY)__fill1\
    $::env(PAD_CELL_LIBRARY)__fillnc\
"

# Pad bondpad information (if needed)
# Note: bondpads are integrated in GF180MCU
#set ::env(PAD_BONDPAD_NAME) "bondpad_70x70"
#set ::env(PAD_BONDPAD_WIDTH) "70"
#set ::env(PAD_BONDPAD_HEIGHT) "70"
#set ::env(PAD_BONDPAD_OFFSETS) [dict create]
#dict set ::env(PAD_BONDPAD_OFFSETS) "instance*" "5.0, -70.0"

# Pad io terminals (if needed)
set ::env(PAD_PLACE_IO_TERMINALS) "\
    $::env(PAD_CELL_LIBRARY)__asig_5p0/ASIG5V\
    $::env(PAD_CELL_LIBRARY)__bi_24t/PAD\
    $::env(PAD_CELL_LIBRARY)__bi_t/PAD\
    $::env(PAD_CELL_LIBRARY)__in_c/PAD\
    $::env(PAD_CELL_LIBRARY)__in_s/PAD\
    $::env(PAD_CELL_LIBRARY)__dvss/DVSS\
    $::env(PAD_CELL_LIBRARY)__dvdd/DVDD\
    gf180mcu_ws_io__dvss/DVSS\
    gf180mcu_ws_io__dvdd/DVDD\
"

# Pad sites to edge offset
set ::env(PAD_EDGE_SPACING) "26"

set ::env(KLAYOUT_SEALRING_SCRIPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/scripts/sealring.py"
