module \$_DLATCH_P_ (input E, input D, output Q);
  sky130_fd_sc_hdll__dlxtp_1 _TECHMAP_DLATCH_P (
    //# {{data|Data Signals}}
    .D(D),
    .Q(Q),

    //# {{clocks|Clocking}}
    .GATE(E)
  );
endmodule

module \$_DLATCH_N_ (input E, input D, output Q);
  sky130_fd_sc_hdll__dlxtn_1 _TECHMAP_DLATCH_N (
    //# {{data|Data Signals}}
    .D(D),
    .Q(Q),

    //# {{clocks|Clocking}}
    .GATE_N(E)
  );
endmodule
