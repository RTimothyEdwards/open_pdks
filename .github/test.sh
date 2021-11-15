#!/bin/bash
# Copyright 2020 Efabless Corporation
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

du -h $SKY130_DIR

echo ::group::Output files
echo
find $SKY130_DIR | sort
echo
echo ::endgroup::

SIZE=$(du -sb $SKY130_DIR | cut -f1)
# 250MB = 131,072,000 bytes; a fair estimate of the size of one library, I guess.
if [[ $SIZE -lt 131072000 ]]; then
    echo 'size is less than 125MB'
    exit -1
fi
echo 'Built without fatal errors'
echo "sky130A size is $SIZE bytes"
exit 0
