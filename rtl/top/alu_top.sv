`timescale 1ns/1ps
// ============================================================
// ALU Top - Wrapper integrating Control Unit + ALU
// Provides a self-contained FSM/ALU block for unit testing
// ============================================================
module alu_top (
    input  wire        clk,
    input  wire        rst_n,

    // Instruction fields (from decoder)
    input  wire [6:0]  opcode,
    input  wire [2:0]  funct3,
    input  wire [6:0]  funct7,

    // Data inputs
    input  wire [31:0] operand_a,
    input  wire [31:0] operand_b,

    // Registered outputs
    output reg  [31:0] alu_result,
    output reg         zero_flag,
    output reg         carry_flag,

    // Control outputs (registered from control_unit)
    output reg         RegWrite,
    output reg  [1:0]  ResultSrc,
    output reg         MemWrite,
    output reg         MemRead,
    output reg         Branch,
    output reg         Jump,
    output reg  [1:0]  ALUSrcA,
    output reg  [1:0]  ALUSrcB,
    output reg  [3:0]  ALUOp,
    output reg  [2:0]  ImmSrc,
    output reg         MacStart,

    // FSM state (for observability)
    output wire [2:0]  fsm_state
);

    // =========================================================
    // FSM states (iverilog-compatible localparam)
    // =========================================================
    localparam [2:0] S_IDLE    = 3'b000;
    localparam [2:0] S_DECODE  = 3'b001;
    localparam [2:0] S_EXECUTE = 3'b010;
    localparam [2:0] S_DONE    = 3'b011;
    localparam [2:0] S_ERROR   = 3'b100;

    reg [2:0] state, next_state;

    // Internal wires
    wire [31:0] alu_result_w;
    wire        zero_w, carry_w;

    // Latched instruction fields
    reg [6:0]  opcode_r;
    reg [2:0]  funct3_r;
    reg [6:0]  funct7_r;
    reg [31:0] operand_a_r, operand_b_r;

    // Control unit outputs (directly wired)
    wire        RegWrite_w;
    wire [1:0]  ResultSrc_w;
    wire        MemWrite_w, MemRead_w;
    wire        Branch_w, Jump_w;
    wire [1:0]  ALUSrcA_w, ALUSrcB_w;
    wire [3:0]  ALUOp_w;
    wire [2:0]  ImmSrc_w;
    wire        MacStart_w;

    // =========================================================
    // Control Unit instantiation
    // =========================================================
    control_unit u_control (
        .opcode   (opcode_r),
        .funct3   (funct3_r),
        .funct7   (funct7_r),
        .RegWrite (RegWrite_w),
        .ResultSrc(ResultSrc_w),
        .MemWrite (MemWrite_w),
        .MemRead  (MemRead_w),
        .Branch   (Branch_w),
        .Jump     (Jump_w),
        .ALUSrcA  (ALUSrcA_w),
        .ALUSrcB  (ALUSrcB_w),
        .ALUOp    (ALUOp_w),
        .ImmSrc   (ImmSrc_w),
        .MacStart (MacStart_w)
    );

    // =========================================================
    // ALU instantiation
    // =========================================================
    alu u_alu (
        .alu_op (ALUOp_w),
        .a      (operand_a_r),
        .b      (operand_b_r),
        .result (alu_result_w),
        .zero   (zero_w),
        .carry  (carry_w)
    );

    // =========================================================
    // FSM State Register
    // =========================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= S_IDLE;
        else
            state <= next_state;
    end

    // =========================================================
    // FSM Next State Logic
    // =========================================================
    always @(*) begin
        next_state = state;
        case (state)
            S_IDLE:    if (opcode != 7'd0) next_state = S_DECODE;
            S_DECODE:  next_state = S_EXECUTE;
            S_EXECUTE: next_state = S_DONE;
            S_DONE:    next_state = S_IDLE;
            S_ERROR:   next_state = S_IDLE;
            default:   next_state = S_IDLE;
        endcase
    end

    // =========================================================
    // Latch inputs on IDLE->DECODE transition
    // =========================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            opcode_r    <= 7'd0;
            funct3_r    <= 3'd0;
            funct7_r    <= 7'd0;
            operand_a_r <= 32'd0;
            operand_b_r <= 32'd0;
        end else if (state == S_IDLE && opcode != 7'd0) begin
            opcode_r    <= opcode;
            funct3_r    <= funct3;
            funct7_r    <= funct7;
            operand_a_r <= operand_a;
            operand_b_r <= operand_b;
        end
    end

    // =========================================================
    // Register ALU result on EXECUTE->DONE
    // =========================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            alu_result <= 32'd0;
            zero_flag  <= 1'b0;
            carry_flag <= 1'b0;
        end else if (state == S_EXECUTE) begin
            alu_result <= alu_result_w;
            zero_flag  <= zero_w;
            carry_flag <= carry_w;
        end
    end

    // =========================================================
    // Control output registration (DECODE phase)
    // =========================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            RegWrite  <= 1'b0;
            ResultSrc <= 2'd0;
            MemWrite  <= 1'b0;
            MemRead   <= 1'b0;
            Branch    <= 1'b0;
            Jump      <= 1'b0;
            ALUSrcA   <= 2'd0;
            ALUSrcB   <= 2'd0;
            ALUOp     <= 4'd0;
            ImmSrc    <= 3'd0;
            MacStart  <= 1'b0;
        end else if (state == S_DECODE) begin
            RegWrite  <= RegWrite_w;
            ResultSrc <= ResultSrc_w;
            MemWrite  <= MemWrite_w;
            MemRead   <= MemRead_w;
            Branch    <= Branch_w;
            Jump      <= Jump_w;
            ALUSrcA   <= ALUSrcA_w;
            ALUSrcB   <= ALUSrcB_w;
            ALUOp     <= ALUOp_w;
            ImmSrc    <= ImmSrc_w;
            MacStart  <= MacStart_w;
        end
    end

    // =========================================================
    // FSM state export
    // =========================================================
    assign fsm_state = state;

endmodule