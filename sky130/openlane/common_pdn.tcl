# Power nets
set ::power_nets $::env(VDD_PIN)
set ::ground_nets $::env(GND_PIN)

set ::macro_blockage_layer_list "li1 met1 met2 met3 met4 met5"

# Used if the design is the core of the chip
set stdcell_core {
    name grid
    rails {
	    met1 {width $::env(FP_PDN_RAIL_WIDTH) pitch $::env(PLACE_SITE_HEIGHT) offset $::env(FP_PDN_RAIL_OFFSET)}
    }
    straps {
	    met4 {width $::env(FP_PDN_VWIDTH) pitch $::env(FP_PDN_VPITCH) offset $::env(FP_PDN_VOFFSET)}
	    met5 {width $::env(FP_PDN_HWIDTH) pitch $::env(FP_PDN_HPITCH) offset $::env(FP_PDN_HOFFSET)}
    }
    connect {{met1 met4} {met4 met5}}
}

# Used if the design is a macro in the core
set stdcell_macro {
    name grid
    rails {
	    met1 {width $::env(FP_PDN_RAIL_WIDTH) pitch $::env(PLACE_SITE_HEIGHT) offset $::env(FP_PDN_RAIL_OFFSET)}
    }
    straps {
	    met4 {width $::env(FP_PDN_VWIDTH) pitch $::env(FP_PDN_VPITCH) offset $::env(FP_PDN_VOFFSET)}
    }
    connect {{met1 met4}}
}

# Assesses whether the deisgn is the core of the chip or not based on the value of $::env(DESIGN_IS_CORE) and uses the appropriate stdcell section
if { [info exists ::env(DESIGN_IS_CORE)] } {
    if { $::env(DESIGN_IS_CORE) == 1 } {
        set stdcell $stdcell_core
    } else {
        set stdcell $stdcell_macro
    }
} else {
    set stdcell $stdcell_core
}

# Adds the core ring if enabled.
if { [info exists ::env(FP_PDN_CORE_RING)] } {
    if { $::env(FP_PDN_CORE_RING) == 1 } {
        dict append stdcell core_ring {
                met4 {width $::env(FP_PDN_CORE_RING_VWIDTH) spacing $::env(FP_PDN_CORE_RING_VSPACING) core_offset $::env(FP_PDN_CORE_RING_VOFFSET)}
                met5 {width $::env(FP_PDN_CORE_RING_HWIDTH) spacing $::env(FP_PDN_CORE_RING_HSPACING) core_offset $::env(FP_PDN_CORE_RING_HOFFSET)}
            }
    }
}

pdngen::specify_grid stdcell $stdcell

# A general macro that follows the premise of the set heirarchy. You may want to modify this or add other macro configs
pdngen::specify_grid macro {
    orient {R0 R180 MX MY R90 R270 MXR90 MYR90}
    power_pins "VDD VPWR"
    ground_pins "VSS VGND"
    blockages "li1 met1 met2 met3 met4"
    straps {
    }
    connect {{met4_PIN_ver met5}}
}

set ::halo [expr min($::env(FP_HORIZONTAL_HALO), $::env(FP_VERTICAL_HALO))]


# Metal layer for rails on every row
set ::rails_mlayer "met1" ;

# POWER or GROUND #Std. cell rails starting with power or ground rails at the bottom of the core area
set ::rails_start_with "POWER" ;

# POWER or GROUND #Upper metal stripes starting with power or ground rails at the left/bottom of the core area
set ::stripes_start_with "POWER" ;
