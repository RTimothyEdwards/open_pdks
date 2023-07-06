###
###     Source file gf013.tcl
###     Process this file with the preprocessor script
###
#-----------------------------------------------------
# Magic/TCL design kit for GF TECHNAME
#-----------------------------------------------------
# Tim Edwards
# Revision 0	4/25/2022
#-----------------------------------------------------

if {[catch {set TECHPATH $env(PDK_ROOT)}]} {
    set TECHPATH STAGING_PATH
}
if [catch {set PDKPATH}] {set PDKPATH ${TECHPATH}/TECHNAME}
set PDKNAME TECHNAME
# "gf180mcu" is the namespace used for all devices
set PDKNAMESPACE gf180mcu
puts stdout "Loading TECHNAME Device Generator Menu ..."

# Initialize toolkit menus to the wrapper window

global Opts
namespace eval gf180mcu {}

# Set the window callback
if [catch {set Opts(callback)}] {set Opts(callback) ""}
set Opts(callback) [subst {gf180mcu::addtechmenu \$framename; $Opts(callback)}]

# if {![info exists Opts(cmdentry)]} {set Opts(cmdentry) 1}

# Set options specific to this PDK
set Opts(hidelocked) 1
set Opts(hidespecial) 0

# Wrap the closewrapper procedure so that closing the last
# window is equivalent to quitting.
if {[info commands closewrapper] == "closewrapper"} {
   rename closewrapper closewrapperonly
   proc closewrapper { framename } {
      if {[llength [windownames all]] <= 1} {
         magic::quit
      } else {
         closewrapperonly $framename
      }
   }
}

# Remove maze router layers from the toolbar by locking them
tech lock fence,magnet,rotate

namespace eval gf180mcu {
    namespace path {::tcl::mathop ::tcl::mathfunc}

    set ruleset [dict create]

    # Process DRC rules (magic style)

    dict set ruleset poly_surround    0.065     ;# Poly surrounds contact
    dict set ruleset diff_surround    0.065     ;# Diffusion surrounds contact
    dict set ruleset gate_to_diffcont 0.26      ;# Gate to diffusion contact center
    dict set ruleset gate_to_polycont 0.28      ;# Gate to poly contact center
    dict set ruleset gate_extension   0.22      ;# Poly extension beyond gate
    dict set ruleset diff_extension   0.23      ;# Diffusion extension beyond gate
    dict set ruleset contact_size     0.23      ;# Minimum contact size
    dict set ruleset via_size         0.26      ;# Minimum via size
    dict set ruleset metal_surround   0.055     ;# Metal1 overlaps contact
    dict set ruleset sub_surround     0.12      ;# Sub/well surrounds diffusion
    dict set ruleset diff_spacing     0.33      ;# Diffusion spacing rule
    dict set ruleset poly_spacing     0.24      ;# Poly spacing rule
    dict set ruleset diffres_spacing  0.40      ;# Diffusion resistor spacing rule
    dict set ruleset polyres_spacing  0.40      ;# Poly resistor spacing rule
    dict set ruleset diff_poly_space  0.10      ;# Diffusion to poly spacing rule
    dict set ruleset diff_gate_space  0.10      ;# Diffusion to gate poly spacing rule
    dict set ruleset metal_spacing    0.23      ;# Metal1 spacing rule
    dict set ruleset mmetal_spacing   0.23      ;# Metal spacing rule (above metal1)
    dict set ruleset sblk_to_cont     0.335     ;# resistor to contact center
    dict set ruleset sblk_diff_space  0.44      ;# resistor to guard ring
}

#-----------------------------------------------------
# magic::addtechmenu
#-----------------------------------------------------

proc gf180mcu::addtechmenu {framename} {
   global Winopts Opts
   
   # Check for difference between magic 8.1.125 and earlier, and 8.1.126 and later
   if {[catch {${framename}.titlebar cget -height}]} {
      set layoutframe ${framename}.pane.top
   } else {
      set layoutframe ${framename}
   }

   # List of devices is long.  Divide into two sections for active and passive deivces
   magic::add_toolkit_menu $layoutframe "Devices 1" pdk1

   magic::add_toolkit_command $layoutframe "nmos - nMOSFET" "magic::gencell gf180mcu::nmos_3p3" pdk1
   magic::add_toolkit_command $layoutframe "pmos - pMOSFET" "magic::gencell gf180mcu::pmos_3p3" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1
   magic::add_toolkit_command $layoutframe "np_3p3 - n-diode" "magic::gencell gf180mcu::np_3p3" pdk1
   magic::add_toolkit_command $layoutframe "pn_3p3 - p-diode" "magic::gencell gf180mcu::pn_3p3" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1
   magic::add_toolkit_command $layoutframe "vnpn_5x5     (3.3V) - 5.0um^2 " "magic::gencell gf180mcu::vnpn_2x2" pdk1
   magic::add_toolkit_command $layoutframe "vnpn_5x0p42  (3.3V) - 5.0um x 0.42um " "magic::gencell gf180mcu::vnpn_5x0p42" pdk1
   magic::add_toolkit_command $layoutframe "vnpn_10x10   (3.3V) - 10.0um^2 " "magic::gencell gf180mcu::vnpn_5x5" pdk1
   magic::add_toolkit_command $layoutframe "vnpn_10x0p42 (3.3V) - 10.0um x 0.42um " "magic::gencell gf180mcu::vnpn_10x0p42" pdk1
   magic::add_toolkit_command $layoutframe "vpnp_5x5     (3.3V) - 5.0um^2 " "magic::gencell gf180mcu::vpnp_5x5" pdk1
   magic::add_toolkit_command $layoutframe "vpnp_5x0p42  (3.3V) - 5.0um^2 x 0.42um " "magic::gencell gf180mcu::vpnp_5x0p42" pdk1
   magic::add_toolkit_command $layoutframe "vpnp_10x10   (3.3V) - 10.0um^2 " "magic::gencell gf180mcu::vpnp_10x10" pdk1
   magic::add_toolkit_command $layoutframe "vpnp_10x0p42 (3.3V) - 10.0um^2 x 0.42um " "magic::gencell gf180mcu::vpnp_10x0p42" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1
   magic::add_toolkit_command $layoutframe "mos capacitor" "magic::gencell gf180mcu::nmoscap_3p3" pdk1

   magic::add_toolkit_menu $layoutframe "Devices 2" pdk2

   magic::add_toolkit_command $layoutframe "ppolyf_s        - 7 Ohm/sq " "magic::gencell gf180mcu::ppolyf_s" pdk2 
   magic::add_toolkit_command $layoutframe "npolyf_s        - 7 Ohm/sq " "magic::gencell gf180mcu::ppolyf_s" pdk2 
   magic::add_toolkit_command $layoutframe "nplus_u   (3.3V) -  85 Ohm/sq " "magic::gencell gf180mcu::nplus_u" pdk2
   magic::add_toolkit_command $layoutframe "pplus_u   (3.3V) - 128 Ohm/sq " "magic::gencell gf180mcu::pplus_u" pdk2
   magic::add_toolkit_command $layoutframe "nplus_u  (6.0V) -  85 Ohm/sq " "magic::gencell gf180mcu::nplus_u_6p0" pdk2
   magic::add_toolkit_command $layoutframe "pplus_u  (6.0V) - 128 Ohm/sq " "magic::gencell gf180mcu::pplus_u_6p0" pdk2

   magic::add_toolkit_command $layoutframe "npolyf_u -  300 Ohm/sq " "magic::gencell gf180mcu::npolyf_u" pdk2
   magic::add_toolkit_command $layoutframe "ppolyf_u - 315 Ohm/sq " "magic::gencell gf180mcu::ppolyf_u" pdk2
#ifdef HRPOLY1K
   magic::add_toolkit_command $layoutframe "ppolyf_u_1k - 1.0k Ohm/sq " "magic::gencell gf180mcu::ppolyf_u_1k" pdk2
#endif (HRPOLY1K)
   magic::add_toolkit_command $layoutframe "nwell  (3.3V) -1680 Ohm/sq " "magic::gencell gf180mcu::nwell_3p3" pdk2
   magic::add_toolkit_separator	$layoutframe pdk2

   magic::add_toolkit_command $layoutframe "rm1 - 90  mOhm/sq " "magic::gencell gf180mcu::rm1" pdk2
   magic::add_toolkit_command $layoutframe "rm2 - 90  mOhm/sq " "magic::gencell gf180mcu::rm2" pdk2

#ifdef METALS3
#ifdef THICKMET3P0
   magic::add_toolkit_command $layoutframe "rm3 - 9.5  mOhm/sq " "magic::gencell gf180mcu::rm3" pdk2
#elseif (THICKMET1P1 || THICKMET0P9)
   magic::add_toolkit_command $layoutframe "rm3 - 40  mOhm/sq " "magic::gencell gf180mcu::rm3" pdk2
#else (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
   magic::add_toolkit_command $layoutframe "rm3 - 60  mOhm/sq " "magic::gencell gf180mcu::rm3" pdk2
#endif (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
#endif (METALS3)
#ifdef METALS4 || METALS5 || METALS6
   magic::add_toolkit_command $layoutframe "rm3 - 90  mOhm/sq " "magic::gencell gf180mcu::rm3" pdk2
#endif (METALS4 || METALS5 || METALS6)

#ifdef METALS4
#ifdef THICKMET3P0
   magic::add_toolkit_command $layoutframe "rm4 - 9.5  mOhm/sq " "magic::gencell gf180mcu::rm4" pdk2
#elseif (THICKMET1P1 || THICKMET0P9)
   magic::add_toolkit_command $layoutframe "rm4 - 40  mOhm/sq " "magic::gencell gf180mcu::rm4" pdk2
#else (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
   magic::add_toolkit_command $layoutframe "rm4 - 60  mOhm/sq " "magic::gencell gf180mcu::rm4" pdk2
#endif (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
#endif (METALS4)
#ifdef METALS5 || METALS6
   magic::add_toolkit_command $layoutframe "rm4 - 90  mOhm/sq " "magic::gencell gf180mcu::rm4" pdk2
#endif (METALS5 || METALS6)

#ifdef METALS5
#ifdef THICKMET3P0
   magic::add_toolkit_command $layoutframe "rm5 - 9.5  mOhm/sq " "magic::gencell gf180mcu::rm5" pdk2
#elseif (THICKMET1P1 || THICKMET0P9)
   magic::add_toolkit_command $layoutframe "rm5 - 40  mOhm/sq " "magic::gencell gf180mcu::rm5" pdk2
#else (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
   magic::add_toolkit_command $layoutframe "rm5 - 60  mOhm/sq " "magic::gencell gf180mcu::rm5" pdk2
#endif (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
#endif (METALS3)
#ifdef METALS6
   magic::add_toolkit_command $layoutframe "rm5 - 90  mOhm/sq " "magic::gencell gf180mcu::rm5" pdk2
#endif (METALS5)
#ifdef METALS6
#ifdef THICKMET3P0
   magic::add_toolkit_command $layoutframe "rmtp - 9.5  mOhm/sq " "magic::gencell gf180mcu::rmtp" pdk2
#elseif (THICKMET1P1 || THICKMET0P9)
   magic::add_toolkit_command $layoutframe "rmtp - 40  mOhm/sq " "magic::gencell gf180mcu::rmtp" pdk2
#else (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
   magic::add_toolkit_command $layoutframe "rmtp - 60  mOhm/sq " "magic::gencell gf180mcu::rmtp" pdk2
#endif (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
#endif (METALS6)

   magic::add_toolkit_separator	$layoutframe pdk2

#ifdef MIM
   magic::add_toolkit_command $layoutframe "mim_2p0fF - MiM cap " "magic::gencell gf180mcu::mim_2p0fF" pdk2
#endif (MIM)
   magic::add_toolkit_separator	$layoutframe pdk2

   magic::add_toolkit_command $layoutframe "substrate contact (3.3V) " "gf180mcu::subcon_3p3_draw" pdk2
   magic::add_toolkit_command $layoutframe "substrate contact (6.0V) " "gf180mcu::subcon_6p0_draw" pdk2
   magic::add_toolkit_command $layoutframe "via1              " "gf180mcu::via1_draw" pdk2
#ifdef METALS3 || METALS4 || METALS5 || METALS6
   magic::add_toolkit_command $layoutframe "via2              " "gf180mcu::via2_draw" pdk2
#endif (METALS3 || METALS4 || METALS5 || METALS6)
#ifdef METALS4 || METALS5 || METALS6
   magic::add_toolkit_command $layoutframe "via3              " "gf180mcu::via3_draw" pdk2
#endif (METALS4 || METALS5 || METALS6)
#ifdef METALS5 || METALS6
   magic::add_toolkit_command $layoutframe "via4              " "gf180mcu::via4_draw" pdk2
#endif (METALS5 || METALS6)
#ifdef METALS6
   magic::add_toolkit_command $layoutframe "viatp             " "gf180mcu::viatp_draw" pdk2
#endif (METALS6)

   ${layoutframe}.titlebar.mbuttons.drc.toolmenu add command -label "DRC Routing" -command {drc style drc(routing)}

   # Add SPICE import function to File menu
   ${layoutframe}.titlebar.mbuttons.file.toolmenu insert 4 command -label "Import SPICE" -command {gf180mcu::importspice}
   ${layoutframe}.titlebar.mbuttons.file.toolmenu insert 4 separator

   # Add command entry window by default if enabled
   if {[info exists Opts(cmdentry)]} {
      set Winopts(${framename},cmdentry) $Opts(cmdentry)
   } else {
      set Winopts(${framename},cmdentry) 0
   }
   if {$Winopts(${framename},cmdentry) == 1} {
      addcommandentry $framename
   }
}

#----------------------------------------------------------------
# Menu callback function to read a SPICE netlist and generate an
# initial layout using the SKYWATER sky130A gencells.
#----------------------------------------------------------------

proc gf180mcu::importspice {} {
   global CAD_ROOT

   set Layoutfilename [ tk_getOpenFile -filetypes \
	    {{SPICE {.spice .spc .spi .ckt .cir .sp \
	    {.spice .spc .spi .ckt .cir .sp}}} {"All files" {*}}}]
   if {$Layoutfilename != ""} {
      magic::netlist_to_layout $Layoutfilename gf180mcu
   }
}

#----------------------------------------------------------------

proc gf180mcu::via1_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.28} {
      puts stderr "Via1 width must be at least 0.28um"
      return
   }
   if {$h < 0.28} {
      puts stderr "Via1 height must be at least 0.28um"
      return
   }
   paint via1
   box grow n 0.05um
   box grow s 0.05um
   paint m2
   box grow n -0.05um
   box grow s -0.05um
   box grow e 0.05um
   box grow w 0.05um
   paint m1
   box grow e -0.05um
   box grow w -0.05um
}

#ifdef METALS3 || METALS4 || METALS5 || METALS6
proc gf180mcu::via2_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.28} {
      puts stderr "Via2 width must be at least 0.28um"
      return
   }
   if {$h < 0.28} {
      puts stderr "Via2 height must be at least 0.28um"
      return
   }
   paint via2
   box grow n 0.05um
   box grow s 0.05um
   paint m2
   box grow n -0.05um
   box grow s -0.05um
   box grow e 0.05um
   box grow w 0.05um
   paint m3
   box grow e -0.05um
   box grow w -0.05um
}
#endif (METALS3 || METALS4 || METALS5 || METALS6)

#ifdef METALS4 || METALS5 || METALS6
proc gf180mcu::via3_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.28} {
      puts stderr "Via3 width must be at least 0.28um"
      return
   }
   if {$h < 0.28} {
      puts stderr "Via3 height must be at least 0.28um"
      return
   }
   paint via3
   box grow n 0.05um
   box grow s 0.05um
   paint m4
   box grow n -0.05um
   box grow s -0.05um
   box grow e 0.05um
   box grow w 0.05um
   paint m3
   box grow e -0.05um
   box grow w -0.05um
}
#endif (METALS4 || METALS5 || METALS6)

#ifdef METALS5 || METALS6
proc gf180mcu::via4_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.28} {
      puts stderr "Via4 width must be at least 0.28um"
      return
   }
   if {$h < 0.28} {
      puts stderr "Via4 height must be at least 0.28um"
      return
   }
   paint via4
   box grow n 0.05um
   box grow s 0.05um
   paint m5
   box grow n -0.05um
   box grow s -0.05um
   box grow e 0.05um
   box grow w 0.05um
   paint m4
   box grow e -0.05um
   box grow w -0.05um
}
#endif (METALS5 || METALS6)

#ifdef METALS6
proc gf180mcu::viatp_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.28} {
      puts stderr "ViaTP width must be at least 0.28um"
      return
   }
   if {$h < 0.28} {
      puts stderr "ViaTP height must be at least 0.28um"
      return
   }
   paint viatp
   box grow c 0.08um
   paint mtp
   box grow c -0.08um
   box grow e 0.05um
   box grow w 0.05um
   paint m5
   box grow e -0.05um
   box grow w -0.05um
}
#endif (METALS6)

proc gf180mcu::subcon_3p3_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.23} {
      puts stderr "Substrate tap width must be at least 0.23um"
      return
   }
   if {$h < 0.23} {
      puts stderr "Substrate tap height must be at least 0.23um"
      return
   }
   paint subdiffc
   box grow c 0.1um
   paint subdiff
   box grow c 0.1um
   paint pwell
   box grow c -0.2um
}

#----------------------------------------------------------------

proc gf180mcu::subconmos_6p0_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.23} {
      puts stderr "Substrate tap width must be at least 0.23um"
      return
   }
   if {$h < 0.23} {
      puts stderr "Substrate tap height must be at least 0.23um"
      return
   }
   paint mvsubdiffc
   box grow c 0.1um
   paint mvsubdiff
   box grow c 0.1um
   paint pwell
   box grow c -0.2um
}

#----------------------------------------------------------------

proc gf180mcu::res_recalc {field parameters} {
    set snake 0
    set sterm 0.0
    set caplen 0
    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }
    set val [magic::spice2float $val]
    set l [magic::spice2float $l]
    set w [magic::spice2float $w]

    if {$snake == 0} {
	# Straight resistor calculation
	switch  $field {
	    val { set l [expr ($val * ($w - $dw) - (2 * $term)) / $rho]
		  set w [expr ((2 * $term + $l * $rho) / $val) + $dw]
		}
	    w   { set val [expr (2 * $term + $l * $rho) / ($w - $dw)]
		  set l [expr ($val * ($w - $dw) - (2 * $term)) / $rho]
		}
	    l   { set val [expr (2 * $term + $l * $rho) / ($w - $dw)]
		  set w [expr ((2 * $term + $l * $rho) / $val) + $dw]
		}
	}
    } else {
        set term [expr $term + $sterm]
	# Snake resistor calculation
	switch  $field {
	    val { set l [expr (($val - $rho * ($nx - 1)) * ($w - $dw) \
			- (2 * $term) - ($rho * $caplen * ($nx - 1))) \
			/ ($rho * $nx)]

		  set w [expr ((2 * $term + $l * $rho * $nx \
			+ $caplen * $rho * ($nx - 1)) \
			/ ($val - $rho * ($nx - 1))) + $dw]
		}
	    w   { set val [expr $rho * ($nx - 1) + ((2 * $term) \
			+ ($rho * $l * $nx) + ($rho * $caplen * ($nx - 1))) \
			/ ($w - $dw)]

		  set l [expr (($val - $rho * ($nx - 1)) * ($w - $dw) \
			- (2 * $term) - ($rho * $caplen * ($nx - 1))) \
			/ ($rho * $nx)]
		}
	    l   { set val [expr $rho * ($nx - 1) + ((2 * $term) \
			+ ($rho * $l * $nx) + ($rho * $caplen * ($nx - 1))) \
			/ ($w - $dw)]

		  set w [expr ((2 * $term + $l * $rho * $nx \
			+ $caplen * $rho * ($nx - 1)) \
			/ ($val - $rho * ($nx - 1))) + $dw]
		}
	}
    }

    set val [magic::3digitpastdecimal $val]
    set w [magic::3digitpastdecimal $w]
    set l [magic::3digitpastdecimal $l]

    dict set parameters val $val
    dict set parameters w $w
    dict set parameters l $l

    return $parameters
}

#----------------------------------------------------------------
# Drawn diode routines
#----------------------------------------------------------------

proc gf180mcu::diode_recalc {field parameters} {
    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }
    switch  $field {
	area { puts stdout "area changed" }
	peri { puts stdout "perimeter changed" }
	w   { puts stdout "width changed" }
	l   { puts stdout "length changed" }
    }
    dict set parameters area $area
    dict set parameters peri $peri
    dict set parameters w $w
    dict set parameters l $l
}

#----------------------------------------------------------------
# diode: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc gf180mcu::diode_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    l -
	    w -
	    peri {
		# Length, width, and perimeter are converted to units of microns
		set value [magic::spice2float $value]
		set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $key] $value
	    }
	    area {
		# area also converted to units of microns
		set value [magic::spice2float $value]
		set value [expr $value * 1e12]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $key] $value
	    }
	    m {
                # Convert m to ny
		dict set pdkparams ny $value
	    }
	}
    }
    return $pdkparams
}

#----------------------------------------------------------------
# diode: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc gf180mcu::diode_dialog {device parameters} {
    # Editable fields:      w, l, area, perim, nx, ny

    magic::add_entry area "Area (um^2)" $parameters
    magic::add_entry peri "Perimeter (um)" $parameters
    gf180mcu::compute_aptot $parameters
    magic::add_message atot "Total area (um^2)" $parameters
    magic::add_message ptot "Total perimeter (um)" $parameters
    magic::add_entry l "Length (um)" $parameters
    magic::add_entry w "Width (um)" $parameters
    magic::add_entry nx "X Repeat" $parameters
    magic::add_entry ny "Y Repeat" $parameters

    if {[dict exists $parameters compatible]} {
       set sellist [dict get $parameters compatible]
       # Reserved word "gencell" has special behavior to change the
       # underlying device type 
       dict set parameters gencell $device
       magic::add_selectlist gencell "Device type" $sellist $parameters
    }

    magic::add_checkbox doverlap "Overlap at end contact" $parameters

    if {[dict exists $parameters elc]} {
        magic::add_checkbox elc "Add left end contact" $parameters
    }
    if {[dict exists $parameters erc]} {
        magic::add_checkbox erc "Add right end contact" $parameters
    }
    if {[dict exists $parameters etc]} {
        magic::add_checkbox etc "Add top end contact" $parameters
    }
    if {[dict exists $parameters ebc]} {
        magic::add_checkbox ebc "Add bottom end contact" $parameters
    }

    if {[dict exists $parameters guard]} {
        magic::add_checkbox full_metal "Full metal guard ring" $parameters
    }
    if {[dict exists $parameters glc]} {
        magic::add_checkbox glc "Add left guard ring contact" $parameters
    }
    if {[dict exists $parameters grc]} {
        magic::add_checkbox grc "Add right guard ring contact" $parameters
    }
    if {[dict exists $parameters gtc]} {
        magic::add_checkbox gtc "Add top guard ring contact" $parameters
    }
    if {[dict exists $parameters gbc]} {
        magic::add_checkbox gbc "Add bottom guard ring contact" $parameters
    }

    magic::add_dependency gf180mcu::diode_recalc $device gf180mcu l w area peri

    # magic::add_checkbox dummy "Add dummy" $parameters
}

#----------------------------------------------------------------
# Diode total area and perimeter computation
#----------------------------------------------------------------

proc gf180mcu::compute_aptot {parameters} {
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }
    set area [magic::spice2float $area]
    set area [magic::3digitpastdecimal $area]
    set peri [magic::spice2float $peri]
    set peri [magic::3digitpastdecimal $peri]

    # Compute total area
    catch {set magic::atot_val [expr ($area * $nx * $ny)]}
    # Compute total perimeter
    catch {set magic::ptot_val [expr ($peri * $nx * $ny)]}
}

#----------------------------------------------------------------
# diode: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc gf180mcu::diode_check {parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set l [magic::spice2float $l]
    set l [magic::3digitpastdecimal $l] 
    set w [magic::spice2float $w]
    set w [magic::3digitpastdecimal $w] 

    set area [magic::spice2float $area]
    set area [magic::3digitpastdecimal $area] 
    set peri [magic::spice2float $peri]
    set peri [magic::3digitpastdecimal $peri] 

    if {$l == 0} {
        # Calculate L from W and area
	set l [expr ($area / $w)]
	dict set parameters l [magic::float2spice $l]
    } elseif {$w == 0} {
        # Calculate W from L and area
	set w [expr ($area / $l)]
	dict set parameters w [magic::float2spice $w]
    }
    if {$w < $wmin} {
	puts stderr "Diode width must be >= $wmin"
	dict set parameters w $wmin
    } 
    if {$l < $lmin} {
	puts stderr "Diode length must be >= $lmin"
	dict set parameters l $lmin
    } 
    # Calculate area and perimeter from L and W
    set area [expr ($l * $w)]
    dict set parameters area [magic::float2spice $area]
    set peri [expr (2 * ($l + $w))]
    dict set parameters peri [magic::float2spice $peri]
    gf180mcu::compute_aptot $parameters

    return $parameters
}

#----------------------------------------------------------------

proc gf180mcu::np_3p3_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 full_metal 1 \
	compatible {np_3p3 np_6p0 np_6p0_nat}}
}

proc gf180mcu::pn_3p3_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 \
	glc 1 grc 1 gtc 0 gbc 0 doverlap 0 full_metal 1 \
	compatible {pn_3p3 pn_6p0}}
}

proc gf180mcu::np_6p0_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 \
	full_metal 1 \
	compatible {np_3p3 np_6p0 np_6p0_nat}}
}

proc gf180mcu::np_6p0_nat_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 \
	full_metal 1 \
	compatible {np_3p3 np_6p0 np_6p0_nat}}
}

proc gf180mcu::pn_6p0_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 \
	glc 1 grc 1 gtc 0 gbc 0 doverlap 0 \
	compatible {pn_3p3 pn_6p0}}
}

#----------------------------------------------------------------

proc gf180mcu::np_3p3_convert {parameters} {
    return [gf180mcu::diode_convert $parameters]
}

proc gf180mcu::pn_3p3_convert {parameters} {
    return [gf180mcu::diode_convert $parameters]
}

proc gf180mcu::np_6p0_convert {parameters} {
    return [gf180mcu::diode_convert $parameters]
}

proc gf180mcu::np_6p0_nat_convert {parameters} {
    return [gf180mcu::diode_convert $parameters]
}

proc gf180mcu::pn_6p0_convert {parameters} {
    return [gf180mcu::diode_convert $parameters]
}

#----------------------------------------------------------------

proc gf180mcu::np_3p3_dialog {parameters} {
    gf180mcu::diode_dialog np_3p3 $parameters
}

proc gf180mcu::pn_3p3_dialog {parameters} {
    gf180mcu::diode_dialog pn_3p3 $parameters
}

proc gf180mcu::np_6p0_dialog {parameters} {
    gf180mcu::diode_dialog np_6p0 $parameters
}

proc gf180mcu::np_6p0_nat_dialog {parameters} {
    gf180mcu::diode_dialog np_6p0_nat $parameters
}

proc gf180mcu::pn_6p0_dialog {parameters} {
    gf180mcu::diode_dialog pn_6p0 $parameters
}

#----------------------------------------------------------------

proc gf180mcu::np_3p3_check {parameters} {
    gf180mcu::diode_check $parameters
}

proc gf180mcu::pn_3p3_check {parameters} {
    gf180mcu::diode_check $parameters
}

proc gf180mcu::np_6p0_check {parameters} {
    gf180mcu::diode_check $parameters
}

proc gf180mcu::np_6p0_nat_check {parameters} {
    gf180mcu::diode_check $parameters
}

proc gf180mcu::pn_6p0_check {parameters} {
    gf180mcu::diode_check $parameters
}

#----------------------------------------------------------------
# Diode: Draw a single device
#----------------------------------------------------------------

proc gf180mcu::diode_device {parameters} {
    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set dev_surround 0
    set dev_sub_type ""

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    if {![dict exists $parameters end_contact_size]} {
	set end_contact_size $contact_size
    }

    # Draw the device
    pushbox
    box size 0 0

    set hw [/ $w 2.0]
    set hl [/ $l 2.0]

    # Calculate ring size (measured to contact center)
    set gx [+ $w [* 2.0 [+ $dev_spacing $dev_surround]] $end_contact_size]
    set gy [+ $l [* 2.0 [+ $dev_spacing $dev_surround]] $end_contact_size]

    # Draw the ring first, because diode may occupy well/substrate plane
    set guardparams $parameters
    dict set guardparams plus_diff_type $end_type
    dict set guardparams plus_contact_type $end_contact_type
    dict set guardparams contact_size $end_contact_size
    dict set guardparams diff_surround $end_surround
    dict set guardparams sub_type $end_sub_type
    dict set guardparams glc $elc
    dict set guardparams grc $erc
    dict set guardparams gtc $etc
    dict set guardparams gbc $ebc
    set cext [gf180mcu::guard_ring $gx $gy $guardparams]

    pushbox
    box grow n ${hl}um
    box grow s ${hl}um
    box grow e ${hw}um
    box grow w ${hw}um
    paint ${dev_type}
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]

    if {$dev_sub_type != ""} {
	box grow n ${sub_surround}um
	box grow s ${sub_surround}um
	box grow e ${sub_surround}um
	box grow w ${sub_surround}um
	paint ${dev_sub_type}
    }
    popbox

    if {${w} < ${l}} {
	set orient vert
    } else {
	set orient horz
    }

    # Reduce width by surround amount
    set w [- $w [* ${dev_surround} 2.0]]
    set l [- $l [* ${dev_surround} 2.0]]

    set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact ${w} ${l} \
		${dev_surround} ${metal_surround} ${contact_size} \
		${dev_type} ${dev_contact_type} m1 ${orient}]]

    popbox
    return $cext
}

#----------------------------------------------------------------
# Diode: Draw the tiled device
#----------------------------------------------------------------

proc gf180mcu::diode_draw {parameters} {
    tech unlock *

    # Set defaults if they are not in parameters
    set doverlap 0	;# overlap diodes at contacts
    set guard 0		;# draw a guard ring

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set w [magic::spice2float $w]
    set l [magic::spice2float $l]

    pushbox
    box values 0 0 0 0

    # Determine the base device dimensions by drawing one device
    # while all layers are locked (nothing drawn).  This allows the
    # base drawing routine to do complicated geometry without having
    # to duplicate it here with calculations.

    tech lock *
    set bbox [gf180mcu::diode_device $parameters]
    # puts stdout "Diagnostic: Device bounding box e $bbox (um)"
    tech unlock *

    set fw [- [lindex $bbox 2] [lindex $bbox 0]]
    set fh [- [lindex $bbox 3] [lindex $bbox 1]]
    set lw [+ [lindex $bbox 2] [lindex $bbox 0]]
    set lh [+ [lindex $bbox 3] [lindex $bbox 1]]

    # Determine tile width and height (depends on overlap)

    if {$doverlap == 0} {
	set dx [+ $fw $end_spacing]
        set dy [+ $fh $end_spacing]
    } else {
        # overlap contact
        set dx [- $fw [+ [* 2.0 $sub_surround] [* 2.0 $end_surround] $contact_size]]
        set dy [- $fh [+ [* 2.0 $sub_surround] [* 2.0 $end_surround] $contact_size]]
    }

    # Determine core width and height
    set corex [+ [* [- $nx 1] $dx] $fw]
    set corey [+ [* [- $ny 1] $dy] $fh]
    set corellx [/ [+ [- $corex $fw] $lw] 2.0]
    set corelly [/ [+ [- $corey $fh] $lh] 2.0]

    if {$guard != 0} {
	# Calculate guard ring size (measured to contact center)
	set gx [+ $corex [* 2.0 [+ $diff_spacing $diff_surround]] $contact_size]
	set gy [+ $corey [* 2.0 [+ $diff_spacing $diff_surround]] $contact_size]

	# Draw the guard ring first, because diode may occupy well/substrate plane
	gf180mcu::guard_ring $gx $gy $parameters
    }

    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    if {($nx > 1) || ($ny > 1)} {
	pushbox
	set hfw [/ $fw 2.0]
	set hfh [/ $fh 2.0]
	box move w ${hfw}um
	box move s ${hfh}um
	box size ${corex}um ${corey}um
	paint $end_sub_type
	popbox
    }
    for {set xp 0} {$xp < $nx} {incr xp} {
	pushbox
	for {set yp 0} {$yp < $ny} {incr yp} {
	    gf180mcu::diode_device $parameters
            box move n ${dy}um
        }
	popbox
        box move e ${dx}um
    }
    popbox
    popbox

    tech revert
}

#----------------------------------------------------------------

proc gf180mcu::np_3p3_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		ndiode \
	    dev_contact_type	ndic \
	    end_type		psd \
	    end_contact_type	psc \
	    end_contact_size	0.16 \
	    end_sub_type	pwell \
	    dev_spacing		0.25 \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::diode_draw $drawdict]
} 

#----------------------------------------------------------------

proc gf180mcu::pn_3p3_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		1 \
	    dev_type		pdiode \
	    dev_contact_type	pdic \
	    end_type		nsd \
	    end_contact_type	nsc \
	    end_contact_size	0.16 \
	    end_sub_type	nwell \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		pwell \
	    dev_spacing		0.25 \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::diode_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::np_6p0_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    diff_poly_space	0.30 \
	    diff_gate_space	0.30 \
	    diff_spacing	0.36 \
	    dev_type		mvndiode \
	    dev_contact_type	mvndic \
	    end_type		mvpsd \
	    end_contact_type	mvpsc \
	    end_sub_type	pwell \
	    dev_spacing		0.25 \
	    dev_surround	${diff_surround} \
	    end_spacing		0.36 \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::diode_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::np_6p0_nat_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		mvnndiode \
	    dev_contact_type	mvnndic \
	    end_type		mvpsd \
	    end_contact_type	mvpsc \
	    end_sub_type	pwell \
	    dev_spacing		0.64 \
	    dev_surround	${diff_surround} \
	    end_spacing		0.36 \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::diode_draw $drawdict]
}

#----------------------------------------------------------------

#----------------------------------------------------------------

proc gf180mcu::pn_6p0_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    diff_poly_space	0.30 \
	    diff_gate_space	0.30 \
	    diff_spacing	0.36 \
	    guard		1 \
	    dev_type 		mvpdiode \
	    dev_contact_type	mvpdic \
	    end_type		mvnsd \
	    end_contact_type	mvnsc \
	    end_sub_type	nwell \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    sub_type		pwell \
	    dev_spacing		${diff_spacing} \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::diode_draw $drawdict]
}

#----------------------------------------------------------------
# Drawn capactitor routines
#----------------------------------------------------------------
# MiM minimum size set to 2.165 to prevent isolated via

#ifdef MIM
proc gf180mcu::mim_2p0fF_defaults {} {
    return {w 5.00 l 5.00 val 50.000 carea 25.00 cperi 20.00 \
		nx 1 ny 1 dummy 0 square 0 lmin 5.00 wmin 5.00 \
		lmax 100.0 wmax 100.0 dc 0 bconnect 1 tconnect 1}
}
#endif MIM

#----------------------------------------------------------------
# Recalculate capacitor values from GUI entries.
# Recomputes W/L and Value as long as 2 of them are present
# (To be completed)
#----------------------------------------------------------------

proc gf180mcu::cap_recalc {field parameters} {
    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }
    switch  $field {
	val { puts stdout "value changed" }
	w   { puts stdout "width changed" }
	l   { puts stdout "length changed" }
    }
    dict set parameters val $val
    dict set parameters w $w
    dict set parameters l $l
}

#----------------------------------------------------------------
# Capacitor defaults:
#----------------------------------------------------------------
#  w      Width of drawn cap
#  l      Length of drawn cap
#  nx     Number of devices in X
#  ny     Number of devices in Y
#  val    Default cap value
#  carea  Area
#  cperi  Perimeter
#  dummy  Add dummy cap
#  square Make square capacitor
#
#  (not user-editable)
#
#  wmin   Minimum allowed width
#  lmin   Minimum allowed length
#  dc     Area to remove to calculated area 
#----------------------------------------------------------------

#----------------------------------------------------------------
# capacitor: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc gf180mcu::cap_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	set canonkey $key
	switch -nocase $key {
	    c_length -
	    c_width -
	    l -
	    w {
		switch -nocase $key {
		    c_length {
			set canonkey l
		    }
		    c_width {
			set canonkey w
		    }
		}
		# Length and width are converted to units of microns
		set value [magic::spice2float $value]
		set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $canonkey] $value
	    }
	    m {
                # Convert m to ny
		dict set pdkparams ny $value
	    }
	}
    }
    return $pdkparams
}

#ifdef MIM
proc gf180mcu::mim_2p0fF_convert {parameters} {
    return [cap_convert $parameters]
}
#endif

#----------------------------------------------------------------
# capacitor: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc gf180mcu::cap_dialog {device parameters} {
    # Editable fields:      w, l, nx, ny, val
    # Checked fields:  	    square, dummy

    magic::add_entry val "Value (fF)" $parameters
    gf180mcu::compute_ctot $parameters
    magic::add_message ctot "Total capacitance (pF)" $parameters
    magic::add_entry l "Length (um)" $parameters
    magic::add_entry w "Width (um)" $parameters
    magic::add_entry nx "X Repeat" $parameters
    magic::add_entry ny "Y Repeat" $parameters

    if {[dict exists $parameters square]} {
	magic::add_checkbox square "Square capacitor" $parameters
    }
    if {[dict exists $parameters bconnect]} {
	magic::add_checkbox bconnect "Connect bottom plates in array" $parameters
    }
    if {[dict exists $parameters tconnect]} {
	magic::add_checkbox tconnect "Connect top plates in array" $parameters
    }

    magic::add_dependency gf180mcu::cap_recalc $device gf180mcu l w val

    # magic::add_checkbox dummy "Add dummy" $parameters
}

#ifdef MIM
proc gf180mcu::mim_2p0fF_dialog {parameters} {
    gf180mcu::cap_dialog mim_2p0fF $parameters
}
#endif

#----------------------------------------------------------------
# Capacitor total capacitance computation
#----------------------------------------------------------------

proc gf180mcu::compute_ctot {parameters} {
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }
    set val [magic::spice2float $val]
    set val [magic::3digitpastdecimal $val]

    # Compute total capacitance (and convert fF to pF)
    catch {set magic::ctot_val [expr (0.001 * $val * $nx * $ny)]}
}

#----------------------------------------------------------------
# Capacitor: Draw a single device
#----------------------------------------------------------------

proc gf180mcu::cap_device {parameters} {
    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set cap_surround 0
    set bot_surround 0
    set top_surround 0

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Draw the device
    pushbox
    box size 0 0

    pushbox
    set hw [/ $w 2.0]
    set hl [/ $l 2.0]
    box grow e ${hw}um
    box grow w ${hw}um
    box grow n ${hl}um
    box grow s ${hl}um
    paint ${cap_type}
    pushbox
    box grow n -${cap_surround}um
    box grow s -${cap_surround}um
    box grow e -${cap_surround}um
    box grow w -${cap_surround}um
    paint ${cap_contact_type}
    pushbox
    box grow n ${top_surround}um
    box grow s ${top_surround}um
    box grow e ${top_surround}um
    box grow w ${top_surround}um
    paint ${top_type}
    set cext [gf180mcu::getbox]
    popbox
    popbox
    pushbox
    box grow n ${bot_surround}um
    box grow s ${bot_surround}um
    box grow e ${bot_surround}um
    box grow w ${bot_surround}um

    paint ${bot_type}
    property FIXED_BBOX [box values]
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]

    # Extend bottom metal under contact to right
    box grow e ${end_spacing}um
    set chw [/ ${contact_size} 2.0]
    box grow e ${chw}um
    box grow e ${end_surround}um
    paint ${bot_type}

    popbox
    popbox

    # Draw contact to right
    pushbox
    box move e ${hw}um
    box move e ${bot_surround}um
    box move e ${end_spacing}um
    set cl [- [+ ${l} [* ${bot_surround} 2.0]] [* ${end_surround} 2.0]]
    set cl [- ${cl} ${metal_surround}]  ;# see below
    set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact 0 ${cl} \
		${end_surround} ${metal_surround} ${contact_size} \
		${bot_type} ${top_contact_type} ${top_type} vert]]
    popbox
    popbox

    return $cext

    # cl shrinks top and bottom to accomodate larger bottom metal
    # surround rule for contacts near a MiM cap.  This should be its
    # own variable, but metal_surround is sufficient.
}

#----------------------------------------------------------------
# Metal plate sandwich capacitor:  Draw a single device
#----------------------------------------------------------------

proc gf180mcu::sandwich_cap_device {parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    pushbox
    box size 0 0

    set hw [/ $w 2.0]
    set hl [/ $l 2.0]

    set cw [- [* $hw [/ 2.0 3]] [* $cont_surround 2.0]]
    set cl [- [* $hl [/ 2.0 3]] [* $cont_surround 2.0]]

    # plate capacitor defines layers p0, p1, etc.
    for {set i 0} {$i < 20} {incr i} {
        if {[catch {set layer [subst \$p${i}_type]}]} {break}  ;# no more layers defined
	pushbox
	box grow e ${hw}um
	box grow w ${hw}um
	box grow n ${hl}um
	box grow s ${hl}um
        if {![catch {set shrink [subst \$p${i}_shrink]}]} {
	    box grow e -${shrink}um
	    box grow w -${shrink}um
	    box grow n -${shrink}um
	    box grow s -${shrink}um
	    set cutout_spacing [+ [* ${shrink} 2.0] [/ $via_size 2.0] $cont_surround]
	} else {
	    set cutout_spacing 0
	}

	paint ${layer}

	if {$i == 1} {
	    # Note that cap_type geometry is coincident with p1_type.
	    # Typically, this will define a layer that outputs as both
	    # poly and a capacitor definition layer.
	    if {[dict exists $parameters cap_type]} {
		paint $cap_type
	    }
	}
	popbox

	# Even layers connect at corners, odd layers connect at sides.
	# Even layers cut out the sides, odd layers cut out the corners.
	# Layer zero has no side contacts or cutout.

	if {[% $i 2] == 0} {
	    set cornercmd  paint
	    set cornersize $cutout_spacing
	    set sidecmd    erase
	    set nssidelong   [+ $cutout_spacing [/ $hw 3.0]]
	    set ewsidelong   [+ $cutout_spacing [/ $hl 3.0]]
	    set sideshort    $cutout_spacing
	} else {
	    set cornercmd  erase
	    set cornersize $cutout_spacing
	    set sidecmd    paint
	    set nssidelong   [/ $hw 3.0]
	    set ewsidelong   [/ $hl 3.0]
	    set sideshort    $cutout_spacing
	}

	if {$i > 0} {
	    pushbox
	    box move e ${hw}um
	    box grow n ${ewsidelong}um
	    box grow s ${ewsidelong}um
	    box grow w ${sideshort}um
	    ${sidecmd} ${layer}
	    popbox
	    pushbox
	    box move n ${hl}um
	    box grow e ${nssidelong}um
	    box grow w ${nssidelong}um
	    box grow s ${sideshort}um
	    ${sidecmd} ${layer}
	    popbox
	    pushbox
	    box move w ${hw}um
	    box grow n ${ewsidelong}um
	    box grow s ${ewsidelong}um
	    box grow e ${sideshort}um
	    ${sidecmd} ${layer}
	    popbox
	    pushbox
	    box move s ${hl}um
	    box grow e ${nssidelong}um
	    box grow w ${nssidelong}um
	    box grow n ${sideshort}um
	    ${sidecmd} ${layer}
	    popbox

	    pushbox
	    box move n ${hl}um
	    box move e ${hw}um
	    box grow s ${cornersize}um
	    box grow w ${cornersize}um
	    ${cornercmd} ${layer}
	    popbox
	    pushbox
	    box move n ${hl}um
	    box move w ${hw}um
	    box grow s ${cornersize}um
	    box grow e ${cornersize}um
	    ${cornercmd} ${layer}
	    popbox
	    pushbox
	    box move s ${hl}um
	    box move e ${hw}um
	    box grow n ${cornersize}um
	    box grow w ${cornersize}um
	    ${cornercmd} ${layer}
	    popbox
	    pushbox
	    box move s ${hl}um
	    box move w ${hw}um
	    box grow n ${cornersize}um
	    box grow e ${cornersize}um
	    ${cornercmd} ${layer}
	    popbox
	}
    }

    # Draw contacts after all layers have been drawn, so that erasing
    # layers does not affect the contacts.

    for {set i 0} {$i < 20} {incr i} {
        if {![catch {set contact [subst \$p${i}_contact_type]}]} {
	    set layer [subst \$p${i}_type]
	    set j [+ $i 1]
	    set toplayer [subst \$p${j}_type]

	    # Draw corner contacts
	    pushbox
	    box move e ${hw}um
	    box move n ${hl}um
	    gf180mcu::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox
	    pushbox
	    box move w ${hw}um
	    box move n ${hl}um
	    gf180mcu::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox
	    pushbox
	    box move e ${hw}um
	    box move s ${hl}um
	    gf180mcu::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox
	    pushbox
	    box move w ${hw}um
	    box move s ${hl}um
	    gf180mcu::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox

	    # Draw side contacts (except on poly)
	    if {$i > 0} {
		pushbox
		box move w ${hw}um
		gf180mcu::draw_contact 0 ${cl} \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
		pushbox
		box move e ${hw}um
		gf180mcu::draw_contact 0 ${cl} \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
		pushbox
		box move n ${hl}um
		gf180mcu::draw_contact ${cw} 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
		pushbox
		box move s ${hl}um
		gf180mcu::draw_contact ${cw} 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
	    }
	} else {
	    break
	}
    }

    popbox
    # Bounding box is the same as the device length and width
    set cext [list -$hw -$hl $hw $hl]
    return $cext
}

#----------------------------------------------------------------
# Capacitor: Draw the tiled device
#----------------------------------------------------------------

proc gf180mcu::cap_draw {parameters} {
    tech unlock *

    # Set defaults if they are not in parameters
    set coverlap 0	;# overlap capacitors at contacts
    set guard 0		;# draw a guard ring
    set sandwich 0	;# this is not a plate sandwich capacitor
    set cap_spacing 0	;# abutted caps if spacing is zero
    set wide_cap_spacing 0  ;# additional spacing for wide metal rule
    set wide_cap_width 0
    set end_spacing 0
    set end_surround 0
    set bot_surround 0
    set top_metal_width 0
    set bconnect 0	;# connect bottom plates in array
    set tconnect 0	;# connect top plates in array
    set top_type ""

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set w [magic::spice2float $w]
    set l [magic::spice2float $l]

    pushbox
    box values 0 0 0 0

    # Determine the base device dimensions by drawing one device
    # while all layers are locked (nothing drawn).  This allows the
    # base drawing routine to do complicated geometry without having
    # to duplicate it here with calculations.

    tech lock *
    if {$sandwich == 1} {
	set bbox [gf180mcu::sandwich_cap_device $parameters]
    } else {
	set bbox [gf180mcu::cap_device $parameters]
    }
    # puts stdout "Diagnostic: Device bounding box e $bbox (um)"
    tech unlock *

    set fw [- [lindex $bbox 2] [lindex $bbox 0]]
    set fh [- [lindex $bbox 3] [lindex $bbox 1]]
    set lw [+ [lindex $bbox 2] [lindex $bbox 0]]
    set lh [+ [lindex $bbox 3] [lindex $bbox 1]]

    set dwide 0
    if {($fw >= $wide_cap_width) && ($fh >= $wide_cap_width)} {
	set dwide $wide_cap_spacing
    }

    # Determine tile width and height (depends on overlap)
    if {$coverlap == 0} {
        set dy [+ $fh $cap_spacing $dwide]
    } else {
        # overlap at end contact
        set dy [- $fh [+ $end_surround $end_surround $contact_size]]
    }
    # Contact is placed on right so spacing is determined by end_spacing.
    set dx [+ $fw $end_spacing $dwide]

    # Determine core width and height
    set corex [+ [* [- $nx 1] $dx] $fw]
    set corey [+ [* [- $ny 1] $dy] $fh]
    set corellx [/ [+ [- $corex $fw] $lw] 2.0]
    set corelly [/ [+ [- $corey $fh] $lh] 2.0]

    if {$guard != 0} {
	# Calculate guard ring size (measured to contact center)
	set gx [+ $corex [* 2.0 [+ $cap_diff_spacing $diff_surround]] $contact_size]
	set gy [+ $corey [* 2.0 [+ $end_spacing $diff_surround]] $contact_size]

	# Draw the guard ring first.
	gf180mcu::guard_ring $gx $gy $parameters
    }

    set top_metal_width [+ ${contact_size} ${end_surround} ${end_surround}]
    set hmw [/ $top_metal_width 2.0]
    set hdy [/ $dy 2.0]
    set cdx [+ [/ ${w} 2.0] ${bot_surround} ${end_spacing}]

    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    for {set xp 0} {$xp < $nx} {incr xp} {
	pushbox
	for {set yp 0} {$yp < $ny} {incr yp} {
	    if {$sandwich == 1} {
		gf180mcu::sandwich_cap_device $parameters
	    } else {
		gf180mcu::cap_device $parameters
	    }
	    if {$ny > 1} {
		pushbox
		box grow e ${hmw}um
		box grow w ${hmw}um
		box grow n ${hdy}um
		box grow s ${hdy}um
		if {($top_type != "") && ($tconnect == 1)} {
		    paint ${top_type}
		}
		if {($top_type != "") && ($bconnect == 1)} {
		    box move e ${cdx}um
		    paint ${top_type}
		}
		popbox
	    }
            box move n ${dy}um
        }
	popbox
        box move e ${dx}um
    }
    popbox
    popbox

    tech revert
}

#----------------------------------------------------------------

#ifdef MIM
proc gf180mcu::mim_2p0fF_draw {parameters} {
    set newdict [dict create \
#ifdef METALS6
	    top_type 		mtp \
	    top_contact_type	viatp \
	    bot_type 		m5 \
#endif
#ifdef METALS5
	    top_type 		m5 \
	    top_contact_type	via4 \
	    bot_type 		m4 \
#endif
#ifdef METALS4
	    top_type 		m4 \
	    top_contact_type	via3 \
	    bot_type 		m3 \
#endif
#ifdef METALS3
	    top_type 		m3 \
	    top_contact_type	via2 \
	    bot_type 		m2 \
#endif
	    cap_type 		mimcap \
	    cap_contact_type	mimcc \
	    bot_surround	0.6 \
	    cap_spacing		0.6 \
	    cap_surround	0.4 \
	    top_surround	0.0 \
	    end_surround	0.31 \
#ifdef THICKMET3P0
	    metal_surround	0.11 \
	    contact_size	1.80 \
	    end_spacing		1.28 \
#elseif (THICKMET1P1 || THICKMET0P9)
	    metal_surround	0.05 \
	    contact_size	0.44 \
	    end_spacing		0.67 \
#else
	    metal_surround	0.05 \
	    contact_size	0.36 \
	    end_spacing		0.60 \
#endif (!(THICKMET3P0 || THICKMET1P1 || THICKMET0P9))
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::cap_draw $drawdict]
}
#endif (MIM)

#----------------------------------------------------------------
# capacitor: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc gf180mcu::cap_check {parameters} {
    # In case wmax and/or lmax are undefined
    set lmax 0
    set wmax 0

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set l [magic::spice2float $l]
    set l [magic::3digitpastdecimal $l] 
    set w [magic::spice2float $w]
    set w [magic::3digitpastdecimal $w] 

    set val   [magic::spice2float $val]
    set carea [magic::spice2float $carea]
    set cperi [magic::spice2float $cperi]
    set dc    [magic::spice2float $dc]

    if {$square == 1} {
        # Calculate L and W from value
	set a $carea
	set b [expr $cperi * 4]
	set c [expr -4 * $dc - $val]
	set l [expr ((-$b + sqrt($b * $b - (4 * $a * $c))) / (2 * $a))]
	dict set parameters l [magic::float2spice $l]
	set w $l
	dict set parameters w [magic::float2spice $w]
    } elseif {$l == 0} {
        # Calculate L from W and value
	set l [expr (($val + 4 * $dc - 2 * $w * $cperi) / ($w * $carea + 2 * $cperi))]
	dict set parameters l [magic::float2spice $l]
    } elseif {$w == 0} {
        # Calculate W from L and value
	set w [expr (($val + 4 * $dc - 2 * $l * $cperi) / ($l * $carea + 2 * $cperi))]
	dict set parameters w [magic::float2spice $w]
    }
    if {$w < $wmin} {
	puts stderr "Capacitor width must be >= $wmin"
	dict set parameters w $wmin
	set w $wmin
    } 
    if {$l < $lmin} {
	puts stderr "Capacitor length must be >= $lmin"
	dict set parameters l $lmin
	set l $lmin
    } 
    if {($wmax > 0) && ($w > $wmax)} {
	puts stderr "Capacitor width must be <= $wmax"
	dict set parameters w $wmax
	set w $wmax
    } 
    if {($lmax > 0) && ($l > $lmax)} {
	puts stderr "Capacitor length must be <= $lmax"
	dict set parameters l $lmax
	set l $lmax
    } 
    # Calculate value from L and W
    set cval [expr ($l * $w * $carea + 2 * ($l + $w) * $cperi - 4 * $dc)]
    dict set parameters val [magic::float2spice $cval]
    gf180mcu::compute_ctot $parameters

    return $parameters
}

#ifdef MIM
proc gf180mcu::mim_2p0fF_check {parameters} {
    return [gf180mcu::cap_check $parameters]
}
#endif

#----------------------------------------------------------------
# Drawn resistors
#----------------------------------------------------------------

#----------------------------------------------------------------
# Resistor defaults:
#----------------------------------------------------------------
# User editable values:
#
#  val   Resistor value in ohms
#  w	 Width
#  l	 Length
#  t	 Number of turns
#  m	 Number devices in Y
#  nx	 Number devices in X
#  snake Use snake geometry
#  dummy Flag to mark addition of dummy resistor
#
# Non-user editable values:
#
#  wmin  Minimum allowed width
#  lmin  Minimum allowed length
#  rho	 Resistance in ohms per square
#  dw    Delta width
#  term  Resistance per terminal
#  sterm Additional resistance per terminal for snake geometry
#----------------------------------------------------------------

#----------------------------------------------------------------
# rnw: Specify all user-editable default values and those
# needed by nwell_check
#----------------------------------------------------------------

proc gf180mcu::nwell_defaults {} {
    return {w 2.000 l 10.00 m 1 nx 1 wmin 2.000 lmin 2.00 \
	 	rho 1680 val 8400 dummy 0 dw 0.25 term 1.0 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# rpp1: Specify all user-editable default values and those
# needed by rp1_check
#----------------------------------------------------------------

proc gf180mcu::ppolyf_u_defaults {} {
    return {w 0.80 l 1.00 m 1 nx 1 wmin 0.80 lmin 1.00 \
		rho 315 val 394 dummy 0 dw 0.07 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

proc gf180mcu::npolyf_u_defaults {} {
    return {w 0.80 l 1.00 m 1 nx 1 wmin 0.80 lmin 1.00 \
		rho 300 val 375 dummy 0 dw 0.09 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# rpp1s: Specify all user-editable default values and those
# needed by rp1_check
#----------------------------------------------------------------

proc gf180mcu::ppolyf_s_defaults {} {
    return {w 0.80 l 1.00 m 1 nx 1 wmin 0.80 lmin 1.00 \
		rho 7 val 8.75 dummy 0 dw 0.01 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

proc gf180mcu::npolyf_s_defaults {} {
    return {w 0.80 l 1.00 m 1 nx 1 wmin 0.80 lmin 1.00 \
		rho 7 val 8.75 dummy 0 dw 0.01 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# nplus_u: Specify all user-editable default values and those
# needed by nplus_u_check 
#----------------------------------------------------------------

proc gf180mcu::nplus_u_defaults {} {
    return {w 1.000 l 1.000 m 1 nx 1 wmin 1.00 lmin 1.00 \
		rho 85 val 85.0 dummy 0 dw 0.05 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# pplus_u: Specify all user-editable default values and those
# needed by pplus_u_check
#----------------------------------------------------------------

proc gf180mcu::pplus_u_defaults {} {
    return {w 1.000 l 1.000 m 1 nx 1 wmin 1.00 lmin 1.00 \
		rho 128 val 128.0 dummy 0 dw 0.02 term 0.0 \
		sterm 0.0 caplen 0.60 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# rm1: Specify all user-editable default values and those needed
# by rm1_check
#----------------------------------------------------------------

proc gf180mcu::rm1_defaults {} {
    return {w 0.160 l 0.160 m 1 nx 1 wmin 0.16 lmin 0.16 \
		rho 0.076 val 0.076 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}

#----------------------------------------------------------------
# rm2: Specify all user-editable default values and those needed
# by rm2_check
#----------------------------------------------------------------

proc gf180mcu::rm2_defaults {} {
    return {w 0.200 l 0.200 m 1 nx 1 wmin 0.20 lmin 0.20 \
		rho 0.053 val 0.053 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}

#----------------------------------------------------------------
# Additional entries for rm3, rm4, rm5, and rmtp, depending on
# the back-end metal stack.
#----------------------------------------------------------------

#ifdef METALS3 || METALS4 || METALS5 || METALS6
proc gf180mcu::rm3_defaults {} {
    return {w 0.200 l 0.200 m 1 nx 1 wmin 0.20 lmin 0.20 \
		rho 0.053 val 0.053 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}
#endif (METALS3 || METALS4 || METALS5 || METALS6)

#ifdef METALS4 || METALS5 || METALS6
proc gf180mcu::rm4_defaults {} {
    return {w 0.200 l 0.200 m 1 nx 1 wmin 0.20 lmin 0.20 \
		rho 0.053 val 0.053 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}
#endif (METALS4 || METALS5 || METALS6)
#ifdef METALS5 || METALS6
proc gf180mcu::rm5_defaults {} {
    return {w 0.200 l 0.200 m 1 nx 1 wmin 0.20 lmin 0.20 \
		rho 0.053 val 0.053 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}
#endif (METALS5 || METALS6)
#ifdef METALS6
proc gf180mcu::rmtp_defaults {} {
    return {w 0.200 l 0.200 m 1 nx 1 wmin 0.20 lmin 0.20 \
		rho 0.053 val 0.053 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}
#endif (METALS6)

#ifdef HRPOLY1K

#----------------------------------------------------------------
# ppolyf_u_1k: Specify all user-editable default values and those
# needed by npolyf_u_check
#----------------------------------------------------------------

proc gf180mcu::ppolyf_u_1k_defaults {} {
    return {w 1.000 l 2.000 m 1 nx 1 wmin 1.000 lmin 1.000 \
		rho 1000 val 2000 dummy 0 dw 0.0 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1 \
		compatible {ppolyf_u_1k ppolyf_u_1k_6p0}}
}

proc gf180mcu::ppolyf_u_1k_6p0_defaults {} {
    return {w 1.000 l 2.000 m 1 nx 1 wmin 1.000 lmin 1.000 \
		rho 1000 val 2000 dummy 0 dw 0.0 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 \
		glc 1 grc 1 gtc 0 gbc 0 roverlap 0 endcov 100 \
		full_metal 1 \
		compatible {ppolyf_u_1k ppolyf_u_1k_6p0}}
}
#endif (HRPOLY1K)
 
#----------------------------------------------------------------
# resistor: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc gf180mcu::res_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	set canonkey $key
	switch -nocase $key {
	    r_length -
	    r_width -
	    l -
	    w {
		switch -nocase $key {
		    r_length {
			set canonkey l
		    }
		    r_width {
			set canonkey w
		    }
		}
		# Length and width are converted to units of microns
		set value [magic::spice2float $value]
		set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $canonkey] $value
	    }
	}
    }
    return $pdkparams
}

#----------------------------------------------------------------

proc gf180mcu::nwell_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::ppolyf_u_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::ppolyf_s_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::npolyf_s_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::npolyf_u_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::nplus_u_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::pplus_u_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::rm1_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::rm2_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

#ifdef METALS3 || METALS4 || METALS5 || METALS6
proc gf180mcu::rm3_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}
#endif (METALS3 || METALS4 || METALS5 || METALS6)

#ifdef METALS4 || METALS5 || METALS6
proc gf180mcu::rm4_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}
#endif (METALS4 || METALS5 || METALS6)
#ifdef METALS5 || METALS6
proc gf180mcu::rm5_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}
#endif (METALS5 || METALS6)
#ifdef METALS6
proc gf180mcu::rmtp_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}
#endif (METALS6)

#ifdef HRPOLY1K
proc gf180mcu::ppolyf_u_1k_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}

proc gf180mcu::ppolyf_u_1k_6p0_convert {parameters} {
    return [gf180mcu::res_convert $parameters]
}
#endif (HRPOLY1K)

#----------------------------------------------------------------
# resistor: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc gf180mcu::res_dialog {device parameters} {
    # Editable fields:      w, l, t, nx, m, val
    # Checked fields:  

    magic::add_entry val "Value (ohms)" $parameters
    if {[dict exists $parameters snake]} {
	gf180mcu::compute_ltot $parameters
	magic::add_message ltot "Total length (um)" $parameters
    }
    magic::add_entry l "Length (um)" $parameters
    magic::add_entry w "Width (um)" $parameters
    magic::add_entry nx "X Repeat" $parameters
    magic::add_entry m "Y Repeat" $parameters
    if {[dict exists $parameters endcov]} {
	magic::add_entry endcov "End contact coverage (%)" $parameters
    }

    if {[dict exists $parameters compatible]} {
       set sellist [dict get $parameters compatible]
       # Reserved word "gencell" has special behavior to change the
       # underlying device type 
       dict set parameters gencell $device
       magic::add_selectlist gencell "Device type" $sellist $parameters
    }

    # magic::add_checkbox dummy "Add dummy" $parameters

    if {[dict exists $parameters snake]} {
	magic::add_checkbox snake "Use snake geometry" $parameters
    }
    if {[dict exists $parameters roverlap]} {
	if {[dict exists $parameters endcov]} {
            magic::add_checkbox roverlap "Overlap at end contact" $parameters
	} else {
            magic::add_checkbox roverlap "Overlap at ends" $parameters
	}
    }
	magic::add_checkbox full_metal "Full metal guard ring" $parameters
    if {[dict exists $parameters glc]} {
	magic::add_checkbox glc "Add left guard ring contact" $parameters
    }
    if {[dict exists $parameters grc]} {
	magic::add_checkbox grc "Add right guard ring contact" $parameters
    }
    if {[dict exists $parameters gtc]} {
	magic::add_checkbox gtc "Add top guard ring contact" $parameters
    }
    if {[dict exists $parameters gbc]} {
	magic::add_checkbox gbc "Add bottom guard ring contact" $parameters
    }

    if {[dict exists $parameters snake]} {
       magic::add_dependency gf180mcu::res_recalc $device gf180mcu l w val nx snake
    } else {
       magic::add_dependency gf180mcu::res_recalc $device gf180mcu l w val nx
    }
}

#----------------------------------------------------------------

proc gf180mcu::nwell_dialog {parameters} {
    gf180mcu::res_dialog nwell $parameters
}

proc gf180mcu::ppolyf_u_dialog {parameters} {
    gf180mcu::res_dialog ppolyf_u $parameters
}

proc gf180mcu::npolyf_u_dialog {parameters} {
    gf180mcu::res_dialog npolyf_u $parameters
}

proc gf180mcu::ppolyf_s_dialog {parameters} {
    gf180mcu::res_dialog ppolyf_s $parameters
}

proc gf180mcu::npolyf_s_dialog {parameters} {
    gf180mcu::res_dialog npolyf_s $parameters
}

proc gf180mcu::nplus_u_dialog {parameters} {
    gf180mcu::res_dialog nplus_u $parameters
}

proc gf180mcu::pplus_u_dialog {parameters} {
    gf180mcu::res_dialog pplus_u $parameters
}

proc gf180mcu::nplus_u_3p3_dialog {parameters} {
    gf180mcu::res_dialog nplus_u_3p3 $parameters
}

proc gf180mcu::pplus_u_3p3_dialog {parameters} {
    gf180mcu::res_dialog pplus_u_3p3 $parameters
}

proc gf180mcu::rm1_dialog {parameters} {
    gf180mcu::res_dialog rm1 $parameters
}

proc gf180mcu::rm2_dialog {parameters} {
    gf180mcu::res_dialog rm2 $parameters
}

#ifdef METALS3 || METALS4 || METALS5 || METALS6
proc gf180mcu::rm3_dialog {parameters} {
    gf180mcu::res_dialog rm3 $parameters
}
#endif (METALS3 || METALS4 || METALS5 || METALS6)

#ifdef METALS4 || METALS5 || METALS6
proc gf180mcu::rm4_dialog {parameters} {
    gf180mcu::res_dialog rm4 $parameters
}
#endif (METALS4 || METALS5 || METALS6)
#ifdef METALS5 || METALS6
proc gf180mcu::rm5_dialog {parameters} {
    gf180mcu::res_dialog rm5 $parameters
}
#endif (METALS5 || METALS6)
#ifdef METALS6
proc gf180mcu::rmtp_dialog {parameters} {
    gf180mcu::res_dialog rmtp $parameters
}
#endif (METALS6)

#ifdef HRPOLY1K
proc gf180mcu::ppolyf_u_1k_dialog {parameters} {
    gf180mcu::res_dialog ppolyf_u_1k $parameters
}

proc gf180mcu::ppolyf_u_1k_6p0_dialog {parameters} {
    gf180mcu::res_dialog ppolyf_u_1k_6p0 $parameters
}
#endif (HRPOLY1K)

#----------------------------------------------------------------
# Resistor: Draw a single device in straight geometry
#----------------------------------------------------------------

proc gf180mcu::res_device {parameters} {
    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set endcov 0	 	;# percent coverage of end contacts
    set well_res_overlap 0 	;# not a well resistor
    set end_contact_type ""	;# no contacts for metal resistors

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Draw the resistor and endcaps
    pushbox
    box size 0 0
    pushbox
    set hw [/ $w 2.0]
    set hl [/ $l 2.0]
    box grow n ${hl}um
    box grow s ${hl}um
    box grow e ${hw}um
    box grow w ${hw}um

    pushbox
    box grow n ${res_to_endcont}um
    box grow s ${res_to_endcont}um
    if {$well_res_overlap > 0} {
	set well_extend [+ ${well_res_overlap} [/ ${contact_size} 2.0] ${end_surround}]
	box grow n ${well_extend}um
	box grow s ${well_extend}um
	paint ${well_res_type}
    } else {
	paint ${end_type}
    }
    set cext [gf180mcu::getbox]
    popbox

    if {$well_res_overlap > 0} {
	erase ${well_res_type}
    } else {
	erase ${end_type}
    }
    paint ${res_type}
    popbox

    # Reduce contact sizes by (end type) surround so that
    # the contact area edges match the device type width.
    # (Minimum dimensions will be enforced by the contact drawing routine)
    set epl [- ${w} [* ${end_surround} 2]]     	    ;# end contact width

    # Reduce end material size for well resistor types
    if {$well_res_overlap > 0} {
	set epl [- ${epl} [* ${well_res_overlap} 2]]
    }

    # Reduce by coverage percentage unless overlapping at contacts
    if {(${roverlap} == 0) && (${endcov} > 0)} {
	set cpl [* ${epl} [/ ${endcov} 100.0]]
    } else {
	set cpl $epl
    }

    set hepl [+ [/ ${epl} 2.0] ${end_surround}]
    set hesz [+ [/ ${contact_size} 2.0] ${end_surround}]

    # Top end material & contact
    pushbox
    box move n ${hl}um
    box move n ${res_to_endcont}um

    pushbox
    box size 0 0
    box grow n ${hesz}um
    box grow s ${hesz}um
    box grow e ${hepl}um
    box grow w ${hepl}um
    paint ${end_type}
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]
    popbox

    if {${end_contact_type} != ""} {
	set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${contact_size} \
		${end_type} ${end_contact_type} m1 horz]]
    }
    popbox

    # Bottom end material & contact
    pushbox
    box move s ${hl}um
    box move s ${res_to_endcont}um

    pushbox
    box size 0 0
    box grow n ${hesz}um
    box grow s ${hesz}um
    box grow e ${hepl}um
    box grow w ${hepl}um
    paint ${end_type}
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]
    popbox

    if {${end_contact_type} != ""} {
	set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${contact_size} \
		${end_type} ${end_contact_type} m1 horz]]
    }
    popbox

    popbox
    return $cext
}

#----------------------------------------------------------------
# Resistor: Draw a single device in snake geometry
#----------------------------------------------------------------

proc gf180mcu::res_snake_device {nf parameters} {
    # nf is the number of fingers of the snake geometry

    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set endcov 100	 	;# percent coverage of end contacts
    set well_res_overlap 0 	;# not a well resistor
    set end_contact_type ""	;# no contacts for metal resistors
    set mask_clearance 0	;# additional length to clear mask

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Compute half width and length
    set hw [/ $w 2.0]
    set hl [/ $l 2.0]

    # Reduce contact sizes by (end type) surround so that
    # the contact area edges match the device type width.
    # (Minimum dimensions will be enforced by the contact drawing routine)
    set epl [- ${w} [* ${end_surround} 2]]     	    ;# end contact width

    # Reduce contact size for well resistor types
    if {$well_res_overlap > 0} {
	set epl [- ${epl} [* ${well_res_overlap} 2]]
    }

    # Reduce contact part of end by coverage percentage
    if {${endcov} > 0} {
	set cpl [* ${epl} [/ ${endcov} 100.0]]
    } else {
	set cpl $epl
    }

    set hepl [+ [/ ${epl} 2.0] ${end_surround}]
    set hesz [+ [/ ${contact_size} 2.0] ${end_surround}]

    pushbox
    box size 0 0	;# Position is taken from caller

    # Front end contact (always bottom)
    pushbox
    box move s ${hl}um
    pushbox
    box move s ${mask_clearance}um
    box move s ${res_to_endcont}um

    pushbox
    box size 0 0
    box grow n ${hesz}um
    box grow s ${hesz}um
    box grow e ${hepl}um
    box grow w ${hepl}um
    paint ${end_type}
    set cext [gf180mcu::getbox]
    popbox

    if {${end_contact_type} != ""} {
	set cext [gf180mcu::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${contact_size} \
		${end_type} ${end_contact_type} m1 horz]
    }
    popbox

    # Draw portion between resistor end and contact.
    box grow e ${hw}um
    box grow w ${hw}um
    pushbox
    box grow s ${mask_clearance}um
    paint ${res_type}
    popbox
    box move s ${mask_clearance}um
    box grow s ${res_to_endcont}um
    if {$well_res_overlap > 0} {
	set well_extend [+ ${well_res_overlap} [/ ${contact_size} 2.0] ${end_surround}]
	box grow s ${well_extend}um
	paint ${well_res_type}
    } else {
	paint ${end_type}
    }
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]
    popbox

    # Draw the resistor and endcaps
    pushbox
    box grow n ${hl}um
    box grow s ${hl}um
    box grow e ${hw}um
    box grow w ${hw}um

    # Capture these extents in the bounding box in case both contacts
    # are on one side.
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]

    set deltax [+ ${res_spacing} ${w}]
    set deltay [- ${l} ${w}]
    for {set i 0} {$i < [- $nf 1]} {incr i} {
	paint ${res_type}
 	pushbox
	if {[% $i 2] == 0} {
	    box move n ${deltay}um
	}
	box height ${w}um
	box width ${deltax}um
	paint ${res_type}
 	popbox
	box move e ${deltax}um
    }
    paint ${res_type}
    # Capture these extents in the bounding box
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]
    popbox

    # Move box to last finger
    set lastf [* [- $nf 1] $deltax]
    box move e ${lastf}um

    # Back-end contact (top or bottom, depending if odd or even turns)
    pushbox

    if {[% $nf 2] == 1} {
	set dir n
    } else {
	set dir s
    }
    box move $dir ${hl}um
    pushbox
    box move $dir ${mask_clearance}um
    box move $dir ${res_to_endcont}um

    pushbox
    box size 0 0
    box grow n ${hesz}um
    box grow s ${hesz}um
    box grow e ${hepl}um
    box grow w ${hepl}um
    paint ${end_type}
    set cext [gf180mcu::unionbox $cext [gf180mcu::getbox]]
    popbox

    if {${end_contact_type} != ""} {
	set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${contact_size} \
		${end_type} ${end_contact_type} m1 horz]]
    }
    popbox
    # Draw portion between resistor end and contact.
    box grow e ${hw}um
    box grow w ${hw}um
    pushbox
    box grow $dir ${mask_clearance}um
    paint ${res_type}
    popbox
    box move $dir ${mask_clearance}um
    box grow $dir ${res_to_endcont}um

    if {$well_res_overlap > 0} {
	set well_extend [+ ${well_res_overlap} [/ ${contact_size} 2.0] ${end_surround}]
	box grow $dir ${well_extend}um
	paint ${well_res_type}
    } else {
	paint ${end_type}
    }
    popbox

    popbox
    return $cext
}

#----------------------------------------------------------------
# Resistor: Draw the tiled device
#----------------------------------------------------------------

proc gf180mcu::res_draw {parameters} {
    tech unlock *

    # Set defaults if they are not in parameters
    set snake 0		;# some resistors don't allow snake geometry
    set roverlap 0	;# overlap resistors at contacts
    set guard 1		;# draw a guard ring
    set overlap_compress 0	;# special Y distance compression
    set well_res_overlap 0	;# additional well extension behind contact

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # For devices where inter-device space is smaller than device-to-guard ring
    if {![dict exists $parameters end_to_end_space]} {
	set end_to_end_space $end_spacing
    }

    # Normalize distance units to microns
    set w [magic::spice2float $w]
    set l [magic::spice2float $l]

    pushbox
    box values 0 0 0 0

    # Determine the base device dimensions by drawing one device
    # while all layers are locked (nothing drawn).  This allows the
    # base drawing routine to do complicated geometry without having
    # to duplicate it here with calculations.

    tech lock *
    set nf $nx
    if {($snake == 1) && ($nx == 1)} {set snake 0}
    if {$snake == 1} {
	set bbox [gf180mcu::res_snake_device $nf $parameters]
	set nx 1
    } else {
	set bbox [gf180mcu::res_device $parameters]
    }
    # puts stdout "Diagnostic: Device bounding box e $bbox (um)"
    tech unlock *

    set fw [- [lindex $bbox 2] [lindex $bbox 0]]
    set fh [- [lindex $bbox 3] [lindex $bbox 1]]
    set lw [+ [lindex $bbox 2] [lindex $bbox 0]]
    set lh [+ [lindex $bbox 3] [lindex $bbox 1]]

    # Determine tile width and height (depends on overlap)
    # Snake resistors cannot overlap.
    # However, snake resistors with an odd number of fingers can
    # compress the space if overlap_compress is defined

    if {($roverlap == 1) && ($snake == 1) && ([% $nf 2] == 1) && ($m > 1)} {
        set dy [- $fh $overlap_compress]
    } elseif {($roverlap == 0) || ($snake == 1)} {
        set dy [+ $fh $end_to_end_space]
    } else {
        # overlap poly
        set dy [- $fh [+ [* [+ $end_surround $well_res_overlap] 2.0] $contact_size]]
    }
    set dx [+ $fw $res_spacing]

    # Determine core width and height
    set corex [+ [* [- $nx 1] $dx] $fw]
    set corey [+ [* [- $m 1] $dy] $fh]
    set corellx [/ [+ [- $corex $fw] $lw] 2.0]
    set corelly [/ [+ [- $corey $fh] $lh] 2.0]

    if {$guard != 0} {
	# Calculate guard ring size (measured to contact center)
	set gx [+ $corex [* 2.0 [+ $res_diff_spacing $diff_surround]] $contact_size]
	set gy [+ $corey [* 2.0 [+ $end_spacing $diff_surround]] $contact_size]

	# Draw the guard ring first, because well resistors are on the substrate plane
	gf180mcu::guard_ring $gx $gy $parameters
    }

    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    # puts "Device position at = [gf180mcu::getbox]"
    for {set xp 0} {$xp < $nx} {incr xp} {
	pushbox
	for {set yp 0} {$yp < $m} {incr yp} {
	    if {$snake == 1} {
		gf180mcu::res_snake_device $nf $parameters
	    } else {
		gf180mcu::res_device $parameters
	    }
            box move n ${dy}um
        }
	popbox
        box move e ${dx}um
    }
    popbox
    popbox

    tech revert
}

#----------------------------------------------------------------

proc gf180mcu::ppolyf_u_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    res_type		rpp \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		nwell \
	    end_surround	$poly_surround \
	    end_spacing		0.44 \
	    end_to_end_space	0.52 \
	    res_to_endcont	$sblk_to_cont \
	    res_spacing		$polyres_spacing \
	    res_diff_spacing	0.44 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::npolyf_u_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    res_type		rnp \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		pwell \
	    end_surround	$poly_surround \
	    end_spacing		0.44 \
	    end_to_end_space	0.52 \
	    res_to_endcont	$sblk_to_cont \
	    res_spacing		$polyres_spacing \
	    res_diff_spacing	0.44 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::ppolyf_s_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    # Distance from resistor to end contact is different between straight
    # and snake geometry.

    set res_to_endcont [+ $poly_surround [/ $contact_size 2.0]]
    if {[dict exists $parameters snake]} {
	if {[dict get $parameters snake] == 1} {
	    set res_to_endcont [+ $res_to_endcont $poly_spacing]
	}
    }

    set newdict [dict create \
	    res_type		rpps \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		nwell \
	    end_surround	$poly_surround \
	    end_spacing		0.28 \
	    end_to_end_space	0.41 \
	    res_to_endcont	$res_to_endcont \
	    res_spacing		$polyres_spacing \
	    res_diff_spacing	0.41 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::npolyf_s_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    # Distance from resistor to end contact is different between straight
    # and snake geometry.

    set res_to_endcont [+ $poly_surround [/ $contact_size 2.0]]
    if {[dict exists $parameters snake]} {
	if {[dict get $parameters snake] == 1} {
	    set res_to_endcont [+ $res_to_endcont $poly_spacing]
	}
    }

    set newdict [dict create \
	    res_type		rnps \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		nwell \
	    end_surround	$poly_surround \
	    end_spacing		0.28 \
	    end_to_end_space	0.41 \
	    res_to_endcont	$res_to_endcont \
	    res_spacing		$polyres_spacing \
	    res_diff_spacing	0.28 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::nplus_u_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    res_type		rnd \
	    end_type 		ndiff \
	    end_contact_type	ndc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		pwell \
	    end_surround	$diff_surround \
	    end_spacing		0.45 \
	    res_to_endcont	0.45 \
	    res_spacing		$diffres_spacing \
	    res_diff_spacing	0.45 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::pplus_u_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    res_type		rpd \
	    end_type 		pdiff \
	    end_contact_type	pdc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		nwell \
	    end_surround	$diff_surround \
	    end_spacing		0.45 \
	    res_to_endcont	0.45 \
	    res_spacing		$diffres_spacing \
	    res_diff_spacing	0.45 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::nwell_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    well_res_type	nwell \
	    res_type		rnw \
	    end_type 		nsd \
	    end_contact_type	nsc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		pwell \
	    end_surround	$diff_surround \
	    end_spacing		1.2 \
	    overlap_compress	-0.84 \
	    res_to_endcont	0.22 \
	    res_spacing		1.2 \
	    res_diff_spacing	0.28 \
	    well_res_overlap	0.24 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

#ifdef HRPOLY1K
proc gf180mcu::ppolyf_u_1k_draw {parameters} {
    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    res_type		hires \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		pwell \
	    end_surround	$poly_surround \
	    end_spacing		0.7 \
	    res_to_endcont	0.43 \
	    res_spacing		$polyres_spacing \
	    res_diff_spacing	0.7 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

proc gf180mcu::ppolyf_u_1k_6p0_draw {parameters} {
    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    diff_poly_space	0.30 \
	    diff_gate_space	0.30 \
	    diff_spacing	0.36 \
	    res_type		mvhires \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    sub_type		pwell \
	    sub_surround	0.16 \
	    end_surround	$poly_surround \
	    end_spacing		0.7 \
	    res_to_endcont	0.43 \
	    res_spacing		$polyres_spacing \
	    res_diff_spacing	0.7 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}
#endif (HRPOLY1K)

#----------------------------------------------------------------

proc gf180mcu::rm1_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm1 \
	    end_type 		m1 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    res_spacing		$metal_spacing \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

proc gf180mcu::rm2_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm2 \
	    end_type 		m2 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------

#ifdef METALS3 || METALS4 || METALS5 || METALS6
proc gf180mcu::rm3_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm3 \
	    end_type 		m3 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}

#----------------------------------------------------------------
#endif (METALS3 || METALS4 || METALS5 || METALS6)

#ifdef METALS4 || METALS5 || METALS6
proc gf180mcu::rm4_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm4 \
	    end_type 		m4 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}
#endif (METALS4 || METALS5 || METALS6)

#ifdef METALS5 || METALS6
proc gf180mcu::rm5_draw {parameters} {
    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm5 \
	    end_type 		m5 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}
#endif (METALS5 || METALS6)
#ifdef METALS6
proc gf180mcu::rmtp_draw {parameters} {
    # Set a local variable for each rule in ruleset
    foreach key [dict keys $gf180mcu::ruleset] {
        set $key [dict get $gf180mcu::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rmtp \
	    end_type 		mtp \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::res_draw $drawdict]
}
#endif (METALS6)

#----------------------------------------------------------------
# Resistor total length computation
#----------------------------------------------------------------

proc gf180mcu::compute_ltot {parameters} {
    # In case snake not defined
    set snake 0
    set caplen 0

    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    set l [magic::spice2float $l]
    set l [magic::3digitpastdecimal $l]

    # Compute total length.  Use catch to prevent error in batch/scripted mode.
    if {$snake == 1} {
	catch {set magic::ltot_val [expr ($caplen * ($nx - 1)) + ($l * $nx) + ($nx - 1)]}
    } else {
	catch {set magic::ltot_val $l}
    }
}

#----------------------------------------------------------------
# resistor: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc gf180mcu::res_check {device parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    set snake 0
    set sterm 0.0
    set caplen 0
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set w [magic::spice2float $w]
    set w [magic::3digitpastdecimal $w]
    set l [magic::spice2float $l]
    set l [magic::3digitpastdecimal $l]

    set val  [magic::spice2float $val]
    set rho  [magic::spice2float $rho]

    # nf, m must be integer
    if {![string is int $nx]} {
	puts stderr "X repeat must be an integer!"
        dict set parameters nx 1
    }
    if {![string is int $m]} {
	puts stderr "Y repeat must be an integer!"
        dict set parameters m 1
    }

    # Width always needs to be specified
    if {$w < $wmin} {
	puts stderr "Resistor width must be >= $wmin um"
	dict set parameters w $wmin
    } 
    # Val and W specified - no L
    if {$l == 0}  {
   	set l [expr ($w - $dw) * $val / $rho]
        set l [magic::3digitpastdecimal $l]
        set stringval [magic::float2spice $val]
	dict set parameters l [magic::float2spice [expr $l * 1e-6]]
	# L and W specified - ignore Val if specified
    } else {
	if {$snake == 0} {
	    set val [expr (2 * $term + $l * $rho) / ($w - $dw)]
	} else {
	    set val [expr $rho * ($nx - 1) + ((2 * ($term + $sterm)) \
			+ ($rho * $l * $nx) + ($rho * $caplen * ($nx - 1))) \
			/ ($w - $dw)]
	}
	set val [magic::float2spice $val]
        dict set parameters val $val
    }
    if {$l < $lmin} {
	puts stderr "Resistor length must be >= $lmin um"
	dict set parameters l $lmin
    } 
    if {$nx < 1} {
	puts stderr "X repeat must be >= 1"
	dict set parameters nx 1
    } 
    if {$m < 1} {
	puts stderr "Y repeat must be >= 1"
	dict set parameters m 1
    } 

    # Snake resistors cannot have width greater than length
    if {$snake == 1} {
	if {$w > $l} {
	    puts stderr "Snake resistor width must be < length"
	    dict set parameters w $l
	}
    }

    # Diffusion resistors must satisfy diffusion-to-tap spacing of 20um.
    # Therefore the maximum of guard ring width or height cannot exceed 40um.
    # If in violation, reduce counts first, as these are easiest to recover
    # by duplicating the device and overlapping the wells.
    if {$device == "rdn" || $device == "rdp"} {
       set origm $m
       set orignx $nx
       while true {
	  set xext [expr ($w + 0.8) * $nx + 1.0]
	  set yext [expr ($l + 1.7) * $m + 1.7]
          if {[expr min($xext, $yext)] > 40.0} {
              if {$yext > 40.0 && $m > 1} {
		 incr m -1
	      } elseif {$xext > 40.0 && $nx > 1} {
		 incr nx -1
	      } elseif {$yext > 40.0} {
		 set l 36.6
		 puts -nonewline stderr "Diffusion resistor length must be < 36.6 um"
		 puts stderr " to avoid tap spacing violation."
		 dict set parameters l $l
	      } elseif {$xext > 40.0} {
		 set w 38.2
		 puts -nonewline stderr "Diffusion resistor width must be < 38.2 um"
		 puts stderr " to avoid tap spacing violation."
		 dict set parameters w $w
	      }
          } else {
	      break
	  }
       }
       if {$m != $origm} {
	  puts stderr "Y repeat reduced to prevent tap distance violation"
	  dict set parameters m $m
       }
       if {$nx != $orignx} {
	  puts stderr "X repeat reduced to prevent tap distance violation"
	  dict set parameters nx $nx
       }
    }
    gf180mcu::compute_ltot $parameters
    return $parameters
}

#----------------------------------------------------------------

proc gf180mcu::nwell_check {parameters} {
    return [gf180mcu::res_check nwell $parameters]
}

proc gf180mcu::ppolyf_u_check {parameters} {
    return [gf180mcu::res_check ppolyf_u $parameters]
}

proc gf180mcu::npolyf_u_check {parameters} {
    return [gf180mcu::res_check npolyf_u $parameters]
}

proc gf180mcu::ppolyf_s_check {parameters} {
    return [gf180mcu::res_check rpp1s $parameters]
}

proc gf180mcu::npolyf_s_check {parameters} {
    return [gf180mcu::res_check rpp1s $parameters]
}

proc gf180mcu::nplus_u_check {parameters} {
    return [gf180mcu::res_check nplus_u $parameters]
}

proc gf180mcu::pplus_u_check {parameters} {
    return [gf180mcu::res_check pplus_u $parameters]
}

proc gf180mcu::rm1_check {parameters} {
    return [gf180mcu::res_check rm1 $parameters]
}

proc gf180mcu::rm2_check {parameters} {
    return [gf180mcu::res_check rm2 $parameters]
}

#ifdef METALS3 || METALS4 || METALS5 || METALS6
proc gf180mcu::rm3_check {parameters} {
    return [gf180mcu::res_check rm3 $parameters]
}
#endif (METALS3 || METALS4 || METALS5 || METALS6)

#ifdef METALS4 || METALS5 || METALS6
proc gf180mcu::rm4_check {parameters} {
    return [gf180mcu::res_check rm4 $parameters]
}
#endif (METALS4 || METALS5 || METALS6)

#ifdef METALS5 || METALS6
proc gf180mcu::rm5_check {parameters} {
    return [gf180mcu::res_check rm5 $parameters]
}
#endif (METALS5 || METALS6)
#ifdef METALS6
proc gf180mcu::rmtp_check {parameters} {
    return [gf180mcu::res_check rmtp $parameters]
}
#endif (METALS6)

#ifdef HRPOLY1K
proc gf180mcu::ppolyf_u_1k_check {parameters} {
    return [gf180mcu::res_check ppolyf_u_1k $parameters]
}

proc gf180mcu::ppolyf_u_1k_6p0_check {parameters} {
    return [gf180mcu::res_check ppolyf_u_1k_6p0 $parameters]
}
#endif (HRPOLY1K)

#----------------------------------------------------------------
# MOS defaults:
#----------------------------------------------------------------
#    w       = Gate width
#    l       = Gate length
#    m	     = Multiplier
#    nf	     = Number of fingers
#    diffcov = Diffusion contact coverage
#    polycov = Poly contact coverage
#    topc    = Top gate contact
#    botc    = Bottom gate contact
#    guard   = Guard ring
#
# (not user-editable)
#
#    lmin    = Gate minimum length
#    wmin    = Gate minimum width
#----------------------------------------------------------------

#----------------------------------------------------------------
# pmos: Specify all user-editable default values and those
# needed by pmos_check
#----------------------------------------------------------------

proc gf180mcu::pmos_3p3_defaults {} {
    return {w 0.220 l 0.280 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.28 wmin 0.22 \
		full_metal 1 \
		compatible {pmos_3p3 pmos_6p0}}
}

proc gf180mcu::pmos_6p0_defaults {} {
    return {w 0.3 l 0.5 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.5 wmin 0.3 \
		full_metal 1 \
		compatible {pmos_3p3 pmos_6p0}}
}

#----------------------------------------------------------------
# nmos: Specify all user-editable default values and those
# needed by nmos_check
#----------------------------------------------------------------

proc gf180mcu::nmos_3p3_defaults {} {
    return {w 0.220 l 0.280 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.28 wmin 0.22 \
		full_metal 1 \
		compatible {nmos_3p3 nmos_6p0 nmos_6p0_nat}}
}

proc gf180mcu::nmos_6p0_defaults {} {
    return {w 0.3 l 0.6 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.6 wmin 0.3 \
		full_metal 1 \
		compatible {nmos_3p3 nmos_6p0 nmos_6p0_nat}}
}

proc gf180mcu::nmos_6p0_nat_defaults {} {
    return {w 0.8 l 1.8 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 1.8 wmin 0.8 \
		full_metal 1 \
		compatible {nmos_3p3 nmos_6p0 nmos_6p0_nat}}
}

#----------------------------------------------------------------
# mosvc: Specify all user-editable default values and those
# needed by nmoscap_3p3_check
#----------------------------------------------------------------

proc gf180mcu::nmoscap_3p3_defaults {} {
    return {w 1.0 l 1.0 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.28 wmin 0.22 \
		full_metal 1 compatible {nmoscap_3p3 nmoscap_6p0}}
}

proc gf180mcu::nmoscap_6p0_defaults {} {
    return {w 1.0 l 1.0 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 0 gbc 0 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.28 wmin 0.3 \
		full_metal 1 compatible {nmoscap_3p3 nmoscap_6p0}}
}

#----------------------------------------------------------------
# mos: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc gf180mcu::mos_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    l -
	    w {
		# Length and width are converted to units of microns
		set value [magic::spice2float $value]
		set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $key] $value
	    }
	    m {
		# M value in an expression like '1*1' convert to
		# M and NF
		if {[regexp {\'([0-9]+)\*([0-9]+)\'} $value valid m nf]} {
		    dict set pdkparams [string tolower $key] $m
		    dict set pdkparams nf $nf
		} else {
		    dict set pdkparams [string tolower $key] $value
		}
	    }
	}
    }
    return $pdkparams
}

#----------------------------------------------------------------

proc gf180mcu::nmos_3p3_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

proc gf180mcu::nmos_6p0_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

proc gf180mcu::nmos_6p0_nat_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

proc gf180mcu::pmos_3p3_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

proc gf180mcu::pmos_6p0_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

proc gf180mcu::nmoscap_3p3_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

proc gf180mcu::nmoscap_6p0_convert {parameters} {
    return [gf180mcu::mos_convert $parameters]
}

#----------------------------------------------------------------
# mos: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc gf180mcu::mos_dialog {device parameters} {
    # Editable fields:      w, l, nf, m, diffcov, polycov
    # Checked fields:  topc, botc

    magic::add_entry w "Width (um)" $parameters
    magic::add_entry l "Length (um)" $parameters
    magic::add_entry nf "Fingers" $parameters
    magic::add_entry m "M" $parameters

    if {[dict exists $parameters compatible]} {
       set sellist [dict get $parameters compatible]
       # Reserved word "gencell" has special behavior to change the
       # underlying device type 
       dict set parameters gencell $device
       magic::add_selectlist gencell "Device type" $sellist $parameters
    }

    magic::add_entry diffcov "Diffusion contact coverage (%)" $parameters
    magic::add_entry polycov "Poly contact coverage (%)" $parameters
    magic::add_entry rlcov "Guard ring contact coverage (%)" $parameters
    if {[dict exists $parameters gbc]} {
	magic::add_entry tbcov "Guard ring top/bottom contact coverage (%)" $parameters
    }

    magic::add_checkbox poverlap "Overlap at poly contact" $parameters
    magic::add_checkbox doverlap "Overlap at diffusion contact" $parameters
    magic::add_checkbox topc "Add top gate contact" $parameters
    magic::add_checkbox botc "Add bottom gate contact" $parameters

    magic::add_checkbox guard "Add guard ring" $parameters
    magic::add_checkbox full_metal "Full metal guard ring" $parameters
    magic::add_checkbox glc "Add left guard ring contact" $parameters
    magic::add_checkbox grc "Add right guard ring contact" $parameters
    if {[dict exists $parameters gbc]} {
	magic::add_checkbox gbc "Add bottom guard ring contact" $parameters
    }
    if {[dict exists $parameters gtc]} {
	magic::add_checkbox gtc "Add top guard ring contact" $parameters
    }
}

#----------------------------------------------------------------

proc gf180mcu::nmos_3p3_dialog {parameters} {
    gf180mcu::mos_dialog nmos_3p3 $parameters
}

proc gf180mcu::nmos_6p0_dialog {parameters} {
    gf180mcu::mos_dialog nmos_6p0 $parameters
}

proc gf180mcu::nmos_6p0_nat_dialog {parameters} {
    gf180mcu::mos_dialog nmos_6p0_nat $parameters
}

proc gf180mcu::pmos_3p3_dialog {parameters} {
    gf180mcu::mos_dialog pmos_3p3 $parameters
}

proc gf180mcu::pmos_6p0_dialog {parameters} {
    gf180mcu::mos_dialog pmos_6p0 $parameters
}

proc gf180mcu::nmoscap_3p3_dialog {parameters} {
    gf180mcu::mos_dialog nmoscap_3p3 $parameters
}

proc gf180mcu::nmoscap_6p0_dialog {parameters} {
    gf180mcu::mos_dialog nmoscap_6p0 $parameters
}

#----------------------------------------------------------------
# getbox:  Get the current cursor box, in microns
#----------------------------------------------------------------

proc gf180mcu::getbox {} {
    set curbox [box values]
    set newbox []
    set oscale [cif scale out]
    for {set i 0} {$i < 4} {incr i} {
        set v [* [lindex $curbox $i] $oscale]
        lappend newbox $v
    }
    return $newbox
}

#----------------------------------------------------------------
# unionbox:  Get the union bounding box of box1 and box2
#----------------------------------------------------------------

proc gf180mcu::unionbox {box1 box2} {
    set newbox []
    for {set i 0} {$i < 2} {incr i} {
        set v [lindex $box1 $i]
        set o [lindex $box2 $i]
        if {$v < $o} {
            lappend newbox $v
        } else {
            lappend newbox $o
        }
    }
    for {set i 2} {$i < 4} {incr i} {
        set v [lindex $box1 $i]
        set o [lindex $box2 $i]
        if {$v > $o} {
            lappend newbox $v
        } else {
            lappend newbox $o
        }
    }
    return $newbox
}

#----------------------------------------------------------------
# Draw a contact
#----------------------------------------------------------------

proc gf180mcu::draw_contact {w h s o x atype ctype mtype {orient vert}} {

    # Draw a minimum-size diff contact centered at current position
    # w is width, h is height.  Minimum size ensured.
    # x is contact size
    # s is contact diffusion (or poly) surround
    # o is contact metal surround
    # atype is active (e.g., ndiff) or bottom metal if a via
    # ctype is contact (e.g., ndc)
    # mtype is metal (e.g., m1) or top metal if a via
    # cover is percent maximum coverage of contact

    pushbox
    box size 0 0
    if {$w < $x} {set w $x}
    if {$h < $x} {set h $x}
    set hw [/ $w 2.0]
    set hh [/ $h 2.0]
    # Bottom layer surrounded on all sides
    box grow e ${hw}um
    box grow w ${hw}um
    box grow n ${hh}um
    box grow s ${hh}um
    pushbox
    paint ${ctype}
    popbox
    pushbox
    box grow c ${s}um
    paint ${atype}
    set extents [gf180mcu::getbox]
    popbox
    if {($orient == "vert") || ($orient == "full")} {
        box grow n ${o}um
        box grow s ${o}um
    }
    if {($orient == "horz") || ($orient == "full")} {
        box grow e ${o}um
        box grow w ${o}um
    }
    paint ${mtype}
    popbox
    return $extents
}

#----------------------------------------------------------------
# Draw a guard ring
#----------------------------------------------------------------

proc gf180mcu::guard_ring {gw gh parameters} {

    # Set local default values if they are not in parameters
    set rlcov 100	;# Right-left contact coverage percentage
    set tbcov 100	;# Top-bottom contact coverage percentage
    set grc 1		;# Draw right side contact
    set glc 1		;# Draw left side contact
    set gtc 0		;# Draw right side contact
    set gbc 0		;# Draw left side contact
    set full_metal 0	;# Draw full (continuous) metal ring

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    set hx [/ $contact_size 2.0]
    set hw [/ $gw 2.0]
    set hh [/ $gh 2.0]

    # Compute diffusion width
    set difft [+ $contact_size $diff_surround $diff_surround]
    set hdifft [/ $difft 2.0]
    # Compute guard ring diffusion width and height
    set hdiffw [/ [+ $gw $difft] 2.0]
    set hdiffh [/ [+ $gh $difft] 2.0]

    pushbox
    box size 0 0

    pushbox
    box move n ${hh}um
    box grow n ${hdifft}um
    box grow s ${hdifft}um
    box grow e ${hdiffw}um
    box grow w ${hdiffw}um
    paint $plus_diff_type
    popbox
    pushbox
    box move s ${hh}um
    box grow n ${hdifft}um
    box grow s ${hdifft}um
    box grow e ${hdiffw}um
    box grow w ${hdiffw}um
    paint $plus_diff_type
    popbox
    pushbox
    box move e ${hw}um
    box grow e ${hdifft}um
    box grow w ${hdifft}um
    box grow n ${hdiffh}um
    box grow s ${hdiffh}um
    paint $plus_diff_type
    popbox
    pushbox
    box move w ${hw}um
    box grow e ${hdifft}um
    box grow w ${hdifft}um
    box grow n ${hdiffh}um
    box grow s ${hdiffh}um
    paint $plus_diff_type
    popbox

    if {$full_metal} {
	set hmetw [/ [+ $gw $contact_size] 2.0]
	set hmeth [/ [+ $gh $contact_size] 2.0]
	pushbox
	box move n ${hh}um
	box grow n ${hx}um
	box grow s ${hx}um
	box grow e ${hmetw}um
	box grow w ${hmetw}um
	paint m1
	popbox
	pushbox
	box move s ${hh}um
	box grow n ${hx}um
	box grow s ${hx}um
	box grow e ${hmetw}um
	box grow w ${hmetw}um
	paint m1
	popbox
	pushbox
	box move e ${hw}um
	box grow e ${hx}um
	box grow w ${hx}um
	box grow n ${hmeth}um
	box grow s ${hmeth}um
	paint m1
	popbox
	pushbox
	box move w ${hw}um
	box grow e ${hx}um
	box grow w ${hx}um
	box grow n ${hmeth}um
	box grow s ${hmeth}um
	paint m1
	popbox
    }

    # Set guard ring height so that contact metal reaches to end, scale by $per
    # set ch [* [+ $gh $contact_size [* $metal_surround -2.0]] [/ $rlcov 100.0]]
    set ch [* [- $gh $contact_size [* [+ $metal_surround $metal_spacing] \
		2.0]] [/ $rlcov 100.0]]
    if {$ch < $contact_size} {set ch $contact_size}

    # Set guard ring width so that contact metal reaches to side contacts
    set cw [* [- $gw $contact_size [* [+ $metal_surround $metal_spacing] \
		2.0]] [/ $tbcov 100.0]]
    if {$cw < $contact_size} {set cw $contact_size}

    if {$tbcov > 0.0} {
        if {$gtc == 1} {
            pushbox
            box move n ${hh}um
            gf180mcu::draw_contact $cw 0 $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type m1 horz
            popbox
	}
	if {$gbc == 1} {
	    pushbox
	    box move s ${hh}um
	    gf180mcu::draw_contact $cw 0 $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type m1 horz
	    popbox
	}
    }
    if {$rlcov > 0.0} {
        if {$grc == 1} {
            pushbox
            box move e ${hw}um
            gf180mcu::draw_contact 0 $ch $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type m1 vert
            popbox
        }
        if {$glc == 1} {
            pushbox
            box move w ${hw}um
            gf180mcu::draw_contact 0 $ch $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type m1 vert
            popbox
        }
    }

    pushbox
    box grow e ${hw}um
    box grow w ${hw}um
    box grow n ${hh}um
    box grow s ${hh}um
    property FIXED_BBOX [box values]
    box grow c ${hx}um  ;# to edge of contact
    box grow c ${diff_surround}um  ;# to edge of diffusion
    box grow c ${sub_surround}um  ;# sub/well overlap of diff
    paint $sub_type
    set cext [gf180mcu::getbox]
    popbox
    popbox

    return $cext
}

#----------------------------------------------------------------
# MOSFET: Draw a single device
#----------------------------------------------------------------

proc gf180mcu::mos_device {parameters} {

    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set diffcov 100	;# percent coverage of diffusion contact
    set polycov 100	;# percent coverage of poly contact
    set topc 1		;# draw top poly contact
    set botc 1		;# draw bottom poly contact
    set dev_sub_type ""	;# device substrate type (if different from guard ring)

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Draw the diffusion and poly
    pushbox
    box size 0 0
    pushbox
    set hw [/ $w 2.0]
    set hl [/ $l 2.0]
    box grow n ${hw}um
    box grow s ${hw}um
    box grow e ${hl}um
    box grow w ${hl}um
    pushbox
    if {${diff_extension} > ${gate_to_diffcont}} {
        box grow e ${diff_extension}um
        box grow w ${diff_extension}um
    } else {
        box grow e ${gate_to_diffcont}um
        box grow w ${gate_to_diffcont}um
        # Grow to far side of contact;  avoids diffusion separation if
	# the contact is a dogbone and is moved outward to meet the DRC
	# diffusion to gate spacing rule.
	set hc [/ ${contact_size} 2.0]
        box grow e ${hc}um
        box grow w ${hc}um
    }
    paint ${diff_type}
    popbox
    pushbox
    if {${gate_extension} > ${gate_to_polycont}} {
	box grow n ${gate_extension}um
	box grow s ${gate_extension}um
    } else {
	if {$topc} {
	    box grow n ${gate_to_polycont}um
	} else {
	    box grow n ${gate_extension}um
	}
	if {$botc} {
	    box grow s ${gate_to_polycont}um
	} else {
	    box grow s ${gate_extension}um
	}
    }
    paint ${poly_type}
    set cext [gf180mcu::getbox]
    popbox
    # gate_type need not be defined if poly over diff paints the right type.
    catch {paint ${gate_type}}
    popbox

    # Adjust position of contacts for dogbone geometry
    # Rule 1: Minimize diffusion length.  Contacts only move out
    # if width <  contact diffusion height.  They move out enough
    # that the diffusion-to-poly spacing is satisfied.  Change the
    # orientation of the diffusion contact from vertical to horizontal

    set diffcont_orient vert
    set ddover 0
    set cdwmin [+ ${contact_size} [* ${diff_surround} 2]]
    set cstem [- ${gate_to_diffcont} [/ ${cdwmin} 2.0]]
    set cgrow [- ${diff_poly_space} ${cstem}]
    if {[+ ${w} ${eps}] < ${cdwmin}} {
        if {${cgrow} > 0} {
            set gate_to_diffcont [+ ${gate_to_diffcont} ${cgrow}]
	    set diffcont_orient horz
        }
	set ddover [/ [- ${cdwmin} ${w}] 2.0]
    }

    # Rule 2: Minimum poly width.  Poly contacts only move out
    # if length < contact poly width.  They move out enough
    # that the diffusion-to-poly spacing is satisfied.

    set gporig ${gate_to_polycont}
    set cplmin [+ ${contact_size} [* ${poly_surround} 2]]
    set cstem [- ${gate_to_polycont} [/ ${cplmin} 2.0]]
    set cgrow [- ${diff_poly_space} ${cstem}]
    if {[+ ${l} ${eps}] < ${cplmin}} {
        if {${cgrow} > 0} {
            set gate_to_polycont [+ ${gate_to_polycont} ${cgrow}]
        }
    }

    # Rule 3: If both poly and diffusion are dogboned, then move
    # poly out further to clear spacing to the diffusion contact.

    if {[+ ${w} ${eps}] < ${cdwmin}} {
        if {[+ ${l} ${eps}] < ${cplmin}} {
            set cgrow [/ [- ${cplmin} ${w}] 2.0]
            set gate_to_polycont [+ ${gate_to_polycont} ${cgrow}]
        }
    }

    # Rule 4: If M > 1 and poly contacts overlap, then increase the
    # transistor-to-poly-contact distance by the amount of any
    # diffusion dogbone overhang.

    if {($poverlap == 1) && ($m > 1)} {
	if {${gate_to_polycont} - $gporig < $ddover} {
	    set gate_to_polycont [+ ${gporig} ${ddover}]
	}
    }

    # Reduce contact sizes by poly or diffusion surround so that
    # the contact area edges match the device diffusion or poly.
    # (Minimum dimensions will be enforced by the contact drawing routine)
    set cdw [- ${w} [* ${diff_surround} 2]]     ;# diff contact height
    set cpl [- ${l} [* ${poly_surround} 2]]     ;# poly contact width

    # Reduce by coverage percentage.  NOTE:  If overlapping multiple devices,
    # keep maximum poly contact coverage.

    set cdw [* ${cdw} [/ ${diffcov} 100.0]]
    if {($poverlap == 0) || ($m == 1)} {
	set cpl [* ${cpl} [/ ${polycov} 100.0]]
    }

    # Right diffusion contact
    pushbox
    box move e ${hl}um
    box move e ${gate_to_diffcont}um
    set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact 0 ${cdw} \
		${diff_surround} ${metal_surround} ${contact_size}\
		${diff_type} ${diff_contact_type} m1 ${diffcont_orient}]]
    popbox
    # Left diffusion contact
    pushbox
    box move w ${hl}um
    box move w ${gate_to_diffcont}um
    set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact 0 ${cdw} \
		${diff_surround} ${metal_surround} ${contact_size} \
		${diff_type} ${diff_contact_type} m1 ${diffcont_orient}]]
    popbox
    # Top poly contact
    if {$topc} {
       pushbox
       box move n ${hw}um
       box move n ${gate_to_polycont}um
       set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact ${cpl} 0 \
		${poly_surround} ${metal_surround} ${contact_size} \
		${poly_type} ${poly_contact_type} m1 horz]]
       popbox
    }
    # Bottom poly contact
    if {$botc} {
       pushbox
       box move s ${hw}um
       box move s ${gate_to_polycont}um
       set cext [gf180mcu::unionbox $cext [gf180mcu::draw_contact ${cpl} 0 \
		${poly_surround} ${metal_surround} ${contact_size} \
		${poly_type} ${poly_contact_type} m1 horz]]
       popbox
    }

    if {$dev_sub_type != ""} {
        # puts stdout "Diagnostic:  bounding box is $cext"
	set llx [lindex $cext 0]
	set lly [lindex $cext 1]
	set urx [lindex $cext 2]
	set ury [lindex $cext 3]
	box values ${llx}um ${lly}um ${urx}um ${ury}um
	box grow n ${sub_surround}um
	box grow s ${sub_surround}um
	box grow e ${sub_surround}um
	box grow w ${sub_surround}um
	paint ${dev_sub_type}
	set cext [gf180mcu::getbox]
        # puts stdout "Diagnostic:  bounding box is $cext"
    }

    popbox
    return $cext
}

#----------------------------------------------------------------
# MOSFET: Draw the tiled device
#----------------------------------------------------------------

proc gf180mcu::mos_draw {parameters} {
    tech unlock *

    # Set defaults if they are not in parameters
    set poverlap 0	;# overlap poly contacts when tiling
    set doverlap 1	;# overlap diffusion contacts when tiling
    set dev_sub_dist 0	;# substrate to guard ring, if dev_sub_type defined
    set dev_surround 0	;# substrate/well surrounds device, if no guard ring

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # If poverlap is 1 then both poly contacts must be present
    if {$poverlap == 1} {
	set topc 1
	set botc 1
	dict set parameters topc 1
	dict set parameters botc 1
    }

    # Normalize distance units to microns
    set w [magic::spice2float $w]
    set l [magic::spice2float $l]

    pushbox
    box values 0 0 0 0

    # Determine the base device dimensions by drawing one device
    # while all layers are locked (nothing drawn).  This allows the
    # base drawing routine to do complicated geometry without having
    # to duplicate it here with calculations.

    tech lock *
    set bbox [gf180mcu::mos_device $parameters]
    # puts stdout "Diagnostic: Device bounding box e $bbox (um)"
    tech unlock *

    set fw [- [lindex $bbox 2] [lindex $bbox 0]]
    set fh [- [lindex $bbox 3] [lindex $bbox 1]]
    set lw [+ [lindex $bbox 2] [lindex $bbox 0]]
    set lh [+ [lindex $bbox 3] [lindex $bbox 1]]

    # Determine tile width and height (depends on overlap)
    if {$poverlap == 0} {
        set dy [+ $fh $poly_spacing]
    } else {
        # overlap poly
        set dy [- $fh [+ $poly_surround $poly_surround $contact_size]]
    }

    if {$doverlap == 0} {
        set dx [+ $fw $diff_spacing]
    } else {
        # overlap diffusions
        set dx [- $fw [+ $diff_surround $diff_surround $contact_size]]
    }

    # Determine core width and height
    set corex [+ [* [- $nf 1] $dx] $fw]
    set corey [+ [* [- $m 1] $dy] $fh]
    set corellx [/ [+ [- $corex $fw] $lw] 2.0]
    set corelly [/ [+ [- $corey $fh] $lh] 2.0]

    # If there is a diffusion dogbone, and no top poly contact, then
    # increase the core height by the amount of the dogbone overhang.

    if {$topc == 0} {
	set cdwmin [+ ${contact_size} [* ${diff_surround} 2]]
	if {${w} < ${cdwmin}} {
	    set corey [+ $corey [/ [- ${cdwmin} ${w}] 2.0]]
	}
    }

    # Calculate guard ring size (measured to contact center)
    if {($dev_sub_dist > 0) && ([+ $dev_sub_dist $sub_surround] > $diff_spacing)} {
	set gx [+ $corex [* 2.0 [+ $dev_sub_dist $diff_surround]] $contact_size]
    } else {
	set gx [+ $corex [* 2.0 [+ $diff_spacing $diff_surround]] $contact_size]
    }
    if {($dev_sub_dist > 0) && ([+ $dev_sub_dist $sub_surround] > $diff_gate_space)} {
	set gy [+ $corey [* 2.0 [+ $dev_sub_dist $diff_surround]] $contact_size]
    } else {
	set gy [+ $corey [* 2.0 [+ $diff_gate_space $diff_surround]] $contact_size]
    }

    if {($guard != 0)} {
        # Somewhat tricky. . . if the width is small and the diffusion is 
        # a dogbone, and the top or bottom poly contact is missing, then
        # the spacing to the guard ring may be limited by diffusion spacing, not
        # poly to diffusion.

        set inset [/ [+ $contact_size [* 2.0 $diff_surround] -$w] 2.0]
        set sdiff [- [+ $inset $diff_spacing] [+ $gate_extension $diff_gate_space]]

        if {$sdiff > 0} {
	    if {$topc == 0} {
	        set gy [+ $gy $sdiff]
	        set corelly [+ $corelly [/ $sdiff 2.0]]
	    }
	    if {$botc == 0} {
	        set gy [+ $gy $sdiff]
	        set corelly [- $corelly [/ $sdiff 2.0]]
	    }
        }
    }
    if {$guard != 0} {
	# Draw the guard ring first, as MOS well may interact with guard ring substrate
	gf180mcu::guard_ring $gx $gy $parameters
    } else {
	pushbox
	if {$dev_surround == 0} {set dev_surround $sub_surround}
	set hgx [+ $dev_surround [/ $corex 2]]
	set hgy [+ $dev_surround [/ $corey 2]]
	box grow e ${hgx}um
	box grow w ${hgx}um
	box grow n ${hgy}um
	box grow s ${hgy}um
	paint $sub_type
	popbox
    }

    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    for {set xp 0} {$xp < $nf} {incr xp} {
        pushbox
        for {set yp 0} {$yp < $m} {incr yp} {
            gf180mcu::mos_device $parameters
            box move n ${dy}um
        }
        popbox
        box move e ${dx}um
    }
    popbox
    popbox

    tech revert
}

#-------------------
# nMOS 3.3V
#-------------------

proc gf180mcu::nmos_3p3_draw {parameters} {
    set newdict [dict create \
	    gate_type		nfet \
	    diff_type 		ndiff \
	    diff_contact_type	ndc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		pwell \
	    sub_surround	0.12 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

#-------------------
# pMOS 3.3V
#-------------------

proc gf180mcu::pmos_3p3_draw {parameters} {
    set newdict [dict create \
	    gate_type		pfet \
	    diff_type 		pdiff \
	    diff_contact_type	pdc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    dev_surround	0.43 \
	    sub_type		nwell \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

#-------------------
# pMOS 6.0V
#-------------------

proc gf180mcu::pmos_6p0_draw {parameters} {
    set newdict [dict create \
	    diff_poly_space	0.30 \
	    diff_gate_space	0.30 \
	    diff_spacing	0.36 \
	    gate_type		mvpfet \
	    diff_type 		mvpdiff \
	    diff_contact_type	mvpdc \
	    plus_diff_type	mvnsd \
	    plus_contact_type	mvnsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_surround	0.16 \
	    dev_surround	0.43 \
	    sub_type		nwell \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

#-------------------
# nMOS 6.0V
#-------------------

proc gf180mcu::nmos_6p0_draw {parameters} {
    set newdict [dict create \
	    diff_poly_space	0.30 \
	    diff_gate_space	0.30 \
	    diff_spacing	0.36 \
	    gate_type		mvnfet \
	    diff_type 		mvndiff \
	    diff_contact_type	mvndc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		pwell \
	    sub_surround	0.16 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

proc gf180mcu::nmos_6p0_nat_draw {parameters} {
    set newdict [dict create \
	    gate_type		mvnnfet \
	    diff_type 		mvndiff \
	    diff_contact_type	mvndc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		pwell \
	    sub_surround	0.16 \
	    gate_extension	0.35 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

#------------------------
# MOS varactor (3.3V)
#------------------------

proc gf180mcu::nmoscap_3p3_draw {parameters} {
    set newdict [dict create \
	    gate_type		var \
	    diff_type 		nsd \
	    diff_contact_type	nsc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		pwell \
	    dev_sub_type	nwell \
	    dev_sub_dist	0.12 \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

#------------------------
# MOS varactor (6.0V)
#------------------------

proc gf180mcu::nmoscap_6p0_draw {parameters} {
    set newdict [dict create \
	    diff_poly_space	0.30 \
	    diff_gate_space	0.30 \
	    diff_spacing	0.36 \
	    gate_type		mvvar \
	    diff_type 		mvnsd \
	    diff_contact_type	mvnsc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		pwell \
	    sub_surround	0.16 \
	    dev_sub_type	nwell \
    ]
    set drawdict [dict merge $gf180mcu::ruleset $newdict $parameters]
    return [gf180mcu::mos_draw $drawdict]
}

#----------------------------------------------------------------
# nmos: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc gf180mcu::mos_check {parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set l [magic::spice2float $l] 
    set l [magic::3digitpastdecimal $l]
    set w [magic::spice2float $w] 
    set w [magic::3digitpastdecimal $w]

    # nf, m must be integer
    if {![string is int $nf]} {
	puts stderr "NF must be an integer!"
        dict set parameters nf 1
    }
    if {![string is int $m]} {
	puts stderr "M must be an integer!"
        dict set parameters m 1
    }
    # diffcov, polycov must be numeric
    if {[catch {expr abs($diffcov)}]} {
	puts stderr "diffcov must be numeric!"
	set diffcov 100
    }
    if {[catch {expr abs($polycov)}]} {
	puts stderr "polycov must be numeric!"
	set polycov 100
    }

    if {$l < $lmin} {
	puts stderr "Mos length must be >= $lmin um"
        dict set parameters l $lmin
    } 
    if {$w < $wmin} {
	puts stderr "Mos width must be >= $wmin um"
        dict set parameters w $wmin
    } 
    if {$nf < 1} {
	puts stderr "NF must be >= 1"
        dict set parameters nf 1
    } 
    if {$m < 1} {
	puts stderr "M must be >= 1"
        dict set parameters m 1
    } 
    if {$diffcov < 20 } {
	puts stderr "Diffusion contact coverage must be at least 20%"
        dict set parameters diffcov 20
    } elseif {$diffcov > 100 } {
	puts stderr "Diffusion contact coverage can't be more than 100%"
        dict set parameters diffcov 100
    }
    if {$polycov < 20 } {
	puts stderr "Poly contact coverage must be at least 20%"
        dict set parameters polycov 20
    } elseif {$polycov > 100 } {
	puts stderr "Poly contact coverage can't be more than 100%"
        dict set parameters polycov 100
    }

    # Values must satisfy diffusion-to-tap spacing of 20um.
    # Therefore the maximum of guard ring width or height cannot exceed 40um.
    # If in violation, reduce counts first, as these are easiest to recover
    # by duplicating the device and overlapping the wells.
    set origm $m
    set orignf $nf
    while true {
       set yext [expr ($w + 3.0) * $m]
       set xext [expr ($l + 1.0) * $nf + 1.1]
       if {[expr min($xext, $yext)] > 40.0} {
          if {$yext > 40.0 && $m > 1} {
	     incr m -1
	  } elseif {$xext > 40.0 && $nf > 1} {
	     incr nf -1
	  } elseif {$yext > 40.0} {
	     set w 37
	     puts -nonewline stderr "Transistor width must be < 37 um"
	     puts stderr " to avoid tap spacing violation."
	     dict set parameters w $w
	  } elseif {$xext > 40.0} {
	     set l 37.9
	     puts -nonewline stderr "Transistor length must be < 37.9 um"
	     puts stderr " to avoid tap spacing violation."
	     dict set parameters l $l
	  }
       } else {
	  break
       }
    }
    if {$m != $origm} {
       puts stderr "Y repeat reduced to prevent tap distance violation"
       dict set parameters m $m
    }
    if {$nf != $orignf} {
       puts stderr "X repeat reduced to prevent tap distance violation"
       dict set parameters nf $nf
    }

    return $parameters
}

#----------------------------------------------------------------

proc gf180mcu::nmos_3p3_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

proc gf180mcu::nmos_6p0_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

proc gf180mcu::nmos_6p0_nat_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

proc gf180mcu::pmos_3p3_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

proc gf180mcu::pmos_6p0_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

proc gf180mcu::nmoscap_3p3_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

proc gf180mcu::nmoscap_6p0_check {parameters} {
   return [gf180mcu::mos_check $parameters]
}

#----------------------------------------------------------------
# Bipolar: Specify all user-editable default values
#
# deltax --- Additional horizontal space between devices
# deltay --- Additional vertical space between devices
# nx     --- Number of arrayed devices in X
# ny     --- Number of arrayed devices in Y
#
# Note that these values, specifically nx, ny, deltax,
# and deltay, are properties of the instance, not the cell.
# They translate to the instance array x and y counts;  while
# deltax is the x pitch less the cell width, and deltay is the
# y pitch less the cell height.
#
# non-user-editable
#
# nocell --- Indicates that this cell has a predefined layout
#	     and therefore there is no cell to draw.
# xstep  --- Width of the cell (nominal array pitch in X)
# ystep  --- Height of the cell (nominal array pitch in Y)
#----------------------------------------------------------------

proc gf180mcu::vnpn_5x5_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 13.94 ystep 13.94}
}

proc gf180mcu::vnpn_5x0p42_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 12.36 ystep 16.22}
}

proc gf180mcu::vnpn_10x10_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 16.94 ystep 16.94}
}

proc gf180mcu::vnpn_10x0p42_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 12.36 ystep 21.22}
}

proc gf180mcu::vpnp_5x5_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 13.94 ystep 13.94}
}

proc gf180mcu::vpnp_5x0p42_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 12.36 ystep 16.22}
}

proc gf180mcu::vpnp_10x10_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 16.94 ystep 16.94}
}

proc gf180mcu::vpnp_10x0p42_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 12.36 ystep 21.22}
}

#----------------------------------------------------------------
# Bipolar: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc gf180mcu::fixed_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    m {
		 dict set pdkparams nx $value
	    }
	}
    }
    return $pdkparams
}

#----------------------------------------------------------------

proc gf180mcu::vnpn_5x5_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vnpn_5x0p42_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vnpn_10x10_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vnpn_10x0p42_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vpnp_5x5_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vpnp_5x0p42_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vpnp_10x10_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

proc gf180mcu::vpnp_10x0p42_convert {parameters} {
    return [gf180mcu::fixed_convert $parameters]
}

#----------------------------------------------------------------
# Bipolar: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc gf180mcu::fixed_dialog {parameters} {
    # Instance fields:	    nx, ny, pitchx, pitchy
    # Editable fields:	    nx, ny, deltax, deltay
    # Non-editable fields:  nocell, xstep, ystep

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # "nocell" field causes nx and ny to be dropped in from
    # "array count".  Also "pitchx" and "pitchy" are passed
    # in internal units.  Convert these to microns and generate
    # If there is no pitchx and pitchy, then the device has not
    # yet been created, so keep the deltax and deltay defaults.

    if [dict exists $parameters pitchx] {
	set pitchux [magic::i2u $pitchx]
	set stepux [magic::spice2float $xstep]
        set deltax [magic::3digitpastdecimal [expr $pitchux - $stepux]] 
        # An array size 1 should not cause deltax to go negative
	if {$deltax < 0.0} {set deltax 0.0}
	dict set parameters deltax $deltax
    }
    if [dict exists $parameters pitchy] {
	set pitchuy [magic::i2u $pitchy]
	set stepuy [magic::spice2float $ystep]
        set deltay [magic::3digitpastdecimal [expr $pitchuy - $stepuy]] 
        # An array size 1 should not cause deltay to go negative
	if {$deltay < 0.0} {set deltay 0.0}
	dict set parameters deltay $deltay
    }

    magic::add_entry nx "NX" $parameters
    magic::add_entry ny "NY" $parameters
    magic::add_entry deltax "X step (um)" $parameters
    magic::add_entry deltay "Y step (um)" $parameters
}

#----------------------------------------------------------------

proc gf180mcu::vnpn_5x5_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vnpn_5x0p42_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vnpn_10x10_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vnpn_10x0p42_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vpnp_5x5_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vpnp_5x0p42_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vpnp_10x10_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

proc gf180mcu::vpnp_10x0p42_dialog {parameters} {
    gf180mcu::fixed_dialog $parameters
}

#----------------------------------------------------------------
# PNP: Draw the device
#----------------------------------------------------------------

proc gf180mcu::fixed_draw {devname parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # This cell declares "nocell" in parameters, so it needs to
    # instance the cell and set properties.

    # Instantiate the cell.  The name corresponds to the cell in the primdev directory.
    set instname [getcell ${devname}]

    set deltax [magic::spice2float $deltax] 
    set deltay [magic::spice2float $deltay] 
    set xstep [magic::spice2float $xstep] 
    set ystep [magic::spice2float $ystep] 

    # Array stepping
    if {$nx > 1 || $ny > 1} {
        set xstep [expr $xstep + $deltax]
        set ystep [expr $ystep + $deltay]
        box size ${xstep}um ${ystep}um
	array $nx $ny
    }
    select cell $instname
    expand
    return $instname
}

#----------------------------------------------------------------
# No additional parameters declared for drawing
#----------------------------------------------------------------

proc gf180mcu::vnpn_5x5_draw {parameters} {
   return [gf180mcu::fixed_draw vnpn_5x5 $parameters]
}

proc gf180mcu::vnpn_5x0p42_draw {parameters} {
   return [gf180mcu::fixed_draw vnpn_5x0p42 $parameters]
}

proc gf180mcu::vnpn_10x10_draw {parameters} {
   return [gf180mcu::fixed_draw vnpn_10X10 $parameters]
}

proc gf180mcu::vnpn_10x0p42_draw {parameters} {
   return [gf180mcu::fixed_draw vnpn_10X0p42 $parameters]
}

proc gf180mcu::vpnp_5x5_draw {parameters} {
   return [gf180mcu::fixed_draw vpnp_5x5 $parameters]
}

proc gf180mcu::vpnp_5x0p42_draw {parameters} {
   return [gf180mcu::fixed_draw vpnp_5x0p42 $parameters]
}

proc gf180mcu::vpnp_10x10_draw {parameters} {
   return [gf180mcu::fixed_draw vpnp_10X10 $parameters]
}

proc gf180mcu::vpnp_10x0p42_draw {parameters} {
   return [gf180mcu::fixed_draw vpnp_10X0p42 $parameters]
}

#----------------------------------------------------------------
# Bipolar: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc gf180mcu::fixed_check {parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Normalize distance units to microns
    set deltax [magic::spice2float $deltax -1] 
    set deltax [magic::3digitpastdecimal $deltax]
    set deltay [magic::spice2float $deltay -1] 
    set deltay [magic::3digitpastdecimal $deltay]

    # nx, ny must be integer
    if {![string is int $nx]} {
	puts stderr "NX must be an integer!"
        dict set parameters nx 1
    }
    if {![string is int $ny]} {
	puts stderr "NY must be an integer!"
        dict set parameters nx 1
    }

    # Number of devices in X and Y must be at least 1
    if {$nx < 1} {
	puts stderr "NX must be >= 1"
        dict set parameters nx 1
    }
    if {$ny < 1} {
	puts stderr "NY must be >= 1"
        dict set parameters nx 1
    }
    # Step less than zero violates DRC
    if {$deltax < 0} {
	puts stderr "X step must be >= 0"
        dict set parameters deltax 0
    }
    if {$deltay < 0} {
	puts stderr "Y step must be >= 0"
        dict set parameters deltay 0
    }
    return $parameters
}

#----------------------------------------------------------------

proc gf180mcu::vnpn_5x5_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vnpn_5x0p42_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vnpn_10x10_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vnpn_10x0p42_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vpnp_5x5_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vpnp_5x0p42_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vpnp_10x10_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}

proc gf180mcu::vpnp_10x0p42_check {parameters} {
    return [gf180mcu::fixed_check $parameters]
}


