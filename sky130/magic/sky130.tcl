###
###     Source file sky130.tcl
###     Process this file with the preprocessor script
###
#-----------------------------------------------------
# Magic/TCL design kit for SKYWATER TECHNAME
#-----------------------------------------------------
# Tim Edwards
# Revision 0	PRE-ALPHA   3/21/2019
#-----------------------------------------------------

set TECHPATH STAGING_PATH
if [catch {set PDKPATH}] {set PDKPATH ${TECHPATH}/TECHNAME}
set PDKNAME TECHNAME
# "sky130" is the namespace used for all devices
set PDKNAMESPACE sky130
puts stdout "Loading TECHNAME Device Generator Menu ..."

# Initialize toolkit menus to the wrapper window

global Opts
namespace eval sky130 {}

# Set the window callback
if [catch {set Opts(callback)}] {set Opts(callback) ""}
set Opts(callback) [subst {sky130::addtechmenu \$framename; $Opts(callback)}]

# if {![info exists Opts(cmdentry)]} {set Opts(cmdentry) 1}

# Set options specific to this PDK
set Opts(hidelocked) 1
set Opts(hidespecial) 1

# Create new "tool" proc that doesn't have the netlist tool.
proc magic::nexttool {} {
   global Opts

   # Don't attempt to switch tools while a selection drag is active
   if {$Opts(motion) == {}} {
      switch $Opts(tool) {
         box { magic::tool wiring }
         wiring { magic::tool pick }
         default { magic::tool box }
      }
   }
}

# This shoule be part of sitedef. . .
macro space magic::nexttool

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

namespace eval sky130 {
    namespace path {::tcl::mathop ::tcl::mathfunc}

    set ruleset [dict create]

    # Process DRC rules (magic style)

    dict set ruleset poly_surround    0.08      ;# Poly surrounds contact
    dict set ruleset diff_surround    0.06      ;# Diffusion surrounds contact
    dict set ruleset gate_to_diffcont 0.145     ;# Gate to diffusion contact center
    dict set ruleset gate_to_polycont 0.275     ;# Gate to poly contact center
    dict set ruleset gate_extension   0.13      ;# Poly extension beyond gate
    dict set ruleset diff_extension   0.29      ;# Diffusion extension beyond gate
    dict set ruleset contact_size     0.17      ;# Minimum contact size
    dict set ruleset via_size         0.17      ;# Minimum via size
    dict set ruleset metal_surround   0.08      ;# Local interconnect overlaps contact
    dict set ruleset sub_surround     0.18      ;# Sub/well surrounds diffusion
    dict set ruleset diff_spacing     0.28      ;# Diffusion spacing rule
    dict set ruleset poly_spacing     0.21      ;# Poly spacing rule
    dict set ruleset diff_poly_space  0.075     ;# Diffusion to poly spacing rule
    dict set ruleset diff_gate_space  0.20      ;# Diffusion to gate poly spacing rule
    dict set ruleset metal_spacing    0.23      ;# Local interconnect spacing rule
    dict set ruleset mmetal_spacing   0.14      ;# Metal spacing rule (above local interconnect)
    dict set ruleset res_to_cont      0.20      ;# resistor to contact center
    dict set ruleset res_diff_space   0.20      ;# resistor to guard ring
}

#-----------------------------------------------------
# magic::addtechmenu
#-----------------------------------------------------

proc sky130::addtechmenu {framename} {
   global Winopts Opts
   
   # Check for difference between magic 8.1.125 and earlier, and 8.1.126 and later
   if {[catch {${framename}.titlebar cget -height}]} {
      set layoutframe ${framename}.pane.top
   } else {
      set layoutframe ${framename}
   }

   # List of devices is long.  Divide into two sections for active and passive deivces
   magic::add_toolkit_menu $layoutframe "Devices 1" pdk1

   magic::add_toolkit_command $layoutframe "nmos (MOSFET)" \
	    "magic::gencell sky130::nshort" pdk1
   magic::add_toolkit_command $layoutframe "pmos (MOSFET)" \
	    "magic::gencell sky130::pshort" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1
   magic::add_toolkit_command $layoutframe "n-diode" \
	    "magic::gencell sky130::ndiode" pdk1
   magic::add_toolkit_command $layoutframe "p-diode" \
	    "magic::gencell sky130::pdiode" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1
   magic::add_toolkit_command $layoutframe "MOS varactor" \
	    "magic::gencell sky130::xcnwvc" pdk1
   magic::add_toolkit_separator	$layoutframe pdk1

   magic::add_toolkit_command $layoutframe "NPN 1x1" \
	    "magic::gencell sky130::sky130_fd_pr_rf_npn_1x1" pdk1
   magic::add_toolkit_command $layoutframe "NPN 1x2" \
	    "magic::gencell sky130::sky130_fd_pr_rf_npn_1x2" pdk1
   magic::add_toolkit_command $layoutframe "PNP 5x" \
	    "magic::gencell sky130::sky130_fd_pr_rf_pnp5x" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1

   magic::add_toolkit_command $layoutframe "balun" \
	    "magic::gencell sky130::balun" pdk1
   magic::add_toolkit_command $layoutframe "inductor 011" \
	    "magic::gencell sky130::xind4_011" pdk1
   magic::add_toolkit_command $layoutframe "inductor 02" \
	    "magic::gencell sky130::xind4_02" pdk1

   magic::add_toolkit_separator	$layoutframe pdk1

   magic::add_toolkit_command $layoutframe "substrate contact (1.8V)" \
	    "sky130::subconn_draw" pdk1
   magic::add_toolkit_command $layoutframe "substrate contact (5.0V)" \
	    "sky130::mvsubconn_draw" pdk1
   magic::add_toolkit_command $layoutframe "deep n-well region" \
	    "sky130::deep_nwell_draw" pdk1
   magic::add_toolkit_command $layoutframe "mcon" \
	    "sky130::mcon_draw" pdk1
   magic::add_toolkit_command $layoutframe "via1" \
	    "sky130::via1_draw" pdk1
   magic::add_toolkit_command $layoutframe "via2" \
	    "sky130::via2_draw" pdk1
#ifdef METAL5
   magic::add_toolkit_command $layoutframe "via3" \
	    "sky130::via3_draw" pdk1
   magic::add_toolkit_command $layoutframe "via4" \
	    "sky130::via4_draw" pdk1
#endif (METAL5)
   

   magic::add_toolkit_menu $layoutframe "Devices 2" pdk2

   magic::add_toolkit_command $layoutframe "mrdn (1.8V) - 120 Ohm/sq" \
	    "magic::gencell sky130::mrdn" pdk2
   magic::add_toolkit_command $layoutframe "mrdp (1.8V) - 197 Ohm/sq" \
	    "magic::gencell sky130::mrdp" pdk2
   magic::add_toolkit_command $layoutframe "mrdn_hv (5.0V) - 114 Ohm/sq" \
	    "magic::gencell sky130::mrdn_hv" pdk2
   magic::add_toolkit_command $layoutframe "mrdp_hv (5.0V) - 191 Ohm/sq" \
	    "magic::gencell sky130::mrdp_hv" pdk2

   magic::add_toolkit_command $layoutframe "mrp1 - 48.2 Ohm/sq" \
	    "magic::gencell sky130::mrp1" pdk2
   magic::add_toolkit_command $layoutframe "xhrpoly_0p35 - 319.8 Ohm/sq" \
	    "magic::gencell sky130::xhrpoly" pdk2
   magic::add_toolkit_command $layoutframe "uhrpoly_0p35 - 2000 Ohm/sq" \
	    "magic::gencell sky130::uhrpoly" pdk2
   magic::add_toolkit_command $layoutframe "xpwres - 3050 Ohm/sq" \
	    "magic::gencell sky130::xpwres" pdk2
   magic::add_toolkit_separator	$layoutframe pdk2

   magic::add_toolkit_command $layoutframe "mrl1 - 12.2 Ohm/sq" \
	    "magic::gencell sky130::mrl1" pdk2
   magic::add_toolkit_command $layoutframe "mrm1 - 125 mOhm/sq" \
	    "magic::gencell sky130::mrm1" pdk2
   magic::add_toolkit_command $layoutframe "mrm2 - 125 mOhm/sq" \
	    "magic::gencell sky130::mrm2" pdk2
   magic::add_toolkit_command $layoutframe "mrm3 - 47 mOhm/sq" \
	    "magic::gencell sky130::mrm3" pdk2
#ifdef METAL5
   magic::add_toolkit_command $layoutframe "mrm4 - 47 mOhm/sq" \
	    "magic::gencell sky130::mrm4" pdk2
   magic::add_toolkit_command $layoutframe "mrm5 - 29 mOhm/sq" \
	    "magic::gencell sky130::mrm5" pdk2
#endif (METAL5)

#ifdef MIM
   magic::add_toolkit_command $layoutframe "xcmimc1 - 1fF/um^2 MiM cap" \
	    "magic::gencell sky130::xcmimc1" pdk2
   magic::add_toolkit_command $layoutframe "xcmimc2 - 1fF/um^2 MiM cap" \
	    "magic::gencell sky130::xcmimc2" pdk2
#endif (MIM)
   magic::add_toolkit_separator	$layoutframe pdk2

   magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 li/m5 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 li/m3/m5 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 m4 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 p/m4 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield" pdk2
   # magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 p/m5 shield" \
   #	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 4.4x4.6 li/m3/m5 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 6.8x6.1 li/m4 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 6.8x6.1 p/m4 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 8.6x7.9 li/m3/m5 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 4.2x2 nhvnat" \
	    "magic::gencell sky130::sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4" pdk2
   magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 li/m3 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 11.5x11.7 m3 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield" pdk2
   # magic::add_toolkit_command $layoutframe "vpp 1.8x1.8 li shield" \
   #	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield" pdk2
   # magic::add_toolkit_command $layoutframe "vpp 1.8x1.8 m3 shield" \
   #	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 4.4x4.6 li/m3 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 4.4x4.6 m3 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 8.6x7.9 li/m3 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield" pdk2
   magic::add_toolkit_command $layoutframe "vpp 8.6x7.9 m3 shield" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield" pdk2
   magic::add_toolkit_command $layoutframe "vpp2" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp2" pdk2
   magic::add_toolkit_command $layoutframe "vpp2 nwell" \
	    "magic::gencell sky130::sky130_fd_pr_rf_xcmvpp2_nwell" pdk2

   ${layoutframe}.titlebar.mbuttons.drc.toolmenu add command -label "DRC Routing" -command {drc style drc(routing)}

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

proc sky130::mcon_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.17} {
      puts stderr "Mcon width must be at least 0.17um"
      return
   }
   if {$h < 0.17} {
      puts stderr "Mcon height must be at least 0.17um"
      return
   }
   paint lic
   box grow n 0.05um
   box grow s 0.05um
   paint m1
   box grow n -0.05um
   box grow s -0.05um
   box grow e 0.05um
   box grow w 0.05um
   paint li
   box grow e -0.05um
   box grow w -0.05um
}

proc sky130::via1_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.26} {
      puts stderr "Via1 width must be at least 0.26um"
      return
   }
   if {$h < 0.26} {
      puts stderr "Via1 height must be at least 0.26um"
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

proc sky130::via2_draw {} {
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

#ifdef METAL5
proc sky130::via3_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.32} {
      puts stderr "Via3 width must be at least 0.32um"
      return
   }
   if {$h < 0.32} {
      puts stderr "Via3 height must be at least 0.32um"
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

proc sky130::via4_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 1.18} {
      puts stderr "Via3 width must be at least 1.18um"
      return
   }
   if {$h < 1.18} {
      puts stderr "Via3 height must be at least 1.18um"
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
#endif (METAL5)

proc sky130::subconn_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.17} {
      puts stderr "Substrate tap width must be at least 0.17um"
      return
   }
   if {$h < 0.17} {
      puts stderr "Substrate tap height must be at least 0.17um"
      return
   }
   paint nsc
   box grow c 0.1um
   paint nsd
   box grow c -0.1um
}

#----------------------------------------------------------------

proc sky130::mvsubconn_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 0.17} {
      puts stderr "Substrate tap width must be at least 0.17um"
      return
   }
   if {$h < 0.17} {
      puts stderr "Substrate tap height must be at least 0.17um"
      return
   }
   paint mvnsc
   box grow c 0.1um
   paint mvnsd
   box grow c -0.1um
}

#----------------------------------------------------------------

proc sky130::deep_nwell_draw {} {
   set w [magic::i2u [box width]]
   set h [magic::i2u [box height]]
   if {$w < 3.0} {
      puts stderr "Deep-nwell region width must be at least 3.0um"
      return
   }
   if {$h < 3.0} {
      puts stderr "Deep-nwell region height must be at least 3.0um"
      return
   }
   suspendall
   tech unlock *
   paint dnwell
   pushbox
   pushbox
   box grow c 0.4um
   paint nwell
   box grow c -1.43um
   erase nwell
   popbox
   box grow c 0.03um

   pushbox
   box width 0
   box grow c 0.085um
   paint li
   pushbox
   box grow n -0.3um
   box grow s -0.3um
   paint nsc
   popbox
   box grow c 0.1um
   paint nsd
   popbox

   pushbox
   box height 0
   box grow c 0.085um
   paint li
   pushbox
   box grow e -0.3um
   box grow w -0.3um
   paint nsc
   popbox
   box grow c 0.1um
   paint nsd
   popbox

   pushbox
   box move n [box height]i
   box height 0
   box grow c 0.085um
   paint li
   pushbox
   box grow e -0.3um
   box grow w -0.3um
   paint nsc
   popbox
   box grow c 0.1um
   paint nsd
   popbox

   pushbox
   box move e [box width]i
   box width 0
   box grow c 0.085um
   paint li
   pushbox
   box grow n -0.3um
   box grow s -0.3um
   paint nsc
   box grow c 0.1um
   paint nsd
   popbox

   popbox
   tech revert
   resumeall
}

#----------------------------------------------------------------

proc sky130::res_recalc {field parameters} {
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

proc sky130::diode_recalc {field parameters} {
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

proc sky130::diode_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    l -
	    w -
	    peri {
		# Length, width, and perimeter are converted to units of microns
		set value [magic::spice2float $value]
		# set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $key] $value
	    }
	    area {
		# area also converted to units of microns
		set value [magic::spice2float $value]
		# set value [expr $value * 1e12]
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

proc sky130::diode_dialog {device parameters} {
    # Editable fields:      w, l, area, perim, nx, ny

    magic::add_entry area "Area (um^2)" $parameters
    magic::add_entry peri "Perimeter (um)" $parameters
    sky130::compute_aptot $parameters
    magic::add_message atot "Total area (um^2)" $parameters
    magic::add_message ptot "Total perimeter (um)" $parameters
    magic::add_entry l "Length (um)" $parameters
    magic::add_entry w "Width (um)" $parameters
    magic::add_entry nx "X Repeat" $parameters
    magic::add_entry ny "Y Repeat" $parameters

    if {[dict exists $parameters compatible]} {
       set sellist [dict get $parameters compatible]
       magic::add_selectlist gencell "Device type" $sellist $parameters $device
    }

    if {[dict exists $parameters doverlap]} {
	magic::add_checkbox doverlap "Overlap at end contact" $parameters
    }
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

    magic::add_dependency sky130::diode_recalc $device sky130 l w area peri

    # magic::add_checkbox dummy "Add dummy" $parameters
}

#----------------------------------------------------------------
# Diode total area and perimeter computation
#----------------------------------------------------------------

proc sky130::compute_aptot {parameters} {
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

proc sky130::diode_check {parameters} {

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
    sky130::compute_aptot $parameters

    return $parameters
}

#------------------------------------------------------------------
# NOTE:  ndiode_lvt, ndiode_native, pdiode_lvt, and pdiode_hvt are
# all considered parasitic diodes.  They may be generated by
# invoking the build procedure on the command line.  To enable them
# in the PDK, add them to the appropriate compatible {} list.
#------------------------------------------------------------------

proc sky130::ndiode_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 \
	compatible {ndiode ndiode_h} full_metal 1}
}

proc sky130::ndiode_lvt_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 \
	full_metal 1}
}

proc sky130::pdiode_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 \
	glc 1 grc 1 gtc 1 gbc 1 doverlap 0 \
	compatible {pdiode pdiode_h} full_metal 1}
}

proc sky130::pdiode_lvt_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 \
	glc 1 grc 1 gtc 1 gbc 1 doverlap 0 \
	full_metal 1}
}

proc sky130::pdiode_hvt_defaults {} {
    return {w 0.45 l 0.45 area 0.2025 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 \
	glc 1 grc 1 gtc 1 gbc 1 doverlap 0 \
	full_metal 1}
}

proc sky130::ndiode_h_defaults {} {
    return {w 0.45 l 0.45 area 0.2024 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 \
	compatible {ndiode ndiode_h} full_metal 1}
}

proc sky130::ndiode_native_defaults {} {
    return {w 0.45 l 0.45 area 0.2024 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 doverlap 0 \
	full_metal 1}
}

proc sky130::pdiode_h_defaults {} {
    return {w 0.45 l 0.45 area 0.2024 peri 1.8 \
	nx 1 ny 1 dummy 0 lmin 0.45 wmin 0.45 \
	elc 1 erc 1 etc 1 ebc 1 \
	glc 1 grc 1 gtc 1 gbc 1 doverlap 0 \
	compatible {pdiode pdiode_h} full_metal 1}
}

#----------------------------------------------------------------

proc sky130::ndiode_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::ndiode_lvt_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::pdiode_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::pdiode_lvt_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::pdiode_hvt_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::ndiode_h_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::ndiode_native_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

proc sky130::pdiode_h_convert {parameters} {
    return [sky130::diode_convert $parameters]
}

#----------------------------------------------------------------

proc sky130::ndiode_dialog {parameters} {
    sky130::diode_dialog ndiode $parameters
}

proc sky130::ndiode_lvt_dialog {parameters} {
    sky130::diode_dialog ndiode_lvt $parameters
}

proc sky130::pdiode_dialog {parameters} {
    sky130::diode_dialog pdiode $parameters
}

proc sky130::pdiode_lvt_dialog {parameters} {
    sky130::diode_dialog pdiode_lvt $parameters
}

proc sky130::pdiode_hvt_dialog {parameters} {
    sky130::diode_dialog pdiode_hvt $parameters
}

proc sky130::ndiode_h_dialog {parameters} {
    sky130::diode_dialog ndiode_h $parameters
}

proc sky130::ndiode_native_dialog {parameters} {
    sky130::diode_dialog ndiode_native $parameters
}

proc sky130::pdiode_h_dialog {parameters} {
    sky130::diode_dialog pdiode_h $parameters
}

#----------------------------------------------------------------

proc sky130::ndiode_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::ndiode_lvt_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::pdiode_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::pdiode_lvt_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::pdiode_hvt_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::ndiode_h_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::ndiode_native_check {parameters} {
    sky130::diode_check $parameters
}

proc sky130::pdiode_h_check {parameters} {
    sky130::diode_check $parameters
}

#----------------------------------------------------------------
# Diode: Draw a single device
#----------------------------------------------------------------

proc sky130::diode_device {parameters} {
    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set dev_surround 0
    set dev_sub_type ""

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # If there is no end_sub_surround, set it to sub_surround
    if {![dict exists $parameters end_sub_surround]} {
	set end_sub_surround $sub_surround
    }

    # Draw the device
    pushbox
    box size 0 0

    set hw [/ $w 2.0]
    set hl [/ $l 2.0]

    # Calculate ring size (measured to contact center)
    set gx [+ $w [* 2.0 [+ $dev_spacing $dev_surround]] $contact_size]
    set gy [+ $l [* 2.0 [+ $dev_spacing $dev_surround]] $contact_size]

    # Draw the ring first, because diode may occupy well/substrate plane
    set guardparams $parameters
    dict set guardparams plus_diff_type $end_type
    dict set guardparams plus_contact_type $end_contact_type
    dict set guardparams diff_surround $end_surround
    dict set guardparams sub_type $end_sub_type
    dict set guardparams sub_surround $sub_surround
    dict set guardparams guard_sub_surround $end_sub_surround
    dict set guardparams glc $elc
    dict set guardparams grc $erc
    dict set guardparams gtc $etc
    dict set guardparams gbc $ebc
    set cext [sky130::guard_ring $gx $gy $guardparams]

    pushbox
    box grow n ${hl}um
    box grow s ${hl}um
    box grow e ${hw}um
    box grow w ${hw}um
    paint ${dev_type}
    set cext [sky130::unionbox $cext [sky130::getbox]]

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

    set cext [sky130::unionbox $cext [sky130::draw_contact ${w} ${l} \
		${dev_surround} ${metal_surround} ${contact_size} \
		${dev_type} ${dev_contact_type} li ${orient}]]

    popbox
    return $cext
}

#----------------------------------------------------------------
# Diode: Draw the tiled device
#----------------------------------------------------------------

proc sky130::diode_draw {parameters} {
    tech unlock *

    # Set defaults if they are not in parameters
    set doverlap 0	;# overlap diodes at contacts
    set guard 0		;# draw a guard ring
    set prohibit_overlap false  ;# don't prohibit overlaps

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
    set bbox [sky130::diode_device $parameters]
    # puts stdout "Diagnostic: Device bounding box e $bbox (um)"
    tech unlock *

    set fw [- [lindex $bbox 2] [lindex $bbox 0]]
    set fh [- [lindex $bbox 3] [lindex $bbox 1]]
    set lw [+ [lindex $bbox 2] [lindex $bbox 0]]
    set lh [+ [lindex $bbox 3] [lindex $bbox 1]]

    # If prohibit_overlap is true, then end overlapping is prohibited when
    # nx or ny is > 1 to prevent DRC errors (typically from well spacing rule)
    if {$prohibit_overlap == true} {
        if {($nx > 1) || ($ny > 1)} {
	    set doverlap 0
	}
    }

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
	sky130::guard_ring $gx $gy $parameters
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
	    sky130::diode_device $parameters
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

proc sky130::ndiode_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		ndiode \
	    dev_contact_type	ndic \
	    end_type		psd \
	    end_contact_type	psc \
	    end_sub_type	psub \
	    dev_spacing		${diff_spacing} \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	0 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
} 

#----------------------------------------------------------------
# NOTE:  Use ppd instead of psd so that there is additional
# diffusion around the contact, allowing more space for the
# implant (likewise pdiode_lvt and pdiode_hvt).

proc sky130::ndiode_lvt_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		ndiodelvt \
	    dev_contact_type	ndilvtc \
	    end_type		ppd \
	    end_contact_type	psc \
	    end_sub_type	psub \
	    dev_spacing		${diff_spacing} \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
} 

#----------------------------------------------------------------

proc sky130::pdiode_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		pdiode \
	    guard		1 \
	    dev_contact_type	pdic \
	    end_type		nsd \
	    end_contact_type	nsc \
	    end_sub_type	nwell \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    dev_spacing		${diff_spacing} \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	0 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::pdiode_lvt_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		pdiodelvt \
	    guard		1 \
	    dev_contact_type	pdilvtc \
	    end_type		nnd \
	    end_contact_type	nsc \
	    end_sub_type	nwell \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    dev_spacing		${diff_spacing} \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::pdiode_hvt_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		pdiodehvt \
	    guard		1 \
	    dev_contact_type	pdihvtc \
	    end_type		nnd \
	    end_contact_type	nsc \
	    end_sub_type	nwell \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    dev_spacing		${diff_spacing} \
	    dev_surround	${diff_surround} \
	    end_spacing		${diff_spacing} \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::ndiode_h_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		mvndiode \
	    dev_contact_type	mvndic \
	    end_type		mvpsd \
	    end_contact_type	mvpsc \
	    end_sub_type	psub \
	    diff_spacing	0.37 \
	    dev_spacing		0.39 \
	    dev_surround	${diff_surround} \
	    end_spacing		0.36 \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
}


proc sky130::ndiode_native_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    dev_type		nndiode \
	    dev_contact_type	nndic \
	    end_type		mvpsd \
	    end_contact_type	mvpsc \
	    end_sub_type	psub \
	    dev_spacing		0.37 \
	    dev_surround	${diff_surround} \
	    end_spacing		0.30 \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
} 


#----------------------------------------------------------------

proc sky130::pdiode_h_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		1 \
	    dev_type 		mvpdiode \
	    dev_contact_type	mvpdic \
	    end_type		mvnsd \
	    end_contact_type	mvnsc \
	    end_sub_type	nwell \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    sub_type		psub \
	    diff_spacing	0.58 \
	    dev_spacing		0.37 \
	    dev_surround	${diff_surround} \
	    end_spacing		0.30 \
	    end_sub_surround	0.33 \
	    end_surround	${diff_surround} \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::diode_draw $drawdict]
}

#----------------------------------------------------------------
# Drawn capactitor routines
# NOTE:  Work in progress.  These values need to be corrected.
#----------------------------------------------------------------

#ifdef MIM
proc sky130::xcmimc1_defaults {} {
    return {w 2.00 l 2.00 val 4.0 carea 1.00 cperi 0.17 \
		nx 1 ny 1 dummy 0 square 0 lmin 2.00 wmin 2.00 \
		lmax 30.0 wmax 30.0 dc 0 bconnect 1 tconnect 1}
}
proc sky130::xcmimc2_defaults {} {
    return {w 2.00 l 2.00 val 4.0 carea 1.00 cperi 0.17 \
		nx 1 ny 1 dummy 0 square 0 lmin 2.00 wmin 2.00 \
		lmax 30.0 wmax 30.0 dc 0 bconnect 1 tconnect 1}
}
#endif (MIM)


#----------------------------------------------------------------
# Recalculate capacitor values from GUI entries.
# Recomputes W/L and Value as long as 2 of them are present
# (To be completed)
#----------------------------------------------------------------

proc sky130::cap_recalc {field parameters} {
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

proc sky130::cap_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    l -
	    w {
		# Length and width are converted to units of microns
		set value [magic::spice2float $value]
		# set value [expr $value * 1e6]
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

#ifdef MIM
proc sky130::xcmimc1_convert {parameters} {
    return [cap_convert $parameters]
}
proc sky130::xcmimc2_convert {parameters} {
    return [cap_convert $parameters]
}
#endif (MIM)

#----------------------------------------------------------------
# capacitor: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc sky130::cap_dialog {device parameters} {
    # Editable fields:      w, l, nx, ny, val
    # Checked fields:  	    square, dummy

    magic::add_entry val "Value (fF)" $parameters
    sky130::compute_ctot $parameters
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
    if {[dict exists $parameters guard]} {
	magic::add_checkbox guard "Add guard ring" $parameters
    }

    magic::add_dependency sky130::cap_recalc $device sky130 l w val

    # magic::add_checkbox dummy "Add dummy" $parameters
}

#ifdef MIM
proc sky130::xcmimc1_dialog {parameters} {
    sky130::cap_dialog xcmimc1 $parameters
}
proc sky130::xcmimc2_dialog {parameters} {
    sky130::cap_dialog xcmimc2 $parameters
}
#endif (MIM)

#----------------------------------------------------------------
# Capacitor total capacitance computation
#----------------------------------------------------------------

proc sky130::compute_ctot {parameters} {
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

proc sky130::cap_device {parameters} {
    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set cap_surround 0
    set bot_surround 0
    set top_surround 0
    set bconnect 0	    ;# bottom plates are connected in array
    set cap_spacing 0	    ;# cap spacing in array
    set top_metal_space 0   ;# top metal spacing (if larger than cap spacing)

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    if {![dict exists $parameters top_metal_space]} {
	set top_metal_space $metal_spacing
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
    set cext [sky130::getbox]
    popbox
    popbox
    pushbox
    box grow n ${bot_surround}um
    box grow s ${bot_surround}um
    box grow e ${bot_surround}um
    box grow w ${bot_surround}um

    paint ${bot_type}
    # Create boundary using properties
    property FIXED_BBOX [box values]
    set cext [sky130::unionbox $cext [sky130::getbox]]

    # Extend bottom metal under contact to right
    box grow e ${end_spacing}um
    set chw [/ ${contact_size} 2.0]
    box grow e ${chw}um
    box grow e ${end_surround}um
    paint ${bot_type}

    popbox
    popbox

    # Draw contact to right.  Reduce contact extent if devices are not
    # wired together and the top metal spacing rule limits the distance
    set lcont $l
    if {($bconnect == 0) && ($ny > 1)} {
	if {$cap_spacing < $top_metal_space} {
	    set cspace [- $top_metal_space $cap_spacing]
	    set lcont [- $l $cspace]
	}
    }

    pushbox
    box move e ${hw}um
    box move e ${bot_surround}um
    box move e ${end_spacing}um
    set cl [- [+ ${lcont} [* ${bot_surround} 2.0]] [* ${end_surround} 2.0]]
    set cl [- ${cl} ${metal_surround}]  ;# see below
    set cext [sky130::unionbox $cext [sky130::draw_contact 0 ${cl} \
		${end_surround} ${metal_surround} ${contact_size} \
		${bot_type} ${top_contact_type} ${top_type} full]]
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

proc sky130::sandwich_cap_device {parameters} {

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
	    sky130::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox
	    pushbox
	    box move w ${hw}um
	    box move n ${hl}um
	    sky130::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox
	    pushbox
	    box move e ${hw}um
	    box move s ${hl}um
	    sky130::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox
	    pushbox
	    box move w ${hw}um
	    box move s ${hl}um
	    sky130::draw_contact 0 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
	    popbox

	    # Draw side contacts (except on poly)
	    if {$i > 0} {
		pushbox
		box move w ${hw}um
		sky130::draw_contact 0 ${cl} \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
		pushbox
		box move e ${hw}um
		sky130::draw_contact 0 ${cl} \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
		pushbox
		box move n ${hl}um
		sky130::draw_contact ${cw} 0 \
			${cont_surround} ${cont_surround} ${via_size} \
			${layer} ${contact} ${toplayer} full
		popbox
		pushbox
		box move s ${hl}um
		sky130::draw_contact ${cw} 0 \
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

proc sky130::cap_draw {parameters} {
    tech unlock *
    set savesnap [snap]
    snap internal

    # Set defaults if they are not in parameters
    set coverlap 0	;# overlap capacitors at contacts
    set guard 0		;# draw a guard ring
    set sandwich 0	;# this is not a plate sandwich capacitor
    set cap_spacing 0	;# abutted caps if spacing is zero
    set cap_diff_spacing 0
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
	set bbox [sky130::sandwich_cap_device $parameters]
    } else {
	set bbox [sky130::cap_device $parameters]
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
	sky130::guard_ring $gx $gy $parameters
    }

    set twidth [+ ${contact_size} ${end_surround} ${end_surround}]
    if {${twidth} < ${top_metal_width}} {
	set twidth ${top_metal_width}
    }
    set hmw [/ $twidth 2.0]
    set hdy [/ $dy 2.0]
    set cdx [+ [/ ${w} 2.0] ${bot_surround} ${end_spacing}]

    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    for {set xp 0} {$xp < $nx} {incr xp} {
	pushbox
	for {set yp 0} {$yp < $ny} {incr yp} {
	    if {$sandwich == 1} {
		sky130::sandwich_cap_device $parameters
	    } else {
		sky130::cap_device $parameters
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

    snap $savesnap
    tech revert
}

#----------------------------------------------------------------

#ifdef MIM
proc sky130::xcmimc1_draw {parameters} {
    set newdict [dict create \
	    top_type 		m4 \
	    top_contact_type	via3 \
	    cap_type 		mimcap \
	    cap_contact_type	mimcc \
	    bot_type 		m3 \
	    bot_surround	0.5 \
	    cap_spacing		0.5 \
	    cap_surround	0.2 \
	    top_surround	0.005 \
	    end_surround	0.1 \
	    end_spacing		0.60 \
	    contact_size	0.32 \
	    metal_surround	0.08 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::cap_draw $drawdict]
}

proc sky130::xcmimc2_draw {parameters} {
    set newdict [dict create \
	    top_type 		m5 \
	    top_contact_type	via4 \
	    cap_type 		mimcap2 \
	    cap_contact_type	mim2cc \
	    bot_type 		m4 \
	    bot_surround	0.5 \
	    cap_spacing		0.5 \
	    cap_surround	0.2 \
	    top_surround	0.12 \
	    end_surround	0.1 \
	    end_spacing		2.10 \
	    contact_size	1.18 \
	    metal_surround	0.21 \
	    top_metal_width	1.6 \
	    top_metal_space	1.7 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::cap_draw $drawdict]
}

#endif (MIM)

#----------------------------------------------------------------
# capacitor: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc sky130::cap_check {parameters} {
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
    sky130::compute_ctot $parameters

    return $parameters
}

#ifdef MIM
proc sky130::xcmimc1_check {parameters} {
    return [sky130::cap_check $parameters]
}
proc sky130::xcmimc2_check {parameters} {
    return [sky130::cap_check $parameters]
}
#endif (MIM)

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
#  snake Use snake geometry (if not present, snake geometry not allowed)
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
# xpwres: Specify all user-editable default values and those
# needed by xpwres_check
# NOTE:  Work in progress.  These values need to be corrected.
#----------------------------------------------------------------

proc sky130::xpwres_defaults {} {
    return {w 2.650 l 26.50 m 1 nx 1 wmin 2.650 lmin 26.50 \
	 	rho 975 val 4875 dummy 0 dw 0.25 term 1.0 \
		guard 1 endcov 100 full_metal 1}
}

#----------------------------------------------------------------
# rpp1: Specify all user-editable default values and those
# needed by rp1_check
#----------------------------------------------------------------

proc sky130::mrp1_defaults {} {
    return {w 0.330 l 1.650 m 1 nx 1 wmin 0.330 lmin 1.650 \
		rho 48.2 val 241 dummy 0 dw 0.0 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 guard 1 \
		glc 1 grc 1 gtc 1 gbc 1 roverlap 0 endcov 100 \
		full_metal 1}
}

# "term" is rho * 0.06, the distance between xpc edge and CONT.
proc sky130::xhrpoly_0p35_defaults {} {
    return {w 0.350 l 0.50 m 1 nx 1 wmin 0.350 lmin 0.50 \
		rho 319.8 val 456.857 dummy 0 dw 0.0 term 19.188 \
		sterm 0.0 caplen 0 guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {xhrpoly_0p35 xhrpoly_0p69 xhrpoly_1p41 \
		xhrpoly_2p85 xhrpoly_5p73} \
		full_metal 1 wmax 0.350}
}
proc sky130::xhrpoly_0p69_defaults {} {
    return {w 0.690 l 1.00 m 1 nx 1 wmin 0.690 lmin 0.50 \
		rho 319.8 val 463.480 dummy 0 dw 0.0 term 19.188 \
		sterm 0.0 caplen 0 guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {xhrpoly_0p35 xhrpoly_0p69 xhrpoly_1p41 \
		xhrpoly_2p85 xhrpoly_5p73} \
		full_metal 1 wmax 0.690}
}
proc sky130::xhrpoly_1p41_defaults {} {
    return {w 1.410 l 2.00 m 1 nx 1 wmin 1.410 lmin 0.50 \
		rho 319.8 val 453.620 dummy 0 dw 0.0 term 19.188 \
		sterm 0.0 caplen 0 guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {xhrpoly_0p35 xhrpoly_0p69 xhrpoly_1p41 \
		xhrpoly_2p85 xhrpoly_5p73} \
		full_metal 1 wmax 1.410}
}
proc sky130::xhrpoly_2p85_defaults {} {
    return {w 2.850 l 3.00 m 1 nx 1 wmin 2.850 lmin 0.50 \
		rho 319.8 val 336.630 dummy 0 dw 0.0 term 19.188 \
		sterm 0.0 caplen 0 guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {xhrpoly_0p35 xhrpoly_0p69 xhrpoly_1p41 \
		xhrpoly_2p85 xhrpoly_5p73} \
		full_metal 1 wmax 2.850}
}
proc sky130::xhrpoly_5p73_defaults {} {
    return {w 5.730 l 6.00 m 1 nx 1 wmin 5.730 lmin 0.50 \
		rho 319.8 val 334.870 dummy 0 dw 0.0 term 19.188 \
		sterm 0.0 caplen 0 guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {xhrpoly_0p35 xhrpoly_0p69 xhrpoly_1p41 \
		xhrpoly_2p85 xhrpoly_5p73} \
		full_metal 1 wmax 5.730}
}

# "term" is rho * 0.06, the distance between xpc edge and CONT.
proc sky130::uhrpoly_0p35_defaults {} {
    return {w 0.350 l 0.50 m 1 nx 1 wmin 0.350 lmin 0.50 \
		rho 2000 val 2875.143 dummy 0 dw 0.0 term 120 \
		sterm 0.0 caplen 0 wmax 0.350 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {uhrpoly_0p35 uhrpoly_0p69 uhrpoly_1p41 \
		uhrpoly_2p85 uhrpoly_5p73} full_metal 1}
}
proc sky130::uhrpoly_0p69_defaults {} {
    return {w 0.690 l 1.00 m 1 nx 1 wmin 0.690 lmin 0.50 \
		rho 2000 val 2898.600 dummy 0 dw 0.0 term 120 \
		sterm 0.0 caplen 0 wmax 0.690 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {uhrpoly_0p35 uhrpoly_0p69 uhrpoly_1p41 \
		uhrpoly_2p85 uhrpoly_5p73} full_metal 1}
}
proc sky130::uhrpoly_1p41_defaults {} {
    return {w 1.410 l 2.00 m 1 nx 1 wmin 1.410 lmin 0.50 \
		rho 2000 val 2836.900 dummy 0 dw 0.0 term 120 \
		sterm 0.0 caplen 0 wmax 1.410 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {uhrpoly_0p35 uhrpoly_0p69 uhrpoly_1p41 \
		uhrpoly_2p85 uhrpoly_5p73} full_metal 1}
}
proc sky130::uhrpoly_2p85_defaults {} {
    return {w 2.850 l 3.00 m 1 nx 1 wmin 2.850 lmin 0.50 \
		rho 2000 val 2105.300 dummy 0 dw 0.0 term 120 \
		sterm 0.0 caplen 0 wmax 2.850 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {uhrpoly_0p35 uhrpoly_0p69 uhrpoly_1p41 \
		uhrpoly_2p85 uhrpoly_5p73} full_metal 1}
}
proc sky130::uhrpoly_5p73_defaults {} {
    return {w 5.730 l 6.00 m 1 nx 1 wmin 5.730 lmin 0.50 \
		rho 2000 val 2094.200 dummy 0 dw 0.0 term 120 \
		sterm 0.0 caplen 0 wmax 5.730 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 \
		compatible {uhrpoly_0p35 uhrpoly_0p69 uhrpoly_1p41 \
		uhrpoly_2p85 uhrpoly_5p73} full_metal 1}
}

#----------------------------------------------------------------
# mrdn: Specify all user-editable default values and those
# needed by rdn_check
#----------------------------------------------------------------

proc sky130::mrdn_defaults {} {
    return {w 0.420 l 2.100 m 1 nx 1 wmin 0.42 lmin 2.10 \
		rho 120 val 600.0 dummy 0 dw 0.05 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 guard 1 \
		glc 1 grc 1 gtc 1 gbc 1 roverlap 0 endcov 100 \
		full_metal 1}
}

proc sky130::mrdn_hv_defaults {} {
    return {w 0.420 l 2.100 m 1 nx 1 wmin 0.42 lmin 2.10 \
		rho 120 val 600.0 dummy 0 dw 0.02 term 0.0 \
		sterm 0.0 caplen 0.4 snake 0 guard 1 \
		glc 1 grc 1 gtc 1 gbc 1 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# mrdp: Specify all user-editable default values and those
# needed by rdp_check
#----------------------------------------------------------------

proc sky130::mrdp_defaults {} {
    return {w 0.420 l 2.100 m 1 nx 1 wmin 0.42 lmin 2.10 \
		rho 197 val 985.0 dummy 0 dw 0.02 term 0.0 \
		sterm 0.0 caplen 0.60 snake 0 guard 1 \
		glc 1 grc 1 gtc 1 gbc 1 roverlap 0 endcov 100 \
		full_metal 1}
}

proc sky130::mrdp_hv_defaults {} {
    return {w 0.420 l 2.100 m 1 nx 1 wmin 0.42 lmin 2.10 \
		rho 197 val 985.0 dummy 0 dw 0.02 term 0.0 \
		sterm 0.0 caplen 0.60 snake 0 guard 1 \
		glc 1 grc 1 gtc 1 gbc 1 roverlap 0 endcov 100 \
		full_metal 1}
}

#----------------------------------------------------------------
# mrl1: Specify all user-editable default values and those needed
# by mrl1_check
#----------------------------------------------------------------

proc sky130::mrl1_defaults {} {
    return {w 0.170 l 0.170 m 1 nx 1 wmin 0.17 lmin 0.17 \
		rho 12.8 val 12.8 dummy 0 dw 0.0 term 0.0 snake 0 \
		roverlap 0}
}

#----------------------------------------------------------------
# mrm1: Specify all user-editable default values and those needed
# by mrm1_check
#----------------------------------------------------------------

proc sky130::mrm1_defaults {} {
    return {w 0.140 l 0.140 m 1 nx 1 wmin 0.14 lmin 0.14 \
		rho 0.125 val 0.125 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}

#----------------------------------------------------------------
# mrm2: Specify all user-editable default values and those needed
# by mrm2_check
#----------------------------------------------------------------

proc sky130::mrm2_defaults {} {
    return {w 0.140 l 0.140 m 1 nx 1 wmin 0.14 lmin 0.14 \
		rho 0.125 val 0.125 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}

#----------------------------------------------------------------
# mrm3: Specify all user-editable default values and those needed
# by mrm3_check
#----------------------------------------------------------------

proc sky130::mrm3_defaults {} {
    return {w 0.300 l 0.300 m 1 nx 1 wmin 0.30 lmin 0.30 \
		rho 0.047 val 0.047 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}

#----------------------------------------------------------------
# Additional entries for mrm4 and mrm5, depending on the
# back-end metal stack.
#----------------------------------------------------------------

#ifdef METAL5
proc sky130::mrm4_defaults {} {
    return {w 0.300 l 0.300 m 1 nx 1 wmin 0.30 lmin 0.30 \
		rho 0.047 val 0.047 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}
proc sky130::mrm5_defaults {} {
    return {w 1.600 l 1.600 m 1 nx 1 wmin 1.60 lmin 1.60 \
		rho 0.029 val 0.029 dummy 0 dw 0.0 term 0.0 \
		roverlap 0}
}
#endif (METAL5)

#----------------------------------------------------------------
# resistor: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc sky130::res_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    l -
	    w {
		# Length and width are converted to units of microns
		set value [magic::spice2float $value]
		# set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $key] $value
	    }
	}
    }
    return $pdkparams
}

#----------------------------------------------------------------

proc sky130::xpwres_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrp1_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::xhrpoly_0p35_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::xhrpoly_0p69_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::xhrpoly_1p41_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::xhrpoly_2p85_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::xhrpoly_5p73_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::uhrpoly_0p35_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::uhrpoly_0p69_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::uhrpoly_1p41_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::uhrpoly_2p85_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::uhrpoly_5p73_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrdn_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrdp_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrdn_hv_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrdp_hv_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrl1_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrm1_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrm2_convert {parameters} {
    return [sky130::res_convert $parameters]
}

proc sky130::mrm3_convert {parameters} {
    return [sky130::res_convert $parameters]
}

#ifdef METAL5
proc sky130::mrm4_convert {parameters} {
    return [sky130::res_convert $parameters]
}
proc sky130::mrm5_convert {parameters} {
    return [sky130::res_convert $parameters]
}
#endif (METAL5)

#----------------------------------------------------------------
# resistor: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc sky130::res_dialog {device parameters} {
    # Editable fields:      w, l, t, nx, m, val
    # Checked fields:  

    magic::add_entry val "Value (ohms)" $parameters
    if {[dict exists $parameters snake]} {
	sky130::compute_ltot $parameters
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
	magic::add_selectlist gencell "Device type" $sellist $parameters $device
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
    if {[dict exists $parameters guard]} {
	magic::add_checkbox guard "Add guard ring" $parameters

	if {[dict exists $parameters full_metal]} {
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
    }

    if {[dict exists $parameters snake]} {
       magic::add_dependency sky130::res_recalc $device sky130 l w val nx snake
    } else {
       magic::add_dependency sky130::res_recalc $device sky130 l w val nx
    }
}

#----------------------------------------------------------------

proc sky130::xpwres_dialog {parameters} {
    sky130::res_dialog xpwres $parameters
}

proc sky130::mrp1_dialog {parameters} {
    sky130::res_dialog mrp1 $parameters
}

proc sky130::xhrpoly_0p35_dialog {parameters} {
    sky130::res_dialog xhrpoly_0p35 $parameters
}
proc sky130::xhrpoly_0p69_dialog {parameters} {
    sky130::res_dialog xhrpoly_0p69 $parameters
}
proc sky130::xhrpoly_1p41_dialog {parameters} {
    sky130::res_dialog xhrpoly_1p41 $parameters
}
proc sky130::xhrpoly_2p85_dialog {parameters} {
    sky130::res_dialog xhrpoly_2p85 $parameters
}
proc sky130::xhrpoly_5p73_dialog {parameters} {
    sky130::res_dialog xhrpoly_5p73 $parameters
}

proc sky130::uhrpoly_0p35_dialog {parameters} {
    sky130::res_dialog uhrpoly_0p35 $parameters
}
proc sky130::uhrpoly_0p69_dialog {parameters} {
    sky130::res_dialog uhrpoly_0p69 $parameters
}
proc sky130::uhrpoly_1p41_dialog {parameters} {
    sky130::res_dialog uhrpoly_1p41 $parameters
}
proc sky130::uhrpoly_2p85_dialog {parameters} {
    sky130::res_dialog uhrpoly_2p85 $parameters
}
proc sky130::uhrpoly_5p73_dialog {parameters} {
    sky130::res_dialog uhrpoly_5p73 $parameters
}

proc sky130::mrdn_dialog {parameters} {
    sky130::res_dialog mrdn $parameters
}

proc sky130::mrdp_dialog {parameters} {
    sky130::res_dialog mrdp $parameters
}

proc sky130::mrdn_hv_dialog {parameters} {
    sky130::res_dialog mrdn_hv $parameters
}

proc sky130::mrdp_hv_dialog {parameters} {
    sky130::res_dialog mrdp_hv $parameters
}

proc sky130::mrl1_dialog {parameters} {
    sky130::res_dialog mrl1 $parameters
}

proc sky130::mrm1_dialog {parameters} {
    sky130::res_dialog mrm1 $parameters
}

proc sky130::mrm2_dialog {parameters} {
    sky130::res_dialog mrm2 $parameters
}

proc sky130::mrm3_dialog {parameters} {
    sky130::res_dialog mrm3 $parameters
}

#ifdef METAL5
proc sky130::mrm4_dialog {parameters} {
    sky130::res_dialog mrm4 $parameters
}
proc sky130::mrm5_dialog {parameters} {
    sky130::res_dialog mrm5 $parameters
}
#endif (METAL5)

#----------------------------------------------------------------
# Resistor: Draw a single device in straight geometry
#----------------------------------------------------------------

proc sky130::res_device {parameters} {
    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set endcov 0	 	;# percent coverage of end contacts
    set roverlap 0		;# overlap resistors at end contacts
    set well_res_overlap 0 	;# not a well resistor
    set end_contact_type ""	;# no contacts for metal resistors
    set end_overlap_cont 0	;# additional end overlap on sides
    set res_idtype none

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    if {![dict exists $parameters end_contact_size]} {
	set end_contact_size $contact_size
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
	set well_extend [+ ${well_res_overlap} [/ ${end_contact_size} 2.0] ${end_surround}]
	box grow n ${well_extend}um
	box grow s ${well_extend}um
	paint ${well_res_type}
    } else {
	paint ${end_type}
    }
    set cext [sky130::getbox]
    popbox

    if {$well_res_overlap > 0} {
	erase ${well_res_type}
    } else {
	erase ${end_type}
    }
    paint ${res_type}
    if {"$res_idtype" != "none"} {
	box grow c 2
	paint ${res_idtype}
    }
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

    # Ensure additional overlap of diffusion contact if required
    set dov [* ${end_overlap_cont} 2]
    if {[- ${epl} ${cpl}] < $dov} {
	set cpl [- ${epl} $dov]    ;# additional end contact width
    }

    set hepl [+ [/ ${epl} 2.0] ${end_surround}]
    set hesz [/ ${end_contact_size} 2.0]

    # LV substrate diffusion types have a different surround requirement
    set lv_sub_types {"psd" "nsd"}
    if {[lsearch $lv_sub_types $end_type] < 0} {
	set hesz [+ ${hesz} ${end_surround}]
    }

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
    set cext [sky130::unionbox $cext [sky130::getbox]]
    popbox

    if {${end_contact_type} != ""} {
	set cext [sky130::unionbox $cext [sky130::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${end_contact_size} \
		${end_type} ${end_contact_type} li horz]]
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
    set cext [sky130::unionbox $cext [sky130::getbox]]
    popbox

    if {${end_contact_type} != ""} {
	set cext [sky130::unionbox $cext [sky130::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${end_contact_size} \
		${end_type} ${end_contact_type} li horz]]
    }
    popbox

    popbox
    return $cext
}

#----------------------------------------------------------------
# Resistor: Draw a single device in snake geometry
#----------------------------------------------------------------

proc sky130::res_snake_device {nf parameters} {
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

    if {![dict exists $parameters end_contact_size]} {
	set end_contact_size $contact_size
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
    set hesz [+ [/ ${end_contact_size} 2.0] ${end_surround}]

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
    set cext [sky130::getbox]
    popbox

    if {${end_contact_type} != ""} {
	set cext [sky130::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${end_contact_size} \
		${end_type} ${end_contact_type} li horz]
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
	set well_extend [+ ${well_res_overlap} [/ ${end_contact_size} 2.0] ${end_surround}]
	box grow s ${well_extend}um
	paint ${well_res_type}
    } else {
	paint ${end_type}
    }
    set cext [sky130::unionbox $cext [sky130::getbox]]
    popbox

    # Draw the resistor and endcaps
    pushbox
    box grow n ${hl}um
    box grow s ${hl}um
    box grow e ${hw}um
    box grow w ${hw}um

    # Capture these extents in the bounding box in case both contacts
    # are on one side.
    set cext [sky130::unionbox $cext [sky130::getbox]]

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
    set cext [sky130::unionbox $cext [sky130::getbox]]
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
    set cext [sky130::unionbox $cext [sky130::getbox]]
    popbox

    if {${end_contact_type} != ""} {
	set cext [sky130::unionbox $cext [sky130::draw_contact ${cpl} 0 \
		${end_surround} ${metal_surround} ${end_contact_size} \
		${end_type} ${end_contact_type} li horz]]
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
	set well_extend [+ ${well_res_overlap} [/ ${end_contact_size} 2.0] ${end_surround}]
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

proc sky130::res_draw {parameters} {
    tech unlock *
    set savesnap [snap]
    snap internal

    # Set defaults if they are not in parameters
    set snake 0		;# some resistors don't allow snake geometry
    set roverlap 0	;# overlap resistors at contacts
    set guard 0		;# draw a guard ring
    set plus_diff_type   nsd	;# guard ring diffusion type
    set overlap_compress 0	;# special Y distance compression
    set well_res_overlap 0	;# additional well extension behind contact
    set res_diff_spacing 0	;# spacing from resistor to diffusion
    set res_idtype  none

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # For devices where inter-device space is smaller than device-to-guard ring
    if {![dict exists $parameters end_to_end_space]} {
	set end_to_end_space $end_spacing
    }

    if {![dict exists $parameters end_contact_size]} {
	set end_contact_size $contact_size
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
	set bbox [sky130::res_snake_device $nf $parameters]
	set nx 1
    } else {
	set bbox [sky130::res_device $parameters]
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
        set dy [- $fh [+ [* [+ $end_surround $well_res_overlap] 2.0] $end_contact_size]]
    }
    set dx [+ $fw $res_spacing]

    # Determine core width and height
    set corex [+ [* [- $nx 1] $dx] $fw]
    set corey [+ [* [- $m 1] $dy] $fh]
    set corellx [/ [+ [- $corex $fw] $lw] 2.0]
    set corelly [/ [+ [- $corey $fh] $lh] 2.0]

    set lv_sub_types {"psd" "nsd"}
    if {[lsearch $lv_sub_types $plus_diff_type] >= 0} {
	set guard_diff_surround 0
    } else {
	set guard_diff_surround ${diff_surround}
    }

    if {$guard != 0} {
	# Calculate guard ring size (measured to contact center)
	set gx [+ $corex [* 2.0 [+ $res_diff_spacing $guard_diff_surround]] $contact_size]
	set gy [+ $corey [* 2.0 [+ $end_spacing $guard_diff_surround]] $contact_size]

	# Draw the guard ring first, because well resistors are on the substrate plane
	sky130::guard_ring $gx $gy $parameters
    }

    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    # puts "Device position at = [sky130::getbox]"
    for {set xp 0} {$xp < $nx} {incr xp} {
	pushbox
	for {set yp 0} {$yp < $m} {incr yp} {
	    if {$snake == 1} {
		sky130::res_snake_device $nf $parameters
	    } else {
		sky130::res_device $parameters
	    }
            box move n ${dy}um
        }
	popbox
        box move e ${dx}um
    }
    popbox
    popbox

    snap $savesnap
    tech revert
}

#----------------------------------------------------------------

proc sky130::mrp1_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		npres \
	    end_type 		poly \
	    end_contact_type	pc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		nwell \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    res_to_endcont	$res_to_cont \
	    res_spacing		$poly_spacing \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::xhrpoly_0p35_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		ppres \
	    res_idtype		res0p35 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::xhrpoly_0p69_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		ppres \
	    res_idtype		res0p69 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::xhrpoly_1p41_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		ppres \
	    res_idtype		res1p41 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::xhrpoly_2p85_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		ppres \
	    res_idtype		res2p85 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::xhrpoly_5p73_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		ppres \
	    res_idtype		res5p73 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::uhrpoly_0p35_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		xpres \
	    res_idtype		res0p35 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::uhrpoly_0p69_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		xpres \
	    res_idtype		res0p69 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::uhrpoly_1p41_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		xpres \
	    res_idtype		res1p41 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::uhrpoly_2p85_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		xpres \
	    res_idtype		res2p85 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::uhrpoly_5p73_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		xpres \
	    res_idtype		res5p73 \
	    end_type 		xpc \
	    end_contact_type	xpc \
	    end_contact_size	0 \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$poly_surround \
	    end_spacing		0.48 \
	    end_to_end_space	0.52 \
	    end_contact_size	0.19 \
	    res_to_endcont	1.985 \
	    res_spacing		1.24 \
	    res_diff_spacing	0.48 \
	    mask_clearance	0.52 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrdn_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		rdn \
	    end_type 		ndiff \
	    end_contact_type	ndc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    sub_type		psub \
	    end_surround	$diff_surround \
	    end_spacing		0.44 \
	    res_to_endcont	0.37 \
	    res_spacing		0.30 \
	    res_diff_spacing	0.44 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrdn_hv_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		mvrdn \
	    end_type 		mvndiff \
	    end_contact_type	mvndc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    sub_type		psub \
	    end_surround	$diff_surround \
	    end_spacing		0.44 \
	    res_to_endcont	0.37 \
	    res_spacing		0.30 \
	    res_diff_spacing	0.44 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrdp_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		rdp \
	    end_type 		pdiff \
	    end_contact_type	pdc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		nwell \
	    end_surround	$diff_surround \
	    end_spacing		0.44 \
	    res_to_endcont	0.37 \
	    res_spacing		$diff_spacing \
	    res_diff_spacing	0.44 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrdp_hv_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    res_type		mvrdp \
	    end_type 		mvpdiff \
	    end_contact_type	mvpdc \
	    plus_diff_type	mvnsd \
	    plus_contact_type	mvnsc \
	    sub_type		nwell \
	    end_surround	$diff_surround \
	    guard_sub_surround	0.33 \
	    end_spacing		0.44 \
	    res_to_endcont	0.37 \
	    res_spacing		0.30 \
	    res_diff_spacing	0.44 \
	    mask_clearance	0.22 \
	    overlap_compress	0.36 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::xpwres_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    well_res_type	pwell \
	    res_type		rpw \
	    end_type 		psd \
	    end_contact_type	psc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    sub_type		dnwell \
	    sub_surround	0.23 \
	    guard_sub_type	nwell \
	    guard_sub_surround	0.63 \
	    end_surround	$diff_surround \
	    end_spacing		0.63 \
	    end_to_end_space	1.15 \
	    end_overlap_cont	0.06 \
	    end_contact_size	0.53 \
	    overlap_compress	-0.17 \
	    res_to_endcont	0.265 \
	    res_spacing		1.4 \
	    res_diff_spacing	0.63 \
	    well_res_overlap	0.2 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrl1_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rli \
	    end_type 		li \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    res_to_endcont	0.2 \
	    end_to_end_space	0.23 \
	    res_spacing		$metal_spacing \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrm1_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm1 \
	    end_type 		m1 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    end_to_end_space	0.28 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrm2_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm2 \
	    end_type 		m2 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    end_to_end_space	0.28 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

proc sky130::mrm3_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm3 \
	    end_type 		m3 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    end_to_end_space	0.28 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

#----------------------------------------------------------------

#ifdef METAL5
proc sky130::mrm4_draw {parameters} {

    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm4 \
	    end_type 		m4 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    end_to_end_space	0.28 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}

proc sky130::mrm5_draw {parameters} {
    # Set a local variable for each rule in ruleset
    foreach key [dict keys $sky130::ruleset] {
        set $key [dict get $sky130::ruleset $key]
    }

    set newdict [dict create \
	    guard		0 \
	    res_type		rm5 \
	    end_type 		m5 \
	    end_surround	0.0 \
	    end_spacing		0.0 \
	    end_to_end_space	1.6 \
	    res_to_endcont	0.2 \
	    res_spacing		$mmetal_spacing \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::res_draw $drawdict]
}
#endif (METAL5)

#----------------------------------------------------------------
# Resistor total length computation
#----------------------------------------------------------------

proc sky130::compute_ltot {parameters} {
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

proc sky130::res_check {device parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    set snake 0
    set sterm 0.0
    set caplen 0
    set wmax 0

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
    if {$wmax > 0 && $w > $wmax} {
	puts stderr "Resistor width must be <= $wmax um"
	dict set parameters w $wmax
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
    sky130::compute_ltot $parameters
    return $parameters
}

#----------------------------------------------------------------

proc sky130::xpwres_check {parameters} {
    return [sky130::res_check xpwres $parameters]
}

proc sky130::mrp1_check {parameters} {
    return [sky130::res_check mrp1 $parameters]
}

proc sky130::xhrpoly_0p35_check {parameters} {
    return [sky130::res_check xhrpoly_0p35 $parameters]
}
proc sky130::xhrpoly_0p69_check {parameters} {
    return [sky130::res_check xhrpoly_0p69 $parameters]
}
proc sky130::xhrpoly_1p41_check {parameters} {
    return [sky130::res_check xhrpoly_1p41 $parameters]
}
proc sky130::xhrpoly_2p85_check {parameters} {
    return [sky130::res_check xhrpoly_2p85 $parameters]
}
proc sky130::xhrpoly_5p73_check {parameters} {
    return [sky130::res_check xhrpoly_5p73 $parameters]
}

proc sky130::uhrpoly_0p35_check {parameters} {
    return [sky130::res_check uhrpoly_0p35 $parameters]
}
proc sky130::uhrpoly_0p69_check {parameters} {
    return [sky130::res_check uhrpoly_0p69 $parameters]
}
proc sky130::uhrpoly_1p41_check {parameters} {
    return [sky130::res_check uhrpoly_1p41 $parameters]
}
proc sky130::uhrpoly_2p85_check {parameters} {
    return [sky130::res_check uhrpoly_2p85 $parameters]
}
proc sky130::uhrpoly_5p73_check {parameters} {
    return [sky130::res_check uhrpoly_5p73 $parameters]
}

proc sky130::mrdn_check {parameters} {
    return [sky130::res_check mrdn $parameters]
}

proc sky130::mrdp_check {parameters} {
    return [sky130::res_check mrdp $parameters]
}

proc sky130::mrdn_hv_check {parameters} {
    return [sky130::res_check mrdn_hv $parameters]
}

proc sky130::mrdp_hv_check {parameters} {
    return [sky130::res_check mrdp_hv $parameters]
}

proc sky130::mrl1_check {parameters} {
    return [sky130::res_check mrl1 $parameters]
}

proc sky130::mrm1_check {parameters} {
    return [sky130::res_check mrm1 $parameters]
}

proc sky130::mrm2_check {parameters} {
    return [sky130::res_check mrm2 $parameters]
}

proc sky130::mrm3_check {parameters} {
    return [sky130::res_check mrm3 $parameters]
}

#ifdef METAL5
proc sky130::mrm4_check {parameters} {
    return [sky130::res_check mrm4 $parameters]
}
proc sky130::mrm5_check {parameters} {
    return [sky130::res_check mrm5 $parameters]
}
#endif (METAL5)

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
# needed by mos_check
#----------------------------------------------------------------

proc sky130::pshort_defaults {} {
    return {w 0.42 l 0.15 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 \
		compatible {pshort plowvt phighvt phv} full_metal 1}
}

proc sky130::plowvt_defaults {} {
    return {w 0.42 l 0.35 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.35 wmin 0.42 \
		compatible {pshort plowvt phighvt phv} full_metal 1}
}

proc sky130::phighvt_defaults {} {
    return {w 0.42 l 0.15 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 \
		compatible {pshort plowvt phighvt phv} full_metal 1}
}

proc sky130::phv_defaults {} {
    return {w 0.42 l 0.50 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.50 wmin 0.42 \
		compatible {pshort plowvt phighvt phv} full_metal 1}
}

#----------------------------------------------------------------
# nmos: Specify all user-editable default values and those
# needed by mos_check
#----------------------------------------------------------------

proc sky130::nshort_defaults {} {
    return {w 0.420 l 0.150 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 \
		compatible {nshort nlowvt sonos_e nhv nhvnative} full_metal 1}
}

proc sky130::nlowvt_defaults {} {
    return {w 0.420 l 0.150 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 \
		compatible {nshort nlowvt sonos_e nhv nhvnative} full_metal 1}
}

proc sky130::sonos_e_defaults {} {
    return {w 0.420 l 0.150 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.15 wmin 0.42 \
		compatible {nshort nlowvt sonos_e nhv nhvnative} full_metal 1}
}

proc sky130::nhv_defaults {} {
    return {w 0.42 l 0.50 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.50 wmin 0.42 \
		compatible {nshort nlowvt sonos_e nhv nhvnative} full_metal 1}
}

proc sky130::nhvnative_defaults {} {
    return {w 0.42 l 0.50 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.50 wmin 0.42 \
		compatible {nshort nlowvt sonos_e nhv nhvnative} full_metal 1}
}

#----------------------------------------------------------------
# mos varactor: Specify all user-editable default values and those
# needed by mosvc_check
#----------------------------------------------------------------

proc sky130::xcnwvc_defaults {} {
    return {w 1.0 l 0.18 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.18 wmin 1.0 \
		compatible {xcnwvc xcnwvc2 xchvnwc} full_metal 1}
}

proc sky130::xcnwvc2_defaults {} {
    return {w 1.0 l 0.18 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.18 wmin 1.0 \
		compatible {xcnwvc xcnwvc2 xchvnwc} full_metal 1}
}

proc sky130::xchvnwc_defaults {} {
    return {w 1.0 l 0.50 m 1 nf 1 diffcov 100 polycov 100 \
		guard 1 glc 1 grc 1 gtc 1 gbc 1 tbcov 100 rlcov 100 \
		topc 1 botc 1 poverlap 0 doverlap 1 lmin 0.50 wmin 1.0 \
		compatible {xcnwvc xcnwvc2 xchvnwc} full_metal 1}
}

#----------------------------------------------------------------
# mos: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc sky130::mos_convert {parameters} {
    set pdkparams [dict create]
    dict for {key value} $parameters {
	switch -nocase $key {
	    l -
	    w {
		# Length and width are converted to units of microns
		set value [magic::spice2float $value]
		# set value [expr $value * 1e6]
		set value [magic::3digitpastdecimal $value]
		dict set pdkparams [string tolower $key] $value
	    }
	    m {
		dict set pdkparams [string tolower $key] $value
	    }
	    nf {
		# Adjustment ot W will be handled below
		dict set pdkparams [string tolower $key] $value
	    }
	}
    }

    # Magic does not understand "nf" as a parameter, but expands to
    # "nf" number of devices connected horizontally.  The "w" value
    # must be divided down accordingly, as the "nf" parameter implies
    # that the total width "w" is divided into "nf" fingers.

    catch {
	set w [dict get $pdkparams w]
	set nf [dict get $pdkparams nf]
	if {$nf > 1} {
	    dict set pdkparams w [expr $w / $nf]
	}
    }

    return $pdkparams
}

#----------------------------------------------------------------

proc sky130::nshort_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::nlowvt_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::sonos_e_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::nhv_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::nhvnative_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::pshort_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::plowvt_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::phighvt_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::phv_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::xcnwvc_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::xcnwvc2_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

proc sky130::xchvnwc_convert {parameters} {
    return [sky130::mos_convert $parameters]
}

#----------------------------------------------------------------
# mos: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc sky130::mos_dialog {device parameters} {
    # Editable fields:      w, l, nf, m, diffcov, polycov
    # Checked fields:  topc, botc
    # For specific devices, gate type is a selection list

    magic::add_entry w "Width (um)" $parameters
    magic::add_entry l "Length (um)" $parameters
    magic::add_entry nf "Fingers" $parameters
    magic::add_entry m "M" $parameters

    if {[dict exists $parameters compatible]} {
       set sellist [dict get $parameters compatible]
       magic::add_selectlist gencell "Device type" $sellist $parameters $device
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

proc sky130::nshort_dialog {parameters} {
    sky130::mos_dialog nshort $parameters
}

proc sky130::nlowvt_dialog {parameters} {
    sky130::mos_dialog nlowvt $parameters
}

proc sky130::sonos_e_dialog {parameters} {
    sky130::mos_dialog sonos_e $parameters
}

proc sky130::nhv_dialog {parameters} {
    sky130::mos_dialog nhv $parameters
}

proc sky130::nhvnative_dialog {parameters} {
    sky130::mos_dialog nhvnative $parameters
}

proc sky130::pshort_dialog {parameters} {
    sky130::mos_dialog pshort $parameters
}

proc sky130::plowvt_dialog {parameters} {
    sky130::mos_dialog plowvt $parameters
}

proc sky130::phighvt_dialog {parameters} {
    sky130::mos_dialog phighvt $parameters
}

proc sky130::phv_dialog {parameters} {
    sky130::mos_dialog phv $parameters
}

proc sky130::xcnwvc_dialog {parameters} {
    sky130::mos_dialog xcnwvc $parameters
}

proc sky130::xcnwvc2_dialog {parameters} {
    sky130::mos_dialog xcnwvc2 $parameters
}

proc sky130::xchvnwc_dialog {parameters} {
    sky130::mos_dialog xchvnwc $parameters
}

#----------------------------------------------------------------
# getbox:  Get the current cursor box, in microns
#----------------------------------------------------------------

proc sky130::getbox {} {
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

proc sky130::unionbox {box1 box2} {
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

proc sky130::draw_contact {w h s o x atype ctype mtype {orient vert}} {

    # Draw a minimum-size diff contact centered at current position
    # w is width, h is height.  Minimum size ensured.
    # x is contact size
    # s is contact diffusion (or poly) surround
    # o is contact metal surround
    # atype is active (e.g., ndiff) or bottom metal if a via
    # ctype is contact (e.g., ndc)
    # mtype is metal (e.g., m1) or top metal if a via
    # orient is the orientation of the contact

    # Set orientations for the bottom material based on material type.
    # Substrate diffusions (tap) need not overlap the contact in all
    # directions, but other (diff) types do.  The metal (local
    # interconnect) layer always overlaps in two directions only.

    set lv_sub_types {"psd" "nsd"}
    if {[lsearch $lv_sub_types $atype] >= 0} {
	set aorient $orient
    } else {
	set aorient "full"
    }

    pushbox
    box size 0 0
    if {$w < $x} {set w $x}
    if {$h < $x} {set h $x}
    set hw [/ $w 2.0]
    set hh [/ $h 2.0]
    box grow n ${hh}um
    box grow s ${hh}um
    box grow e ${hw}um
    box grow w ${hw}um
    paint ${ctype}
    pushbox
    # Bottom layer surrounded on sides as declared by aorient
    if {($aorient == "vert") || ($aorient == "full")} {
	box grow n ${s}um
	box grow s ${s}um
    }
    if {($aorient == "horz") || ($aorient == "full")} {
	box grow e ${s}um
	box grow w ${s}um
    }
    paint ${atype}
    set extents [sky130::getbox]
    popbox
    # Top layer surrounded on sides as declared by orient
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

proc sky130::guard_ring {gw gh parameters} {

    # Set local default values if they are not in parameters
    set rlcov 100	;# Right-left contact coverage percentage
    set tbcov 100	;# Top-bottom contact coverage percentage
    set grc 1		;# Draw right side contact
    set glc 1		;# Draw left side contact
    set gtc 1		;# Draw right side contact
    set gbc 1		;# Draw left side contact
    set full_metal 1	;# Draw full (continuous) metal ring
    set guard_sub_type	 pwell	;# substrate type under guard ring
    set guard_sub_surround  0	;# substrate type surrounds guard ring
    set plus_diff_type   nsd	;# guard ring diffusion type
    set plus_contact_type nsc	;# guard ring diffusion contact type
    set sub_type	 pwell	;# substrate type

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Set guard_sub_type to sub_type if it is not defined
    if {![dict exists $parameters guard_sub_type]} {
	set guard_sub_type $sub_type
    }

    set hx [/ $contact_size 2.0]
    set hw [/ $gw 2.0]
    set hh [/ $gh 2.0]

    # Watch for (LV) substrate diffusion types, which have a different
    # contact surround amount depending on the direction

    set lv_sub_types {"psd" "nsd"}
    if {[lsearch $lv_sub_types $plus_diff_type] >= 0} {
	set diff_surround 0
    }

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
    if {$guard_sub_surround > 0} {
	box grow c ${guard_sub_surround}um
	paint $guard_sub_type
    }
    popbox
    pushbox
    box move s ${hh}um
    box grow n ${hdifft}um
    box grow s ${hdifft}um
    box grow e ${hdiffw}um
    box grow w ${hdiffw}um
    paint $plus_diff_type
    if {$guard_sub_surround > 0} {
	box grow c ${guard_sub_surround}um
	paint $guard_sub_type
    }
    popbox
    pushbox
    box move e ${hw}um
    box grow e ${hdifft}um
    box grow w ${hdifft}um
    box grow n ${hdiffh}um
    box grow s ${hdiffh}um
    paint $plus_diff_type
    if {$guard_sub_surround > 0} {
	box grow c ${guard_sub_surround}um
	paint $guard_sub_type
    }
    popbox
    pushbox
    box move w ${hw}um
    box grow e ${hdifft}um
    box grow w ${hdifft}um
    box grow n ${hdiffh}um
    box grow s ${hdiffh}um
    paint $plus_diff_type
    if {$guard_sub_surround > 0} {
	box grow c ${guard_sub_surround}um
	paint $guard_sub_type
    }
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
	paint li
	popbox
	pushbox
	box move s ${hh}um
	box grow n ${hx}um
	box grow s ${hx}um
	box grow e ${hmetw}um
	box grow w ${hmetw}um
	paint li
	popbox
	pushbox
	box move e ${hw}um
	box grow e ${hx}um
	box grow w ${hx}um
	box grow n ${hmeth}um
	box grow s ${hmeth}um
	paint li
	popbox
	pushbox
	box move w ${hw}um
	box grow e ${hx}um
	box grow w ${hx}um
	box grow n ${hmeth}um
	box grow s ${hmeth}um
	paint li
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
            sky130::draw_contact $cw 0 $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type li horz
            popbox
	}
	if {$gbc == 1} {
	    pushbox
	    box move s ${hh}um
	    sky130::draw_contact $cw 0 $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type li horz
	    popbox
	}
    }
    if {$rlcov > 0.0} {
        if {$grc == 1} {
            pushbox
            box move e ${hw}um
            sky130::draw_contact 0 $ch $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type li vert
            popbox
        }
        if {$glc == 1} {
            pushbox
            box move w ${hw}um
            sky130::draw_contact 0 $ch $diff_surround $metal_surround \
		$contact_size $plus_diff_type $plus_contact_type li vert
            popbox
        }
    }

    pushbox
    box grow e ${hw}um
    box grow w ${hw}um
    box grow n ${hh}um
    box grow s ${hh}um
    # Create boundary using properties
    property FIXED_BBOX [box values]
    box grow c ${hx}um  ;# to edge of contact
    box grow c ${diff_surround}um  ;# to edge of diffusion
    box grow c ${sub_surround}um  ;# sub/well overlap of diff (NOT guard_sub)
    paint $sub_type
    set cext [sky130::getbox]
    popbox
    popbox

    return $cext
}

#----------------------------------------------------------------
# MOSFET: Draw a single device
#----------------------------------------------------------------

proc sky130::mos_device {parameters} {

    # Epsilon for avoiding round-off errors
    set eps  0.0005

    # Set local default values if they are not in parameters
    set diffcov 100	;# percent coverage of diffusion contact
    set polycov 100	;# percent coverage of poly contact
    set topc 1		;# draw top poly contact
    set botc 1		;# draw bottom poly contact
    set evenodd 1	;# even or odd numbered device finger, in X
    set dev_sub_type ""	;# device substrate type (if different from guard ring)
    set min_effl 0	;# gate length below which finger pitch must be stretched
    set diff_overlap_cont 0	;# extra overlap of end contact by diffusion

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
    set he [/ $min_effl 2.0]
    if {$nf == 1 || $he < $hl} {set he $hl}
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
    set cext [sky130::getbox]
    popbox
    # save gate area now and paint later, so that diffusion surrounding the
    # contact does not paint over the gate area, in case the gate type is
    # not part of a "compose" entry in the techfile.
    set gaterect [box values]
    popbox

    # Adjust position of contacts for dogbone geometry
    # Rule 1: Minimize diffusion length.  Contacts only move out
    # if width <  contact diffusion height.  They move out enough
    # that the diffusion-to-poly spacing is satisfied.

    set ddover 0
    set cdwmin [+ ${contact_size} [* ${diff_surround} 2]]
    set cstem [- ${gate_to_diffcont} [/ ${cdwmin} 2.0]]
    set cgrow [- ${diff_poly_space} ${cstem}]
    if {[+ ${w} ${eps}] < ${cdwmin}} {
        if {${cgrow} > 0} {
            set gate_to_diffcont [+ ${gate_to_diffcont} ${cgrow}]
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
    # poly out further to clear spacing to the diffusion contact

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
    set tsurround [+ ${diff_surround} ${diff_overlap_cont}]
    set cdw [- ${w} [* ${tsurround} 2]]		;# diff contact height
    set cpl [- ${l} [* ${poly_surround} 2]]     ;# poly contact width

    # Reduce by coverage percentage.  NOTE:  If overlapping multiple devices,
    # keep maximum poly contact coverage.

    set cdw [* ${cdw} [/ ${diffcov} 100.0]]
    if {($poverlap == 0) || ($m == 1)} {
	set cpl [* ${cpl} [/ ${polycov} 100.0]]
    }

    # Right diffusion contact
    pushbox
    box move e ${he}um
    box move e ${gate_to_diffcont}um
    set cext [sky130::unionbox $cext [sky130::draw_contact 0 ${cdw} \
		${diff_surround} ${metal_surround} ${contact_size}\
		${diff_type} ${diff_contact_type} li vert]]
    popbox
    # Left diffusion contact
    pushbox
    box move w ${he}um
    box move w ${gate_to_diffcont}um
    set cext [sky130::unionbox $cext [sky130::draw_contact 0 ${cdw} \
		${diff_surround} ${metal_surround} ${contact_size} \
		${diff_type} ${diff_contact_type} li vert]]
    set diffarea $cext
    popbox
    # Top poly contact
    if {$topc} {
       pushbox
       box move n ${hw}um
       box move n ${gate_to_polycont}um
       set cext [sky130::unionbox $cext [sky130::draw_contact ${cpl} 0 \
		${poly_surround} ${metal_surround} ${contact_size} \
		${poly_type} ${poly_contact_type} li horz]]
       popbox
    }
    # Bottom poly contact
    if {$botc} {
       pushbox
       box move s ${hw}um
       box move s ${gate_to_polycont}um
       set cext [sky130::unionbox $cext [sky130::draw_contact ${cpl} 0 \
		${poly_surround} ${metal_surround} ${contact_size} \
		${poly_type} ${poly_contact_type} li horz]]
       popbox
    }

    # Now draw the gate, after contacts have been drawn
    pushbox
    box values {*}${gaterect}
    # gate_type need not be defined if poly over diff paints the right type.
    catch {paint ${gate_type}}
    # sub_surround_dev, if defined, may create a larger area around the gate
    # than sub_surround creates around the diffusion/poly area.
    if [dict exists $parameters sub_surround_dev] {
	box grow n ${sub_surround_dev}um
	box grow s ${sub_surround_dev}um
	box grow e ${sub_surround_dev}um
	box grow w ${sub_surround_dev}um
	paint ${dev_sub_type}
	set cext [sky130::unionbox $cext [sky130::getbox]]
    }
    popbox

    if {$dev_sub_type != ""} {
	box values [lindex $diffarea 0]um [lindex $diffarea 1]um \
	    [lindex $diffarea 2]um [lindex $diffarea 3]um
	box grow n ${sub_surround}um
	box grow s ${sub_surround}um
	box grow e ${sub_surround}um
	box grow w ${sub_surround}um
	paint ${dev_sub_type}
	set cext [sky130::unionbox $cext [sky130::getbox]]
        # puts stdout "Diagnostic:  bounding box is $cext"
    }

    popbox
    return $cext
}

#----------------------------------------------------------------
# MOSFET: Draw the tiled device
#----------------------------------------------------------------

proc sky130::mos_draw {parameters} {
    tech unlock *
    set savesnap [snap]
    snap internal

    # Set defaults if they are not in parameters
    set poverlap 0	;# overlap poly contacts when tiling
    set doverlap 1	;# overlap diffusion contacts when tiling
    set dev_sub_dist 0	;# substrate to guard ring, if dev_sub_type defined
    set dev_sub_space 0	;# distance between substrate areas for arrayed devices
    set min_allc 0	;# gate length below which poly contacts must be interleaved
    set id_type ""	;# additional type covering everything
    set id_surround 0	;# amount of surround on above type
    set id2_type ""	;# additional type covering everything
    set id2_surround 0	;# amount of surround on above type

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # Diff-to-tap spacing is by default the same as diff spacing
    if {![dict exist $parameters diff_tap_space]} {
	set diff_tap_space $diff_spacing
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

    # If dx < (poly contact space + poly contact width), then there is not
    # enough room for a row of contacts, so force alternating contacts

    if {$nf > 1 && $l < $min_allc} {
	set intc 1
	set evenodd 1
	set topc 1
	set botc 1
	dict set parameters topc 1
	dict set parameters botc 1
	set poverlap 0
    } else {
	set intc 0
    }

    # Determine the base device dimensions by drawing one device
    # while all layers are locked (nothing drawn).  This allows the
    # base drawing routine to do complicated geometry without having
    # to duplicate it here with calculations.

    tech lock *
    set bbox [sky130::mos_device $parameters]
    # puts stdout "Diagnostic: Device bounding box e $bbox (um)"
    tech unlock *

    set fw [- [lindex $bbox 2] [lindex $bbox 0]]
    set fh [- [lindex $bbox 3] [lindex $bbox 1]]
    set lw [+ [lindex $bbox 2] [lindex $bbox 0]]
    set lh [+ [lindex $bbox 3] [lindex $bbox 1]]

    # If dev_sub_dist > 0 then each device must be in its own substrate
    # (well) area, and overlaps are disallowed.  dev_sub_space determines
    # the distance between individual devices in an array.

    if {$dev_sub_dist > 0} {
        set poverlap 0
        set doverlap 0

	if {$dev_sub_space > $poly_spacing} {
	    set dx [+ $fw $dev_sub_space]
	    set dy [+ $fh $dev_sub_space]
	} else {
	    set dx [+ $fw $poly_spacing]
	    set dy [+ $fh $poly_spacing]
	}

    } else {

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

    if {$guard != 0} {
	# Calculate guard ring size (measured to contact center)
	if {($dev_sub_dist > 0) && ([+ $dev_sub_dist $sub_surround] > $diff_tap_space)} {
	    set gx [+ $corex [* 2.0 [+ $dev_sub_dist $diff_surround]] $contact_size]
	} else {
	    set gx [+ $corex [* 2.0 [+ $diff_tap_space $diff_surround]] $contact_size]
	}
	if {($dev_sub_dist > 0) && ([+ $dev_sub_dist $sub_surround] > $diff_gate_space)} {
	    set gy [+ $corey [* 2.0 [+ $dev_sub_dist $diff_surround]] $contact_size]
	} else {
	    set gy [+ $corey [* 2.0 [+ $diff_gate_space $diff_surround]] $contact_size]
	}

	# Somewhat tricky. . . if the width is small and the diffusion is 
	# a dogbone, and the top or bottom poly contact is missing, then
	# the spacing to the guard ring may be limited by diffusion spacing, not
	# poly to diffusion.

	set inset [/ [+ $contact_size [* 2.0 $diff_surround] -$w] 2.0]
	set sdiff [- [+ $inset $diff_tap_space] [+ $gate_extension $diff_gate_space]]

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

	# Draw the guard ring first, as MOS well may interact with guard ring substrate
	sky130::guard_ring $gx $gy $parameters
    }

    pushbox
    # If any surrounding identifier type is defined, draw it
    if {${id_type} != ""} {
	set hw [/ $gx 2]
	set hh [/ $gy 2]
	box grow e ${hw}um
	box grow w ${hw}um
	box grow n ${hh}um
	box grow s ${hh}um
	box grow c ${id_surround}um
	paint ${id_type}
    }
    popbox
    pushbox
    box move w ${corellx}um
    box move s ${corelly}um
    for {set xp 0} {$xp < $nf} {incr xp} {
        pushbox
	if {$intc == 1} {
	    set evenodd [- 1 $evenodd]
	    if {$evenodd == 1} {
		dict set parameters topc 1
		dict set parameters botc 0
	    } else {
		dict set parameters topc 0
		dict set parameters botc 1
	    }
	    set saveeo $evenodd
	}
        for {set yp 0} {$yp < $m} {incr yp} {
            sky130::mos_device $parameters
            box move n ${dy}um
	    if {$intc == 1} {
		set evenodd [- 1 $evenodd]
		if {$evenodd == 1} {
		    dict set parameters topc 1
		    dict set parameters botc 0
		} else {
		    dict set parameters topc 0
		    dict set parameters botc 1
		}
	    }
        }
	if {$intc == 1} {
	    set evenodd $saveeo
	}
        popbox
        box move e ${dx}um
    }
    popbox
    popbox

    snap $savesnap
    tech revert
}

#-------------------
# nMOS 1.8V
#-------------------

proc sky130::nshort_draw {parameters} {
    set newdict [dict create \
	    gate_type		nfet \
	    diff_type 		ndiff \
	    diff_contact_type	ndc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    min_effl		0.185 \
	    min_allc		0.26 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

proc sky130::nlowvt_draw {parameters} {
    set newdict [dict create \
	    gate_type		nfetlvt \
	    diff_type 		ndiff \
	    diff_contact_type	ndc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    min_effl		0.185 \
	    min_allc		0.26 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

proc sky130::sonos_e_draw {parameters} {
    set newdict [dict create \
	    gate_type		nsonos \
	    diff_type 		ndiff \
	    diff_contact_type	ndc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    id_type		dnwell \
	    id_surround		1.355 \
	    min_effl		0.185 \
	    min_allc		0.26 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

#-------------------
# pMOS 1.8V
#-------------------

proc sky130::pshort_draw {parameters} {
    set newdict [dict create \
	    gate_type		pfet \
	    diff_type 		pdiff \
	    diff_contact_type	pdc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		nwell \
	    gate_to_polycont	0.32 \
	    min_effl		0.185 \
	    min_allc		0.26 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

proc sky130::plowvt_draw {parameters} {
    set newdict [dict create \
	    gate_type		pfetlvt \
	    diff_type 		pdiff \
	    diff_contact_type	pdc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		nwell \
	    gate_to_polycont	0.32 \
	    min_effl		0.185 \
	    min_allc		0.26 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

proc sky130::phighvt_draw {parameters} {
    set newdict [dict create \
	    gate_type		pfethvt \
	    diff_type 		pdiff \
	    diff_contact_type	pdc \
	    plus_diff_type	nsd \
	    plus_contact_type	nsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		nwell \
	    gate_to_polycont	0.32 \
	    min_effl		0.185 \
	    min_allc		0.26 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

#-------------------
# pMOS 5.0V
#-------------------

proc sky130::phv_draw {parameters} {
    set newdict [dict create \
	    gate_type		mvpfet \
	    diff_type 		mvpdiff \
	    diff_contact_type	mvpdc \
	    plus_diff_type	mvnsd \
	    plus_contact_type	mvnsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		nwell \
	    guard_sub_surround	0.33 \
	    gate_to_polycont	0.32 \
	    diff_spacing	0.31 \
	    diff_tap_space	0.38 \
	    diff_gate_space	0.38 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

#-------------------
# nMOS 5.0V
#-------------------

proc sky130::nhv_draw {parameters} {
    set newdict [dict create \
	    gate_type		mvnfet \
	    diff_type 		mvndiff \
	    diff_contact_type	mvndc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    diff_spacing	0.31 \
	    diff_tap_space	0.38 \
	    diff_gate_space	0.38 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

proc sky130::nhvnative_draw {parameters} {
    set newdict [dict create \
	    gate_type		mvnnfet \
	    diff_type 		mvndiff \
	    diff_contact_type	mvndc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    diff_spacing	0.30 \
	    diff_tap_space	0.38 \
	    diff_gate_space	0.38 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

#------------------------
# MOS varactor (1.8V)
#------------------------

proc sky130::xcnwvc_draw {parameters} {
    set newdict [dict create \
	    gate_type		var \
	    diff_type 		nnd \
	    diff_contact_type	nsc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    dev_sub_type	nwell \
	    diff_overlap_cont	0.06 \
	    dev_sub_dist	0.14 \
	    dev_sub_space	1.27 \
	    gate_to_diffcont	0.34 \
	    diff_extension	0.485 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

proc sky130::xcnwvc2_draw {parameters} {
    set newdict [dict create \
	    gate_type		varhvt \
	    diff_type 		nnd \
	    diff_contact_type	nsc \
	    plus_diff_type	psd \
	    plus_contact_type	psc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    dev_sub_type	nwell \
	    diff_overlap_cont	0.06 \
	    dev_sub_dist	0.14 \
	    dev_sub_space	1.27 \
	    gate_to_diffcont	0.34 \
	    diff_extension	0.485 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

#---------------------------------------------------------
# MOS varactor (5.0V)
# NOTE:  dev_sub_space set to 2.0 assuming different nets.
# Should have option for same-net with merged wells.
#---------------------------------------------------------

proc sky130::xchvnwc_draw {parameters} {
    set newdict [dict create \
	    gate_type		mvvar \
	    diff_type 		mvnsd \
	    diff_contact_type	mvnsc \
	    plus_diff_type	mvpsd \
	    plus_contact_type	mvpsc \
	    poly_type		poly \
	    poly_contact_type	pc \
	    sub_type		psub \
	    dev_sub_type	nwell \
	    sub_surround	0.38 \
	    sub_surround_dev	0.56 \
	    guard_sub_surround	0.18 \
	    diff_overlap_cont	0.06 \
	    dev_sub_dist	0.785 \
	    dev_sub_space	2.0 \
	    gate_to_diffcont	0.34 \
	    diff_extension	0.485 \
    ]
    set drawdict [dict merge $sky130::ruleset $newdict $parameters]
    return [sky130::mos_draw $drawdict]
}

#----------------------------------------------------------------
# MOSFET: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc sky130::mos_check {device parameters} {

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

proc sky130::nshort_check {parameters} {
   return [sky130::mos_check nshort $parameters]
}

proc sky130::nlowvt_check {parameters} {
   return [sky130::mos_check nlowvt $parameters]
}

proc sky130::sonos_e_check {parameters} {
   return [sky130::mos_check sonos_e $parameters]
}

proc sky130::nhv_check {parameters} {
   return [sky130::mos_check nhv $parameters]
}

proc sky130::nhvnative_check {parameters} {
   return [sky130::mos_check nhvnative $parameters]
}

proc sky130::pshort_check {parameters} {
   return [sky130::mos_check pshort $parameters]
}

proc sky130::plowvt_check {parameters} {
   return [sky130::mos_check plowvt $parameters]
}

proc sky130::phighvt_check {parameters} {
   return [sky130::mos_check phighvt $parameters]
}

proc sky130::phv_check {parameters} {
   return [sky130::mos_check phv $parameters]
}

proc sky130::xcnwvc_check {parameters} {
   return [sky130::mos_check xcnwvc $parameters]
}

proc sky130::xcnwvc2_check {parameters} {
   return [sky130::mos_check xcnwvc2 $parameters]
}

proc sky130::xchvnwc_check {parameters} {
   return [sky130::mos_check xchvnwc $parameters]
}

#----------------------------------------------------------------
# Fixed device: Specify all user-editable default values
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

# Fixed-layout devices (from sky130_fd_pr_base, _rf, and _rf2 libraries)
#
# Bipolar transistors:
#
# sky130_fd_pr_rf_npn_1x1
# sky130_fd_pr_rf_npn_1x2
# sky130_fd_pr_rf_pnp5x
#
# Parallel Plate Capacitors:
#
# sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield
# sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield
# sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield
# sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield
# sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield
# sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield
# sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield
# sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield
# sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield
# sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4
# sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield
# sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield
# sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield
# sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield
# sky130_fd_pr_rf_xcmvpp2
# sky130_fd_pr_rf_xcmvpp2_nwell
# sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield
# sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield
# sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield
# sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield
#
# Inductors:
#
# balun
# xind4_011
# xind4_02

proc sky130::sky130_fd_pr_rf_npn_1x1_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 7.03 ystep 7.03}
}

proc sky130::sky130_fd_pr_rf_npn_1x2_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 7.03 ystep 8.03}
}

proc sky130::sky130_fd_pr_rf_pnp5x_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 6.44 ystep 6.44}
}

proc sky130::balun_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 292 ystep 292}
}

proc sky130::xind4_02_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 258 ystep 258}
}

proc sky130::xind4_011_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 290 ystep 404}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 4.05 ystep 4.26}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 6.47 ystep 5.76}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 6.47 ystep 5.76}
}

proc sky130::sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 8.25 ystep 7.51}
}

proc sky130::sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 10.41 ystep 11.54}
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 11.08 ystep 11.36}
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 1.77 ystep 1.77}
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 3.88 ystep 3.88}
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 4.55 ystep 4.76}
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_nwell_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 4.55 ystep 4.76}
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 4.05 ystep 4.26}
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 4.05 ystep 4.26}
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 8.25 ystep 7.51}
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield_defaults {} {
    return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 8.25 ystep 7.51}
}

#----------------------------------------------------------------
# Fixed device: Conversion from SPICE netlist parameters to toolkit
#----------------------------------------------------------------

proc sky130::fixed_convert {parameters} {
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

proc sky130::sky130_fd_pr_rf_npn_1x1_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_npn_1x2_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_pnp5x_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::balun_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::xind4_011_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::xind4_02_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_nwell_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield_convert {parameters} {
    return [sky130::fixed_convert $parameters]
}

#----------------------------------------------------------------
# Fixed device: Interactively specifies the fixed layout parameters
#----------------------------------------------------------------

proc sky130::fixed_dialog {parameters} {
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

proc sky130::sky130_fd_pr_rf_npn_1x1_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_npn_1x2_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_pnp5x_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::balun_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::xind4_011_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::xind4_02_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_nwell_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield_dialog {parameters} {
    sky130::fixed_dialog $parameters
}

#----------------------------------------------------------------
# Fixed device: Draw the device
#----------------------------------------------------------------

proc sky130::fixed_draw {devname parameters} {

    # Set a local variable for each parameter (e.g., $l, $w, etc.)
    foreach key [dict keys $parameters] {
        set $key [dict get $parameters $key]
    }

    # This cell declares "nocell" in parameters, so it needs to
    # instance the cell and set properties.

    # Instantiate the cell.  The name corresponds to the cell in the sky130_fd_pr_* directory.
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

proc sky130::sky130_fd_pr_rf_npn_1x1_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_npn_1x1 $parameters]
}

proc sky130::sky130_fd_pr_rf_npn_1x2_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_npn_1x2 $parameters]
}

proc sky130::sky130_fd_pr_rf_pnp5x_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_pnp5x $parameters]
}

proc sky130::balun_draw {parameters} {
    return [sky130::fixed_draw balun $parameters]
}

proc sky130::xind4_011_draw {parameters} {
    return [sky130::fixed_draw xind4_011 $parameters]
}

proc sky130::xind4_02_draw {parameters} {
    return [sky130::fixed_draw xind4_02 $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4 $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp2 $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_nwell_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp2_nwell $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield_draw {parameters} {
    return [sky130::fixed_draw sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield $parameters]
}

#----------------------------------------------------------------
# Fixed device: Check device parameters for out-of-bounds values
#----------------------------------------------------------------

proc sky130::fixed_check {parameters} {

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

proc sky130::sky130_fd_pr_rf_npn_1x1_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_npn_1x2_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_pnp5x_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::balun_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::xind4_011_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::xind4_02_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp2_nwell_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

proc sky130::sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield_check {parameters} {
    return [sky130::fixed_check $parameters]
}

