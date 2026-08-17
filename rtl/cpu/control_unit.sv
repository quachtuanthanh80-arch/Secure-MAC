`timescale 1ns/1ps
module control_unit (
    input  logic [6:0] opcode,
    input  logic [2:0] funct3,
    input  logic [6:0] funct7,

    output logic       RegWrite,
    output logic [1:0] ResultSrc,  // 00: ALU, 01: Mem, 10: PC+4 (for JAL/JALR), 11: MAC
    output logic       MemWrite,
    output logic       MemRead,
    output logic       Branch,
    output logic       Jump,       // 1 for JAL/JALR
    output logic [1:0] ALUSrcA,    // 00: rs1, 01: PC, 10: 0
    output logic [1:0] ALUSrcB,    // 00: rs2, 01: imm, 10: 4
    output logic [3:0] ALUOp,
    output logic [2:0] ImmSrc,     // 000: I, 001: S, 010: B, 011: J, 100: U

    output logic       MacStart    // Custom control signal for MAC operation
);

    // Opcodes
    localparam logic [6:0] RType  = 7'b0110011;
    localparam logic [6:0] IType  = 7'b0010011;
    localparam logic [6:0] LOAD   = 7'b0000011;
    localparam logic [6:0] STORE  = 7'b0100011;
    localparam logic [6:0] BRANCH = 7'b1100011;
    localparam logic [6:0] LUI    = 7'b0110111;
    localparam logic [6:0] AUIPC  = 7'b0010111;
    localparam logic [6:0] JAL    = 7'b1101111;
    localparam logic [6:0] JALR   = 7'b1100111;

    // Custom Opcode for MAC (e.g. CUSTOM-0)
    localparam logic [6:0] MacOp  = 7'b0001011;

    always_comb begin
        // Defaults
        RegWrite  = 1'b0;
        ResultSrc = 2'b00;
        MemWrite  = 1'b0;
        MemRead   = 1'b0;
        Branch    = 1'b0;
        Jump      = 1'b0;
        ALUSrcA   = 2'b00;
        ALUSrcB   = 2'b00;
        ALUOp     = 4'b0000;
        ImmSrc    = 3'b000;
        MacStart  = 1'b0;

        case (opcode)
            RType: begin
                RegWrite = 1'b1;
                ALUSrcA  = 2'b00; // rs1
                ALUSrcB  = 2'b00; // rs2
                // ALUOp decoded from funct3 and funct7
                case (funct3)
                    3'b000: ALUOp = (funct7[5]) ? 4'b0001 : 4'b0000; // SUB : ADD
                    3'b010: ALUOp = 4'b1000; // SLT
                    3'b011: ALUOp = 4'b1001; // SLTU
                    3'b100: ALUOp = 4'b0100; // XOR
                    3'b110: ALUOp = 4'b0011; // OR
                    3'b111: ALUOp = 4'b0010; // AND
                    3'b001: ALUOp = 4'b0101; // SLL
                    3'b101: ALUOp = (funct7[5]) ? 4'b0111 : 4'b0110; // SRA : SRL
                    default: ALUOp = 4'b0000;
                endcase
            end

            IType: begin
                RegWrite = 1'b1;
                ImmSrc   = 3'b000; // I-type
                ALUSrcA  = 2'b00; // rs1
                ALUSrcB  = 2'b01; // imm
                case (funct3)
                    3'b000: ALUOp = 4'b0000; // ADDI
                    3'b010: ALUOp = 4'b1000; // SLTI
                    3'b011: ALUOp = 4'b1001; // SLTIU
                    3'b100: ALUOp = 4'b0100; // XORI
                    3'b110: ALUOp = 4'b0011; // ORI
                    3'b111: ALUOp = 4'b0010; // ANDI
                    3'b001: ALUOp = 4'b0101; // SLLI
                    3'b101: ALUOp = (funct7[5]) ? 4'b0111 : 4'b0110; // SRAI : SRLI
                    default: ALUOp = 4'b0000;
                endcase
            end

            LOAD: begin
                RegWrite  = 1'b1;
                ResultSrc = 2'b01; // Mem
                ImmSrc    = 3'b000; // I-type
                ALUSrcA   = 2'b00; // rs1
                ALUSrcB   = 2'b01; // imm
                ALUOp     = 4'b0000; // ADD (rs1 + imm)
                MemRead   = 1'b1;
            end

            STORE: begin
                ImmSrc    = 3'b001; // S-type
                ALUSrcA   = 2'b00; // rs1
                ALUSrcB   = 2'b01; // imm
                ALUOp     = 4'b0000; // ADD (rs1 + imm)
                MemWrite  = 1'b1;
            end

            BRANCH: begin
                Branch    = 1'b1;
                ImmSrc    = 3'b010; // B-type
                ALUSrcA   = 2'b00; // rs1
                ALUSrcB   = 2'b00; // rs2 (for comparison)
                // ALUOp can be SUB for comparison, or we can use a dedicated branch comparator.
                // We will use a dedicated branch comparator.
                ALUOp     = 4'b0000;
            end

            LUI: begin
                RegWrite = 1'b1;
                ImmSrc   = 3'b100; // U-type
                ALUSrcA  = 2'b10; // 0
                ALUSrcB  = 2'b01; // imm
                ALUOp    = 4'b0000; // ADD (0 + imm)
            end

            AUIPC: begin
                RegWrite = 1'b1;
                ImmSrc   = 3'b100; // U-type
                ALUSrcA  = 2'b01; // PC
                ALUSrcB  = 2'b01; // imm
                ALUOp    = 4'b0000; // ADD (PC + imm)
            end

            JAL: begin
                RegWrite  = 1'b1;
                ResultSrc = 2'b10; // PC + 4
                ImmSrc    = 3'b011; // J-type
                Jump      = 1'b1;
            end

            JALR: begin
                RegWrite  = 1'b1;
                ResultSrc = 2'b10; // PC + 4
                ImmSrc    = 3'b000; // I-type
                Jump      = 1'b1;
            end

            MacOp: begin
                MacStart = 1'b1;
                // Wait, MAC reads from registers.
                // Assuming R-type custom format: mac_out = rs1 * rs2 + c?
                // For now, just generate MacStart.
            end

            default: ;
        endcase
    end
endmodule
