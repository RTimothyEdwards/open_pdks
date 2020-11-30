module \$_TBUF_ (input A, input E, output Y);
  sky130_fd_sc_hd__ebufn_2 _TECHMAP_REPLACE_ (
    .A(A),
    .Z(Z),
    .TE_B(~E));
endmodule