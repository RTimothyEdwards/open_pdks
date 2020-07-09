Open-PDKs (open_pdks)
-----------------------------------------

Summary:

Automatic setup of PDKs for open-source tools from foundry sources.

Builds out and populates a new set of directories and subdirectories in
the efabless format, with the efabless name for the PDK at the top,
followed by categories "libs.ref" (IP) and "libs.tech" (EDA tool setup),
each with subcategories corresponding to layout, abstract views,
netlists, etc. for the IP;  and magic, netgen, qflow, etc., for the
EDA tool setup.

The populated PDK directories can contain either copies of files from
the foundry sources, links to the foundry sources, or links back to
another PDK.

Generates magic layout views for all vendor IP for which either a GDS
view or a LEF view exists.  Annotates the views as needed to handle
ports, bounding boxes, etc.

-----------------------------------------

This distribution contains sources for building out the SkyWater s8
130nm process.  Sources for the foundry process data must be obtained
separately.  Read the README file in subdirectory s8/ for instructions
on obtaining and building the SkyWater s8 PDK.

-----------------------------------------

License:

Open_PDKs is open-source software distributed under the Apache-2.0 license.
See file LICENSE for the complete license text.

-----------------------------------------

Instructions:

There is a top-level Makefile but generally it is recommended to cd
to the directory for the target foundry process and follow the instructions
in the README file there.

Also see the website at http://opencircuitdesign.com/open_pdks

