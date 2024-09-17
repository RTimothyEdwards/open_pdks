These decap cells were redesigned to cut back on its use of the LI layer because the corresponding SkyWater cell was covered in something like 70-80% LI, and using enough of the decap in any one design would cause an LI density error.

The fill cells were redesigned to add tap diffusion in the middle because otherwise the spacing of the nwells and the height of the cells prevents FOM fill, resulting in a different density error.

Cell "newfill_12" was added to satisfy the change in the poly density rule to 38%;  this cell is effectively the decap_12 cell with the poly removed, rendering it a fill cell.  Its use is to replace some percentage of decap_12 cells until the maximum poly density rule is satisfied.
