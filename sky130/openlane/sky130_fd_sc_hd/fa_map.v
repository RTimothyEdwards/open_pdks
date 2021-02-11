`define FA_CELL         sky130_fd_sc_hd__fa_1 

(* techmap_celltype = "$fa" *)
module _90_fa (A, B, C, X, Y);
	parameter WIDTH = 1;

	(* force_downto *)
	input [WIDTH-1:0] A, B, C;
	(* force_downto *)
	output [WIDTH-1:0] X, Y;

	(* force_downto *)
	wire [WIDTH-1:0] t1, t2, t3;

    wire _TECHMAP_FAIL_ = WIDTH > 1;

    `FA_CELL FA ( .COUT(X), .CIN(C), .A(A), .B(B), .SUM(Y) );

endmodule
