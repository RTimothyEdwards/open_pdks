# Process node
set ::env(PROCESS) 130
set ::env(DEF_UNITS_PER_MICRON) 1000

# Placement site for core cells
# This can be found in the technology lef

set ::env(VDD_PIN) "VPWR"
set ::env(GND_PIN) "VGND"

# Technology LEF
#ifdef EF_FORMAT
set ::env(TECH_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/techLEF/$::env(STD_CELL_LIBRARY)/$::env(STD_CELL_LIBRARY).tlef"
set ::env(CELLS_LEF) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/$::env(STD_CELL_LIBRARY)/*.lef"]
set ::env(GPIO_PADS_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/lef/sky130_fd_io/sky130_fd_io.lef"
#else (!EF_FORMAT)
set ::env(TECH_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/techlef/$::env(STD_CELL_LIBRARY).tlef"
set ::env(CELLS_LEF) [glob "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/$::env(STD_CELL_LIBRARY)/lef/*.lef"]
set ::env(GPIO_PADS_LEF) "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_io/lef/sky130_fd_io.lef"
#endif (!EF_FORMAT)

# magic setup
#ifdef EF_FORMAT
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/20200508/TECHNAME.magicrc"
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/20200508/TECHNAME.tech"
#else (!EF_FORMAT)
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/TECHNAME.magicrc"
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/magic/TECHNAME.tech"
#endif (!EF_FORMAT)

# netgen setup
set ::env(NETGEN_SETUP_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/netgen/TECHNAME_setup.tcl"
# CTS luts
set ::env(CTS_TECH_DIR) "N/A"

set ::env(CTS_SQR_CAP) 0.258e-3
set ::env(CTS_SQR_RES) 0.125
set ::env(FP_TAPCELL_DIST) 14

# Tracks info
set ::env(TRACKS_INFO_FILE) "$::env(PDK_ROOT)/$::env(PDK)/libs.tech/openlane/$::env(STD_CELL_LIBRARY)/tracks.info"

set ::env(GLB_RT_L1_ADJUSTMENT) 0.99
