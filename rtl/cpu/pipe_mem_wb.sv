`timescale 1ns/1ps
module pipe_mem_wb (
    input  logic        clk,
    input  logic        rst_n,
    
    input  logic        RegWrite_in,
    input  logic [1:0]  ResultSrc_in,
    
    input  logic [31:0] alu_result_in,
    input  logic [31:0] mem_rdata_in,
    input  logic [4:0]  rd_addr_in,
    input  logic [31:0] pc_plus_4_in,
    
    output logic        RegWrite_out,
    output logic [1:0]  ResultSrc_out,
    
    // Data Out
    output logic [31:0] alu_result_out,
    output logic [31:0] mem_rdata_out,
    output logic [4:0]  rd_addr_out,
    output logic [31:0] pc_plus_4_out
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            RegWrite_out   <= 0;
            ResultSrc_out  <= 0;
            
            alu_result_out <= 0;
            mem_rdata_out  <= 0;
            rd_addr_out    <= 0;
            pc_plus_4_out  <= 0;
        end else begin
            RegWrite_out   <= RegWrite_in;
            ResultSrc_out  <= ResultSrc_in;
            
            alu_result_out <= alu_result_in;
            mem_rdata_out  <= mem_rdata_in;
            rd_addr_out    <= rd_addr_in;
            pc_plus_4_out  <= pc_plus_4_in;
        end
    end

endmodule
