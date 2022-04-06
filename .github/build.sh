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

export OPEN_PDKS_ROOT=$(pwd)
export PDK_ROOT=$(pwd)/pdks
mkdir -p $PDK_ROOT

cd .github

echo ::group::.github/build-docker.sh
bash ./build-docker.sh
echo ::endgroup::

echo ::group::make skywater-pdk
make skywater-pdk
echo ::endgroup::

cd ..

docker run \
	\
	-v $(pwd):/some_root \
	-v $(pwd)/.github:/build_root \
	-v $OPEN_PDKS_ROOT:$OPEN_PDKS_ROOT \
	-v $PDK_ROOT:$PDK_ROOT \
	\
	-e OPEN_PDKS_ROOT=$OPEN_PDKS_ROOT \
	-e PDK_ROOT=$PDK_ROOT \
	-u $(id -u $USER):$(id -g $USER) \
	\
	magic:latest \
	\
	bash -c "cd /build_root && make build-pdk"
exit 0
