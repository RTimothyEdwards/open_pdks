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

set devices {}
lappend devices sky130_fd_pr__res_iso_pw
lappend devices sky130_fd_pr__res_generic_po
lappend devices sky130_fd_pr__res_high_po_0p35
lappend devices sky130_fd_pr__res_high_po_0p69
lappend devices sky130_fd_pr__res_high_po_1p41
lappend devices sky130_fd_pr__res_high_po_2p85
lappend devices sky130_fd_pr__res_high_po_5p73
lappend devices sky130_fd_pr__res_high_po
lappend devices sky130_fd_pr__res_xhigh_po_0p35
lappend devices sky130_fd_pr__res_xhigh_po_0p69
lappend devices sky130_fd_pr__res_xhigh_po_1p41
lappend devices sky130_fd_pr__res_xhigh_po_2p85
lappend devices sky130_fd_pr__res_xhigh_po_5p73
lappend devices sky130_fd_pr__res_xhigh_po
lappend devices sky130_fd_pr__res_generic_nd
lappend devices sky130_fd_pr__res_generic_pd
lappend devices mrdn_hv mrdp_hv

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
	property "-circuit1 $dev" delete mult
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 2
	property "-circuit2 $dev" series enable
	property "-circuit2 $dev" series {w critical}
	property "-circuit2 $dev" series {l add}
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" parallel {value par}
	property "-circuit2 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete mult
    }
}

#-------------------------------------------
# MRM (metal) resistors
#-------------------------------------------

set devices {}
lappend devices sky130_fd_pr__res_generic_l1
lappend devices sky130_fd_pr__res_generic_m1
lappend devices sky130_fd_pr__res_generic_m2
lappend devices sky130_fd_pr__res_generic_m3
#ifdef METAL5
lappend devices sky130_fd_pr__res_generic_m4
lappend devices sky130_fd_pr__res_generic_m5
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
	property "-circuit1 $dev" delete mult
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 2
	property "-circuit2 $dev" series enable
	property "-circuit2 $dev" series {w critical}
	property "-circuit2 $dev" series {l add}
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" parallel {value par}
	property "-circuit2 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete mult
    }
}

#-------------------------------------------
# (MOS) transistors
#-------------------------------------------

set devices {}
lappend devices sky130_fd_pr__nfet_01v8
lappend devices sky130_fd_pr__nfet_01v8_lvt
lappend devices sky130_fd_bs_flash__special_sonosfet_star
lappend devices sky130_fd_pr__nfet_g5v0d10v5
lappend devices sky130_fd_pr__pfet_01v8
lappend devices sky130_fd_pr__pfet_01v8_lvt
lappend devices sky130_fd_pr__pfet_01v8_mvt
lappend devices sky130_fd_pr__pfet_01v8_hvt
lappend devices sky130_fd_pr__pfet_g5v0d10v5
lappend devices sky130_fd_pr__special_pfet_pass
lappend devices sky130_fd_pr__special_nfet_pass
lappend devices sky130_fd_pr__special_nfet_latch
lappend devices sky130_fd_pr__cap_var_lvt
lappend devices sky130_fd_pr__cap_var_hvt
lappend devices sky130_fd_pr__cap_var

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	permute "-circuit1 $dev" 1 3
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {l critical}
	property "-circuit1 $dev" parallel {w add}
	property "-circuit1 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete as ad ps pd mult sa sb sd nf nrd nrs
    }
    if {[lsearch $cells2 $dev] >= 0} {
	permute "-circuit2 $dev" 1 3
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {l critical}
	property "-circuit2 $dev" parallel {w add}
	property "-circuit2 $dev" tolerance {w 0.01} {l 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete as ad ps pd mult sa sb sd nf nrd nrs
    }
}

#-------------------------------------------
# diodes
#-------------------------------------------

set devices {}
lappend devices sky130_fd_pr__diode_pw2nd_05v5
lappend devices sky130_fd_pr__diode_pw2nd_05v5_lvt
lappend devices sky130_fd_pr__diode_pw2nd_05v5_nvt
lappend devices sky130_fd_pr__diode_pd2nw_05v5
lappend devices sky130_fd_pr__diode_pd2nw_05v5_lvt
lappend devices sky130_fd_pr__diode_pd2nw_05v5_hvt
lappend devices sky130_fd_pr__diode_pw2nd_11v0
lappend devices sky130_fd_pr__diode_pd2nw_11v0

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {area add}
	property "-circuit1 $dev" parallel {value add}
	property "-circuit1 $dev" tolerance {area 0.02}
	# Ignore these properties
	property "-circuit1 $dev" delete mult perim
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {area add}
	property "-circuit2 $dev" parallel {value add}
	property "-circuit2 $dev" tolerance {area 0.02}
	# Ignore these properties
	property "-circuit2 $dev" delete mult perim
    }
}

#-------------------------------------------
# capacitors
# MiM capacitors
#-------------------------------------------

set devices {}
lappend devices sky130_fd_pr__cap_mim_m3_1
lappend devices sky130_fd_pr__cap_mim_m3_2

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	property "-circuit1 $dev" parallel {area add}
	property "-circuit1 $dev" parallel {value add}
	property "-circuit1 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit1 $dev" delete mult perim mf
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	property "-circuit2 $dev" parallel {area add}
	property "-circuit2 $dev" parallel {value add}
	property "-circuit2 $dev" tolerance {l 0.01} {w 0.01}
	# Ignore these properties
	property "-circuit2 $dev" delete mult perim mf
    }
}

#-------------------------------------------
# Fixed-layout devices
# bipolar transistors,
# VPP capacitors
#-------------------------------------------

set devices {}
lappend devices sky130_fd_pr__npn_05v5_W1p00L1p00
lappend devices sky130_fd_pr__npn_05v5_W1p00L2p00
lappend devices sky130_fd_pr__pnp_05v5_W0p68L0p68
lappend devices sky130_fd_pr__pnp_05v5_W3p40L3p40

#ifdef METAL5
lappend devices sky130_fd_pr__cap_vpp_11p5x11p7_lim5_shield
lappend devices sky130_fd_pr__cap_vpp_11p5x11p7_m3_lim5_shield
lappend devices sky130_fd_pr__cap_vpp_11p5x11p7_m4_shield
lappend devices sky130_fd_pr__cap_vpp_11p5x11p7_pom4_shield
lappend devices sky130_fd_pr__cap_vpp_4p4x4p6_m3_lim5_shield
lappend devices sky130_fd_pr__cap_vpp_6p8x6p1_lim4_shield
lappend devices sky130_fd_pr__cap_vpp_6p8x6p1_polym4_shield
#endif (METAL5)
lappend devices sky130_fd_pr__cap_vpp_8p6x7p9_m3_lim5_shield
lappend devices sky130_fd_pr__cap_vpp_11p5x11p7_m3_li_shield
lappend devices sky130_fd_pr__cap_vpp_11p5x11p7_m3_shield
lappend devices sky130_fd_pr__cap_vpp_1p8x1p8_li_shield
lappend devices sky130_fd_pr__cap_vpp_1p8x1p8_m3_shield
lappend devices sky130_fd_pr__cap_vpp_4p4x4p6_m3_li_shield
lappend devices sky130_fd_pr__cap_vpp_4p4x4p6_m3_shield
lappend devices sky130_fd_pr__cap_vpp_8p6x7p9_m3_li_shield
lappend devices sky130_fd_pr__cap_vpp_8p6x7p9_m3_shield
#ifdef REDISTRIBUTION
lappend devices sky130_fd_pr__ind_04_01
lappend devices sky130_fd_pr__ind_04_02
#endif (REDISTRIBUTION)

foreach dev $devices {
    if {[lsearch $cells1 $dev] >= 0} {
	property "-circuit1 $dev" parallel enable
	# Ignore these properties
	property "-circuit1 $dev" delete mult
    }
    if {[lsearch $cells2 $dev] >= 0} {
	property "-circuit2 $dev" parallel enable
	# Ignore these properties
	property "-circuit2 $dev" delete mult
    }
}

#---------------------------------------------------------------
# Digital cells (ignore decap, fill, and tap cells)
# Make a separate list for each supported library
#---------------------------------------------------------------
# e.g., ignore class "-circuit2 sky130_fc_sc_hd__decap_3"
#---------------------------------------------------------------

foreach cell $cells1 {
    if {[regexp {sky130_fd_sc_[^_]+__decap_[[:digit:]]+} $cell match]} {
        ignore class "-circuit1 $cell"
    }
    if {[regexp {sky130_fd_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
        ignore class "-circuit1 $cell"
    }
}
foreach cell $cells2 {
    if {[regexp {sky130_fd_sc_[^_]+__decap_[[:digit:]]+} $cell match]} {
        ignore class "-circuit2 $cell"
    }
    if {[regexp {sky130_fd_sc_[^_]+__fill_[[:digit:]]+} $cell match]} {
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
