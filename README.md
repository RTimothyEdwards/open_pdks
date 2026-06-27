# Open PDKs

Automatic setup of PDKs for open-source tools from foundry sources.

Open PDKs currently has support for building the sky130 and gf180mcu PDK families for the SkyWater SKY130 and GlobalFoundries GF180MCU process.
Sources for the foundry process data are cloned automatically from repository services (primarily github).

Other non-free processes (such as X-Fab XH035 or XH018) can be obtained as "plug-ins" for Open PDKs.  Sources for non-free foundry process data must be obtained separately.

> [!NOTE]
> IHP GmbH released their open PDK for the SG13G2 process using
> the format described in Open PDKs.  For this reason, there is
> no need to use Open PDKs to build the IHP open PDK, because it
> already comes pre-built, with full support for open source EDA
> tools.  Also for this reason, the SG13G2 open PDK is supported
> by the "Ciel" PDK package manager (see below).

An important consideration for anyone wishing to obtain one of the open
source PDKs is that Open PDKs is a PDK builder, and running it is like
running a compiler to build a complex software application.  Doing so
can be difficult, time consuming, and resource-intensive.  The software
world came up with the idea of a "package manager" application that
handles pre-built software.  Likewise, there is a "PDK package manager"
for handling pre-built PDKs, called Ciel (formerly called Volare).

> [!TIP]
> You can find information on how to install Ciel here: https://github.com/fossi-foundation/ciel

Table of Contents:

- [Open PDKs Format](##open-pdks-format)
- [Build Instructions](##build-instructions)
- [Example Usage](##example-usage)
- [Licenses](##licenses)

## Open PDKs Format

### PDK Naming Conventions

For a given PDK, Open PDKs expects a single PDK family with one or more PDK variants.
PDK variants differ from one another, for example, by using a different metal stack or other process options.

| PDK family | PDK variant                                |
|------------|--------------------------------------------|
| sky130     | sky130A, sky130B                           |
| gf180mcu   | gf180mcuA, gf180mcuB, gf180mcuD, gf180mcuD |
| ...        | ...                                        |

The PDK variant is an extension of the PDK family name.

The PDK family and PDK variants can consist of letters (`a`-`z` and `A`-`Z`), digits (`0`-`9`) and underscores (`_`).
Please do not use hyphens (`-`), periods (`.`), commas (`,`), colons (`:`) or any other special punctuation (`@`, `#`, `!` etc.).

The `PDK_ROOT` environment variable points to a directory in which each the PDK variant has a subdirectory. The `PDK` environment variable contains the name of the PDK variant.

Therefore, the path `$PDK_ROOT/$PDK/` points to the PDK file structure of the specified PDK variant.

### IP Naming Conventions

IP libraries are named according to the following structure:

```
<pdk-family>_<tag>_[pr|sc|io|sram|...]
```

For example, `sky130_fd_sc_hd` is the foundry-provided high-density standard cell library for sky130.

The tag is chosen by the entity providing the IP. The `fd` tag is used when the IP library is foundry-provided. If you supply your own IP library, you can choose your own tag (that is not yet used). For example, `ef` was used by Efabless. 

IPs extend this structure after two underscores by their name:

```
<pdk-family>_<tag>_[pr|sc_<scl-name>|io|sram|...]__<ip-name>
```

For example `gf180mcu_fd_sc_mcu7t5v0__and2_1` is a two-input and gate with a buffer strength of one from the `gf180mcu_fd_sc_mcu7t5v0` standard cell library.

### Structuring the PDK

The general file structure of a PDK variant is as follows:

```
<pdk-variant>
├── libs.doc
├── libs.qa
├── libs.ref
└── libs.tech   
```

Within `libs.ref/` you can find the IP libraries:

```
libs.ref
├── <pdk-family>_fd_io              Foundry I/O cells
├── <pdk-family>_fd_pr              Foundry primitives (devices)
├── <pdk-family>_fd_sc_<scl-name>   Foundry standard cell library
...
```

Within an IP library you can find folders for the different views:

```
<pdk-family>_fd_io
├── cdl             CDL files
├── gds             FDS layout
├── lef             LEF files
├── lib             Liberty files
├── mag             Magic layout files
├── maglef          Magic LEF files
├── spice           Spice netlists
├── verilog         Verilog files
├── xschem          Xschem schematics
...
```

Within `libs.tech/` you can find the EDA tool setups:

```
libs.tech
├── klayout                     KLayout technolog files
├── librelane                   LibreLane setup
├── magic                       Magic setup and device generators
├── netgen                      Netgen setup 
...
```

Directories are typically named after the tools that use the files they contain.
Symbolic links are permitted within the PDK file structure to enable the sharing of common files and directories between PDK variants.

## Build Instructions

Read the README file in subdirectory sky130/ for instructions on building
the SkyWater sky130A PDK, or in the directory gf180mcu/ for instructions
on building the GlobalFoundries gf180MCU PDK.

Instructions:

```
git clone https://github.com/RTimothyEdwards/open_pdks.git
cd open_pdks
./configure [options]
make
[sudo] make install
```

where the configure [options] are specific to each foundry PDK supported
by Open PDKs and can be queried using

```
./configure --help
```

At a minimum you will want to pass a configure option to declare the PDK
that you want to build.  It is possible to build multiple PDKs at once,
but not recommended due to the large memory and disk space overhead
required by each one.

```
./configure --enable-[PDK_name]-pdk
```

The Open PDKs version of the PDK can be built locally within Open PDKs without
the need to declare an install target or run "make install".  However, it is
highly recommended to declare a target location and install there, using

```
./configure --prefix=[path] --enable-[PDK_name]-pdk
```

followed by "make" and "make install".  The default install location is
/usr/local/share/pdk ([path] above is /usr/local).  The install location
should be a read-only filesystem area for regular users, since the PDK
contents should not be altered.

Also see the website at http://opencircuitdesign.com/open_pdks/.  The "Install"
page has full instructions for configuring and installing Open PDKs.

## Example Usage

SkyWater sky130 PDK:

```
./configure --prefix=/usr --enable-sky130-pdk --enable-sram-sky130 \
	--enable-sram-space-sky130 --enable-reram-sky130
make
sudo make install
```

GlobalFoundries GF180MCU PDK:

```
./configure --prefix=/usr --enable-gf180mcu-pdk
make
sudo make install
```

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

```
export PDK_ROOT=/usr/share/pdk		(sh, bash)
or
setenv PDK_ROOT /usr/share/pdk		(csh, tcsh)
```

## Licenses

Open PDKs is open-source software distributed under the Apache-2.0 license.
See file LICENSE for the complete license text.
