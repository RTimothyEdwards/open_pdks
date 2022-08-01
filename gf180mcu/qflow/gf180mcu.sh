#!/bin/tcsh
#---------------------------------------------------------------
# Shell script setting up all variables used by the qflow scripts
# for this project
#---------------------------------------------------------------

# The LEF file containing standard cell macros

#ifdef EF_STYLE
set leffile=LOCAL_PREFIX/TECHNAME/libs.ref/lef/LIBRARY/LIBRARY.lef
#else
set leffile=LOCAL_PREFIX/TECHNAME/libs.ref/LIBRARY/lef/LIBRARY.lef
#endif

# The SPICE netlist containing subcell definitions for all the standard cells

#ifdef EF_STYLE
set spicefile=LOCAL_PREFIX/TECHNAME/libs.ref/spi/LIBRARY/LIBRARY.spi
#else
set spicefile=LOCAL_PREFIX/TECHNAME/libs.ref/LIBRARY/spice/LIBRARY.spice
#endif

# The liberty format file containing standard cell timing and function information

#ifdef EF_STYLE
set libertyfile=LOCAL_PREFIX/TECHNAME/libs.ref/lib/LIBRARY/LIBRARY__ss_1p62v_125c.lib
#else
set libertyfile=LOCAL_PREFIX/TECHNAME/libs.ref/LIBRARY/liberty/LIBRARY__ss_1p62v_125c.lib
#endif

# If there is another LEF file containing technology information
# that is separate from the file containing standard cell macros,
# set this.  Otherwise, leave it defined as an empty string.

# NOTE:  Backend-specific technology LEF files come from BEOL-specific
# directories, and all have the same name.

set techleffile=LOCAL_PREFIX/TECHNAME/TECHLEF_PATH/LIBRARY.nom.tlef

# All cells below should be the lowest output drive strength value,
# if the standard cell set has multiple cells with different drive
# strengths.  Comment out any cells that do not exist.

set flopcell=LIBRARY__dffq_x1	;# Standard positive-clocked DFF, no set or reset
set flopsetreset=LIBRARY__dffrsnq_x1 ;# DFF with both set and clear
set setpin=SETN		;# The name of the set pin on DFFs
set resetpin=RN		;# The name of the clear/reset pin on DFFs
set setpininvert=1	;# Set this to 1 if the set pin is inverted (!set)
set resetpininvert=1	;# Set this to 1 if the reset pin is inverted (!reset)
set floppinout=Q	;# Name of the output pin on DFFs
set floppinin=D		;# Name of the output pin on DFFs
set floppinclk=CLK	;# Name of the clock pin on DFFs
set bufcell=LIBRARY__buf_x2	;# Minimum drive strength buffer cell
set bufpin_in=I		;# Name of input port to buffer cell
set bufpin_out=Z	;# Name of output port to buffer cell
set clkbufcell=LIBRARY__clkbuf_x2	;# Minimum drive strength buffer cell
set clkbufpin_in=I	;# Name of input port to buffer cell
set clkbufpin_out=Z	;# Name of output port to buffer cell
set inverter=LIBRARY__inv_x1	;# Minimum drive strength inverter cell
set invertpin_in=I	;# Name of input port to inverter cell
set invertpin_out=ZN	;# Name of output port to inverter cell
set norgate=LIBRARY__nor2_x1	;# 2-input NOR gate, minimum drive strength
set norpin_in1=A1	;# Name of first input pin to NOR gate
set norpin_in2=A2	;# Name of second input pin to NOR gate
set norpin_out=ZN	;# Name of output pin from OR gate
set nandgate=LIBRARY__nand2_x1	;# 2-input NAND gate, minimum drive strength
set nandpin_in1=A1	;# Name of first input pin to NAND gate
set nandpin_in2=A2	;# Name of second input pin to NAND gate
set nandpin_out=ZN	;# Name of output pin from NAND gate
# Synchronize it with .par's TWSC*feedThruWidth
set fillcell=LIBRARY__fill	;# Spacer (filler) cell (prefix, if more than one)
set decapcell=LIBRARY__fillcap	;# Decap (filler) cell (prefix, if more than one)
set antennacell=LIBRARY__antenna	;# Antenna (filler) cell (prefix, if more than one)
set antennapin_in="I"	;# Antenna cell input connection
set bodytiecell=LIBRARY__filltie

# yosys tries to eliminate use of these; depends on source .v
set tiehi="tieh"	;# Cell to connect to power, if one exists
set tiehipin_out="ZN"	;# Output pin name of tiehi cell, if it exists
set tielo="tiel"	;# Cell to connect to ground, if one exists
set tielopin_out="Z"	;# Output pin name of tielo cell, if it exists

set gndnet="VSS,VPW"	;# Name used for ground pins in standard cells
set vddnet="VDD,VNW"	;# Name used for power pins in standard cells

set separator=x		;# Separator between gate names and drive strengths
set techfile=LOCAL_PREFIX/TECHNAME/MAGIC_CURRENT/TECHNAME.tech	;# magic techfile
set magicrc=LOCAL_PREFIX/TECHNAME/MAGIC_CURRENT/TECHNAME.magicrc	;# magic startup script
set magic_display="XR" 	;# magic display, defeat display query and OGL preference
set netgen_setup=LOCAL_PREFIX/TECHNAME/libs.tech/netgen/TECHNAME_setup.tcl	;# netgen setup file for LVS
#ifdef EF_STYLE
set gdsfile=LOCAL_PREFIX/TECHNAME/libs.ref/gds/LIBRARY/LIBRARY.gds	;# GDS database of standard cells
set verilogfile=LOCAL_PREFIX/TECHNAME/libs.ref/verilog/LIBRARY/LIBRARY.v	;# Verilog models of standard cells
#else
set gdsfile=LOCAL_PREFIX/TECHNAME/libs.ref/LIBRARY/gds/LIBRARY.gds	;# GDS database of standard cells
set verilogfile=LOCAL_PREFIX/TECHNAME/libs.ref/LIBRARY/verilog/LIBRARY.v	;# Verilog models of standard cells
#endif

# Set a conditional default in the project_vars.sh file for this process
set postproc_options="-anchors"
#ifdef METALS3
set route_layers = 3
#endif (METALS3)
#ifdef METALS4
set route_layers = 4
#endif (METALS4)
#ifdef METALS5
set route_layers = 5
#endif (METALS5)
#ifdef METALS6
set route_layers = 6
#endif (METALS6)
set fill_ratios="0,70,10,20"
set fanout_options="-l 150 -c 15"
set addspacers_options="-stripe 2.5 50.0 PG"
set xspice_options="-io_time=250p -time=50p -idelay=20p -odelay=50p -cload=250f"
