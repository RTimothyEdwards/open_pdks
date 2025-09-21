# Set GDS import styles as needed to deal with the I/O cells.
# NOTE: "gds polygon subcells true" removed since magic v. 8.3.352
# no longer has the issue of slow reads of complex polygons.
# gds ordering on
# gds flatten true
# gds polygon subcells true
gds flatglob *_CDNS_*
