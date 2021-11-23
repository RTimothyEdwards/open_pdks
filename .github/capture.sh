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

SKY130_DIR="$(pwd)/pdks/pdk/sky130A"
if ! [[ -d $SKY130_DIR ]]; then
    echo "Missing $SKY130_DIR"
    exit -1
fi

# Try to create a deterministic tar file
# https://reproducible-builds.org/docs/archives/
mkdir ${GITHUB_WORKSPACE}/output/
(
	cd ${SKY130_DIR}
	tar \
		--create \
		--xz \
		--verbose \
		\
		--mtime='2020-05-07 00:00Z' \
		--sort=name \
		--owner=0 \
		--group=0 \
		--numeric-owner \
		--pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
		\
		--file ${GITHUB_WORKSPACE}/output/pdk-SKY130A-${STD_CELL_LIBRARY}.tar.xz .
)
