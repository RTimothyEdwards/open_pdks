# Process node
set ::env(PROCESS) 130
set ::env(DEF_UNITS_PER_MICRON) 1000


# Placement site for core cells
# This can be found in the technology lef

set ::env(VDD_PIN) "vpwr"
set ::env(GND_PIN) "vgnd"

# Technology LEF
set ::env(TECH_LEF) "$::env(PDK_ROOT)/TECHNAME/libs.ref/techLEF/$::env(PDK_VARIANT)/*.tlef"
set ::env(CELLS_LEF) [glob "$::env(PDK_ROOT)/TECHNAME/libs.ref/lef/$::env(PDK_VARIANT)/*.lef"]
set ::env(MAGIC_TECH_FILE) "$::env(PDK_ROOT)/TECHNAME/libs.tech/magic/sky130A.tech"
set ::env(MAGIC_MAGICRC) "$::env(PDK_ROOT)/TECHNAME/libs.tech/magic/sky130A.magicrc"
set ::env(GPIO_PADS_LEF) [glob "$::env(PDK_ROOT)/TECHNAME/libs.ref/sky130_fd_io/lef/routing_abstract.lef"]

# netgen setup
set ::env(NETGEN_SETUP_FILE) $::env(PDK_ROOT)/TECHNAME/libs.tech/netgen/TECHNAME_setup.tcl
# CTS luts
set ::env(CTS_TECH_DIR) "N/A"

set ::env(FP_TAPCELL_DIST) 14


set ::env(GLB_RT_L1_ADJUSTMENT) 0.99
