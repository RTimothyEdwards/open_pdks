#!/bin/sh
#
#  pdk_download.sh --
#
#	Download and install a PDK from git
# 	(mainly for use with the Google/SkyWater SKY130 PDK)
#
#  Usage:	pdk_download.sh <url> <destination>
#

pdir=`dirname $2`
mkdir -p $pdir
cd $pdir

# Clone repository

echo "Cloning PDK repository"
git clone $1 $2

# Get submodules

echo "Getting PDK library submodules"
cd $2
for i in $(git submodule | grep /latest | awk '{print $2}'); do
	git submodule init $i
done
git submodule update

# Generate liberty files

echo "Building liberty timing files"
make timing
