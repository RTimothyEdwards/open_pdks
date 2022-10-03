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

# Copy any core dupmps into the output directory.
find . -name core -not \( -path '*/skywater-pdk/*' -prune \) | \
	awk -v ln=1 '{print "cp " $0 " ${GITHUB_WORKSPACE}/output/core." ln++ }' | \
	bash

# Copy the magic tarball into output
cp .github/magic.tar.gz ${GITHUB_WORKSPACE}/output/

# Try to create a deterministic tar file
# https://reproducible-builds.org/docs/archives/
(
	HSPICE_DIR="$(pwd)/sky130/sky130A/libs.tech/hspice"
	if ! [[ -d $HSPICE_DIR ]]; then
	    echo "Missing $HSPICE_DIR"
	    exit -1
	fi

	echo ::group::PDK tarball

	cd ${HSPICE_DIR}
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
		--file ${GITHUB_WORKSPACE}/output/hspice-model.tar.bz2 .

	echo ::endgroup::
)

# Output which files are being saved.
echo ::group::Output files
du -h  ${GITHUB_WORKSPACE}/output/*
echo ::endgroup::

exit 0
