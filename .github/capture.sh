#!/bin/bash
# Copyright 2021 Open PDKs Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

mkdir -p ${GITHUB_WORKSPACE}/output/

# Copy build log.
cp ./sky130/sky130A_install.log ${GITHUB_WORKSPACE}/output/

# Copy any core dupmps into the output directory.
find . -name core -not \( -path '*/skywater-pdk/*' -prune \) | \
	awk -v ln=1 '{print "cp " $0 " ${GITHUB_WORKSPACE}/output/core." ln++ }' | \
	bash

# Copy the magic tarball into output
cp .github/magic.tar.gz ${GITHUB_WORKSPACE}/output/

# Try to create a deterministic tar file
# https://reproducible-builds.org/docs/archives/
(
	SKY130_DIR="$(pwd)/pdks/pdk/sky130A"
	if ! [[ -d $SKY130_DIR ]]; then
	    echo "Missing $SKY130_DIR"
	    exit -1
	fi

	echo ::group::PDK tarball

	cd ${SKY130_DIR}
	tar \
		--create \
		--bzip2 \
		--verbose \
		\
		--mtime='2020-05-07 00:00Z' \
		--sort=name \
		--owner=0 \
		--group=0 \
		--numeric-owner \
		--pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
		\
		--file ${GITHUB_WORKSPACE}/output/pdk-SKY130A-${STD_CELL_LIBRARY}.tar.bz2 .

	echo ::endgroup::
)

# Free up disk space so the GitHub Action runner doesn't die when collecting
# the artifacts.
echo ::group::Freeup space

df -h

for DIR in ${GITHUB_WORKSPACE}/*; do
	if [ x$DIR = x"${GITHUB_WORKSPACE}/output" ]; then
		continue
	fi
	echo
	echo "Removing $DIR"
	rm -rvf $DIR
done

df -h

echo ::endgroup::

# Output which files are being saved.
echo ::group::Output files
du -h  ${GITHUB_WORKSPACE}/output/*
echo ::endgroup::

exit 0
