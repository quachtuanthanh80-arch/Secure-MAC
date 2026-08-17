`timescale 1ns/1ps
module dmem (
    input  logic        clk,
    input  logic        we,
    input  logic [31:0] a,
    input  logic [31:0] wd,
    output logic [31:0] rd
);

    logic [31:0] RAM[63:0];

    integer i;
    initial begin
        for (i = 0; i < 64; i = i + 1) begin
            RAM[i] = 32'd0;
        end
    end

    // Ghi dữ liệu đồng bộ theo xung nhịp
    always_ff @(posedge clk) begin
        if (we) begin
            RAM[a[7:2]] <= wd;
        end
    end

    // Đọc dữ liệu tổ hợp (không đợi xung nhịp)
    assign rd = RAM[a[7:2]];

endmodule
