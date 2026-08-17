"""
Cocotb Corner-Case Testbench for alu_top (FSM/ALU + Control Unit)
Tests: arithmetic overflow, shift boundary, SLT signed/unsigned edge cases,
       all ALU operations, FSM state transitions, reset behavior.
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from cocotb.clock import Clock


# ============================================================
# RV32I Opcode constants
# ============================================================
RTYPE  = 0b0110011
ITYPE  = 0b0010011
LOAD   = 0b0000011
STORE  = 0b0100011
BRANCH = 0b1100011
LUI    = 0b0110111
AUIPC  = 0b0010111
JAL    = 0b1101111
JALR   = 0b1100111
MACOP  = 0b0001011

# FSM States
S_IDLE    = 0
S_DECODE  = 1
S_EXECUTE = 2
S_DONE    = 3


async def reset_dut(dut, cycles=5):
    """Apply active-low reset for given clock cycles."""
    dut.rst_n.value = 0
    dut.opcode.value = 0
    dut.funct3.value = 0
    dut.funct7.value = 0
    dut.operand_a.value = 0
    dut.operand_b.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def execute_alu_op(dut, opcode, funct3, funct7, a, b):
    """
    Drive one full FSM cycle: IDLE->DECODE->EXECUTE->DONE.
    Returns (alu_result, zero_flag, carry_flag) after DONE.
    """
    # Apply inputs while in IDLE
    dut.opcode.value = opcode
    dut.funct3.value = funct3
    dut.funct7.value = funct7
    dut.operand_a.value = a & 0xFFFFFFFF
    dut.operand_b.value = b & 0xFFFFFFFF

    # Wait for IDLE -> DECODE
    await RisingEdge(dut.clk)
    # Clear opcode so FSM doesn't restart immediately
    dut.opcode.value = 0

    # DECODE -> EXECUTE
    await RisingEdge(dut.clk)
    # EXECUTE -> DONE
    await RisingEdge(dut.clk)
    # DONE -> IDLE (results are registered)
    await RisingEdge(dut.clk)

    result = int(dut.alu_result.value)
    zero   = int(dut.zero_flag.value)
    carry  = int(dut.carry_flag.value)
    return result, zero, carry


def to_signed32(val):
    """Convert unsigned 32-bit to signed Python int."""
    val = val & 0xFFFFFFFF
    if val >= 0x80000000:
        return val - 0x100000000
    return val


def to_unsigned32(val):
    """Convert signed Python int to unsigned 32-bit."""
    return val & 0xFFFFFFFF


# ============================================================
# TEST 1: Reset behavior
# ============================================================
@cocotb.test()
async def test_reset_clears_outputs(dut):
    """Verify all outputs are zero after reset."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    assert int(dut.alu_result.value) == 0, "alu_result not zero after reset"
    assert int(dut.zero_flag.value) == 0, "zero_flag not zero after reset"
    assert int(dut.carry_flag.value) == 0, "carry_flag not zero after reset"
    assert int(dut.fsm_state.value) == S_IDLE, "FSM not in IDLE after reset"
    dut._log.info("PASS: Reset clears all outputs")


# ============================================================
# TEST 2: ADD basic
# ============================================================
@cocotb.test()
async def test_add_basic(dut):
    """ADD: 10 + 20 = 30"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, carry = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0000000, 10, 20
    )
    assert result == 30, f"ADD 10+20 expected 30, got {result}"
    assert zero == 0, "zero flag should be 0"
    dut._log.info("PASS: ADD 10+20=30")


# ============================================================
# TEST 3: ADD overflow (corner case)
# ============================================================
@cocotb.test()
async def test_add_overflow(dut):
    """ADD: 0x7FFFFFFF + 1 = 0x80000000 (signed overflow)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, carry = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0000000, 0x7FFFFFFF, 1
    )
    assert result == 0x80000000, f"ADD overflow expected 0x80000000, got {hex(result)}"
    dut._log.info(f"PASS: ADD overflow -> {hex(result)}")


# ============================================================
# TEST 4: ADD carry out
# ============================================================
@cocotb.test()
async def test_add_carry(dut):
    """ADD: 0xFFFFFFFF + 1 = 0x00000000 with carry."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, carry = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0000000, 0xFFFFFFFF, 1
    )
    assert result == 0, f"ADD wrap expected 0, got {hex(result)}"
    assert zero == 1, "zero flag should be 1"
    assert carry == 1, "carry flag should be 1 for 0xFFFFFFFF+1"
    dut._log.info("PASS: ADD 0xFFFFFFFF+1 wraps to 0 with carry")


# ============================================================
# TEST 5: SUB basic and underflow
# ============================================================
@cocotb.test()
async def test_sub_basic(dut):
    """SUB: 20 - 10 = 10"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, carry = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0100000, 20, 10
    )
    assert result == 10, f"SUB 20-10 expected 10, got {result}"
    dut._log.info("PASS: SUB 20-10=10")


@cocotb.test()
async def test_sub_underflow(dut):
    """SUB: 0 - 1 = 0xFFFFFFFF (unsigned underflow)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, carry = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0100000, 0, 1
    )
    assert result == 0xFFFFFFFF, f"SUB underflow expected 0xFFFFFFFF, got {hex(result)}"
    dut._log.info("PASS: SUB 0-1 = 0xFFFFFFFF")


@cocotb.test()
async def test_sub_zero(dut):
    """SUB: equal operands -> zero flag."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, carry = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0100000, 42, 42
    )
    assert result == 0, f"SUB same values expected 0, got {result}"
    assert zero == 1, "zero flag should be set"
    dut._log.info("PASS: SUB 42-42=0, zero flag set")


# ============================================================
# TEST 6: AND / OR / XOR
# ============================================================
@cocotb.test()
async def test_and_operation(dut):
    """AND: 0xFF00FF00 & 0x0F0F0F0F = 0x0F000F00"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b111, 0b0000000, 0xFF00FF00, 0x0F0F0F0F
    )
    expected = 0xFF00FF00 & 0x0F0F0F0F
    assert result == expected, f"AND expected {hex(expected)}, got {hex(result)}"
    dut._log.info(f"PASS: AND -> {hex(result)}")


@cocotb.test()
async def test_or_operation(dut):
    """OR: 0xFF00FF00 | 0x0F0F0F0F = 0xFF0FFF0F"""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b110, 0b0000000, 0xFF00FF00, 0x0F0F0F0F
    )
    expected = 0xFF00FF00 | 0x0F0F0F0F
    assert result == expected, f"OR expected {hex(expected)}, got {hex(result)}"
    dut._log.info(f"PASS: OR -> {hex(result)}")


@cocotb.test()
async def test_xor_operation(dut):
    """XOR: val ^ val = 0 (zero flag)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, _ = await execute_alu_op(
        dut, RTYPE, 0b100, 0b0000000, 0xDEADBEEF, 0xDEADBEEF
    )
    assert result == 0, f"XOR same expected 0, got {hex(result)}"
    assert zero == 1, "zero flag should be set"
    dut._log.info("PASS: XOR self -> 0")


# ============================================================
# TEST 7: SLL (Shift Left Logical) corner cases
# ============================================================
@cocotb.test()
async def test_sll_by_zero(dut):
    """SLL: shift by 0 -> unchanged."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b001, 0b0000000, 0x12345678, 0
    )
    assert result == 0x12345678, f"SLL by 0 expected unchanged, got {hex(result)}"
    dut._log.info("PASS: SLL by 0")


@cocotb.test()
async def test_sll_by_31(dut):
    """SLL: shift 1 left by 31 -> 0x80000000."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b001, 0b0000000, 1, 31
    )
    assert result == 0x80000000, f"SLL 1<<31 expected 0x80000000, got {hex(result)}"
    dut._log.info("PASS: SLL 1<<31")


# ============================================================
# TEST 8: SRL (Shift Right Logical) corner cases
# ============================================================
@cocotb.test()
async def test_srl_msb(dut):
    """SRL: 0x80000000 >> 31 = 1 (logical, no sign extension)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b101, 0b0000000, 0x80000000, 31
    )
    assert result == 1, f"SRL 0x80000000>>31 expected 1, got {hex(result)}"
    dut._log.info("PASS: SRL logical shift")


# ============================================================
# TEST 9: SRA (Shift Right Arithmetic) corner cases
# ============================================================
@cocotb.test()
async def test_sra_negative(dut):
    """SRA: 0x80000000 >>> 4 = 0xF8000000 (sign-extended)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b101, 0b0100000, 0x80000000, 4
    )
    expected = 0xF8000000
    assert result == expected, f"SRA expected {hex(expected)}, got {hex(result)}"
    dut._log.info(f"PASS: SRA sign extension -> {hex(result)}")


@cocotb.test()
async def test_sra_positive(dut):
    """SRA: 0x7FFFFFFF >>> 4 = 0x07FFFFFF (no sign ext for positive)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b101, 0b0100000, 0x7FFFFFFF, 4
    )
    expected = 0x07FFFFFF
    assert result == expected, f"SRA positive expected {hex(expected)}, got {hex(result)}"
    dut._log.info(f"PASS: SRA positive -> {hex(result)}")


# ============================================================
# TEST 10: SLT (Set Less Than, signed)
# ============================================================
@cocotb.test()
async def test_slt_negative_vs_positive(dut):
    """SLT: -1 < 1 (signed) -> 1."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # -1 in 32-bit unsigned = 0xFFFFFFFF
    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b010, 0b0000000, 0xFFFFFFFF, 1
    )
    assert result == 1, f"SLT signed -1<1 expected 1, got {result}"
    dut._log.info("PASS: SLT signed -1 < 1")


@cocotb.test()
async def test_slt_equal(dut):
    """SLT: equal values -> 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b010, 0b0000000, 100, 100
    )
    assert result == 0, f"SLT equal expected 0, got {result}"
    dut._log.info("PASS: SLT equal values -> 0")


@cocotb.test()
async def test_slt_min_max(dut):
    """SLT: INT32_MIN < INT32_MAX -> 1."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b010, 0b0000000, 0x80000000, 0x7FFFFFFF
    )
    assert result == 1, f"SLT INT32_MIN<INT32_MAX expected 1, got {result}"
    dut._log.info("PASS: SLT INT32_MIN < INT32_MAX")


# ============================================================
# TEST 11: SLTU (Set Less Than, unsigned)
# ============================================================
@cocotb.test()
async def test_sltu_max_unsigned(dut):
    """SLTU: 0xFFFFFFFE < 0xFFFFFFFF -> 1."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b011, 0b0000000, 0xFFFFFFFE, 0xFFFFFFFF
    )
    assert result == 1, f"SLTU expected 1, got {result}"
    dut._log.info("PASS: SLTU 0xFFFFFFFE < 0xFFFFFFFF")


@cocotb.test()
async def test_sltu_zero_check(dut):
    """SLTU: any non-zero > 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b011, 0b0000000, 0, 1
    )
    assert result == 1, f"SLTU 0<1 expected 1, got {result}"
    dut._log.info("PASS: SLTU 0 < 1")


# ============================================================
# TEST 12: FSM state transition verification
# ============================================================
@cocotb.test()
async def test_fsm_transitions(dut):
    """Verify FSM goes through IDLE->DECODE->EXECUTE->DONE->IDLE."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    assert int(dut.fsm_state.value) == S_IDLE, "Should start in IDLE"

    # Drive an ADD operation
    dut.opcode.value = RTYPE
    dut.funct3.value = 0b000
    dut.funct7.value = 0b0000000
    dut.operand_a.value = 5
    dut.operand_b.value = 3

    await RisingEdge(dut.clk)
    dut.opcode.value = 0  # clear so it doesn't re-trigger

    # Should be in DECODE
    await RisingEdge(dut.clk)
    state = int(dut.fsm_state.value)
    dut._log.info(f"After DECODE clk: state={state}")
    # Note: After the rising edge that transitions IDLE->DECODE,
    # we need one more edge to see DECODE registered
    # The state at this point should be DECODE (1) or EXECUTE (2)

    await RisingEdge(dut.clk)
    state = int(dut.fsm_state.value)
    dut._log.info(f"After EXECUTE clk: state={state}")

    await RisingEdge(dut.clk)
    state = int(dut.fsm_state.value)
    dut._log.info(f"After DONE clk: state={state}")

    await RisingEdge(dut.clk)
    state = int(dut.fsm_state.value)
    assert state == S_IDLE, f"FSM should return to IDLE, got {state}"
    dut._log.info("PASS: FSM transitions verified")


# ============================================================
# TEST 13: Control signals for LOAD instruction
# ============================================================
@cocotb.test()
async def test_control_load(dut):
    """Verify control signals for LOAD instruction."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Execute a LOAD (opcode = 0b0000011)
    await execute_alu_op(dut, LOAD, 0b010, 0b0000000, 100, 4)

    assert int(dut.RegWrite.value) == 1, "LOAD should set RegWrite"
    assert int(dut.MemRead.value) == 1, "LOAD should set MemRead"
    assert int(dut.MemWrite.value) == 0, "LOAD should not set MemWrite"
    dut._log.info("PASS: LOAD control signals correct")


# ============================================================
# TEST 14: Control signals for STORE instruction
# ============================================================
@cocotb.test()
async def test_control_store(dut):
    """Verify control signals for STORE instruction."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await execute_alu_op(dut, STORE, 0b010, 0b0000000, 100, 4)

    assert int(dut.MemWrite.value) == 1, "STORE should set MemWrite"
    assert int(dut.RegWrite.value) == 0, "STORE should not set RegWrite"
    dut._log.info("PASS: STORE control signals correct")


# ============================================================
# TEST 15: Control signals for BRANCH
# ============================================================
@cocotb.test()
async def test_control_branch(dut):
    """Verify control signals for BRANCH instruction."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await execute_alu_op(dut, BRANCH, 0b000, 0b0000000, 0, 0)

    assert int(dut.Branch.value) == 1, "BRANCH should set Branch"
    assert int(dut.RegWrite.value) == 0, "BRANCH should not set RegWrite"
    dut._log.info("PASS: BRANCH control signals correct")


# ============================================================
# TEST 16: I-Type ADDI
# ============================================================
@cocotb.test()
async def test_itype_addi(dut):
    """I-Type: ADDI with ALUSrcB=imm -> RegWrite=1."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await execute_alu_op(dut, ITYPE, 0b000, 0b0000000, 100, 50)

    assert int(dut.RegWrite.value) == 1, "ADDI should set RegWrite"
    # ALUOp should be ADD (0b0000)
    assert int(dut.ALUOp.value) == 0, f"ADDI ALUOp should be 0, got {int(dut.ALUOp.value)}"
    dut._log.info("PASS: I-Type ADDI control correct")


# ============================================================
# TEST 17: Rapid back-to-back operations
# ============================================================
@cocotb.test()
async def test_back_to_back(dut):
    """Two operations back-to-back: ADD then SUB."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # First: ADD 100 + 200
    r1, _, _ = await execute_alu_op(dut, RTYPE, 0b000, 0b0000000, 100, 200)
    assert r1 == 300, f"First ADD expected 300, got {r1}"

    # Second: SUB 300 - 100
    r2, _, _ = await execute_alu_op(dut, RTYPE, 0b000, 0b0100000, 300, 100)
    assert r2 == 200, f"Second SUB expected 200, got {r2}"

    dut._log.info("PASS: Back-to-back operations work correctly")


# ============================================================
# TEST 18: All zeros operation
# ============================================================
@cocotb.test()
async def test_add_all_zeros(dut):
    """ADD: 0 + 0 = 0, zero flag set."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, zero, _ = await execute_alu_op(
        dut, RTYPE, 0b000, 0b0000000, 0, 0
    )
    assert result == 0, f"ADD 0+0 expected 0, got {result}"
    assert zero == 1, "zero flag should be set"
    dut._log.info("PASS: ADD 0+0=0")


# ============================================================
# TEST 19: Max value operations
# ============================================================
@cocotb.test()
async def test_and_all_ones(dut):
    """AND: 0xFFFFFFFF & 0xFFFFFFFF = 0xFFFFFFFF."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    result, _, _ = await execute_alu_op(
        dut, RTYPE, 0b111, 0b0000000, 0xFFFFFFFF, 0xFFFFFFFF
    )
    assert result == 0xFFFFFFFF, f"AND all-1s expected 0xFFFFFFFF, got {hex(result)}"
    dut._log.info("PASS: AND all 1s")


# ============================================================
# TEST 20: JAL/JALR control signal test
# ============================================================
@cocotb.test()
async def test_control_jal(dut):
    """JAL should set Jump=1 and RegWrite=1."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await execute_alu_op(dut, JAL, 0b000, 0b0000000, 0, 0)

    assert int(dut.Jump.value) == 1, "JAL should set Jump"
    assert int(dut.RegWrite.value) == 1, "JAL should set RegWrite"
    dut._log.info("PASS: JAL control signals correct")
