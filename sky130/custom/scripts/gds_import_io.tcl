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

### flatten within the isolated VSSIO domain
gds flatglob *sky130_fd_io__feas_com_pupredrvr*
gds flatglob *sky130_fd_io__com_pupredrvr_strong_slowv2*
gds flatglob *sky130_fd_io__com_pdpredrvr_pbiasv2*
gds flatglob *sky130_fd_io__gpiov2_pdpredrvr_strong*

### flatten in opathv2
gds flatglob *sky130_fd_io__com_pudrvr_strong_slowv2*
gds flatglob *sky130_fd_io__com_pdpredrvr_strong_slowv2*
gds flatglob *sky130_fd_io__gpiov2_obpredrvr*
gds flatglob *sky130_fd_io__hvsbt_*

### flatten in ipath
gds flatglob *sky130_fd_io__gpiov2_ictl_logic*

### avoid splitting a netlist that passes in contorted ways through the
### layout hierarchy
gds flatglob *sky130_fd_io__gpio_pddrvr_strong_slowv2*
gds flatglob *sky130_fd_io__gpiov2_pddrvr_strong*

### flatten ESD devices in SIO.  Note:  HVI covering the entire device
### in nhvnative cell would avoid this issue.
gds flatglob *reg_pu_nhvnative*
gds flatglob *pu_natives*
