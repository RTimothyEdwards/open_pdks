These decap cells were redesigned to cut back on its use of the LI layer because the corresponding SkyWater cell was covered in something like 70-80% LI, and using enough of the decap in any one design would cause an LI density error.

The fill cells were redesigned to add tap diffusion in the middle because otherwise the spacing of the nwells and the height of the cells prevents FOM fill, resulting in a different density error.

Cell "newfill_12" was added to satisfy the change in the poly density rule to 38%;  this cell is effectively the decap_12 cell with the poly removed, rendering it a fill cell.  Its use is to replace some percentage of decap_12 cells until the maximum poly density rule is satisfied.

12/10/2024:  Cell "newfill_12" was removed and replace with (a modified version of) "fill_12", which serves the same purpose but avoids the error in "newfill_12" where the nwell did not extend to the edge and would cause nwell spacing violations.  Because SkyWater imposed stricter limits on poly density, cells "decap_20_12", "decap_40_12", "decap_60_12", and "decap_80_12" have been added to allow selection of poly densities in the decap (relative to the original cell) to meet an overall target poly density in a design.
