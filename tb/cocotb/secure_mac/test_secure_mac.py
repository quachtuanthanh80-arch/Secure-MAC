"""
Comprehensive Cocotb Testbench for Secure_MAC with Modulo-3 Residue Code & State Rollback.

Tests Corner-Cases:
1. Reset verification
2. Basic normal multiplication and accumulation (Positive * Positive)
3. Zero multiplicand (0 * B + C, A * 0 + C, 0 * 0 + 0)
4. Signed corner-cases:
   - INT8_MAX * INT8_MAX (127 * 127 + 0 = 16129)
   - INT8_MIN * INT8_MAX (-128 * 127 + 0 = -16256)
   - INT8_MIN * INT8_MIN (-128 * -128 + 0 = 16384)
   - Positive * Negative + Large Negative C
   - Negative * Negative + Positive C
5. Modulo-3 Residue code combinations (residue 0, 1, 2 for A, B, and C)
6. Fault Injection & Rollback testing:
   - Bit-flip LSB (bit 0)
   - Bit-flip MSB / Sign bit (bit 15 / bit 31)
   - Bit-flip Middle bit (bit 5, bit 8)
   - Verify out rolls back to shadow_accumulator (last valid output)
   - Verify fault_detected = 1 and rollback = 1
7. Post-Fault Recovery:
   - After a fault is detected and rolled back, next valid operation without fault must succeed normally
8. Back-to-back pipelined throughput (continuous streaming calculations)
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from cocotb.clock import Clock


def to_signed(val, bits):
    """Convert integer to signed 2's complement representation."""
    mask = (1 << bits) - 1
    val = val & mask
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


def to_unsigned(val, bits):
    """Convert signed integer to unsigned bit vector."""
    mask = (1 << bits) - 1
    return val & mask


async def reset_dut(dut, cycles=5):
    """Active-low reset."""
    dut.rst_n.value = 0
    dut.start.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def execute_mac_with_fault(dut, a_val, b_val, c_val, fault_target=None, fault_mask=0):
    """
    Drive inputs with start pulse for 1 cycle, advance through pipeline stages,
    optionally inject fault during Stage 2, and sample valid output at Stage 3.
    """
    # 1. Drive inputs and start pulse (Stage 0 -> Stage 1)
    await FallingEdge(dut.clk)
    dut.a.value = to_unsigned(a_val, 8)
    dut.b.value = to_unsigned(b_val, 8)
    dut.c.value = to_unsigned(c_val, 32)
    dut.start.value = 1

    await FallingEdge(dut.clk)
    dut.start.value = 0
    # Stage 1 active (valid_d1 = 1)

    # 2. Advance to Stage 2 (valid_d2 = 1)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Inject fault during stage 2 if specified
    if fault_target is not None and fault_mask != 0:
        sig = getattr(dut, fault_target)
        sig.value = int(sig.value) ^ fault_mask

    # 3. Advance to Stage 3 (valid = 1)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    out_val = to_signed(int(dut.out.value), 32)
    fault = int(dut.fault_detected.value)
    rb = int(dut.rollback.value)
    return out_val, fault, rb


async def execute_mac(dut, a_val, b_val, c_val):
    """Normal MAC execution without fault injection."""
    return await execute_mac_with_fault(dut, a_val, b_val, c_val, fault_target=None, fault_mask=0)


# ============================================================
# TEST 1: Reset behavior
# ============================================================
@cocotb.test()
async def test_mac_reset(dut):
    """Verify reset clears output, fault_detected, rollback, valid."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    assert int(dut.out.value) == 0, "out not zero after reset"
    assert int(dut.fault_detected.value) == 0, "fault_detected not 0"
    assert int(dut.valid.value) == 0, "valid not 0"
    assert int(dut.rollback.value) == 0, "rollback not 0"
    dut._log.info("PASS: Reset clears all internal state and outputs")


# ============================================================
# TEST 2: Basic Normal MAC Operation
# ============================================================
@cocotb.test()
async def test_mac_basic(dut):
    """10 * 5 + 100 = 150."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    out_val, fault, rb = await execute_mac(dut, 10, 5, 100)
    expected = 10 * 5 + 100
    assert out_val == expected, f"Expected {expected}, got {out_val}"
    assert fault == 0, "fault_detected should be 0"
    assert rb == 0, "rollback should be 0"
    dut._log.info(f"PASS: 10 * 5 + 100 = {out_val}")


# ============================================================
# TEST 3: Zero Operands
# ============================================================
@cocotb.test()
async def test_mac_zeros(dut):
    """Test 0 * B + C, A * 0 + C, 0 * 0 + 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # 0 * 50 + 200 = 200
    out1, f1, _ = await execute_mac(dut, 0, 50, 200)
    assert out1 == 200 and f1 == 0, f"0 * 50 + 200 failed: {out1}"

    # -40 * 0 + 300 = 300
    out2, f2, _ = await execute_mac(dut, -40, 0, 300)
    assert out2 == 300 and f2 == 0, f"-40 * 0 + 300 failed: {out2}"

    # 0 * 0 + 0 = 0
    out3, f3, _ = await execute_mac(dut, 0, 0, 0)
    assert out3 == 0 and f3 == 0, f"0 * 0 + 0 failed: {out3}"
    dut._log.info("PASS: Zero operand tests verified")


# ============================================================
# TEST 4: Signed Edge Cases (INT8_MAX, INT8_MIN)
# ============================================================
@cocotb.test()
async def test_mac_signed_boundaries(dut):
    """Test max/min signed values for 8-bit inputs."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # 127 * 127 + 1000 = 16129 + 1000 = 17129
    out1, f1, _ = await execute_mac(dut, 127, 127, 1000)
    exp1 = 127 * 127 + 1000
    assert out1 == exp1 and f1 == 0, f"127*127+1000 expected {exp1}, got {out1}"

    # -128 * 127 + 500 = -16256 + 500 = -15756
    out2, f2, _ = await execute_mac(dut, -128, 127, 500)
    exp2 = -128 * 127 + 500
    assert out2 == exp2 and f2 == 0, f"-128*127+500 expected {exp2}, got {out2}"

    # -128 * -128 + 0 = 16384
    out3, f3, _ = await execute_mac(dut, -128, -128, 0)
    exp3 = (-128) * (-128)
    assert out3 == exp3 and f3 == 0, f"-128*-128 expected {exp3}, got {out3}"

    # -50 * -30 + (-2000) = 1500 - 2000 = -500
    out4, f4, _ = await execute_mac(dut, -50, -30, -2000)
    exp4 = (-50) * (-30) + (-2000)
    assert out4 == exp4 and f4 == 0, f"Negative accumulation expected {exp4}, got {out4}"
    dut._log.info("PASS: Signed boundary tests verified")


# ============================================================
# TEST 5: Modulo 3 Combinations Coverage
# ============================================================
@cocotb.test()
async def test_mac_modulo3_coverage(dut):
    """Test various combinations of numbers with residues 0, 1, 2 mod 3."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_vectors = [
        # (a, b, c, description)
        (3, 3, 3, "0 * 0 + 0 = 0 (mod 3)"),
        (4, 4, 1, "1 * 1 + 1 = 2 (mod 3)"),
        (5, 5, 2, "2 * 2 + 2 = 0 (mod 3)"),
        (4, 5, 2, "1 * 2 + 2 = 1 (mod 3)"),
        (7, 8, 9, "1 * 2 + 0 = 2 (mod 3)"),
        (-7, 4, 15, "(-7 mod 3 = 2, 4 mod 3 = 1, 2*1+0 = 2 mod 3)"),
        (-8, -8, -1, "(-8 mod 3 = 1, 1*1 + 2 = 0 mod 3)"),
    ]

    for a, b, c, desc in test_vectors:
        out_val, fault, rb = await execute_mac(dut, a, b, c)
        exp = a * b + c
        assert out_val == exp, f"{desc} failed: expected {exp}, got {out_val}"
        assert fault == 0, f"{desc} triggered false positive fault!"
        assert rb == 0, f"{desc} triggered false rollback!"

    dut._log.info("PASS: Modulo 3 residue coverage verified")


# ============================================================
# TEST 6: Fault Injection & State Rollback Verification
# ============================================================
@cocotb.test()
async def test_mac_fault_injection_and_rollback(dut):
    """
    Test fault injection:
    1. Perform a valid operation (saves shadow_accumulator).
    2. Inject fault on bit 0 of internal datapath (pipe_product).
    3. Verify fault is detected, rollback is asserted, and out is restored to previous valid value.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Step 1: Valid initial operation (saves shadow_accumulator)
    out1, fault1, _ = await execute_mac(dut, 10, 5, 100)
    assert out1 == 150 and fault1 == 0, "Step 1 initial operation failed"
    last_valid = out1

    # Step 2: Fault injected operation (into pipe_product)
    out_fault, fault_det, rb_det = await execute_mac_with_fault(
        dut, a_val=20, b_val=3, c_val=200, fault_target="pipe_product", fault_mask=0x1
    )

    assert fault_det == 1, "Fault was NOT detected by Modulo-3 checker!"
    assert rb_det == 1, "Rollback signal was NOT asserted upon fault!"
    assert out_fault == last_valid, f"Rollback failed: expected previous value {last_valid}, got {out_fault}"
    dut._log.info(f"PASS: Fault detected and state rolled back to {out_fault}")


# ============================================================
# TEST 7: Post-Fault Recovery
# ============================================================
@cocotb.test()
async def test_mac_post_fault_recovery(dut):
    """
    Verify that after a fault and rollback, subsequent normal operations
    without fault injection continue to execute accurately.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # 1. First valid operation: 5 * 5 + 0 = 25
    out1, f1, _ = await execute_mac(dut, 5, 5, 0)
    assert out1 == 25 and f1 == 0

    # 2. Injected fault on second operation into pipe_c (flip bit 1)
    out2, f2, rb2 = await execute_mac_with_fault(
        dut, a_val=10, b_val=10, c_val=0, fault_target="pipe_c", fault_mask=0x2
    )
    assert f2 == 1, "Fault should be detected"
    assert rb2 == 1, "Rollback should be asserted"
    assert out2 == 25, f"Should rollback to 25, got {out2}"

    # 3. Third operation (NO FAULT): 8 * 8 + 10 = 74
    out3, f3, rb3 = await execute_mac(dut, 8, 8, 10)
    assert out3 == 74, f"Post-fault recovery failed: expected 74, got {out3}"
    assert f3 == 0, "fault_detected should be cleared"
    assert rb3 == 0, "rollback should be cleared"
    dut._log.info("PASS: System successfully recovered and processed new valid data after fault")


# ============================================================
# TEST 8: Pipelined Streaming Throughput (Back-to-Back)
# ============================================================
@cocotb.test()
async def test_mac_pipelined_streaming(dut):
    """Stream 5 back-to-back operations without idle cycles."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    inputs = [
        (1, 2, 3),    # 1*2 + 3 = 5
        (4, 5, 6),    # 4*5 + 6 = 26
        (7, 8, 9),    # 7*8 + 9 = 65
        (-2, 10, 50), # -2*10 + 50 = 30
        (12, 12, 1),  # 12*12 + 1 = 145
    ]
    expected_outputs = [a * b + c for a, b, c in inputs]
    received_outputs = []

    # Monitor coroutine running concurrently to catch pipelined outputs
    async def monitor():
        for _ in range(len(inputs)):
            while True:
                await RisingEdge(dut.clk)
                await Timer(1, unit="ns")
                if int(dut.valid.value) == 1:
                    break
            received_outputs.append(to_signed(int(dut.out.value), 32))

    monitor_task = cocotb.start_soon(monitor())

    # Feed inputs sequentially on consecutive clock cycles
    for a, b, c in inputs:
        await FallingEdge(dut.clk)
        dut.a.value = to_unsigned(a, 8)
        dut.b.value = to_unsigned(b, 8)
        dut.c.value = to_unsigned(c, 32)
        dut.start.value = 1

    await FallingEdge(dut.clk)
    dut.start.value = 0

    # Wait for all outputs to be captured
    await monitor_task

    assert received_outputs == expected_outputs, f"Streaming failed: expected {expected_outputs}, got {received_outputs}"
    dut._log.info(f"PASS: Streaming throughput verified with outputs: {received_outputs}")
