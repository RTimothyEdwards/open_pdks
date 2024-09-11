These decap cells were redesigned to cut back on its use of the LI layer because the corresponding SkyWater cell was covered in something like 70-80% LI, and using enough of the decap in any one design would cause an LI density error.

The fill cells were redesigned to add tap diffusion in the middle because otherwise the spacing of the nwells and the height of the cells prevents FOM fill, resulting in a different density error.

The conb cell was altered to make the npc layer more compatible with the other cells. Previously it would generate npc.2 DRC errors when placed next to some of the cells.
