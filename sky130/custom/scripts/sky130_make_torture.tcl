#---------------------------------------
# Torture test generator for EFS8
# (Specifically for EFS8B)
# (work in progress)
#---------------------------------------

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

         set r [int [* [rand] 20]]
         set w [+ 0.22 [* 0.5 $r]]
         set r [int [* [rand] 20]]
         set l [+ 0.18 [* 0.3 $r]]
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

proc res_array {n devname startx starty {deltax 12700} {deltay 254}} {
   suspendall
   box position $startx $starty
   set i 0
   for {set x 0} {$x < $n} {incr x} {
      for {set y 0} {$y < $n} {incr y} {

         set r [int [* [rand] 10]]
         set w [+ 0.42 [* 0.5 $r]]
         set r [int [* [rand] 50]]
         set l [+ 2.10 [* 2.0 $r]]
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

	 # Snake geometry does not apply to xhrpoly, uhrpoly, and xpwres, and
	 # roverlap and endcov are prohibited.
	 if {$devname == "xhrpoly" || $devname == "uhrpoly" || $devname == "xpwres"} {
	    magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l m $m nx $nx full_metal $fm \
		glc $gl grc $gr gbc $gb gtc $gt
	 } else {
	    magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l m $m nx $nx endcov $ecov roverlap $rov \
		snake $sn full_metal $fm glc $gl grc $gr gbc $gb gtc $gt
	 }
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

         set r [int [* [rand] 10]]
         set w [+ 0.42 [* 0.5 $r]]
         set r [int [* [rand] 10]]
         set l [+ 0.42 [* 0.5 $r]]
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

         set r [int [* [rand] 10]]
         set w [+ 2.00 [* 1.0 $r]]
         set r [int [* [rand] 10]]
         set l [+ 2.00 [* 1.0 $r]]
         set nx [int [+ 1 [* [rand] 4]]]
         set ny [int [+ 1 [* [rand] 4]]]

         if {[rand] > 0.5} {set bc 1} else {set bc 0}
         if {[rand] > 0.5} {set tc 1} else {set tc 0}

         magic::gencell sky130::${devname} ${devname}_$i \
		w $w l $l nx $nx ny $ny bconnect $bc tconnect $tc
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

snap int
box size 0 0
 
# Layout:
#  phv
#        mrl1     mrp1   mrdp   mrdp_hv  
#  nhv                                  pdiode_h
#                                       ndiode_h
#  pshort                               nndiode
#        xhrpoly  xpwres mrdn   mrdn_hv  pdiode
#  nshort                               ndiode
#

mos_array 6 nshort 0 0
mos_array 6 pshort 0 75000
mos_array 6 nhv 0 150000 
mos_array 6 phv 0 225000
mos_array 6 nlowvt 0 300000
mos_array 6 sonos_e 0 375000 12700 1650
mos_array 6 plowvt 0 450000
mos_array 6 phighvt 0 525000
mos_array 6 nhvnative 0 600000 

res_array 6 xhrpoly 100000 0
res_array 6 mrl1 100000 180000
res_array 6 uhrpoly 100000 360000

res_array 6 xpwres 200000 0 13500 1100
res_array 6 mrp1 200000 200000

res_array 6 mrdn 300000 0
res_array 6 mrdp 300000 180000

res_array 6 mrdn_hv 400000 0
res_array 6 mrdp_hv 400000 180000
 
diode_array 6 ndiode 500000 0
diode_array 6 pdiode 500000 30000 
diode_array 6 ndiode_h 500000 60000
diode_array 6 pdiode_h 500000 90000 

cap_array 6 xcmimc1 600000 0
cap_array 6 xcmimc2 600000 70000 18000 650

mos_array 6 xcnwvc 700000 0 15000 254
mos_array 6 xchvnwc 700000 70000 18000 254
mos_array 6 xcnwvc2 700000 140000 15000 254

fixed_array 2 sky130_fd_pr_rf_npn_1x1 850000 0
fixed_array 2 sky130_fd_pr_rf_npn_1x2 850000 30000
fixed_array 2 sky130_fd_pr_rf_pnp5x 850000 60000

fixed_array 2 sky130_fd_pr_rf2_xcmvpp11p5x11p7_lim5shield 900000 0
fixed_array 2 sky130_fd_pr_rf2_xcmvpp11p5x11p7_m3_lim5shield 900000 30000
fixed_array 2 sky130_fd_pr_rf2_xcmvpp11p5x11p7_m4shield 900000 60000
fixed_array 2 sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym4shield 900000 90000
fixed_array 2 sky130_fd_pr_rf2_xcmvpp4p4x4p6_m3_lim5shield 900000 120000
fixed_array 2 sky130_fd_pr_rf2_xcmvpp6p8x6p1_lim4shield 900000 150000
fixed_array 2 sky130_fd_pr_rf2_xcmvpp6p8x6p1_polym4shield 900000 180000
fixed_array 2 sky130_fd_pr_rf2_xcmvpp8p6x7p9_m3_lim5shield 900000 210000
fixed_array 2 sky130_fd_pr_rf2_xcmvppx4_2xnhvnative10x4 900000 240000
# fixed_array 2 sky130_fd_pr_rf2_xcmvpp11p5x11p7_polym50p4shield 900000 270000

fixed_array 2 sky130_fd_pr_rf_xcmvpp11p5x11p7_m3_lishield 950000 0
fixed_array 2 sky130_fd_pr_rf_xcmvpp11p5x11p7_m3shield 950000 30000
fixed_array 2 sky130_fd_pr_rf_xcmvpp2 950000 60000
fixed_array 2 sky130_fd_pr_rf_xcmvpp2_nwell 950000 90000
fixed_array 2 sky130_fd_pr_rf_xcmvpp4p4x4p6_m3_lishield 950000 120000
fixed_array 2 sky130_fd_pr_rf_xcmvpp4p4x4p6_m3shield 950000 150000
fixed_array 2 sky130_fd_pr_rf_xcmvpp8p6x7p9_m3_lishield 950000 180000
fixed_array 2 sky130_fd_pr_rf_xcmvpp8p6x7p9_m3shield 950000 210000
# fixed_array 2 sky130_fd_pr_rf_xcmvpp1p8x1p8_lishield 950000 240000
# fixed_array 2 sky130_fd_pr_rf_xcmvpp1p8x1p8_m3shield 950000 270000

fixed_array 1 balun 1000000 0
fixed_array 1 xind4_02 1000000 200000
fixed_array 1 xind4_011 1250000 0

# Draw a deep nwell region around the sonos transistor block
box values -5200i 369500i 76800i 427500i
sky130::deep_nwell_draw

save torture_test_sky130
gds write torture_test_sky130
