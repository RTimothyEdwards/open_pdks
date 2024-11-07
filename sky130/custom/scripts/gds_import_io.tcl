cif istyle sky130()
#
gds flatten true
gds flatglob *_CDNS_*
gds flatglob *_cdns_*
gds flatglob *sky130_fd_pr__*_example_*

# ! flatten the 120x2 ESD device
gds flatglob *sky130_fd_io__gnd2gnd_*

# The following cells have to be flattened for the gpiov2 pad to read in
# correctly, and produce a layout that can be extracted and generate an
# LVS clean netlist.

### flatten within the analog mux isolated P region
gds flatglob *sky130_fd_io__amx*
gds flatglob *sky130_fd_io__xor*
gds flatglob *sky130_fd_io__gpiov2_amx*
gds flatglob *sky130_fd_io__gpiov2_amux*
gds flatglob *sky130_fd_io__gpio_ovtv2_amx*
gds flatglob *sky130_fd_io__gpio_ovtv2_amux*

### flatten within the isolated VSSIO domain
gds flatglob *sky130_fd_io__feas_com_pupredrvr*
gds flatglob *sky130_fd_io__com_pupredrvr_strong_slowv2*
gds flatglob *sky130_fd_io__com_pdpredrvr_pbiasv2*
gds flatglob *sky130_fd_io__gpiov2_pdpredrvr_strong*
gds flatglob *sky130_fd_io__gpio_ovtv2_pdpredrvr_strong*
gds flatglob *sky130_fd_io__sio_pdpredrvr_strong*

### flatten in opathv2
gds flatglob *sky130_fd_io__com_pudrvr_strong_slowv2*
gds flatglob *sky130_fd_io__com_pdpredrvr_strong_slowv2*
gds flatglob *sky130_fd_io__gpiov2_obpredrvr*
gds flatglob *sky130_fd_io__gpio_ovtv2_obpredrvr*
gds flatglob *sky130_fd_io__gpio_ovtv2_hotswap*
gds flatglob *sky130_fd_io__sio_obpredrvr*
gds flatglob *sky130_fd_io__hvsbt_*

### flatten in ipath
gds flatglob *sky130_fd_io__gpiov2_ictl_logic*
gds flatglob *sky130_fd_io__gpio_ovtv2_ictl_logic*

### avoid splitting a netlist that passes in contorted ways through the
### layout hierarchy
gds flatglob *sky130_fd_io__gpio_pddrvr_strong_slowv2*
gds flatglob *sky130_fd_io__gpiov2_pddrvr_strong*
gds flatglob *sky130_fd_io__gpio_ovtv2_pddrvr_strong*
gds flatglob *sky130_fd_io__sio_pddrvr_strong*

### flatten ESD devices in SIO.  Note:  HVI covering the entire device
### in nhvnative cell would avoid this issue.
gds flatglob *reg_pu_nhvnative*
gds flatglob *pu_natives*
# Other flattening needed for SIO (possibly this could be more targeted)
gds flatglob *__sio_hotswap*

### flatten parts of pwrdetv2, where there are devices in deep nwell
### that are in sibling cells, and resistors separated from HVI
gds flatglob *top_pwrdetv2_res*
gds flatglob *pwrdet_vddd*
gds flatglob *pwrdet_vddio*

### flatten parts of amuxsplitv2, where there are subcells that are
### spread across areas inside and outside of dnwell
gds flatglob *switch_levelshifter*
gds flatglob *amuxsplitv2_switch_*
gds flatglob *amuxsplitv2_hvsbt_nand*
gds flatglob *amuxsplitv2_delay*

### flatten parts of refgen_new, where there are subcells that are
### spread across areas inside and outside of dnwell
gds flatglob *refgen_ctl*
gds flatglob *__opamp_*
gds flatglob *refgen_vdda*
gds flatglob *refgen_t_switch*
