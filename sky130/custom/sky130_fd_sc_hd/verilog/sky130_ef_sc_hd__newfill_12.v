/**
 * Copyright 2020 The SkyWater PDK Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

`ifndef SKY130_EF_SC_HD__NEWFILL_12_V
`define SKY130_EF_SC_HD__NEWFILL_12_V

/**
 * newfill_12:  Designed to replace the decap_12 cell while reducing
 * the amount of local interconnect and satisfying the more restrictive
 * poly density rule of 38%.
 */

`timescale 1ns / 1ps
`default_nettype none


`ifdef USE_POWER_PINS
/*********************************************************/

`celldefine
module sky130_ef_sc_hd__newfill_12 (
    VPWR,
    VGND,
    VPB ,
    VNB
);

    input VPWR;
    input VGND;
    input VPB ;
    input VNB ;
    // No contents.
endmodule
`endcelldefine

/*********************************************************/
`else // If not USE_POWER_PINS
/*********************************************************/

`celldefine
module sky130_ef_sc_hd__newfill_12 ();

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;
    // No contents.
endmodule
`endcelldefine

/*********************************************************/
`endif // USE_POWER_PINS

`default_nettype wire
`endif  // SKY130_EF_SC_HD__NEWFILL_12_V
