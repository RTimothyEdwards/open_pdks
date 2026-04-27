/*
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
 */

module gf180mcu_ef_io__bi_t (CS, SL, IE, OE, PU, PD, A, ANA, PDRV0, PDRV1, PAD, Y, DVDD, DVSS, VDD, VSS);
	input	CS;
	input	SL;
	input	IE;
	input	OE;
	input	PU;
	input	PD;
	input	A;
	inout	ANA;
	input	PDRV0;
	input	PDRV1;
	inout	PAD;
	output	Y;
	inout	DVDD;
	inout	DVSS;
	inout	VDD;
	inout	VSS;
endmodule
