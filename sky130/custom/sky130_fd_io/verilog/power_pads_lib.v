//-----------------------------------------------------------------------
// Verilog entries for standard power pads (sky130 power pads + overlays)
// Also includes stub entries for the corner and fill cells
// Also includes the custom gpiov2 cell (adds m5 on buses), which is a wrapper
// for the sky130 gpiov2 cell.
//
// This file is distributed as open source under the Apache 2.0 license
// Copyright 2020 efabless, Inc.
// Written by Tim Edwards 
//-----------------------------------------------------------------------

module sky130_fd_io__vccd_hvc_pad (amuxbus_a, amuxbus_b, drn_hvc,
	src_bdy_hvc, vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_hvc;
  inout src_bdy_hvc;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying power pad (connects p_pad to vccd)
  sky130_fd_io__top_power_hvc_wpad sky130_fd_io__top_power_hvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.p_pad(vccd),
	.ogc_hvc(),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_hvc(drn_hvc),
	.src_bdy_hvc(src_bdy_hvc)
  );

endmodule

module sky130_fd_io__vccd_lvc_pad (amuxbus_a, amuxbus_b,
	drn_lvc1, drn_lvc2, src_bdy_lvc1, src_bdy_lvc2, bdy2_b2b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_lvc1;
  inout drn_lvc2;
  inout src_bdy_lvc1;
  inout src_bdy_lvc2;
  inout bdy2_b2b;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying power pad (connects p_pad to vccd)
  sky130_fd_io__top_power_lvc_wpad sky130_fd_io__top_power_lvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.p_pad(vccd),
	.ogc_lvc(),
	.bdy2_b2b(bdy2_b2b),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_lvc1(drn_lvc1),
	.drn_lvc2(drn_lvc2),
	.src_bdy_lvc1(src_bdy_lvc1),
	.src_bdy_lvc2(src_bdy_lvc2)
  );

endmodule

module sky130_fd_io__vdda_lvc_pad (amuxbus_a, amuxbus_b,
	drn_lvc1, drn_lvc2, src_bdy_lvc1, src_bdy_lvc2, bdy2_b2b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_lvc1;
  inout drn_lvc2;
  inout src_bdy_lvc1;
  inout src_bdy_lvc2;
  inout bdy2_b2b;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying power pad (connects p_pad to vdda)
  sky130_fd_io__top_power_lvc_wpad sky130_fd_io__top_power_lvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.p_pad(vdda),
	.ogc_lvc(),
	.bdy2_b2b(bdy2_b2b),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_lvc1(drn_lvc1),
	.drn_lvc2(drn_lvc2),
	.src_bdy_lvc1(src_bdy_lvc1),
	.src_bdy_lvc2(src_bdy_lvc2)
  );

endmodule

module sky130_fd_io__vdda_hvc_pad (amuxbus_a, amuxbus_b, drn_hvc,
	src_bdy_hvc,vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_hvc;
  inout src_bdy_hvc;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying power pad (connects p_pad to vdda)
  sky130_fd_io__top_power_hvc_wpad sky130_fd_io__top_power_hvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.p_pad(vdda),
	.ogc_hvc(),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_hvc(drn_hvc),
	.src_bdy_hvc(src_bdy_hvc)
  );

endmodule

module sky130_fd_io__vddio_lvc_pad (amuxbus_a, amuxbus_b,
	drn_lvc1, drn_lvc2, src_bdy_lvc1, src_bdy_lvc2, bdy2_b2b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_lvc1;
  inout drn_lvc2;
  inout src_bdy_lvc1;
  inout src_bdy_lvc2;
  inout bdy2_b2b;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying power pad (connects p_pad and vddio_q to vddio)
  sky130_fd_io__top_power_lvc_wpad sky130_fd_io__top_power_lvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.p_pad(vddio),
	.ogc_lvc(),
	.bdy2_b2b(bdy2_b2b),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_lvc1(drn_lvc1),
	.drn_lvc2(drn_lvc2),
	.src_bdy_lvc1(src_bdy_lvc1),
	.src_bdy_lvc2(src_bdy_lvc2)
  );

  assign vddio_q = vddio;

endmodule

module sky130_fd_io__vddio_hvc_pad (amuxbus_a, amuxbus_b, drn_hvc,
	src_bdy_hvc,vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_hvc;
  inout src_bdy_hvc;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying power pad (connects p_pad and vddio_q to vddio)
  sky130_fd_io__top_power_hvc_wpad sky130_fd_io__top_power_hvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.p_pad(vddio),
	.ogc_hvc(),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_hvc(drn_hvc),
	.src_bdy_hvc(src_bdy_hvc)
  );

  assign vddio_q = vddio;

endmodule

module sky130_fd_io__vssd_lvc_pad (amuxbus_a, amuxbus_b,
	drn_lvc1, drn_lvc2, src_bdy_lvc1, src_bdy_lvc2, bdy2_b2b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_lvc1;
  inout drn_lvc2;
  inout src_bdy_lvc1;
  inout src_bdy_lvc2;
  inout bdy2_b2b;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying ground pad (connects g_pad to vssd)
  sky130_fd_io__top_ground_lvc_wpad sky130_fd_io__top_ground_lvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.g_pad(vssd),
	.ogc_lvc(),
	.bdy2_b2b(bdy2_b2b),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_lvc1(drn_lvc1),
	.drn_lvc2(drn_lvc2),
	.src_bdy_lvc1(src_bdy_lvc1),
	.src_bdy_lvc2(src_bdy_lvc2)
  );

endmodule

module sky130_fd_io__vssd_hvc_pad (amuxbus_a, amuxbus_b, drn_hvc,
	src_bdy_hvc, vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_hvc;
  inout src_bdy_hvc;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying ground pad (connects g_pad to vssd)
  sky130_fd_io__top_ground_hvc_wpad sky130_fd_io__top_ground_hvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.g_pad(vssd),
	.ogc_hvc(),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_hvc(drn_hvc),
	.src_bdy_hvc(src_bdy_hvc)
  );

endmodule

module sky130_fd_io__vssio_lvc_pad (amuxbus_a, amuxbus_b,
	drn_lvc1, drn_lvc2, src_bdy_lvc1, src_bdy_lvc2, bdy2_b2b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_lvc1;
  inout drn_lvc2;
  inout src_bdy_lvc1;
  inout src_bdy_lvc2;
  inout bdy2_b2b;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying ground pad (connects g_pad and vssio_q to vssio)
  sky130_fd_io__top_ground_lvc_wpad sky130_fd_io__top_ground_lvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.g_pad(vssio),
	.ogc_lvc(),
	.bdy2_b2b(bdy2_b2b),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_lvc1(drn_lvc1),
	.drn_lvc2(drn_lvc2),
	.src_bdy_lvc1(src_bdy_lvc1),
	.src_bdy_lvc2(src_bdy_lvc2)
  );

  assign vssio_q = vssio;

endmodule


module sky130_fd_io__vssio_hvc_pad (amuxbus_a, amuxbus_b, drn_hvc,
	src_bdy_hvc,vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_hvc;
  inout src_bdy_hvc;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying ground pad (connects g_pad and vssio_q to vssio)
  sky130_fd_io__top_ground_hvc_wpad sky130_fd_io__top_ground_hvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.g_pad(vssio),
	.ogc_hvc(),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_hvc(drn_hvc),
	.src_bdy_hvc(src_bdy_hvc)
  );

  assign vssio_q = vssio;

endmodule

module sky130_fd_io__vssa_lvc_pad (amuxbus_a, amuxbus_b,
	drn_lvc1, drn_lvc2, src_bdy_lvc1, src_bdy_lvc2, bdy2_b2b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_lvc1;
  inout drn_lvc2;
  inout src_bdy_lvc1;
  inout src_bdy_lvc2;
  inout bdy2_b2b;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying ground pad (connects g_pad to vssa)
  sky130_fd_io__top_ground_lvc_wpad sky130_fd_io__top_ground_lvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.g_pad(vssa),
	.ogc_lvc(),
	.bdy2_b2b(bdy2_b2b),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_lvc1(drn_lvc1),
	.drn_lvc2(drn_lvc2),
	.src_bdy_lvc1(src_bdy_lvc1),
	.src_bdy_lvc2(src_bdy_lvc2)
  );

endmodule

module sky130_fd_io__vssa_hvc_pad (amuxbus_a, amuxbus_b, drn_hvc,
	src_bdy_hvc,vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout drn_hvc;
  inout src_bdy_hvc;
  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

  // Instantiate the underlying ground pad (connects g_pad to vssa)
  sky130_fd_io__top_ground_hvc_wpad sky130_fd_io__top_ground_hvc_base ( 
	.vssa(vssa),
	.vdda(vdda),
	.vswitch(vswitch),
	.vddio_q(vddio_q),
	.vcchib(vcchib),
	.vddio(vddio),
	.vccd(vccd),
	.vssio(vssio),
	.vssd(vssd),
	.vssio_q(vssio_q),
	.g_pad(vssa),
	.ogc_hvc(),
	.amuxbus_a(amuxbus_a),
	.amuxbus_b(amuxbus_b),
	.drn_hvc(drn_hvc),
	.src_bdy_hvc(src_bdy_hvc)
  );

endmodule

module sky130_fd_io__corner_pad (amuxbus_a, amuxbus_b, 
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

endmodule

module sky130_fd_io__com_bus_slice (amuxbus_a, amuxbus_b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

endmodule

module sky130_fd_io__com_bus_slice_1um (amuxbus_a, amuxbus_b,
	vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
	vssio, vssd, vssio_q
);
  inout amuxbus_a;
  inout amuxbus_b;

  inout vddio;	
  inout vddio_q;	
  inout vdda;
  inout vccd;
  inout vswitch;
  inout vcchib;
  inout vssa;
  inout vssd;
  inout vssio_q;
  inout vssio;

endmodule

module sky130_fd_io__gpiov2_pad (in_h, pad_a_noesd_h, pad_a_esd_0_h, pad_a_esd_1_h,
    pad, dm, hld_h_n, in, inp_dis, ib_mode_sel, enable_h, enable_vdda_h,
    enable_inp_h, oe_n, tie_hi_esd, tie_lo_esd, slow, vtrip_sel, hld_ovr,
    analog_en, analog_sel, enable_vddio, enable_vswitch_h, analog_pol, out,
    amuxbus_a, amuxbus_b,vssa, vdda, vswitch, vddio_q, vcchib, vddio, vccd,
    vssio, vssd, vssio_q 
    );

input out;  		
input oe_n;  		
input hld_h_n;		
input enable_h;
input enable_inp_h;	
input enable_vdda_h;	
input enable_vswitch_h;	
input enable_vddio;	
input inp_dis;		
input ib_mode_sel;
input vtrip_sel;	
input slow;		
input hld_ovr;		
input analog_en;	
input analog_sel;	
input analog_pol;	
input [2:0] dm;		

	inout vddio;	
	inout vddio_q;	
	inout vdda;
	inout vccd;
	inout vswitch;
	inout vcchib;
	inout vssa;
	inout vssd;
	inout vssio_q;
	inout vssio;

inout pad;
inout pad_a_noesd_h,pad_a_esd_0_h,pad_a_esd_1_h;
inout amuxbus_a;
inout amuxbus_b;

output in;
output in_h;
output tie_hi_esd, tie_lo_esd;

// Instantiate original version with metal4-only power bus
sky130_fd_io__top_gpiov2 gpiov2_base (
    .in_h(in_h),
    .pad_a_noesd_h(pad_a_noesd_h),
    .pad_a_esd_0_h(pad_a_esd_0_h),
    .pad_a_esd_1_h(pad_a_esd_1_h),
    .pad(pad),
    .dm(dm),
    .hld_h_n(hld_h_n),
    .in(in),
    .inp_dis(inp_dis),
    .ib_mode_sel(ib_mode_sel),
    .enable_h(enable_h),
    .enable_vdda_h(enable_vdda_h),
    .enable_inp_h(enable_inp_h),
    .oe_n(oe_n),
    .tie_hi_esd(tie_hi_esd),
    .tie_lo_esd(tie_lo_esd),
    .slow(slow),
    .vtrip_sel(vtrip_sel),
    .hld_ovr(hld_ovr),
    .analog_en(analog_en),
    .analog_sel(analog_sel),
    .enable_vddio(enable_vddio),
    .enable_vswitch_h(enable_vswitch_h),
    .analog_pol(analog_pol),
    .out(out),
    .amuxbus_a(amuxbus_a),
    .amuxbus_b(amuxbus_b) ,
    .vssa(vssa),
    .vdda(vdda),
    .vswitch(vswitch),
    .vddio_q(vddio_q),
    .vcchib(vcchib),
    .vddio(vddio),
    .vccd(vccd),
    .vssio(vssio),
    .vssd(vssd),
    .vssio_q(vssio_q) 
);

endmodule
