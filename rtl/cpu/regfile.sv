`timescale 1ns/1ps
module regfile (
    input  logic        clk,
    input  logic        rst_n,
    
    input  logic [4:0]  rs1_addr,
    output logic [31:0] rs1_data,
    
    input  logic [4:0]  rs2_addr,
    output logic [31:0] rs2_data,
    
    input  logic        reg_write,
    input  logic [4:0]  rd_addr,
    input  logic [31:0] rd_data
);

    logic [31:0] registers [31:0];
    integer i;

    // Thao tác ghi (đồng bộ)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 32; i = i + 1) begin
                registers[i] <= 32'd0;
            end
        end else begin
            if (reg_write && (rd_addr != 5'd0)) begin
                registers[rd_addr] <= rd_data;
            end
        end
    end

    // Thao tác đọc (bất đồng bộ) có chuyển tiếp nội bộ
    always_comb begin
        if (rs1_addr == 5'd0) begin
            rs1_data = 32'd0;
        end else if (reg_write && (rs1_addr == rd_addr)) begin
            rs1_data = rd_data; // Chuyển tiếp (Forwarding)
        end else begin
            rs1_data = registers[rs1_addr];
        end
        
        if (rs2_addr == 5'd0) begin
            rs2_data = 32'd0;
        end else if (reg_write && (rs2_addr == rd_addr)) begin
            rs2_data = rd_data; // Chuyển tiếp (Forwarding)
        end else begin
            rs2_data = registers[rs2_addr];
        end
    end

endmodule
