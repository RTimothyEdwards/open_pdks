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

# exit when any command fails
set -e

mkdir pdks
export OPEN_PDKS_ROOT=$(pwd)
export PDK_ROOT=$(pwd)/pdks
cd ./.travisCI
sh ./build-docker.sh > /dev/null
make skywater-pdk > /dev/null
if [ $STD_CELL_LIBRARY == all ]; then
    cnt=0
    until make all-skywater-libraries; do
    cnt=$((cnt+1))
    if [ $cnt -eq 5 ]; then
        exit 2
    fi
    rm -rf $PDK_ROOT/skywater-pdk
    make skywater-pdk > /dev/null
    done
else
    cnt=0
    until make skywater-library; do
    cnt=$((cnt+1))
    if [ $cnt -eq 5 ]; then
        exit 2
    fi
    rm -rf $PDK_ROOT/skywater-pdk
    make skywater-pdk > /dev/null
    done
fi
cd ..
docker run -it -v $(pwd):/some_root -v $(pwd)/.travisCI:/build_root -v $OPEN_PDKS_ROOT:$OPEN_PDKS_ROOT -v $PDK_ROOT:$PDK_ROOT -e OPEN_PDKS_ROOT=$OPEN_PDKS_ROOT -e PDK_ROOT=$PDK_ROOT -u $(id -u $USER):$(id -g $USER) magic:latest  bash -c "cd /build_root && make build-pdk"
exit 0
