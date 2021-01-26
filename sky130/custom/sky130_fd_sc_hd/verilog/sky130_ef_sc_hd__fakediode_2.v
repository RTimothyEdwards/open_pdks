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

`ifndef SKY130_EF_SC_HD__FAKEDIODE_2_V
`define SKY130_EF_SC_HD__FAKEDIODE_2_V

/**
 * fakediode: Antenna tie-down diode with no connection between the DIODE
 * pin and the diode.  This is just the sky130_fd_sc_hd__diode_2 cell with
 * the contacts removed between the diode and the pin.  It is used by the
 * openlane synthesis flow to preemptively put antenna tie-downs close to
 * every pin without making a connection.  If the net needs an antenna
 * tiedown, the fakediode cell can be replaced by the real diode cell.
 *
 * Verilog wrapper for diode with size of 2 units.  Note that the wrapper
 * is around the original SkyWater diode base cell;  because the diode
 * has no function in verilog, there is no difference between the verilog
 * definitions of the diode and fake diode other than the cell name.
 *
 */

`timescale 1ns / 1ps
`default_nettype none


`ifdef USE_POWER_PINS
/*********************************************************/

`celldefine
module sky130_ef_sc_hd__fakediode_2 (
    DIODE,
    VPWR ,
    VGND ,
    VPB  ,
    VNB
);

    input DIODE;
    input VPWR ;
    input VGND ;
    input VPB  ;
    input VNB  ;
    sky130_fd_sc_hd__diode base (
        .DIODE(DIODE),
        .VPWR(VPWR),
        .VGND(VGND),
        .VPB(VPB),
        .VNB(VNB)
    );

endmodule
`endcelldefine

/*********************************************************/
`else // If not USE_POWER_PINS
/*********************************************************/

`celldefine
module sky130_ef_sc_hd__fakediode_2 (
    DIODE
);

    input DIODE;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__diode base (
        .DIODE(DIODE)
    );

endmodule
`endcelldefine

/*********************************************************/
`endif // USE_POWER_PINS

`default_nettype wire
`endif  // SKY130_EF_SC_HD__FAKEDIODE_2_V
