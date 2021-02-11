# Power nets

if { ! [info exists ::env(VDD_NET)] } {
	set ::env(VDD_NET) $::env(VDD_PIN)
}

if { ! [info exists ::env(GND_NET)] } {
	set ::env(GND_NET) $::env(GND_PIN)
}

set ::power_nets $::env(VDD_NET)
set ::ground_nets $::env(GND_NET)

if { [info exists ::env(FP_PDN_ENABLE_GLOBAL_CONNECTIONS)] } {
    if { $::env(FP_PDN_ENABLE_GLOBAL_CONNECTIONS) == 1 } {
        # to parameterize -- needs a PDNGEN fix
        set pdngen::global_connections {
            VPWR {
                {inst_name .* pin_name VPWR}
                {inst_name .* pin_name VPB}
            }
            VGND {
                {inst_name .* pin_name VGND}
                {inst_name .* pin_name VNB}
            }
        }
    }
}

# Used if the design is the core of the chip
set stdcell_core {
    name grid
    straps {
	    $::env(FP_PDN_LOWER_LAYER) {width $::env(FP_PDN_VWIDTH) pitch $::env(FP_PDN_VPITCH) offset $::env(FP_PDN_VOFFSET)}
	    $::env(FP_PDN_UPPER_LAYER) {width $::env(FP_PDN_HWIDTH) pitch $::env(FP_PDN_HPITCH) offset $::env(FP_PDN_HOFFSET)}
    }
    connect {{$::env(FP_PDN_LOWER_LAYER) $::env(FP_PDN_UPPER_LAYER)}}
}

# Used if the design is a macro in the core
set stdcell_macro {
    name grid
    straps {
	    $::env(FP_PDN_LOWER_LAYER) {width $::env(FP_PDN_VWIDTH) pitch $::env(FP_PDN_VPITCH) offset $::env(FP_PDN_VOFFSET)}
    }
    connect {}
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
                $::env(FP_PDN_LOWER_LAYER) {width $::env(FP_PDN_CORE_RING_VWIDTH) spacing $::env(FP_PDN_CORE_RING_VSPACING) core_offset $::env(FP_PDN_CORE_RING_VOFFSET)}
                $::env(FP_PDN_UPPER_LAYER) {width $::env(FP_PDN_CORE_RING_HWIDTH) spacing $::env(FP_PDN_CORE_RING_HSPACING) core_offset $::env(FP_PDN_CORE_RING_HOFFSET)}
            }
    }
}

# Adds the core ring if enabled.
if { [info exists ::env(FP_PDN_ENABLE_RAILS)] } {
    if { $::env(FP_PDN_ENABLE_RAILS) == 1 } {
		dict append stdcell rails {
			$::env(FP_PDN_RAILS_LAYER) {width $::env(FP_PDN_RAIL_WIDTH) pitch $::env(PLACE_SITE_HEIGHT) offset $::env(FP_PDN_RAIL_OFFSET)}
		}
		dict update stdcell connect current_connect {
			append current_connect { {$::env(FP_PDN_RAILS_LAYER) $::env(FP_PDN_LOWER_LAYER)}}
		}
    } else {
		dict append stdcell rails {}
	}
}

pdngen::specify_grid stdcell [subst $stdcell]

# A general macro that follows the premise of the set heirarchy. You may want to modify this or add other macro configs
# TODO: generate automatically per instance:
set macro {
    orient {R0 R180 MX MY R90 R270 MXR90 MYR90}
    power_pins $::env(VDD_NET)
    ground_pins $::env(GND_NET)
    blockages "li1 met1 met2 met3 met4"
    straps {
    }
    connect {{$::env(FP_PDN_LOWER_LAYER)_PIN_ver $::env(FP_PDN_UPPER_LAYER)}}
}

pdngen::specify_grid macro [subst $macro]

set ::halo [expr min($::env(FP_HORIZONTAL_HALO), $::env(FP_VERTICAL_HALO))]

# POWER or GROUND #Std. cell rails starting with power or ground rails at the bottom of the core area
set ::rails_start_with "POWER" ;

# POWER or GROUND #Upper metal stripes starting with power or ground rails at the left/bottom of the core area
set ::stripes_start_with "POWER" ;
