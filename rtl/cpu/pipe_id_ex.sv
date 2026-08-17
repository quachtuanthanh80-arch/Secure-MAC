`timescale 1ns/1ps
module pipe_id_ex (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        flush,
    
    input  logic        RegWrite_in,
    input  logic [1:0]  ResultSrc_in,
    input  logic        MemWrite_in,
    input  logic        MemRead_in,
    input  logic        Branch_in,
    input  logic        Jump_in,
    input  logic [1:0]  ALUSrcA_in,
    input  logic [1:0]  ALUSrcB_in,
    input  logic [3:0]  ALUOp_in,
    
    input  logic [31:0] pc_in,
    input  logic [31:0] rs1_data_in,
    input  logic [31:0] rs2_data_in,
    input  logic [31:0] imm_in,
    input  logic [4:0]  rs1_addr_in,
    input  logic [4:0]  rs2_addr_in,
    input  logic [4:0]  rd_addr_in,
    
    output logic        RegWrite_out,
    output logic [1:0]  ResultSrc_out,
    output logic        MemWrite_out,
    output logic        MemRead_out,
    output logic        Branch_out,
    output logic        Jump_out,
    output logic [1:0]  ALUSrcA_out,
    output logic [1:0]  ALUSrcB_out,
    output logic [3:0]  ALUOp_out,
    
    output logic [31:0] pc_out,
    output logic [31:0] rs1_data_out,
    output logic [31:0] rs2_data_out,
    output logic [31:0] imm_out,
    output logic [4:0]  rs1_addr_out,
    output logic [4:0]  rs2_addr_out,
    output logic [4:0]  rd_addr_out
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            RegWrite_out  <= 0;
            ResultSrc_out <= 0;
            MemWrite_out  <= 0;
            MemRead_out   <= 0;
            Branch_out    <= 0;
            Jump_out      <= 0;
            ALUSrcA_out   <= 0;
            ALUSrcB_out   <= 0;
            ALUOp_out     <= 0;
            
            pc_out        <= 0;
            rs1_data_out  <= 0;
            rs2_data_out  <= 0;
            imm_out       <= 0;
            rs1_addr_out  <= 0;
            rs2_addr_out  <= 0;
            rd_addr_out   <= 0;
        end else if (flush) begin
            RegWrite_out  <= 0;
            ResultSrc_out <= 0;
            MemWrite_out  <= 0;
            MemRead_out   <= 0;
            Branch_out    <= 0;
            Jump_out      <= 0;
            ALUSrcA_out   <= 0;
            ALUSrcB_out   <= 0;
            ALUOp_out     <= 0;
            
            pc_out        <= 0;
            rs1_data_out  <= 0;
            rs2_data_out  <= 0;
            imm_out       <= 0;
            rs1_addr_out  <= 0;
            rs2_addr_out  <= 0;
            rd_addr_out   <= 0;
        end else begin
            RegWrite_out  <= RegWrite_in;
            ResultSrc_out <= ResultSrc_in;
            MemWrite_out  <= MemWrite_in;
            MemRead_out   <= MemRead_in;
            Branch_out    <= Branch_in;
            Jump_out      <= Jump_in;
            ALUSrcA_out   <= ALUSrcA_in;
            ALUSrcB_out   <= ALUSrcB_in;
            ALUOp_out     <= ALUOp_in;
            
            pc_out        <= pc_in;
            rs1_data_out  <= rs1_data_in;
            rs2_data_out  <= rs2_data_in;
            imm_out       <= imm_in;
            rs1_addr_out  <= rs1_addr_in;
            rs2_addr_out  <= rs2_addr_in;
            rd_addr_out   <= rd_addr_in;
        end
    end

endmodule
