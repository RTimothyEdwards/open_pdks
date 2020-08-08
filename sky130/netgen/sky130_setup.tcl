###
###     Source file sky130_setup.tcl
###     Process this file with the preproc.py processor
###
#---------------------------------------------------------------
# Setup file for netgen LVS
# SkyWater TECHNAME
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

set devices {xpwres mrp1 xhrpoly uhrpoly mrdn mrdp mrdn_hv mrdp_hv}

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 2
	property "-circuit1 $dev" series enable
	property "-circuit1 $dev" series {w critical}
	property "-circuit1 $dev" series {l add}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" parallel {value par}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	# property "-circuit2 $dev" delete
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 2
	property "-circuit1 $dev" series enable
	property "-circuit1 $dev" series {w critical}
	property "-circuit1 $dev" series {l add}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" parallel {value par}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	# property "-circuit2 $dev" delete
    }
}

#-------------------------------------------
# MRM (metal) resistors
#-------------------------------------------

set devices {mrl1 mrm1 mrm2 mrm3}
#ifdef METAL5
lappend devices mrm4 mrm5
#endif (METAL5)

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 2
	property "-circuit1 $dev" series enable
	property "-circuit1 $dev" series {w critical}
	property "-circuit1 $dev" series {l add}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" parallel {value par}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	# property "-circuit2 $dev" delete
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 2
	property "-circuit1 $dev" series enable
	property "-circuit1 $dev" series {w critical}
	property "-circuit1 $dev" series {l add}
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" parallel {value par}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	# property "-circuit2 $dev" delete
    }
}

#-------------------------------------------
# (MOS) transistors
#-------------------------------------------

set devices {nshort nlowvt sonos_e nhvnative nhv pshort plowvt phighvt phv}
lappend devices ppu npass npd
lappend devices xcnwvc xcnwvc2 xchvnwc

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 3
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete as ad ps pd
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 3
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete as ad ps pd
    }
}

#-------------------------------------------
# diodes
#-------------------------------------------

set devices {ndiode ndiode_lvt pdiode pdiode_lvt pdiode_hvt ndiode_h pdiode_h}
lappend devices ndiode_native

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {area add}
	property "-circuit1 $dev" parallel {value add}
	property "-circuit1 $dev" tolerance {area 0.02}
	# Ignore these properties
	property "-circuit2 $dev" delete perim
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit1 $dev" parallel {area add}
	property "-circuit1 $dev" parallel {value add}
	property "-circuit2 $dev" tolerance {area 0.02}
	# Ignore these properties
	property "-circuit2 $dev" delete perim
    }
}

#-------------------------------------------
# capacitors
# MiM capacitors
#-------------------------------------------

set devices {xcmimc1 xcmimc2}

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {area add}
	property "-circuit1 $dev" parallel {value add}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	# property "-circuit2 $dev" delete perim
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {area add}
	property "-circuit1 $dev" parallel {value add}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	# property "-circuit2 $dev" delete perim
    }
}

#-------------------------------------------
# Fixed-layout devices
# bipolar transistors,
# VPP capacitors
#-------------------------------------------

set devices {sky130rf_npn_1x1 sky130rf_npn_1x2 sky130rf_pnp5x}
#ifdef METAL5
lappend devices balun xint4_011 xind4_02
lappend devices sky130rf2_xcmvpp11p5x11p7_lim5shield
lappend devices sky130rf2_xcmvpp11p5x11p7_m3_lim5shield
lappend devices sky130rf2_xcmvpp11p5x11p7_m4shield
lappend devices sky130rf2_xcmvpp11p5x11p7_polym4shield
lappend devices sky130rf2_xcmvpp11p5x11p7_polym50p4shield
lappend devices sky130rf2_xcmvpp4p4x4p6_m3_lim5shield
lappend devices sky130rf2_xcmvpp6p8x6p1_lim4shield
lappend devices sky130rf2_xcmvpp6p8x6p1_polym4shield
#endif (METAL5)
lappend devices sky130rf2_xcmvpp8p6x7p9_m3_lim5shield
lappend devices sky130rf2_xcmvppx4_2xnhvnative10x4
lappend devices sky130rf_xcmvpp11p5x11p7_m3_lishield
lappend devices sky130rf_xcmvpp11p5x11p7_m3shield
lappend devices sky130rf_xcmvpp1p8x1p8_lishield
lappend devices sky130rf_xcmvpp1p8x1p8_m3shield
lappend devices sky130rf_xcmvpp2
lappend devices sky130rf_xcmvpp2_nwell
lappend devices sky130rf_xcmvpp4p4x4p6_m3_lishield
lappend devices sky130rf_xcmvpp4p4x4p6_m3shield
lappend devices sky130rf_xcmvpp8p6x7p9_m3_lishield
lappend devices sky130rf_xcmvpp8p6x7p9_m3shield

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	# Ignore these properties
	# property "-circuit2 $dev" delete
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	# Ignore these properties
	# property "-circuit2 $dev" delete
    }
}

#---------------------------------------------------------------
# Digital cells (ignore decap, fill, and tap cells)
# Make a separate list for each supported library
#---------------------------------------------------------------
# e.g., ignore class "-circuit2 sky130_fc_sc_hd_decap_3"
#---------------------------------------------------------------

foreach cell $cells1 {
    if {[regexp {sky130_fd_sc_\w\w__decap_[[:digit:]]+} $cell match]} {
        ignore class "-circuit1 $cell"
    }
    if {[regexp {sky130_fd_sc_\w\w__fill_[[:digit:]]+} $cell match]} {
        ignore class "-circuit1 $cell"
    }
}
foreach cell $cells2 {
    if {[regexp {sky130_fd_sc_\w\w__decap_[[:digit:]]+} $cell match]} {
        ignore class "-circuit2 $cell"
    }
    if {[regexp {sky130_fd_sc_\w\w__fill_[[:digit:]]+} $cell match]} {
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
