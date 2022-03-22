#!/bin/bash
#
#  pdk_update.sh --
#
#	Update the PDK from git
# 	(mainly for use with the Google/SkyWater SKY130 PDK)
#
#  Usage:	pdk_update.sh <directory>
#

if [ ! -d $1 ] ; then
    echo "Project does not exist in $1 ;  Cannot update."
    exit 0
fi

cd $1

# Update top-level PDK repository

echo "Pulling PDK repository"
git pull

# Update submodules

echo "Updating PDK library submodules"
git submodule update --remote

# Regenerate liberty files

echo "Regenerating liberty timing files"
make -j$(nproc) timing
