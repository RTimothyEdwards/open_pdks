/*
 * $Id: $
 * Copyright 2022 GlobalFoundries PDK Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http:www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Project:             018 5VGREEN SRAM
 * Author:              GlobalFoundries PDK Authors
 * Data Created:        05-06-2014
 * Revision:            0.0
 *
 * Description:         gf180mcu_fd_ip_sram__sram512x8m8wm1 Simulation Model
 */

module gf180mcu_ocd_ip_sram__sram512x8m8wm1 (
  input           CLK,
  input           CEN,    //Chip Enable Negative
  input           GWEN,   //Global Write Enable Negative
  input   [7:0]   WEN,    //Write Enable Negative
  input   [9:0]   A,
  input   [7:0]   D,
  output  [7:0]   Q,
  inout           VDD,
  inout           VSS
);
endmodule
