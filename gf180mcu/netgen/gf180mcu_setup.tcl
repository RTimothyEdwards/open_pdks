###
###     Source file gf013_setup.tcl
###     Process this file with the preproc.py processor
###
#---------------------------------------------------------------
# Setup file for netgen LVS
# Global Foundries TECHNAME
#---------------------------------------------------------------
permute default
property default
property parallel none

#---------------------------------------------------------------
# For the following, get the cell lists from
# circuit1 and circuit2.
#---------------------------------------------------------------

set cells1 [cells list -all -circuit1]
set cells2 [cells list -all -circuit2]

# NOTE:  In accordance with the LVS manager GUI, the schematic is
# always circuit2, so some items like property "par1" only need to
# be specified for circuit2.

#-------------------------------------------
# Resistors (except metal)
#-------------------------------------------

set devices {nwell_1p5 ppolyf_u npolyf_u ppolyf_s nplus_u pplus_u nw1a_6p0}
lappend devices npolyf_s pfield_1p5 pf1va_6p0
#ifdef HRPOLY1K
lappend devices ppolyf_u_1k ppolyf_u_1k_6p0
#endif
#ifdef HRPOLY2K
lappend devices ppolyf_u_2k ppolyf_u_2k_6p0
#endif

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" serial enable
	permute "-circuit1 $dev" 1 2
	property "-circuit1 $dev" merge {l ser_critical} {w add_critical}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 pm
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" serial enable
	permute "-circuit2 $dev" 1 2
	property "-circuit2 $dev" merge {l ser_critical} {w add_critical}
	property "-circuit2 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 pm
    }
}

#-------------------------------------------
# RM (metal) resistors
#-------------------------------------------

set devices {rm1 rm2}
#ifdef METALS4 || METALS5 || METALS6 || METALS7
lappend devices rm3
#endif (METALS4 || METALS5 || METALS6 || METALS7)
#ifdef METALS5 || METALS6 || METALS7
lappend devices rm4
#endif (METALS5 || METALS6 || METALS7)
#ifdef METALS6 || METALS7
lappend devices rm5
#endif (METALS6 || METALS7)
#ifdef METALS7
lappend devices rm6
#endif (METALS7)
#ifndef THICKMET
lappend devices rmtp
#endif (THICKMET)
#ifdef THICKMET || THICK2MET
lappend devices rmtk
#endif (THICKMET || THICK2MET)

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	permute "-circuit1 $dev" 1 2
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 pm
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	permute "-circuit2 $dev" 1 2
	property "-circuit2 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 pm
    }
}

#-------------------------------------------
# (MOS) transistors
#-------------------------------------------

set devices {nmos_1p5 pmos_1p5 nmos_6p0 pmos_6p0 nmoscap_1p5 nmoscap_6p0}

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	permute "-circuit1 $dev" 1 3
	property "-circuit1 $dev" merge {w add_critical}
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 NRD NRS
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	permute "-circuit2 $dev" 1 3
	property "-circuit2 $dev" merge {w add_critical}
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 NRD NRS
    }
}

#-------------------------------------------
# diodes
#-------------------------------------------

set devices {np_1p5 pn_1p5 np_6p0 pn_6p0 nwp_1p5 nwp_6p0}

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" merge {area add_critical}
	property "-circuit1 $dev" tolerance {area 0.02}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 peri
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" merge {area add_critical}
	property "-circuit2 $dev" tolerance {area 0.02}
	# Ignore these properties
	property "-circuit2 $dev" delete par1 peri
    }
}

#-----------------------------------------------
# Fixed-layout devices
# NPN bipolar transistors,
# sandwich (MoM) capacitors, and MiM capacitors
#-----------------------------------------------

set devices {vnpn_lv_2p5x2p5 vnpn_lv_5x5 vnpn_lv_10x10}
lappend devices vnpn_mv_2p5x2p5 vnpn_mv_5x5 vnpn_mv_10x10
lappend devices apmom_bb
#ifdef MIM
lappend devices mim_sm_bb
#endif
#ifdef DMIM
lappend devices mim_dm_bb
#endif

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	# Ignore these properties
	property "-circuit2 $dev" delete par1
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	# Ignore these properties
	property "-circuit2 $dev" delete par1
    }
}

#---------------------------------------------------------------
# D_CELLS_SC9 (ignore FILL cells)
#---------------------------------------------------------------
# e.g., ignore class "-circuit2 FILL5"
#---------------------------------------------------------------

foreach cell $cells1 {
    if {[regexp "FILL\[0-9\]+" $cell match]} {
        ignore class "-circuit1 $cell"
    }
}
foreach cell $cells2 {
    if {[regexp "FILL\[0-9\]+" $cell match]} {
        ignore class "-circuit2 $cell"
    }
}

#---------------------------------------------------------------
# ICPIO_5P0 (ignore FILL cells)
#---------------------------------------------------------------
# e.g., ignore class "-circuit1 GF_CI_FILL5"
#---------------------------------------------------------------
foreach cell $cells1 {
    if {[regexp "GF_CI_FILL.*" $cell match]} {
        ignore class "-circuit1 $cell"
    }
}
foreach cell $cells2 {
    if {[regexp "GF_CI_FILL.*" $cell match]} {
        ignore class "-circuit2 $cell"
    }
}

#---------------------------------------------------------------
# Handle cells captured from Electric
#
# Find cells of the form "<library>__<cellname>" in the netlist
# from Electric where the extracted layout netlist has only
# "<cellname>".  Cross-check by ensuring that the full name
# "<library>__<cellname>" does not exist in both cells, and that
# the truncated name "<cellname>" does not exist in both cells.
#---------------------------------------------------------------
# e.g., hydra_spi_controller__hydra_spi_controller
#---------------------------------------------------------------
foreach cell $cells1 {
    if {[regexp "(.+)__(.+)" $cell match library cellname]} {
        if {([lsearch $cells2 $cell] < 0) && \
                ([lsearch $cells2 $cellname] >= 0) && \
                ([lsearch $cells1 $cellname] < 0)} {
            equate classes "-circuit1 $cell" "-circuit2 $cellname"
	    puts stdout "Matching pins of $cell in circuit 1 and $cellname in circuit 2"
	    equate pins "-circuit1 $cell" "-circuit2 $cellname"
        }
    }
}

foreach cell $cells2 {
    if {[regexp "(.+)__(.+)" $cell match library cellname]} {
        if {([lsearch $cells1 $cell] < 0) && \
                ([lsearch $cells1 $cellname] >= 0) && \
                ([lsearch $cells2 $cellname] < 0)} {
            equate classes "-circuit1 $cellname" "-circuit2 $cell"
	    puts stdout "Matching pins of $cellname in circuit 1 and $cell in circuit 2"
	    equate pins "-circuit1 $cellname" "-circuit2 $cell"
        }
    }
}

# Match pins on black-box cells if LVS is called with "-blackbox"
if {[model blackbox]} {
    foreach cell $cells1 {
	if {[model "-circuit1 $cell"] == "blackbox"} {
	    if {[lsearch $cells2 $cell] >= 0} {
		puts stdout "Matching pins of $cell in circuits 1 and 2"
		equate pins "-circuit1 $cell" "-circuit2 $cell"
	    }
	}
    }
}

#---------------------------------------------------------------
