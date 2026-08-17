`timescale 1ns/1ps
module pipe_ex_mem (
    input  logic        clk,
    input  logic        rst_n,
    
    input  logic        RegWrite_in,
    input  logic [1:0]  ResultSrc_in,
    input  logic        MemWrite_in,
    input  logic        MemRead_in,
    
    input  logic [31:0] alu_result_in,
    input  logic [31:0] rs2_data_in,
    input  logic [4:0]  rd_addr_in,
    input  logic [31:0] pc_plus_4_in,
    
    output logic        RegWrite_out,
    output logic [1:0]  ResultSrc_out,
    output logic        MemWrite_out,
    output logic        MemRead_out,
    
    output logic [31:0] alu_result_out,
    output logic [31:0] rs2_data_out,
    output logic [4:0]  rd_addr_out,
    output logic [31:0] pc_plus_4_out
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            RegWrite_out   <= 0;
            ResultSrc_out  <= 0;
            MemWrite_out   <= 0;
            MemRead_out    <= 0;
            
            alu_result_out <= 0;
            rs2_data_out   <= 0;
            rd_addr_out    <= 0;
            pc_plus_4_out  <= 0;
        end else begin
            RegWrite_out   <= RegWrite_in;
            ResultSrc_out  <= ResultSrc_in;
            MemWrite_out   <= MemWrite_in;
            MemRead_out    <= MemRead_in;
            
            alu_result_out <= alu_result_in;
            rs2_data_out   <= rs2_data_in;
            rd_addr_out    <= rd_addr_in;
            pc_plus_4_out  <= pc_plus_4_in;
        end
    end

endmodule
