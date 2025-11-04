# Set GDS import styles as needed to deal with the SRAM layouts.
gds flatten true
gds flatglob *$$*
gds flatglob M1_N*
gds flatglob M1_P*
gds flatglob M2_M1*
gds flatglob M3_M2*
gds flatglob nmos_5p0*
gds flatglob nmos_1p2*
gds flatglob pmos_5p0*
gds flatglob pmos_1p2*
gds flatglob via1_*
gds flatglob ypass_gate*
gds flatglob G_ring_*
# These additional cells must be flattened to get rid of 3.3V devices
# (DUALGATE drawn into high-level cells)
gds flatglob dcap_103*
gds flatglob din_*
gds flatglob mux821_*
gds flatglob rdummy_*
gds flatglob pmoscap_*
gds flatglob xdec_*
gds flatglob ypredec*
gds flatglob xpredec*
gds flatglob xdec8_*
gds flatglob prexdec_*
gds flatglob xdec32_*
gds flatglob sa_*
# Ensure unique cell names when reading multiple GDS files
calma unique true
