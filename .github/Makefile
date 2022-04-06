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

# Adopted from OpenLANE's Makefile.

OPEN_PDKS_ROOT ?= $(shell pwd)/..
THREADS ?= $(shell nproc)
SKYWATER_COMMIT ?= b5ff6174d9aa921f670f12a2893969fe4a516f6c

.DEFAULT_GOAL := all

.PHONY: all
all: pdk

.PHONY: pdk
pdk: skywater-pdk build-pdk

$(PDK_ROOT)/skywater-pdk:
	git clone https://github.com/google/skywater-pdk.git $(PDK_ROOT)/skywater-pdk

.PHONY: skywater-pdk
skywater-pdk: $(PDK_ROOT)/skywater-pdk
	cd $(PDK_ROOT)/skywater-pdk && \
		git checkout -qf $(SKYWATER_COMMIT)

.PHONY: build-pdk
build-pdk: $(PDK_ROOT)/skywater-pdk
	[[ -d $(PDK_ROOT)/sky130A ]] && \
		(echo "Warning: A sky130A build already exists under $(PDK_ROOT). It will be deleted first!" && \
		sleep 5 && \
		rm -rf $(PDK_ROOT)/sky130A) || \
		true
	cd $(OPEN_PDKS_ROOT) && \
		./configure \
			--prefix=$(PDK_ROOT) \
			--datarootdir=$(PDK_ROOT) \
			--enable-sky130-pdk=$(PDK_ROOT)/skywater-pdk \
			&& \
		cd sky130 && \
		$(MAKE) veryclean && \
		$(MAKE) primitive-A