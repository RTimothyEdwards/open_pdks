#!/bin/tcsh
#---------------------------------------------------------------
# Shell script setting up all variables used by the qflow scripts
# for this project
#---------------------------------------------------------------

# The LEF file containing standard cell macros

#ifdef EF_FORMAT
set leffile=STAGING_PATH/TECHNAME/libs.ref/lef/sky130_osu130/sky130_osu130.lef
#else (!EF_FORMAT)
set leffile=STAGING_PATH/TECHNAME/libs.ref/sky130_osu130/lef/sky130_osu130.lef
#endif (!EF_FORMAT)

# The SPICE netlist containing subcell definitions for all the standard cells
#ifdef EF_FORMAT
set spicefile=STAGING_PATH/TECHNAME/libs.ref/spice/sky130_osu130/sky130_osu130.spice
#else (!EF_FORMAT)
set spicefile=STAGING_PATH/TECHNAME/libs.ref/sky130_osu130/spice/sky130_osu130.spice
#endif (!EF_FORMAT)

# The liberty format file containing standard cell timing and function information
#ifdef EF_FORMAT
set libertyfile=STAGING_PATH/TECHNAME/libs.ref/lib/sky130_osu130/sky130_osu130.lib
#else (!EF_FORMAT)
set libertyfile=STAGING_PATH/TECHNAME/libs.ref/sky130_osu130/lib/sky130_osu130.lib
#endif (!EF_FORMAT)

# If there is another LEF file containing technology information
# that is separate from the file containing standard cell macros,
# set this.  Otherwise, leave it defined as an empty string.

#ifdef METAL5
#ifdef EF_FORMAT
set techleffile=STAGING_PATH/TECHNAME/libs.ref/techLEF/sky130_osu130/sky130_osu130_tech.lef
#else (!EF_FORMAT)
set techleffile=STAGING_PATH/TECHNAME/libs.ref/sky130_osu130/techLEF/sky130_osu130_tech.lef
#endif (!EF_FORMAT)
#else
# NOTE:  There is no technology LEF file for the 3-metal stack!
#endif

# All cells below should be the lowest output drive strength value,
# if the standard cell set has multiple cells with different drive
# strengths.  Comment out any cells that do not exist.

set bufcell=BUFX2		;# Minimum drive strength buffer cell
set bufpin_in=A			;# Name of input port to buffer cell
set bufpin_out=Y		;# Name of output port to buffer cell
set clkbufcell=BUFX2		;# Minimum drive strength buffer cell
set clkbufpin_in=A		;# Name of input port to buffer cell
set clkbufpin_out=Y		;# Name of output port to buffer cell

set fillcell=FILL		;# Spacer (filler) cell (prefix, if more than one)
set decapcell=""		;# Decap (filler) cell (prefix, if more than one)
set antennacell=""		;# Antenna (filler) cell (prefix, if more than one)
set antennapin_in=""		;# Antenna cell input connection
set bodytiecell=""		;# Body tie (filler) cell (prefix, if more than one)

# yosys tries to eliminate use of these; depends on source .v
set tiehi=""			;# Cell to connect to power, if one exists
set tiehipin_out=""		;# Output pin name of tiehi cell, if it exists
set tielo=""			;# Cell to connect to ground, if one exists
set tielopin_out=""		;# Output pin name of tielo cell, if it exists

set gndnet="vdd"		;# Name used for ground pins in standard cells
set vddnet="vss"		;# Name used for power pins in standard cells

set separator=""		;# Separator between gate names and drive strengths
set techfile=STAGING_PATH/TECHNAME/MAGIC_CURRENT/TECHNAME.tech	    ;# magic techfile
set magicrc=STAGING_PATH/TECHNAME/MAGIC_CURRENT/TECHNAME.magicrc    ;# magic startup script
set magic_display="XR" 	;# magic display, defeat display query and OGL preference
set netgen_setup=STAGING_PATH/TECHNAME/libs.tech/netgen/TECHNAME_setup.tcl	;# netgen setup file for LVS
#ifdef EF_FORMAT
set gdsfile=STAGING_PATH/TECHNAME/libs.ref/gds/sky130_osu130/sky130_osu130.gds	;# GDS database of standard cells
set verilogfile=STAGING_PATH/TECHNAME/libs.ref/verilog/sky130_osu130/sky130_osu130.v	;# Verilog models of standard cells
#else (!EF_FORMAT)
set gdsfile=STAGING_PATH/TECHNAME/libs.ref/sky130_osu130/gds/sky130_osu130.gds	;# GDS database of standard cells
set verilogfile=STAGING_PATH/TECHNAME/libs.ref/sky130_osu130/verilog/sky130_osu130.v	;# Verilog models of standard cells
#endif (!EF_FORMAT)

# Set a conditional default in the project_vars.sh file for this process
set postproc_options=""
#ifdef METAL5
# Normally one does not want to use the top metal for signal routing
set route_layers = 5
#else
set route_layers = 3
#endif
set fill_ratios="100,0,0,0"
set fanout_options="-l 100 -c 10"
set addspacers_options="-stripe 1.6 40.0 PG"
set xspice_options="-io_time=250p -time=50p -idelay=20p -odelay=50p -cload=250f"
