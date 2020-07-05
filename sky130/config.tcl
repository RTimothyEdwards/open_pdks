# Process node
set ::env(PROCESS) 130
set ::env(DEF_UNITS_PER_MICRON) 1000


# Placement site for core cells
# This can be found in the technology lef
set ::env(PLACE_SITE) "unithd"
set ::env(PLACE_SITE_WIDTH) 0.460
set ::env(PLACE_SITE_HEIGHT) 2.720

set ::env(VDD_PIN) "vpwr"
set ::env(GND_PIN) "vgnd"

# Track information for generating DEF tracks
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/common_tracks.info"


# Technology LEF
set ::env(TECH_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/techLEF/$::env(PDK_VARIANT)/$::env(PDK_VARIANT)_tech.lef"
set ::env(CELLS_LEF) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/$::env(PDK_VARIANT)/*.lef"]
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/current/EFS8A.tech"
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/current/EFS8A.magicrc"
set ::env(GPIO_PADS_LEF) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/sky130_fd_io/routing_abstract/*.lef"]

# netgen setup
set ::env(NETGEN_SETUP_FILE) $::env(PDK_ROOT)/$::env(PDK)/libs.tech/netgen/$::env(PDK)_setup.tcl 
# CTS luts
set ::env(CTS_TECH_DIR) "N/A"

set ::env(FP_TAPCELL_DIST) 20
