#!/bin/bash
#
echo -n 'Select PDK to extract fixed devices from [gf180/sky130] ' 
read PDK

# set path for .mag fd files
case $PDK in
	sky130 ) filepath="/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_pr/mag/" ;;
	gf180  ) filepath="/usr/local/share/pdk/gf180mcuD/libs.ref/gf180mcu_fd_pr/mag/" ;;
	*      ) echo "Wrong PDK entered. Please rerun the script and enter sky130 or gf180"
		     exit 1 ;; 
esac

device_name=($(find "$filepath/" -name '*.mag' -printf "%f " | sed 's/.mag//g'))
routine_name=(dialog defaults draw check convert)

# set tabulation (\t charecters) to be 4 whitespaces 
tabs 4

output_file=$(printf "%s.tcl" $PDK)
printf " " > $output_file
for routine in "${routine_name[@]}";do 
	printf "\n#-----------------\n#%s\n#-----------------\n" \
				"$routine" \
				>> $output_file
	for device in "${device_name[@]}"; do 

		# set the text of the proc body 
		case $routine in
			defaults ) proc_text=$(printf "return {nx 1 ny 1 deltax 0 deltay 0 nocell 1 xstep 1000 ystep 1000}" ) ;;
			dialog   ) proc_text=$(printf "%s::fixed_dialog \$parameters " \
				                          "$PDK" ) ;;
			draw     ) proc_text=$(printf "return [%s::fixed_draw %s \$parameters] " \
				                          "$PDK" \
										  "$device") ;;
			check    ) proc_text=$(printf "return [%s::fixed_check \$parameters] " \
				                          "$PDK" ) ;;
			convert  ) proc_text=$(printf "return [%s::fixed_convert \$parameters] " \
				                          "$PDK" ) ;;
		esac

		# write the procedures to the output file
		case $routine in
			# defaults procedure
			defaults )  printf "proc %s::%s_%s {} {\n\t%s \n} \n" \
							"$PDK" \
							"$device" \
							"$routine" \
							"$proc_text" \
							>> $output_file ;;
			# all other procedures
			*        )  printf "proc %s::%s_%s {parameters} {\n\t%s \n} \n" \
							"$PDK" \
							"$device" \
							"$routine" \
							"$proc_text" \
							>> $output_file ;;
		esac	
	done 
done


