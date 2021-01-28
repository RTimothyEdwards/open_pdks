# SPDX-FileCopyrightText: 2020 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-License-Identifier: Apache-2.0

namespace path {::tcl::mathop ::tcl::mathfunc}

#-----------------------------------------------------------------------
# Routines for generating bump bonds.
# Use with "micross.tech" technology file.
#
# SkyWater top layers:
# 	m5	metal5 (thick top metal)
#	glass	polyimide (glass) cut
#	
# Bump bond layers:
#	p1	polyimide via
#	rdl	redistribution metal
#	p2	polyimide via2
#	ubm	under-bump material
# 
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# Internal units to microns conversion
#-----------------------------------------------------------------------

proc magic::i2u {value} {
    return [expr {((round([magic::cif scale output] * 10000)) / 10000.0) * $value}]
}

#-----------------------------------------------------------------------
# Microns to internal units conversion
#-----------------------------------------------------------------------

proc magic::u2i {value} {
    return [expr {$value / ((round([magic::cif scale output] * 10000)) / 10000.0)}]
}

#-----------------------------------------------------------------------
# make_bump_bond ---
#-----------------------------------------------------------------------
# Description:
#	Create geometry for a bump bond in a subcell, centered at the
#	origin.  The bump bond itself is a circle (approximated by a
#	36-sided polygon) of diameter nominally 250um.  The RDL layer
#	is 10um larger (rule M4) and the under-bump material layer is
#	15um smaller (rule U4).
#
# Arguments:
#	angle:	0 or 45
#
#	The angle represents the direction toward which the taper of
#	the RDL layer points.  The angle is appended to the subcell
#	name, so the cell is "bump_bond0" or "bump_bond45".
#
#	The version with suffix "45" has the RDL tapering toward the
#	NE corner when the cell is in its natural orientation.  The
#	version suffix "0" has the RDL tapering toward the E side when
#	the cell is in its natural orientation.
#
#-----------------------------------------------------------------------

proc make_bump_bond {{orient 0}} {
    suspendall
    select top cell
    set orig_cell [cellname list self]

    load bump_bond${orient} -quiet
    box values 0 0 0 0

    set rbump 125.0	;# under-bump material radius, in microns
    set coords []
    for {set i 0} {$i < 36} {incr i} {
        set angle [* $i 10]
        set arad [/ [* 3.1415926 $angle] 180.0]
        lappend coords [* $rbump [cos $arad]]um
        lappend coords [* $rbump [sin $arad]]um
    }
    polygon ubm {*}$coords

    set rbump 110.0	;# polyimide 2 via radius, in microns
    set coords []
    for {set i 0} {$i < 36} {incr i} {
        set angle [* $i 10]
        set arad [/ [* 3.1415926 $angle] 180.0]
        lappend coords [* $rbump [cos $arad]]um
        lappend coords [* $rbump [sin $arad]]um
    }
    polygon pi2 {*}$coords

    set rbump 135.0	;# rdl layer radius, in microns
    set rdiag [expr {$rbump * sqrt(2.0)}]
    set coords []

    if {$orient == 45} {
    	for {set i 9} {$i <= 36} {incr i} {
            set angle [* $i 10]
            set arad [/ [* 3.1415926 $angle] 180.0]
            lappend coords [* $rbump [cos $arad]]um
            lappend coords [* $rbump [sin $arad]]um
    	}
    	lappend coords ${rbump}um
    	lappend coords ${rbump}um
    } else {
    	for {set i 0} {$i <= 27} {incr i} {
            set angle [* [+ $i 4.5] 10]
            set arad [/ [* 3.1415926 $angle] 180.0]
            lappend coords [* $rbump [cos $arad]]um
            lappend coords [* $rbump [sin $arad]]um
    	}
    	lappend coords ${rdiag}um
    	lappend coords 0
    }
    polygon rdl {*}$coords

    # Make cell bound that encompasses the rdl circle only
    box grow c ${rbump}um
    set bounds [box values]
    property FIXED_BBOX "$bounds"

    load $orig_cell
    resumeall
}

#-----------------------------------------------------------------------
# draw_bump_bond ---
#-----------------------------------------------------------------------
# Description:
#	Bump bond is a circle (approximated by a 36-sided polygon) of
#	diameter nominally 250um.
#
#
# Arguments:
#	x y	:  Coordinates of the bump bond center position, in microns
#	orient	:  Direction of tapered RDL joining the pad to a route
#		   value is in integer degrees, 0 is oriented E (east),
#		   and value must be a multiple of 45.
#-----------------------------------------------------------------------

proc draw_bump_bond {x y {orient 0}} {
    suspendall
    box size 0 0
    box position ${x}um ${y}um
    if {[% $orient 90] != 0} {
	set bondcell bump_bond45
	set orient [- $orient 45]
    } else {
	set bondcell bump_bond0
    }

    if {$orient < 0} {
	set orient [+ 360 $orient]
    }
    if {$orient != 0} {
        set orient [- 360 $orient]
    }
    getcell $bondcell $orient child 0 0
    resumeall
}

#-----------------------------------------------------------------------
# bevel_corners ---
#-----------------------------------------------------------------------
# Description:
#	Bevel the corners of the indicated layer in the current box
#	with the indicated bevel length
#
# Arguments:
#	layer	:  The layer to be cropped
#	length	:  The length of the bevel (in microns)
#-----------------------------------------------------------------------

proc bevel_corners {layer length} {
    suspendall
    snap internal
    pushbox
    set ilength [magic::u2i $length]
    set side [* $ilength 0.7071]
    set iside [expr {int($side)}]

    set padbox [box values]
    set boxwidth [- [lindex $padbox 2] [lindex $padbox 0]]
    set boxheight [- [lindex $padbox 3] [lindex $padbox 1]]

    set iwidth  [- $boxwidth $iside]
    set iheight [- $boxheight $iside]

    box size $iside $iside
    spliterase sw $layer

    box move n $iheight
    spliterase nw $layer

    box move e $iwidth
    spliterase ne $layer

    box move s $iheight
    spliterase se $layer

    popbox
    resumeall
}

#-----------------------------------------------------------------------
# draw_pad_bond ---
#-----------------------------------------------------------------------
# Description:
#	Draws layers over a wirebond pad to connect to the RDL layer
#
# Arguments:
#	x y	:  Coordinates of the bond pad center position, in microns
#-----------------------------------------------------------------------

proc draw_pad_bond {x y} {
    suspendall
    snap internal
    box values 0 0 0 0
    box position ${x}um ${y}um
    box grow c 50um

    # Make sure there is glass underneath.  If not, assume the square
    # center of a 60um x 70um bond pad (60um x 60um).
    select area glass
    set stuff [what -list]
    set layers [lindex $stuff 0]
    if {$layers == {}} {
    	box position ${x}um ${y}um
	box size 0 0
        box grow c 30um
    } else {
        set padbox [select bbox]
        box values {*}$padbox
    }
    # Satisfy rule V3:  P1 via inside pad cut by 10um
    box grow c -10um
    paint pi1
    bevel_corners pi1 7.5

    # Satisfy rule M3:  RDL overlap of P1 >= 10um
    box grow c 10um
    paint rdl
    bevel_corners rdl 10.0
    resumeall
}

#-----------------------------------------------------------------------
# draw_pad_route ---
#-----------------------------------------------------------------------
# Description:
#	Draws a route on the RDL layer connecting the points given in
#	the coordinate list.
#
# Arguments:
#	coords	:  List of coordinate pairs, in microns
#	width	:  Route width in microns, default 15
#-----------------------------------------------------------------------

proc draw_pad_route {coords {width 15.0}} {
    suspendall
    set icoords []
    foreach coord $coords {
        lappend icoords ${coord}um
    }
    wire segment rdl ${width}um {*}$icoords
    resumeall
}

