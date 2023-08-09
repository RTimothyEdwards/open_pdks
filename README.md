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

This distribution contains sources for building out the SkyWater SKY130
130nm process.  Sources for the foundry process data must be obtained
separately.  Read the README file in subdirectory sky130/ for instructions
on obtaining and building the SkyWater sky130A PDK.

-----------------------------------------

License:

Open_PDKs is open-source software distributed under the Apache-2.0 license.
See file LICENSE for the complete license text.

-----------------------------------------

Instructions:

    git clone https://github.com/RTimothyEdwards/open_pdks.git
    cd open_pdks
    ./configure [options]
    make
    [sudo] make install

where the configure [options] are specific to each foundry PDK supported
by open_pdks and can be queried using

    ./configure --help

At a minimum you will want to pass a configure option to declare the PDK
that you want to build.  It is possible to build multiple PDKs at once,
but not recommended due to the large memory and disk space overhead
required by each one.

    ./configure --enable-[PDK_name]-pdk

The open_pdks version of the PDK can be built locally within open_pdks without
the need to declare an install target or run "make install".  However, it is
highly recommended to declare a target location and install there, using

    ./configure --prefix=[path] --enable-[PDK_name]-pdk

followed by "make" and "make install".  The default install location is
/usr/local/share/pdk ([path] above is /usr/local).  The install location
should be a read-only filesystem area for regular users, since the PDK
contents should not be altered.

Also see the website at http://opencircuitdesign.com/open_pdks/.  The "Install"
page has full instructions for configuring and installing open_pdks.

