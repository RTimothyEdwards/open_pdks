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

# Allow override of default #columns in the output format.
catch {format $env(NETGEN_COLUMNS)}

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

set devices {}
lappend devices nwell_1p5
lappend devices ppolyf_u
lappend devices npolyf_u
lappend devices ppolyf_s
lappend devices nplus_u
lappend devices pplus_u
lappend devices nw1a_6p0

lappend devices npolyf_s
lappend devices pfield_1p5
lappend devices pf1va_6p0
#ifdef HRPOLY1K
lappend devices ppolyf_u_1k
lappend devices ppolyf_u_1k_6p0
#endif
#ifdef HRPOLY2K
lappend devices ppolyf_u_2k
lappend devices ppolyf_u_2k_6p0
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

set devices {}
lappend devices rm1
lappend devices rm2
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

set devices {}
lappend devices nmos_1p5
lappend devices pmos_1p5
lappend devices nmos_6p0
lappend devices pmos_6p0
lappend devices nmoscap_1p5
lappend devices nmoscap_6p0

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

set devices {}
lappend devices np_1p5
lappend devices pn_1p5
lappend devices np_6p0
lappend devices pn_6p0
lappend devices nwp_1p5
lappend devices nwp_6p0

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

set devices {}
lappend devices vnpn_lv_2p5x2p5
lappend devices vnpn_lv_5x5
lappend devices vnpn_lv_10x10

lappend devices vnpn_mv_2p5x2p5
lappend devices vnpn_mv_5x5
lappend devices vnpn_mv_10x10
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
# Digital cells (ignore decap, fill, and tap cells)
# Make a separate list for each supported library
#---------------------------------------------------------------
# e.g., ignore class "-circuit2 gf180mcu_fd_sc_7t5v0__endcap"
#---------------------------------------------------------------

foreach cell $cells1 {
#   if {[regexp {gf180mcu_fd_sc_[^_]+__fillcap_[[:digit:]]+} $cell match]} {
#       ignore class "-circuit1 $cell"
#   }
    if {[regexp {gf180mcu_fd_sc_[^_]+__endcap} $cell match]} {
        ignore class "-circuit1 $cell"
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        ignore class "-circuit1 $cell"
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__filltie} $cell match]} {
        ignore class "-circuit1 $cell"
    }
}

foreach cell $cells2 {
#   if {[regexp {gf180mcu_fd_sc_[^_]+__fillcap_[[:digit:]]+} $cell match]} {
#       ignore class "-circuit2 $cell"
#   }
    if {[regexp {gf180mcu_fd_sc_[^_]+__endcap} $cell match]} {
        ignore class "-circuit2 $cell"
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        ignore class "-circuit2 $cell"
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__filltie} $cell match]} {
        ignore class "-circuit2 $cell"
    }
}

# Do the same for the OSU standard cell libraries

foreach cell $cells1 {
    if {[regexp {gf180mcu_osu_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        ignore class "-circuit1 $cell"
    }
}

foreach cell $cells2 {
    if {[regexp {gf180mcu_osu_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        ignore class "-circuit2 $cell"
    }
}

#---------------------------------------------------------------
# Allow the fill, decap, etc., cells to be parallelized
#---------------------------------------------------------------

foreach cell $cells1 {
    if {[regexp {gf180mcu_fd_sc_[^_]+__fillcap_[[:digit:]]+} $cell match]} {
        property "-circuit1 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__endcap} $cell match]} {
        property "-circuit1 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        property "-circuit1 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__filltie} $cell match]} {
        property "-circuit1 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__antenna} $cell match]} {
        property "-circuit1 $cell" parallel enable
    }
}

foreach cell $cells2 {
    if {[regexp {gf180mcu_fd_sc_[^_]+__fillcap_[[:digit:]]+} $cell match]} {
        property "-circuit2 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__endcap} $cell match]} {
        property "-circuit2 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        property "-circuit2 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__filltie} $cell match]} {
        property "-circuit2 $cell" parallel enable
    }
    if {[regexp {gf180mcu_fd_sc_[^_]+__antenna} $cell match]} {
        property "-circuit2 $cell" parallel enable
    }
}

# Do the same for the OSU 3.3V standard cell library

foreach cell $cells1 {
    if {[regexp {gf180mcu_osu_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        property "-circuit1 $cell" parallel enable
    }
}

foreach cell $cells2 {
    if {[regexp {gf180mcu_osu_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        property "-circuit2 $cell" parallel enable
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
