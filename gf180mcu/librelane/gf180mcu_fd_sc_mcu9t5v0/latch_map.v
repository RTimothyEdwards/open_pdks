// positive D-latch
module \$_DLATCH_P_ (input E, input D, output Q);
    gf180mcu_fd_sc_mcu9t5v0__latq_1 _TECHMAP_REPLACE_ (
        .E  (E),
        .D  (D),
        .Q  (Q)
    );
endmodule

// positive D-latch, active low reset
module \$_DLATCH_PN0_ (input E, input R, input D, output Q);
    gf180mcu_fd_sc_mcu9t5v0__latrnq_1 _TECHMAP_REPLACE_ (
        .E  (E),
        .D  (D),
        .RN (R),
        .Q  (Q)
    );
endmodule

// positive D-latch, active low set/reset
//gf180mcu_fd_sc_mcu9t5v0__latrsnq_1 ( E, D, RN, SETN, Q);

// positive D-latch, active low set
module \$_DLATCH_PN1_ (input E, input R, input D, output Q);
    gf180mcu_fd_sc_mcu9t5v0__latsnq_1 _TECHMAP_REPLACE_ (
        .E  (E),
        .D  (D),
        .SETN (R),
        .Q  (Q)
    );
endmodule
