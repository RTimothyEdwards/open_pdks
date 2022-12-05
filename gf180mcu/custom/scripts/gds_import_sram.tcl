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
# Ensure unique cell names when reading multiple GDS files
calma unique true
