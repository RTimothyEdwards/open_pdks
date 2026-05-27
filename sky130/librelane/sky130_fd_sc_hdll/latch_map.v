// Delay latch, inverted enable, single output
module \$_DLATCH_N_ (input E, input D, output Q);
  sky130_fd_sc_hd__dlxtn_1 _TECHMAP_DLATCH_N (
    .Q      (Q),
    .D      (D),
    .GATE_N (E)
  );
endmodule

// Delay latch, inverted reset, non-inverted enable, single output
module \$_DLATCH_PN0_ (input E, input R, input D, output Q);
  sky130_fd_sc_hd__dlrtp_1 _TECHMAP_DLATCH_PN0 (
    .Q       (Q),
    .RESET_B (R),
    .D       (D),
    .GATE    (E)
  );
endmodule

// Delay latch, inverted reset, inverted enable, single output
module \$_DLATCH_NN0_ (input E, input R, input D, output Q);
  sky130_fd_sc_hd__dlrtn_1 _TECHMAP_DLATCH_NN0 (
    .Q       (Q),
    .RESET_B (R),
    .D       (D),
    .GATE_N  (E)
  );
endmodule
