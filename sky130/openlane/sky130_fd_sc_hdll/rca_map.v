`define FA_CELL         sky130_fd_sc_hdll__fa_1 

(* techmap_celltype = "$add" *)
module sky130_rca (A, B, Y);
	parameter A_SIGNED = 0;
	parameter B_SIGNED = 0;
	parameter A_WIDTH = 1;
	parameter B_WIDTH = 1;
	parameter Y_WIDTH = 1;

	(* force_downto *)
	input [A_WIDTH-1:0] A;
	(* force_downto *)
	input [B_WIDTH-1:0] B;
	(* force_downto *)
	output [Y_WIDTH-1:0] Y;

	(* force_downto *)
	wire [Y_WIDTH-1:0] CO;

	wire _TECHMAP_FAIL_ = Y_WIDTH <= 2;

	(* force_downto *)
	wire [Y_WIDTH-1:0] A_buf, B_buf;
	\$pos #(.A_SIGNED(A_SIGNED), .A_WIDTH(A_WIDTH), .Y_WIDTH(Y_WIDTH)) A_conv (.A(A), .Y(A_buf));
	\$pos #(.A_SIGNED(B_SIGNED), .A_WIDTH(B_WIDTH), .Y_WIDTH(Y_WIDTH)) B_conv (.A(B), .Y(B_buf));

	(* force_downto *)
	wire [Y_WIDTH-1:0] AA = A_buf;
	(* force_downto *)
	wire [Y_WIDTH-1:0] BB = B_buf; 
	(* force_downto *)
	wire [Y_WIDTH-1:0] C = {CO, 1'b0};

    
    generate 
		genvar i;
		for(i=0; i<Y_WIDTH; i=i+1) begin: stage
			`FA_CELL FA ( .COUT(CO[i]), .CIN(C[i]), .A(AA[i]), .B(BB[i]), .SUM(Y[i]) );
        end endgenerate

endmodule

(* techmap_celltype = "$sub" *)
module sky130_rca_sub (A, B, Y);
	parameter A_SIGNED = 0;
	parameter B_SIGNED = 0;
	parameter A_WIDTH = 1;
	parameter B_WIDTH = 1;
	parameter Y_WIDTH = 1;

	(* force_downto *)
	input [A_WIDTH-1:0] A;
	(* force_downto *)
	input [B_WIDTH-1:0] B;
	(* force_downto *)
	output [Y_WIDTH-1:0] Y;

	//input CI, BI;
	(* force_downto *)
	wire [Y_WIDTH-1:0] CO;

	wire _TECHMAP_FAIL_ = Y_WIDTH <= 2;

	(* force_downto *)
	wire [Y_WIDTH-1:0] A_buf, B_buf;
	\$pos #(.A_SIGNED(A_SIGNED), .A_WIDTH(A_WIDTH), .Y_WIDTH(Y_WIDTH)) A_conv (.A(A), .Y(A_buf));
	\$pos #(.A_SIGNED(B_SIGNED), .A_WIDTH(B_WIDTH), .Y_WIDTH(Y_WIDTH)) B_conv (.A(B), .Y(B_buf));

	(* force_downto *)
	wire [Y_WIDTH-1:0] AA = A_buf;
	(* force_downto *)
	wire [Y_WIDTH-1:0] BB = ~B_buf;
	(* force_downto *)
	wire [Y_WIDTH-1:0] C = {CO, 1'b1};

    
    generate 
		genvar i;
		for(i=0; i<Y_WIDTH; i=i+1) begin: stage
			`FA_CELL FA ( .COUT(CO[i]), .CIN(C[i]), .A(AA[i]), .B(BB[i]), .SUM(Y[i]) );
        end endgenerate

endmodule
