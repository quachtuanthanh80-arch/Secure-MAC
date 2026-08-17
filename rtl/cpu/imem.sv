`timescale 1ns/1ps
module imem (
    input  logic [31:0] a,
    output logic [31:0] rd
);

    logic [31:0] RAM[63:0];

    initial begin
        // Chương trình khởi động mặc định:
        // 0: ADDI x1, x0, 10
        RAM[0] = 32'h00A00093;
        // 1: ADDI x2, x0, 20
        RAM[1] = 32'h01400113;
        // 2: ADD x3, x1, x2
        RAM[2] = 32'h002081B3;
        // 3: JAL x0, 0 (Vòng lặp vô hạn)
        RAM[3] = 32'h0000006F;
    end

    assign rd = RAM[a[7:2]];

endmodule
