#---------------------------------------
# Torture test generator for EFGF013H
# (Specifically for EFGF013H; note that
# MiM and MoM caps need to be tested in
# each BEOL stack.)
#---------------------------------------

namespace path {::tcl::mathop ::tcl::mathfunc}

# Set random seed so that torture test is not totally random.
srand 1234567

# NxN array MOSFET devices

proc mos_array {n devname startx starty} {
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

         magic::gencell gf180mcu::${devname} ${devname}_$i w $w l $l m $m nf $nf diffcov $dcov polycov $pcov rlcov $rlcov poverlap $pov doverlap $dov topc $tc botc $bc full_metal $fm glc $gl grc $gr gbc $gb gtc $gt
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh 200]
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

# NxN array resistor devices

proc res_array {n devname startx starty} {
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

         magic::gencell gf180mcu::${devname} ${devname}_$i w $w l $l m $m nx $nx endcov $ecov roverlap $rov snake $sn full_metal $fm glc $gl grc $gr gbc $gb gtc $gt
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh 200]
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

         magic::gencell gf180mcu::${devname} ${devname}_$i w $w l $l nx $nx ny $ny doverlap $dov full_metal $fm elc $el erc $er etc $et ebc $eb glc $gl grc $gr gbc $gb gtc $gt
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh 200]
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

proc cap_array {n devname startx starty} {
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

         magic::gencell gf180mcu::${devname} ${devname}_$i w $w l $l nx $nx ny $ny bconnect $bc tconnect $tc
         select cell ${devname}_$i
         set bh [box height]
         set bh [+ $bh 160]
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

         magic::gencell gf180mcu::${devname} ${devname}_$i nx $nx ny $ny deltax $deltax deltay $deltay
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
tech unlock *
snap int
box size 0 0
 
#
# Generate device arrays
#

mos_array 6 nfet_03v3 	   0      0
mos_array 6 pfet_03v3 	   0  75000
mos_array 6 nfet_06v0 	   0 150000 
mos_array 6 pfet_06v0 	   0 225000
mos_array 6 nfet_03v3_nvt  0 300000
mos_array 6 nfet_03v3_dss  0 375000
mos_array 6 pfet_03v3_dss  0 450000
mos_array 6 nfet_06v0_dss  0 525000
mos_array 6 nfet_06v0_dss  0 600000
mos_array 6 pfet_06v0_nat  0 675000
mos_array 6 nfet_10v0_asym 0 675000
mos_array 6 pfet_10v0_asym 0 725000

res_array 6 npolyf_u 	100000      0 
res_array 6 ppolyf_u 	100000 180000

res_array 6 ppolyf_u_1k	    200000      0
res_array 6 ppolyf_u_1k_6p0 200000 180000

res_array 6 nplus_u 	300000      0
res_array 6 pplus_u 	300000 180000

res_array 6 npolyf_s 	400000      0
res_array 6 ppolyf_s 	400000 180000
 
res_array 6 nwell 	500000      0
res_array 6 rm1   	500000 180000
res_array 6 rm2   	500000 360000
res_array 6 rm3   	500000 540000
res_array 6 rm4   	500000 720000
res_array 6 rm5   	500000 900000

diode_array 6 diode_nd2ps_03v3 	   600000      0
diode_array 6 diode_pd2nw_03v3 	   600000  30000 
diode_array 6 diode_nd2ps_06v0 	   600000  60000
diode_array 6 diode_pd2nw_06v0 	   600000  90000 
diode_array 6 diode_nw2pw_03v3 	   600000 120000
diode_array 6 diode_nw2pw_06v0 	   600000 150000
diode_array 6 diode_dnw2pw     	   600000 180000
diode_array 6 diode_dnw2ps     	   600000 210000 
diode_array 6 sc_diode 		   600000 240000 
diode_array 6 diode_nd2ps_06v0_nvt 600000 270000

cap_array 6 cap_mim_2p0fF	700000      0
cap_array 6 nmoscap_3p3   	700000 100000 
cap_array 6 nmoscap_6p0   	700000 200000 

# Add individual devices from primdev, check GDS pointers
fixed_array 2 efuse_cell      800000      0
fixed_array 2 npn_00p54x02p00 800000  50000
fixed_array 2 npn_00p54x04p00 800000 100000
fixed_array 2 npn_00p54x08p00 800000 150000
fixed_array 2 npn_00p54x16p00 800000 200000
fixed_array 2 npn_05p00x05p00 800000 250000
fixed_array 2 npn_10p00x10p00 800000 300000
fixed_array 2 pnp_05p00x00p42 800000 350000
fixed_array 2 pnp_05p00x05p00 800000 400000
fixed_array 2 pnp_10p00x00p42 800000 450000
fixed_array 2 pnp_10p00x10p00 800000 500000

save torture_test_gf180mcu
gds write torture_test_gf180mcu
