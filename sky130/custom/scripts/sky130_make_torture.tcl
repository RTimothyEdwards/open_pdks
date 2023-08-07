#---------------------------------------
# Torture test generator for EFS8
# (Specifically for EFS8B)
# (work in progress)
#---------------------------------------
## 2 torture 
# 1 with invalid params, to show up in drc
# 
namespace path {::tcl::mathop ::tcl::mathfunc}

# Set random seed so that torture test is not random from run to run.
srand 1234567

# NxN array MOSFET devices

proc mos_array {n devname startx starty {deltax 12700} {deltay 254}} {
   suspendall
   box position $startx $starty
   set i 0
   for {set x 0} {$x < $n} {incr x} {
      for {set y 0} {$y < $n} {incr y} {
		
	 set device_defaults [dict create {*}[sky130::${devname}_defaults]]
	 set lmin [dict get $device_defaults lmin]
	 set wmin [dict get $device_defaults wmin]
         
	 set r [int [* [rand] 20]]
         set w [+ $wmin [* 0.5 $r]]
         set r [int [* [rand] 20]]
         set l [+ $lmin [* 0.3 $r]]
         set m [int [+ 1 [* [rand] 8]]]
         set nf [int [+ 1 [* [rand] 8]]]

         set r [int [* [rand] 8]]
         set dcov [+ 20 [* 10 $r]]
         set r [int [* [rand] 8]]
         set pcov [+ 20 [* 10 $r]]
         set r [int [* [rand] 8]]
         set rlcov [+ 20 [* 10 $r]]

         if {[rand] > 0.5} {set pov 1} else {set pov 0}
         if {[rand] > 0.5} {set dov 1} else {set dov 0}
         if {[rand] > 0.5} {set tc 1} else {set tc 0}
         if {[rand] > 0.5} {set bc 1} else {set bc 0}
         if {[rand] > 0.5} {set fm 1} else {set fm 0}
         if {[rand] > 0.5} {set gl 1} else {set gl 0}
         if {[rand] > 0.5} {set gr 1} else {set gr 0}
         if {[rand] > 0.5} {set gt 1} else {set gt 0}
         if {[rand] > 0.5} {set gb 1} else {set gb 0}

         magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l m $m nf $nf diffcov $dcov polycov $pcov \
		rlcov $rlcov poverlap $pov doverlap $dov topc $tc \
		botc $bc full_metal $fm glc $gl grc $gr gbc $gb gtc $gt
	 extract_drc_errors_to_file ${devname}_$i
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh $deltay]
         box move n $bh
         incr i
      }
      set bp [box position]
      set bpx [lindex $bp 0]
      box position $bpx $starty
      box move e $deltax
   }
   resumeall
}

# NxN array resistor devices

proc sky130_fd_pr__res_array {n devname startx starty {deltax 12700} {deltay 254}} {
   suspendall
   box position $startx $starty
   set i 0
   for {set x 0} {$x < $n} {incr x} {
      for {set y 0} {$y < $n} {incr y} {

	 set device_defaults [dict create {*}[sky130::${devname}_defaults]]
	 set lmin [dict get $device_defaults lmin]
	 set wmin [dict get $device_defaults wmin]
         
	 set r [int [* [rand] 10]]
         set w [+ $wmin [* 0.5 $r]]
         set r [int [* [rand] 50]]
         set l [+ $lmin [* 2.0 $r]]
         set m [int [+ 1 [* [rand] 2]]]
         set nx [int [+ 1 [* [rand] 10]]]

         set r [int [* [rand] 8]]
         set ecov [+ 20 [* 10 $r]]

         if {[rand] > 0.5} {set rov 1} else {set rov 0}
	 if {[rand] > 0.5} {set sn 1} else {set sn 0}
         if {[rand] > 0.5} {set fm 1} else {set fm 0}
         if {[rand] > 0.5} {set gl 1} else {set gl 0}
         if {[rand] > 0.5} {set gr 1} else {set gr 0}
         if {[rand] > 0.5} {set gt 1} else {set gt 0}
         if {[rand] > 0.5} {set gb 1} else {set gb 0}

	 # Snake geometry does not apply to sky130_fd_pr_res_high_po, sky130_fd_pr__res_xhigh_po, and sky130_fd_pr__res_iso_pw, and
	 # roverlap and endcov are prohibited.
	 if {$devname == "sky130_fd_pr_res_high_po" || $devname == "res_xhigh_po" || $devname == "res_iso_pw"} {
	    magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l m $m nx $nx full_metal $fm \
		glc $gl grc $gr gbc $gb gtc $gt
	 } else {
	    magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l m $m nx $nx endcov $ecov roverlap $rov \
		snake $sn full_metal $fm glc $gl grc $gr gbc $gb gtc $gt
	 }
	 extract_drc_errors_to_file ${devname}_$i
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh $deltay]
         box move n $bh
         incr i
      }
      set bp [box position]
      set bpx [lindex $bp 0]
      box position $bpx $starty
      box move e $deltax
   }
   resumeall
}

# NxN array diode devices

proc diode_array {n devname startx starty} {
   suspendall
   box position $startx $starty
   set i 0
   for {set x 0} {$x < $n} {incr x} {
      for {set y 0} {$y < $n} {incr y} {

	 set device_defaults [dict create {*}[sky130::${devname}_defaults]]
	 set lmin [dict get $device_defaults lmin]
	 set wmin [dict get $device_defaults wmin]
         
	 set r [int [* [rand] 10]]
         set w [+ $wmin [* 0.5 $r]]
         set r [int [* [rand] 10]]
         set l [+ $lmin [* 0.5 $r]]
         set nx [int [+ 1 [* [rand] 4]]]
         set ny [int [+ 1 [* [rand] 4]]]

         if {[rand] > 0.5} {set dov 1} else {set dov 0}
         if {[rand] > 0.5} {set el 1} else {set el 0}
         if {[rand] > 0.5} {set er 1} else {set er 0}
         if {[rand] > 0.5} {set et 1} else {set et 0}
         if {[rand] > 0.5} {set eb 1} else {set eb 0}
         if {[rand] > 0.5} {set fm 1} else {set fm 0}
         if {[rand] > 0.5} {set gl 1} else {set gl 0}
         if {[rand] > 0.5} {set gr 1} else {set gr 0}
         if {[rand] > 0.5} {set gt 1} else {set gt 0}
         if {[rand] > 0.5} {set gb 1} else {set gb 0}

         magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l nx $nx ny $ny doverlap $dov \
		full_metal $fm elc $el erc $er etc $et \
		ebc $eb glc $gl grc $gr gbc $gb gtc $gt
	 extract_drc_errors_to_file ${devname}_$i
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh 254]
         box move n $bh
         incr i
      }
      set bp [box position]
      set bpx [lindex $bp 0]
      box position $bpx $starty
      box move e 12700
   }
   resumeall
}


# NxN array cap devices

proc cap_array {n devname startx starty {deltax 12700} {deltay 160}} {
   suspendall
   box position $startx $starty
   set i 0
   for {set x 0} {$x < $n} {incr x} {
      for {set y 0} {$y < $n} {incr y} {

	 set device_defaults [dict create {*}[sky130::${devname}_defaults]]
	 set lmin [dict get $device_defaults lmin]
	 set wmin [dict get $device_defaults wmin]
         
	 set r [int [* [rand] 10]]
         set w [+ $wmin [* 1.0 $r]]
         set r [int [* [rand] 10]]
         set l [+ $lmin [* 1.0 $r]]
         set nx [int [+ 1 [* [rand] 4]]]
         set ny [int [+ 1 [* [rand] 4]]]

         if {[rand] > 0.5} {set bc 1} else {set bc 0}
         if {[rand] > 0.5} {set tc 1} else {set tc 0}

         magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l nx $nx ny $ny bconnect $bc tconnect $tc
	 extract_drc_errors_to_file ${devname}_$i
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh $deltay]
         box move n $bh
         incr i
      }
      set bp [box position]
      set bpx [lindex $bp 0]
      box position $bpx $starty
      box move e $deltax
   }
   resumeall
}

# NxN fixed devices

proc fixed_array {n devname startx starty} {
   suspendall
   box position $startx $starty
   set i 0
   for {set x 0} {$x < $n} {incr x} {
      for {set y 0} {$y < $n} {incr y} {

         set nx [int [+ 1 [* [rand] 4]]]
         set ny [int [+ 1 [* [rand] 4]]]

         # Do not change the deltas---this will cause DRC problems
         set r 0
         # set r [int [* [rand] 10]]
         set deltax [/ $r 10.0]
         # set r [int [* [rand] 10]]
         set deltay [/ $r 10.0]

         magic::gencell sky130::${devname} ${devname}_$i \
		nx $nx ny $ny deltax $deltax deltay $deltay
	 extract_drc_errors_to_file ${devname}_$i
         select cell ${devname}_$i
         set bh [box height]
         set bh [* $bh [+ $ny 1]]
         box move n $bh
         incr i
      }
      set bp [box position]
      set bpx [lindex $bp 0]
      box position $bpx $starty
      box move e 20000
   }
   resumeall
}

proc extract_drc_errors_to_file {cell_name
	{drc_errors_filename "drc_errors_list.txt"}} {

	# go down to cell level
	select cell $cell_name 
	magic::pushstack

	# extract the device properties, and store them in a
	# dictionary
	set device_c [dict create {*}[property parameters]]
	set device_l [dict get $device_c l]
	set device_w [dict get $device_c w]

	# select the cell in the lower hierarchy
	select
	
	# find drc errors in the entire cell, and output
	# them to the errors file
	set drcdict [dict create {*}[drc listall why]]
	
	# if there are any errors, output them to file
	if {[dict size $drcdict] > 0} {
	set drc_file [open $drc_errors_filename a]	
		set name_extracted [exec echo $cell_name | sed {s/_[^_]*$//}]
		# puts $drc_file "cellname extracted: $name_extracted"
		puts $drc_file "device: $cell_name"
		dict for {id value} $drcdict {
			puts $drc_file "drc error: $id"
		}


		# find from the device defaults the lmin and
		# wmin, and if the device has been generated
		# with wrong parameters from the torture
		# test, put them in the file
		set device_defaults [dict create {*}[sky130::${name_extracted}_defaults]]
		
		set device_lmin [dict get $device_defaults lmin]
		set device_wmin [dict get $device_defaults wmin]

		if { $device_l < $device_lmin || $device_w < $device_wmin } {
			puts $drc_file "torture test generated wrong parameters"
			puts $drc_file "l_min: $device_lmin l: $device_l"
			puts $drc_file "w_min: $device_wmin w: $device_w"
		}
		puts $drc_file "\n"
		close $drc_file
		
		# clear selection
		select clear 
		
	}
	# return to top of hierarchy
	magic::popstack
	select clear
}

snap int
box size 0 0
 
# Layout:
#  phv
#        sky130_fd_pr__res_generic_l1     sky130_fd_pr__res_generic_po   res_generic_pd   res_generic_pd_hv  
#  nfet_g5v0d10v5                                  diode_pd2nw_11v0
#                                       diode_pw2nd_11v0
#  pfet_01v8                               ndiode_pw2nd_05v5
#       res_high_po  res_iso_pw res_generic_nd   res_generic_nd_hv  diode_pd2nw_05v5
#  nfet_01v8                               diode_pw2nd_05v5
#
# create a drc errors file, or if one exits, delete contents
set file_created [open ./drc_errors_list.txt w]
close $file_created

mos_array 6 sky130_fd_pr__nfet_01v8 0 0
mos_array 6 sky130_fd_pr__pfet_01v8 0 75000
mos_array 6 sky130_fd_pr__nfet_g5v0d10v5 0 150000 
mos_array 6 sky130_fd_pr__pfet_g5v0d10v5 0 225000
mos_array 6 sky130_fd_pr__nfet_01v8_lvt 0 300000
mos_array 6 sky130_fd_bs_flash__special_sonosfet_star 0 375000 12700 1650
mos_array 6 sky130_fd_pr__pfet_01v8_lvt 0 450000
mos_array 6 sky130_fd_pr__pfet_01v8_hvt 0 525000
mos_array 6 sky130_fd_pr__nfet_03v3_nvt 0 600000 

sky130_fd_pr__res_array 6 sky130_fd_pr_res_high_po 100000 0
sky130_fd_pr__res_array 6 sky130_fd_pr__res_generic_l1 100000 180000
sky130_fd_pr__res_array 6 sky130_fd_pr__res_xhigh_po 100000 360000

sky130_fd_pr__res_array 6 sky130_fd_pr__res_iso_pw 200000 0 13500 1100
sky130_fd_pr__res_array 6 sky130_fd_pr__res_generic_po 200000 200000

sky130_fd_pr__res_array 6 sky130_fd_pr__res_generic_nd 300000 0
sky130_fd_pr__res_array 6 sky130_fd_pr__res_generic_pd 300000 180000

diode_array 6 sky130_fd_pr__diode_pw2nd_05v5 500000 0
diode_array 6 sky130_fd_pr__diode_pd2nw_05v5 500000 30000 
diode_array 6 sky130_fd_pr__diode_pw2nd_11v0 500000 60000
diode_array 6 sky130_fd_pr__diode_pd2nw_11v0 500000 90000 

cap_array 6 sky130_fd_pr__cap_mim_m3_1 600000 0
cap_array 6 sky130_fd_pr__cap_mim_m3_2 600000 70000 18000 650

mos_array 6 sky130_fd_pr__cap_var_lvt 700000 0 15000 254
mos_array 6 sky130_fd_pr__cap_var 700000 70000 18000 254
mos_array 6 sky130_fd_pr__cap_var_hvt 700000 140000 15000 254


# pnp both exits, and npn rf, first two (in libs.ref/mag/)
fixed_array 2 sky130_fd_pr__rf_npn_1x1 850000 0
fixed_array 2 sky130_fd_pr__rf_npn_1x2 850000 30000
fixed_array 2 sky130_fd_pr__rf_pnp5x 850000 60000

fixed_array 2 sky130_fd_pr__cap_vpp_01p8x01p8_m1m2_noshield 900000 0
fixed_array 2 sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield 900000 30000
fixed_array 2 sky130_fd_pr__cap_vpp_02p7x6p1_m1m2m3m4_shield1_fingercap 900000 60000
fixed_array 2 sky130_fd_pr__cap_vpp_01p8x01p8_m1m2_shield1 900000 90000
fixed_array 2 sky130_fd_pr__cap_vpp_03p9x03p9_m1m2_shield1_floatm3 900000 120000
fixed_array 2 sky130_fd_pr__cap_vpp_04p4x04p6_l1m1m2_noshield 900000 150000
fixed_array 2 sky130_fd_pr__cap_vpp_04p4x04p6_l1m1m2_shieldm3_floatpo 900000 180000
fixed_array 2 sky130_fd_pr__cap_vpp_04p4x04p6_l1m1m2m3m4_shieldpom5 900000 210000
fixed_array 2 sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2_noshield 900000 240000
fixed_array 2 sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2m3m4_shieldpo_floatm5 900000 270000

fixed_array 2 sky130_fd_pr__cap_vpp_08p6x07p8_l1m1m2_noshield 950000 0
fixed_array 2 sky130_fd_pr__cap_vpp_08p6x07p8_l1m1m2_shieldnw_nwell 950000 30000
fixed_array 2 sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shield1 950000 60000
fixed_array 2 sky130_fd_pr__cap_vpp_11p3x11p3_m1m2m3m4_shield1_wafflecap 950000 90000
fixed_array 2 sky130_fd_pr__cap_vpp_11p3x11p8_l1m1m2m3m4_shield5_nhv 950000 120000
fixed_array 2 sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2_noshield 950000 150000
fixed_array 2 sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2_shieldpom3 950000 180000
fixed_array 2 sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5 950000 210000
fixed_array 2 sky130_fd_pr__cap_vpp_11p5x11p7_m1m4_noshield 950000 240000
fixed_array 2 sky130_fd_pr__cap_vpp_22p5x11p7_pol1m1m2m3m4m5_noshield 950000 270000

fixed_array 1 balun 1000000 0
fixed_array 1 sky130_fd_pr__ind_02_04 1000000 200000
fixed_array 1 sky130_fd_pr__ind_11_04 1250000 0

# Draw a deep nwell region around the sonos transistor block
box values -5200i 369500i 76800i 427500i
sky130::deep_nwell_draw

save torture_test_sky130
gds write torture_test_sky130
