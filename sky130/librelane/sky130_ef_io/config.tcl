set current_folder [file dirname [file normalize [info script]]]

# Pad IO sites
set ::env(PAD_SITE_NAME) "sky130_io"
set ::env(PAD_CORNER_SITE_NAME) "sky130_io_corner"

set ::env(PAD_FAKE_SITES) [dict create]
dict set ::env(PAD_FAKE_SITES) "sky130_io" "1.0, 200"
dict set ::env(PAD_FAKE_SITES) "sky130_io_corner" "200.0, 204.0"

set ::env(PAD_ROTATION_HORIZONTAL) "R180"
set ::env(PAD_ROTATION_VERTICAL) "R180"
set ::env(PAD_ROTATION_CORNER) "R180"

# Set IO pad information
set ::env(PAD_CELLS) [dict create]
dict set ::env(PAD_CELLS) "sky130_io*" "80, 200"
set ::env(PAD_CORNER) "sky130_ef_io__corner_pad"
set ::env(PAD_FILLERS) "\
    sky130_ef_io__com_bus_slice_20um\
    sky130_ef_io__com_bus_slice_10um\
    sky130_ef_io__com_bus_slice_5um\
    sky130_ef_io__com_bus_slice_1um\
"

# Technology lib
set ::env(PAD_LIBS) [dict create]
dict set ::env(PAD_LIBS) "*_tt_025C_1v80" "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/$::env(PAD_CELL_LIBRARY)__*_tt_025C_1v80_3v30*.lib] \
"
dict set ::env(PAD_LIBS) "*_ff_n40C_1v95" "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/$::env(PAD_CELL_LIBRARY)__*_ff_n40C_1v95_5v50*.lib] \
"
dict set ::env(PAD_LIBS) "*_ss_100C_1v60" "\
    [glob $::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(PAD_CELL_LIBRARY)/lib/$::env(PAD_CELL_LIBRARY)__*_ss_100C_1v60_3v00*.lib] \
"

# Pad bondpad information (if needed)
#set ::env(PAD_BONDPAD_NAME) "bondpad_70x70"
#set ::env(PAD_BONDPAD_WIDTH) "70"
#set ::env(PAD_BONDPAD_HEIGHT) "70"
#set ::env(PAD_BONDPAD_OFFSETS) [dict create]
#dict set ::env(PAD_BONDPAD_OFFSETS) "sg13g2_IOPad*" "5.0, -70.0"

# Pad io terminals (if needed)
set ::env(PAD_PLACE_IO_TERMINALS) "\
    sky130_fd_io__top_gpiov2/PAD\
    sky130_ef_io__gpiov2_pad/PAD\
    sky130_ef_io__vccd_lvc_pad/VCCD_PAD\
    sky130_ef_io__vssd_lvc_pad/VSSD_PAD\
    sky130_ef_io__vddio_lvc_pad/VDDIO_PAD\
    sky130_ef_io__vssio_lvc_pad/VSSIO_PAD\
"

# Sealring is added afterwards
set ::env(PAD_EDGE_SPACING) "0"

#set ::env(KLAYOUT_SEALRING_SCRIPT) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/klayout/tech/scripts/sealring.py"
