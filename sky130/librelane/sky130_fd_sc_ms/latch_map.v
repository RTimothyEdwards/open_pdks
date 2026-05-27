// Delay latch, non-inverted enable, single output
module \$_DLATCH_P_ (input E, input D, output Q);
  sky130_fd_sc_ms__dlxtp_1 _TECHMAP_DLATCH_P (
    .Q    (Q),
    .D    (D),
    .GATE (E)
  );
endmodule

// Delay latch, inverted enable, single output
module \$_DLATCH_N_ (input E, input D, output Q);
  sky130_fd_sc_ms__dlxtn_1 _TECHMAP_DLATCH_N (
    .Q      (Q),
    .D      (D),
    .GATE_N (E)
  );
endmodule

// Delay latch, inverted reset, non-inverted enable, single output
module \$_DLATCH_PN0_ (input E, input R, input D, output Q);
  sky130_fd_sc_ms__dlrtp_1 _TECHMAP_DLATCH_PN0 (
    .Q       (Q),
    .RESET_B (R),
    .D       (D),
    .GATE    (E)
  );
endmodule

// Delay latch, inverted reset, inverted enable, single output
module \$_DLATCH_NN0_ (input E, input R, input D, output Q);
  sky130_fd_sc_ms__dlrtn_1 _TECHMAP_DLATCH_NN0 (
    .Q       (Q),
    .RESET_B (R),
    .D       (D),
    .GATE_N  (E)
  );
endmodule

// while the SCL also contains the following lathes with complementary outputs,
// they are commented out, since Yosys lacks primities mapping for complementary outputs

// Delay latch, non-inverted enable, complementary outputs
//module sky130_fd_sc_ms__dlxbp_1 (
//    Q   ,
//    Q_N ,
//    D   ,
//    GATE
//);

// Delay latch, inverted enable, complementary outputs
//module sky130_fd_sc_ms__dlxbn_1 (
//    Q     ,
//    Q_N   ,
//    D     ,
//    GATE_N
//);

// Delay latch, inverted reset, non-inverted enable, complementary outputs
//module sky130_fd_sc_ms__dlrbp_1 (
//    Q      ,
//    Q_N    ,
//    RESET_B,
//    D      ,
//    GATE
//);

// Delay latch, inverted reset, inverted enable, complementary outputs
//module sky130_fd_sc_ms__dlrbn_1 (
//    Q      ,
//    Q_N    ,
//    RESET_B,
//    D      ,
//    GATE_N
//);
