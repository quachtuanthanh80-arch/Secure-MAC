`timescale 1ns/1ps
module branch_cmp (
    input  logic [31:0] a,
    input  logic [31:0] b,
    input  logic [2:0]  funct3,
    input  logic        branch_en,
    output logic        branch_taken
);

    logic eq, lt, ltu;

    assign eq  = (a == b);
    assign lt  = ($signed(a) < $signed(b));
    assign ltu = (a < b);

    always_comb begin
        if (branch_en) begin
            case (funct3)
                3'b000: branch_taken = eq;
                3'b001: branch_taken = ~eq;
                3'b100: branch_taken = lt;
                3'b101: branch_taken = ~lt;
                3'b110: branch_taken = ltu;
                3'b111: branch_taken = ~ltu;
                default: branch_taken = 1'b0;
            endcase
        end else begin
            branch_taken = 1'b0;
        end
    end

endmodule
