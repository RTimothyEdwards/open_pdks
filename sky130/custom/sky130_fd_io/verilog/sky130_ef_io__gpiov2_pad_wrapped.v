module sky130_ef_io__gpiov2_pad_wrapped (IN_H, PAD_A_NOESD_H, PAD_A_ESD_0_H, PAD_A_ESD_1_H,
    PAD, DM, HLD_H_N, IN, INP_DIS, IB_MODE_SEL, ENABLE_H, ENABLE_VDDA_H,
    ENABLE_INP_H, OE_N, TIE_HI_ESD, TIE_LO_ESD, SLOW, VTRIP_SEL, HLD_OVR,
    ANALOG_EN, ANALOG_SEL, ENABLE_VDDIO, ENABLE_VSWITCH_H, ANALOG_POL, OUT,
    AMUXBUS_A, AMUXBUS_B, VSSA, VDDA, VSWITCH, VDDIO_Q, VCCHIB, VDDIO, VCCD,
    VSSIO, VSSD, VSSIO_Q 
    );

input OUT;  		
input OE_N;  		
input HLD_H_N;		
input ENABLE_H;
input ENABLE_INP_H;	
input ENABLE_VDDA_H;	
input ENABLE_VSWITCH_H;	
input ENABLE_VDDIO;	
input INP_DIS;		
input IB_MODE_SEL;
input VTRIP_SEL;	
input SLOW;		
input HLD_OVR;		
input ANALOG_EN;	
input ANALOG_SEL;	
input ANALOG_POL;	
input [2:0] DM;		

inout VDDIO;	
inout VDDIO_Q;	
inout VDDA;
inout VCCD;
inout VSWITCH;
inout VCCHIB;
inout VSSA;
inout VSSD;
inout VSSIO_Q;
inout VSSIO;

inout PAD;
inout PAD_A_NOESD_H,PAD_A_ESD_0_H,PAD_A_ESD_1_H;
inout AMUXBUS_A;
inout AMUXBUS_B;

output IN;
output IN_H;
output TIE_HI_ESD, TIE_LO_ESD;

// Instantiate original version with metal4-only power bus
sky130_fd_io__top_gpiov2 gpiov2_base (
    .IN_H(IN_H),
    .PAD_A_NOESD_H(PAD_A_NOESD_H),
    .PAD_A_ESD_0_H(PAD_A_ESD_0_H),
    .PAD_A_ESD_1_H(PAD_A_ESD_1_H),
    .PAD(PAD),
    .DM(DM),
    .HLD_H_N(HLD_H_N),
    .IN(IN),
    .INP_DIS(INP_DIS),
    .IB_MODE_SEL(IB_MODE_SEL),
    .ENABLE_H(ENABLE_H),
    .ENABLE_VDDA_H(ENABLE_VDDA_H),
    .ENABLE_INP_H(ENABLE_INP_H),
    .OE_N(OE_N),
    .TIE_HI_ESD(TIE_HI_ESD),
    .TIE_LO_ESD(TIE_LO_ESD),
    .SLOW(SLOW),
    .VTRIP_SEL(VTRIP_SEL),
    .HLD_OVR(HLD_OVR),
    .ANALOG_EN(ANALOG_EN),
    .ANALOG_SEL(ANALOG_SEL),
    .ENABLE_VDDIO(ENABLE_VDDIO),
    .ENABLE_VSWITCH_H(ENABLE_VSWITCH_H),
    .ANALOG_POL(ANALOG_POL),
    .OUT(OUT),
    .AMUXBUS_A(AMUXBUS_A),
    .AMUXBUS_B(AMUXBUS_B),
    .VSSA(VSSA),
    .VDDA(VDDA),
    .VSWITCH(VSWITCH),
    .VDDIO_Q(VDDIO_Q),
    .VCCHIB(VCCHIB),
    .VDDIO(VDDIO),
    .VCCD(VCCD),
    .VSSIO(VSSIO),
    .VSSD(VSSD),
    .VSSIO_Q(VSSIO_Q) 
);

endmodule
