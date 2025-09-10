Open-PDKs (open_pdks)
-----------------------------------------

Summary:

Automatic setup of PDKs for open-source tools from foundry sources.

Builds out and populates a new set of directories and subdirectories in
the open source format (started by Efabless), with the name for the PDK
at the top, followed by categories "libs.ref" (IP) and "libs.tech"
(EDA tool setup), each with subcategories corresponding to layout,
abstract views, netlists, etc. for the IP;  and magic, netgen, qflow,
etc., for the EDA tool setup.

The populated PDK directories can contain either copies of files from
the foundry sources, links to the foundry sources, or links back to
another PDK.

Generates magic layout views for all vendor IP for which either a GDS
view or a LEF view exists.  Annotates the views as needed to handle
ports, bounding boxes, etc.

-----------------------------------------

This distribution contains sources for building out the SkyWater SKY130
130nm process and the GlobalFoundries GF180MCU process.  Sources for the
foundry process data are cloned automatically from repository services
(primarily github).

Other non-free processes (such as X-Fab XH035 or XH018) can be obtained
as "plug-ins" for open_pdks.  Sources for non-free foundry process data
must be obtained separately.

Read the README file in subdirectory sky130/ for instructions on building
the SkyWater sky130A PDK, or in the directory gf180mcu/ for instructions
on building the GlobalFoundries gf180MCU PDK.

-----------------------------------------

License:

Open_PDKs is open-source software distributed under the Apache-2.0 license.
See file LICENSE for the complete license text.

-----------------------------------------

"Ciel" package manager:

An important consideration for anyone wishing to obtain one of the open
source PDKs is that "open_pdks" is a PDK builder, and running it is like
running a compiler to build a complex software application.  Doing so
can be difficult, time consuming, and resource-intensive.  The software
world came up with the idea of a "package manager" application that
handles pre-built software.  Likewise, there is a "PDK package manager"
for handling pre-built PDKs, called "ciel" (formerly called "volare"),
which can be found at https://github.com/fossi-foundation/ciel;
However, "ciel" can be installed simply by doing:

	pip install ciel

Most PDK end-users are likely to want this option.  The "pip install"
command will put "ciel" in ~/.local/bin/ciel where it may be necessary
to either call it with the full path on the command line, or you may
need to add "~/.local/bin" to your PATH environment variable.  Assuming
it is in PATH, use the following commands:

	ciel ls-pdks

returns a list of processes supported by ciel.  To get a list of
pre-built PDKs, use, e.g.,

	ciel ls-remote --pdk-family=sky130

which lists PDKs by commit hash number.  Then to install the PDK, use, e.g.,

	ciel enable --pdk-family=sky130 <commit_hash>

The PDK will be installed into directory ~/.ciel/.  Most open source
EDA tools will be able to find the PDK if the environment variable
"PDK_ROOT" is set to point to this location:

	export PDK_ROOT=~/.ciel

for bash/sh environments, and

	setenv PDK_ROOT ~/.ciel

for csh/tcsh environments.

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

-----------------------------------------

Example usage:

    SkyWater sky130 PDK:

	./configure --prefix=/usr --enable-sky130-pdk --enable-sram-sky130 \
		--enable-sram-space-sky130 --enable-reram-sky130
	make
	sudo make install

    GlobalFoundries GF180MCU PDK:

	./configure --prefix=/usr --enable-gf180mcu-pdk
	make
	sudo make install

    Both of these examples install into the directory /usr/share/pdk/.
    The first one builds PDKs sky130A (standard) and sky130B (with the
    ReRAM option).  The second one builds PDKs gf180mcuA (3 metal stack),
    gf180mcuB (4 metal stack), gf180mcuC (5 metal stack with 0.9um thick
    top metal), and gf180mcuD (5 metal stack with 1.1um thick top metal).

    Existing shuttle services as of this writing (September 2025) use
    sky130A, sky130B (Cadence, Chip Foundry), and gf180mcuD
    (Wafer.Space).

    Given the configurations above with prefix "/usr", most open source
    tools will expect

	export PDK_ROOT=/usr/share/pdk		(sh, bash)
    or
	setenv PDK_ROOT /usr/share/pdk		(csh, tcsh)

-----------------------------------------

A note about IHP SG13G2:

    IHP GmbH released their open PDK for the SG13G2 process using
    the format described in open_pdks.  For this reason, there is
    no need to use open_pdks to build the IHP open PDK, because it
    already comes pre-built, with full support for open source EDA
    tools.  Also for this reason, the SG13G2 open PDK is supported
    by the "ciel" PDK package manager (see above).
