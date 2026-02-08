module \$_TBUF_ (input A, input E, output Y);
  sky130_fd_sc_ls__ebufn_2 _TECHMAP_EBUF_N_ (
    .A(A),
    .Z(Y),
    .TE_B(~E));
endmodule