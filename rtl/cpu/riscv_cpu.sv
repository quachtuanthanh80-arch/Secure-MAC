`timescale 1ns/1ps
module riscv_cpu (
    input  wire        clk,
    input  wire        rst_n,

    output wire [31:0] mem_addr,
    output wire        mem_write,
    output wire [31:0] mem_wdata,
    output wire        mem_valid,
    input  wire        mem_ready,
    input  wire [31:0] mem_rdata,

    output wire        mac_start,
    output wire [7:0]  mac_a,
    output wire [7:0]  mac_b,
    output wire [15:0] mac_c,
    input  wire [15:0] mac_out,
    input  wire        mac_fault,
    input  wire        mac_valid,
    input  wire        mac_rollback,

    input  wire        irq,

    output wire        reg_write,
    output wire [4:0]  rd_addr,
    output wire [4:0]  rs1_addr,
    output wire [4:0]  rs2_addr,
    output wire [31:0] alu_out,
    output wire [31:0] pc,
    output wire        mem_read,
    output wire [31:0] pc_next
);

    logic [31:0] PC_IF, PCNext_IF, PCPlus4_IF;
    logic [31:0] Instr_IF;
    
    logic [31:0] PC_ID, Instr_ID;
    logic [6:0]  opcode;
    logic [2:0]  funct3;
    logic [6:0]  funct7;
    logic [4:0]  rd_addr_ID, rs1_addr_ID, rs2_addr_ID;
    logic [31:0] imm_i, imm_s, imm_b, imm_u, imm_j, Imm_ID;
    logic [31:0] rs1_data_ID, rs2_data_ID;
    
    logic RegWrite_ID, MemWrite_ID, MemRead_ID, Branch_ID, Jump_ID, MacStart_ID;
    logic [1:0] ResultSrc_ID, ALUSrcA_ID, ALUSrcB_ID;
    logic [3:0] ALUOp_ID;
    logic [2:0] ImmSrc_ID;
    
    logic branch_taken_ID;
    logic [31:0] PCTarget_ID;
    
    logic [31:0] PC_EX, rs1_data_EX, rs2_data_EX, Imm_EX;
    logic [4:0]  rd_addr_EX, rs1_addr_EX, rs2_addr_EX;
    logic RegWrite_EX, MemWrite_EX, MemRead_EX, Branch_EX, Jump_EX;
    logic [1:0] ResultSrc_EX, ALUSrcA_EX, ALUSrcB_EX;
    logic [3:0] ALUOp_EX;
    
    logic [31:0] ALU_A, ALU_B, ALUResult_EX;
    logic [31:0] forward_valA, forward_valB;
    logic zero_EX, carry_EX;
    
    logic RegWrite_MEM, MemWrite_MEM, MemRead_MEM;
    logic [1:0] ResultSrc_MEM;
    logic [31:0] ALUResult_MEM, WriteData_MEM, ReadData_MEM;
    logic [4:0]  rd_addr_MEM;
    logic [31:0] PCPlus4_MEM;
    
    logic RegWrite_WB;
    logic [1:0] ResultSrc_WB;
    logic [31:0] ALUResult_WB, ReadData_WB, Result_WB;
    logic [4:0]  rd_addr_WB;
    logic [31:0] PCPlus4_WB;
    
    logic stall_IF, stall_ID, flush_ID, flush_EX;
    logic [1:0] forwardA_EX, forwardB_EX;

    // TẦNG 1: NẠP LỆNH (IF)
    assign PCPlus4_IF = PC_IF + 32'd4;
    
    always_comb begin
        if (branch_taken_ID || Jump_ID) begin
            PCNext_IF = PCTarget_ID;
        end else begin
            PCNext_IF = PCPlus4_IF;
        end
    end
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            PC_IF <= 32'd0;
        end else if (!stall_IF) begin
            PC_IF <= PCNext_IF;
        end
    end
    
    imem u_imem (
        .a  (PC_IF),
        .rd (Instr_IF)
    );
    
    // TẦNG PIPELINE: IF/ID
    pipe_if_id u_pipe_if_id (
        .clk        (clk),
        .rst_n      (rst_n),
        .stall      (stall_ID),
        .flush      (flush_ID),
        .pc_in      (PC_IF),
        .instr_in   (Instr_IF),
        .pc_out     (PC_ID),
        .instr_out  (Instr_ID)
    );
    
    // TẦNG 2: GIẢI MÃ LỆNH (ID)
    instruction_decoder u_decoder (
        .instr    (Instr_ID),
        .opcode   (opcode),
        .funct3   (funct3),
        .funct7   (funct7),
        .rs1      (rs1_addr_ID),
        .rs2      (rs2_addr_ID),
        .rd_addr  (rd_addr_ID),
        .imm_i    (imm_i),
        .imm_s    (imm_s),
        .imm_b    (imm_b),
        .imm_u    (imm_u),
        .imm_j    (imm_j)
    );
    
    control_unit u_control (
        .opcode   (opcode),
        .funct3   (funct3),
        .funct7   (funct7),
        .RegWrite (RegWrite_ID),
        .ResultSrc(ResultSrc_ID),
        .MemWrite (MemWrite_ID),
        .MemRead  (MemRead_ID),
        .Branch   (Branch_ID),
        .Jump     (Jump_ID),
        .ALUSrcA  (ALUSrcA_ID),
        .ALUSrcB  (ALUSrcB_ID),
        .ALUOp    (ALUOp_ID),
        .ImmSrc   (ImmSrc_ID),
        .MacStart (MacStart_ID)
    );
    
    always_comb begin
        case (ImmSrc_ID)
            3'b000: Imm_ID = imm_i;
            3'b001: Imm_ID = imm_s;
            3'b010: Imm_ID = imm_b;
            3'b011: Imm_ID = imm_j;
            3'b100: Imm_ID = imm_u;
            default: Imm_ID = 32'd0;
        endcase
    end
    
    regfile u_regfile (
        .clk        (clk),
        .rst_n      (rst_n),
        .rs1_addr   (rs1_addr_ID),
        .rs1_data   (rs1_data_ID),
        .rs2_addr   (rs2_addr_ID),
        .rs2_data   (rs2_data_ID),
        .reg_write  (RegWrite_WB),
        .rd_addr    (rd_addr_WB),
        .rd_data    (Result_WB)
    );
    
    branch_cmp u_branch_cmp (
        .a             (rs1_data_ID),
        .b             (rs2_data_ID),
        .funct3        (funct3),
        .branch_en     (Branch_ID),
        .branch_taken  (branch_taken_ID)
    );
    
    // Lệnh JALR có đích là rs1 + imm. Lệnh Branch/JAL có đích là PC + imm.
    assign PCTarget_ID = (opcode == 7'b1100111) ? (rs1_data_ID + Imm_ID) : (PC_ID + Imm_ID);
    
    // TẦNG PIPELINE: ID/EX
    pipe_id_ex u_pipe_id_ex (
        .clk           (clk),
        .rst_n         (rst_n),
        .flush         (flush_EX),
        
        .RegWrite_in   (RegWrite_ID),
        .ResultSrc_in  (ResultSrc_ID),
        .MemWrite_in   (MemWrite_ID),
        .MemRead_in    (MemRead_ID),
        .Branch_in     (Branch_ID),
        .Jump_in       (Jump_ID),
        .ALUSrcA_in    (ALUSrcA_ID),
        .ALUSrcB_in    (ALUSrcB_ID),
        .ALUOp_in      (ALUOp_ID),
        
        .pc_in         (PC_ID),
        .rs1_data_in   (rs1_data_ID),
        .rs2_data_in   (rs2_data_ID),
        .imm_in        (Imm_ID),
        .rs1_addr_in   (rs1_addr_ID),
        .rs2_addr_in   (rs2_addr_ID),
        .rd_addr_in    (rd_addr_ID),
        
        .RegWrite_out  (RegWrite_EX),
        .ResultSrc_out (ResultSrc_EX),
        .MemWrite_out  (MemWrite_EX),
        .MemRead_out   (MemRead_EX),
        .Branch_out    (Branch_EX),
        .Jump_out      (Jump_EX),
        .ALUSrcA_out   (ALUSrcA_EX),
        .ALUSrcB_out   (ALUSrcB_EX),
        .ALUOp_out     (ALUOp_EX),
        
        .pc_out        (PC_EX),
        .rs1_data_out  (rs1_data_EX),
        .rs2_data_out  (rs2_data_EX),
        .imm_out       (Imm_EX),
        .rs1_addr_out  (rs1_addr_EX),
        .rs2_addr_out  (rs2_addr_EX),
        .rd_addr_out   (rd_addr_EX)
    );
    
    // TẦNG 3: THỰC THI LỆNH (EX)
    always_comb begin
        case (forwardA_EX)
            2'b00: forward_valA = rs1_data_EX;
            2'b01: forward_valA = Result_WB;
            2'b10: forward_valA = ALUResult_MEM;
            default: forward_valA = rs1_data_EX;
        endcase
        
        case (forwardB_EX)
            2'b00: forward_valB = rs2_data_EX;
            2'b01: forward_valB = Result_WB;
            2'b10: forward_valB = ALUResult_MEM;
            default: forward_valB = rs2_data_EX;
        endcase
    end
    
    always_comb begin
        case (ALUSrcA_EX)
            2'b00: ALU_A = forward_valA;
            2'b01: ALU_A = PC_EX;
            2'b10: ALU_A = 32'd0;
            default: ALU_A = forward_valA;
        endcase
        
        case (ALUSrcB_EX)
            2'b00: ALU_B = forward_valB;
            2'b01: ALU_B = Imm_EX;
            2'b10: ALU_B = 32'd4;
            default: ALU_B = forward_valB;
        endcase
    end
    
    alu u_alu (
        .alu_op (ALUOp_EX),
        .a      (ALU_A),
        .b      (ALU_B),
        .result (ALUResult_EX),
        .zero   (zero_EX),
        .carry  (carry_EX)
    );
    
    // TẦNG PIPELINE: EX/MEM
    pipe_ex_mem u_pipe_ex_mem (
        .clk             (clk),
        .rst_n           (rst_n),
        
        .RegWrite_in     (RegWrite_EX),
        .ResultSrc_in    (ResultSrc_EX),
        .MemWrite_in     (MemWrite_EX),
        .MemRead_in      (MemRead_EX),
        
        .alu_result_in   (ALUResult_EX),
        .rs2_data_in     (forward_valB),
        .rd_addr_in      (rd_addr_EX),
        .pc_plus_4_in    (PC_EX + 32'd4),
        
        .RegWrite_out    (RegWrite_MEM),
        .ResultSrc_out   (ResultSrc_MEM),
        .MemWrite_out    (MemWrite_MEM),
        .MemRead_out     (MemRead_MEM),
        
        .alu_result_out  (ALUResult_MEM),
        .rs2_data_out    (WriteData_MEM),
        .rd_addr_out     (rd_addr_MEM),
        .pc_plus_4_out   (PCPlus4_MEM)
    );
    
    // TẦNG 4: TRUY XUẤT BỘ NHỚ (MEM)
    assign mem_addr  = ALUResult_MEM;
    assign mem_wdata = WriteData_MEM;
    assign mem_write = MemWrite_MEM;
    assign mem_valid = MemRead_MEM | MemWrite_MEM;
    
    assign ReadData_MEM = mem_rdata;
    
    // Tín hiệu MAC nội bộ được set bằng 0 do khối MAC thực tế nằm ở top_module thông qua MMIO
    assign mac_start = 1'b0;
    assign mac_a     = 8'd0;
    assign mac_b     = 8'd0;
    assign mac_c     = 16'd0;
    
    // TẦNG PIPELINE: MEM/WB
    pipe_mem_wb u_pipe_mem_wb (
        .clk             (clk),
        .rst_n           (rst_n),
        
        .RegWrite_in     (RegWrite_MEM),
        .ResultSrc_in    (ResultSrc_MEM),
        
        .alu_result_in   (ALUResult_MEM),
        .mem_rdata_in    (ReadData_MEM),
        .rd_addr_in      (rd_addr_MEM),
        .pc_plus_4_in    (PCPlus4_MEM),
        
        .RegWrite_out    (RegWrite_WB),
        .ResultSrc_out   (ResultSrc_WB),
        
        .alu_result_out  (ALUResult_WB),
        .mem_rdata_out   (ReadData_WB),
        .rd_addr_out     (rd_addr_WB),
        .pc_plus_4_out   (PCPlus4_WB)
    );
    
    // TẦNG 5: GHI LẠI KẾT QUẢ (WB)
    always_comb begin
        case (ResultSrc_WB)
            2'b00: Result_WB = ALUResult_WB;
            2'b01: Result_WB = ReadData_WB;
            2'b10: Result_WB = PCPlus4_WB;
            2'b11: Result_WB = {16'b0, mac_out}; // if needed
            default: Result_WB = ALUResult_WB;
        endcase
    end
    
    // KHỐI XỬ LÝ RỦI RO (HAZARD UNIT)
    hazard_unit u_hazard (
        .rs1_addr_EX     (rs1_addr_EX),
        .rs2_addr_EX     (rs2_addr_EX),
        .rd_addr_MEM     (rd_addr_MEM),
        .RegWrite_MEM    (RegWrite_MEM),
        .rd_addr_WB      (rd_addr_WB),
        .RegWrite_WB     (RegWrite_WB),
        
        .MemRead_EX      (MemRead_EX),
        .rd_addr_EX      (rd_addr_EX),
        .rs1_addr_ID     (rs1_addr_ID),
        .rs2_addr_ID     (rs2_addr_ID),
        .branch_taken_ID (branch_taken_ID),
        .jump_ID         (Jump_ID),
        
        .forwardA_EX     (forwardA_EX),
        .forwardB_EX     (forwardB_EX),
        
        .stall_IF        (stall_IF),
        .stall_ID        (stall_ID),
        .flush_ID        (flush_ID),
        .flush_EX        (flush_EX)
    );
    
    assign reg_write = RegWrite_WB;
    assign rd_addr   = rd_addr_WB;
    assign rs1_addr  = rs1_addr_ID;
    assign rs2_addr  = rs2_addr_ID;
    assign alu_out   = ALUResult_EX;
    assign pc        = PC_IF;
    assign mem_read  = MemRead_MEM;
    assign pc_next   = PCNext_IF;

endmodule