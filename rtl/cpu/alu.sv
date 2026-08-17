`timescale 1ns/1ps
module alu (
    input  logic [3:0]  alu_op,
    input  logic [31:0] a,
    input  logic [31:0] b,
    output logic [31:0] result,
    output logic        zero,
    output logic        carry
);

    wire [32:0] sum_result = {1'b0, a} + {1'b0, b};

    always_comb begin
        case (alu_op)
            4'b0000: result = sum_result[31:0];
            4'b0001: result = a - b;
            4'b0010: result = a & b;
            4'b0011: result = a | b;
            4'b0100: result = a ^ b;
            4'b0101: result = a << b[4:0];
            4'b0110: result = a >> b[4:0];
            4'b0111: result = $unsigned($signed(a) >>> b[4:0]);
            4'b1000: result = ($signed(a) < $signed(b)) ? 32'd1 : 32'd0;
            4'b1001: result = (a < b) ? 32'd1 : 32'd0;
            default: result = 32'd0;
        endcase
    end

    assign zero  = (result == 32'd0);
    assign carry = (alu_op == 4'b0000) ? sum_result[32] : 1'b0;

endmodule