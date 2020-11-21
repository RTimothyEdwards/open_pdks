#-------------------------------------------------------------------
# General-purpose routines for the PDK script in all technologies
#-------------------------------------------------------------------
# 
#----------------------------------------
# Number Conversion Functions
#----------------------------------------

#---------------------
# Microns to Lambda
#---------------------
proc magic::u2l {micron} {
    set techlambda [magic::tech lambda]
    set tech1 [lindex $techlambda 1]
    set tech0 [lindex $techlambda 0]
    set tscale [expr {$tech1 / $tech0}]
    set lambdaout [expr {((round([magic::cif scale output] * 10000)) / 10000.0)}]
    return [expr $micron / ($lambdaout*$tscale) ]
}

#---------------------
# Lambda to Microns
#---------------------
proc magic::l2u {lambda} {
    set techlambda [magic::tech lambda]
    set tech1 [lindex $techlambda 1] ; set tech0 [lindex $techlambda 0]
    set tscale [expr {$tech1 / $tech0}]
    set lambdaout [expr {((round([magic::cif scale output] * 10000)) / 10000.0)}]
    return [expr $lambda * $lambdaout * $tscale ]
}

#---------------------
# Internal to Microns
#---------------------
proc magic::i2u { value } {
    return [expr {((round([magic::cif scale output] * 10000)) / 10000.0) * $value}]
}

#---------------------
# Microns to Internal
#---------------------
proc magic::u2i {value} {
    return [expr {$value / ((round([magic::cif scale output] * 10000)) / 10000.0)}]
}

#---------------------
# Float to Spice 
#---------------------
proc magic::float2spice {value} { 
    if {$value >= 1.0e+6} { 
	set exponent 1e+6
	set unit "meg"
    } elseif {$value >= 1.0e+3} { 
	set exponent 1e+3
	set unit "k"
    } elseif { $value >= 1} { 
	set exponent 1
	set unit ""
    } elseif {$value >= 1.0e-3} { 
	set exponent 1e-3
	set unit "m"
    } elseif {$value >= 1.0e-6} { 
	set exponent 1e-6
	set unit "u"
    } elseif {$value >= 1.0e-9} { 
	set exponent 1e-9
	set unit "n"
    } elseif {$value >= 1.0e-12} { 
	set exponent 1e-12
	set unit "p"
    } elseif {$value >= 1.0e-15} { 
	set exponent 1e-15
	set unit "f"
    } else {
	set exponent 1e-18
	set unit "a"
    }
    set val [expr $value / $exponent]
    set val [expr int($val * 1000) / 1000.0]
    if {$val == 0} {set unit ""}
    return $val$unit
}

#---------------------
# Spice to Float
#---------------------
proc magic::spice2float {value {faultval 0.0}} { 
    # Remove trailing units, at least for some common combinations
    set value [string tolower $value]
    set value [string map {um u nm n uF n nF n pF p aF a} $value]
    set value [string map {meg "* 1.0e6" k "* 1.0e3" m "* 1.0e-3" u "* 1.0e-6" \
		 n "* 1.0 e-9" p "* 1.0e-12" f "* 1.0e-15" a "* 1.0e-15"} $value]
    if {[catch {set rval [expr $value]}]} {
	puts stderr "Value is not numeric!"
	set rval $faultval
    }
    return $rval
}

#---------------------
# Numeric Precision
#---------------------
proc magic::3digitpastdecimal {value} {
    set new [expr int([expr $value * 1000 + 0.5 ]) / 1000.0]
    return $new
}

#-------------------------------------------------------------------
# File Access Functions
#-------------------------------------------------------------------

#-------------------------------------------------------------------
# Ensures that a cell name does not already exist, either in
# memory or on disk. Modifies the name until it does.
#-------------------------------------------------------------------
proc magic:cellnameunique {cellname} {
    set i 0
    set newname $cellname
    while {[cellname list exists $newname] != 0 || [magic::searchcellondisk $newname] != 0} {
	incr i
	set newname ${cellname}_$i
    }
    return $newname
}

#-------------------------------------------------------------------
# Looks to see if a cell exists on disk
#-------------------------------------------------------------------
proc magic::searchcellondisk {name} {
    set rlist {}
    foreach dir [path search] {
	set ftry [file join $dir ${name}.mag]
	if [file exists $ftry] {
	    return 1
	}
    }
    return 0
} 

#-------------------------------------------------------------------
# Checks to see if a cell already exists on disk or in memory
#-------------------------------------------------------------------
proc magic::iscellnameunique {cellname} {
    if {[cellname list exists $cellname] == 0 && [magic::searchcellondisk $cellname] == 0} { 
	return 1
    } else {
	return 0
    }
}

#--------------------------------------------------------------
# Procedure that checks the user's "ip" subdirectory on startup
# and adds each one's maglef subdirectory to the path.
#--------------------------------------------------------------

proc magic::query_mylib_ip {} {
    global TECHPATH
    global env
    if [catch {set home $env(SUDO_USER)}] {
        set home $env(USER)
    }
    set homedir /home/${home}
    set ip_dirs [glob -directory ${homedir}/design/ip *]
    set proj_dir [pwd]
    set config_dir .config
    set info_dir ${proj_dir}/${config_dir}
    if {![file exists ${info_dir}]} {
	set config_dir .ef-config
	set info_dir ${proj_dir}/${config_dir}
    }

    set info_file ${info_dir}/info
    set depends [dict create]
    if {![catch {open $info_file r} ifd]} {
        set depsec false
        while {[gets $ifd line] >= 0} {
	    if {[string first dependencies: $line] >= 0} {
	        set depsec true
	    }
	    if {$depsec} {
		if {[string first version: $line] >= 0} {
		    if {$ipname != ""} {
			set ipvers [string trim [lindex [split $line] 1] ']
			dict set depends $ipname $ipvers
			set ipname ""
		    } else {
			puts stderr "Badly formatted info file in ${config_dir}!"
		    }
		} else {
		    set ipname [string trim $line :]
		}
	    }
	}
    }

    foreach dir $ip_dirs {
	# Version handling:  version dependencies are found in
	# ${config_dir}/info.  For all other IP, use the most recent
	# version number.
	set ipname [lindex [file split $dir] end]
	if {![catch {set version [dict get $depends $ipname]}]} {
	    if {[file isdirectory ${dir}/${version}/maglef]} {
		addpath ${dir}/${version}/maglef
		continue
	    } else {
		puts stderr "ERROR:  Dependency ${ipname} version ${version} does not exist"
	    }
	}

	# Secondary directory is the version number.  Use the highest
	# version available.

	set sub_dirs {}
        catch {set sub_dirs [glob -directory $dir *]}
	set maxver 0.0
	foreach subdir $sub_dirs {
	    set vidx [string last / $subdir]
	    incr vidx
	    set version [string range $subdir $vidx end]
	    if {$version > $maxver} {
		set maxver $version
	    }
	}
	if {[file exists ${dir}/${maxver}/maglef]} {
	    # Compatibility rule:  foundry name must match.
	    # Get foundry name from ${config_dir}/techdir symbolic link reference
	    if {[file exists ${dir}/${maxver}/${config_dir}/techdir]} {
		set technodedir [file link ${dir}/${maxver}/${config_dir}/techdir]
		set nidx [string last / $technodedir]
		set techdir [string range $technodedir 0 $nidx-1]
		if {$techdir == $TECHPATH} {
		    addpath ${dir}/${maxver}/maglef
		}
	    }
	}
    }
}

#--------------------------------------------------------------
# Procedure that checks the user's design directory on startup
# and adds each one's mag subdirectory to the path.
#--------------------------------------------------------------

proc magic::query_my_projects {} {
    global TECHPATH
    global env
    if [catch {set home $env(SUDO_USER)}] {
        set home $env(USER)
    }
    set homedir /home/${home}
    set proj_dirs [glob -directory ${homedir}/design *]
    foreach dir $proj_dirs {
	# Compatibility rule:  foundry name must match.
	# Get foundry name from ${config_dir}/techdir symbolic link reference
	if {[file exists ${dir}/mag]} {
	    set config_dir .config
	    set tech_dir ${dir}/${config_dir}
	    if {![file exists ${tech_dir}]} {
		set config_dir .ef-config
		set tech_dir ${dir}/${config_dir}
	    }
	    if {[file exists ${dir}/${config_dir}/techdir]} {
		set technodedir [file link ${dir}/${config_dir}/techdir]
		set nidx [string last / $technodedir]
		set techdir [string range $technodedir 0 $nidx-1]
		if {$techdir == $TECHPATH} {
		    addpath ${dir}/mag
		}
	    }
	}
    }
}

#----------------------------------------------------------------
