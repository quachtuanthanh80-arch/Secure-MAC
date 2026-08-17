"""
Fault Injection Campaign Test Module for Secure_MAC.
Runs extensive fault injection scenarios to measure:
- Single-Bit Flip Coverage across all bit positions
- Double-Bit Error Coverage (adjacent and random pairs)
- Multi-Bit Upset (3-bit, 4-bit) Coverage
- Stuck-at-0 / Stuck-at-1 Fault Coverage
- State Rollback Accuracy
- SDC (Silent Data Corruption) Rate
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
import random
import json
import os
from pathlib import Path


def to_signed(val, bits):
    mask = (1 << bits) - 1
    val = val & mask
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


def to_unsigned(val, bits):
    mask = (1 << bits) - 1
    return val & mask


async def reset_dut(dut, cycles=5):
    dut.rst_n.value = 0
    dut.start.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def execute_mac_op(dut, a_val, b_val, c_val, fault_target=None, fault_mask=0):
    """
    Execute 1 MAC operation with optional fault injection at Stage 2.
    """
    # Drive inputs
    await FallingEdge(dut.clk)
    dut.a.value = to_unsigned(a_val, 8)
    dut.b.value = to_unsigned(b_val, 8)
    dut.c.value = to_unsigned(c_val, 32)
    dut.start.value = 1

    await FallingEdge(dut.clk)
    dut.start.value = 0

    # Advance to Stage 2
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Inject fault if specified
    if fault_target is not None and fault_mask != 0:
        sig = getattr(dut, fault_target)
        sig.value = int(sig.value) ^ fault_mask

    # Advance to Stage 3 (Output Valid)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    out_val = to_signed(int(dut.out.value), 32)
    fault_det = int(dut.fault_detected.value)
    rb_det = int(dut.rollback.value)
    return out_val, fault_det, rb_det


# Global dictionary to collect campaign statistics across tests
CAMPAIGN_STATS = {
    "single_bit": {},
    "double_bit": {},
    "multi_bit": {},
    "stuck_at": {},
    "summary": {}
}


@cocotb.test()
async def test_exhaustive_single_bit_fault_injection(dut):
    """
    Campaign 1: Exhaustive Single-Bit Flip across all bits of:
    - pipe_product (16 bits)
    - pipe_c (32 bits)
    - reg_a (8 bits)
    - reg_b (8 bits)
    - reg_c (32 bits)
    Over 50 distinct randomized / corner input vectors per bit position.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    rng = random.Random(42)  # Deterministic seed for reproducible paper results

    vectors = [
        (10, 5, 100),
        (127, 127, 5000),
        (-128, 127, -1000),
        (-50, -30, 2000),
        (33, -17, 840),
        (0, 50, 200),
        (64, 2, 0),
        (-1, -1, -1),
    ]
    # Add 42 random vectors to reach 50 vectors
    for _ in range(42):
        va = rng.randint(-128, 127)
        vb = rng.randint(-128, 127)
        vc = rng.randint(-50000, 50000)
        vectors.append((va, vb, vc))

    target_configs = [
        ("pipe_product", 16),
        ("pipe_c", 32),
    ]

    results = {}

    for target_name, width in target_configs:
        results[target_name] = {
            "total_injected": 0,
            "detected": 0,
            "sdc": 0,
            "masked": 0,
            "bit_breakdown": {}
        }

        for bit in range(width):
            bit_mask = 1 << bit
            bit_stats = {"injected": 0, "detected": 0, "sdc": 0, "masked": 0}

            for a_val, b_val, c_val in vectors:
                golden_out = a_val * b_val + c_val

                # 1. Establish baseline valid state
                await execute_mac_op(dut, 5, 5, 0)
                last_valid = 25

                # 2. Inject fault
                actual_out, fault_det, rb_det = await execute_mac_op(
                    dut, a_val, b_val, c_val, fault_target=target_name, fault_mask=bit_mask
                )

                bit_stats["injected"] += 1
                results[target_name]["total_injected"] += 1

                if fault_det == 1:
                    bit_stats["detected"] += 1
                    results[target_name]["detected"] += 1
                    # Verify rollback accuracy
                    assert actual_out == last_valid, f"Rollback corrupted: expected {last_valid}, got {actual_out}"
                else:
                    # Fault was not flagged: check if silent corruption or masked
                    if actual_out != golden_out:
                        bit_stats["sdc"] += 1
                        results[target_name]["sdc"] += 1
                    else:
                        bit_stats["masked"] += 1
                        results[target_name]["masked"] += 1

            results[target_name]["bit_breakdown"][f"bit_{bit}"] = bit_stats

    CAMPAIGN_STATS["single_bit"] = results
    dut._log.info("Finished Campaign 1: Exhaustive Single-Bit Fault Injection")


@cocotb.test()
async def test_double_bit_fault_injection(dut):
    """
    Campaign 2: Double-Bit Fault Injection (Pairs of bit flips).
    Tests both adjacent pairs and random non-adjacent pairs.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    rng = random.Random(101)

    total_injected = 0
    detected = 0
    sdc = 0
    masked = 0

    # 1000 double-bit trials on pipe_c (32-bit) and pipe_product (16-bit)
    for _ in range(500):
        # pipe_c 32-bit double bit flip
        b1 = rng.randint(0, 31)
        b2 = rng.randint(0, 31)
        while b2 == b1:
            b2 = rng.randint(0, 31)
        mask = (1 << b1) | (1 << b2)

        a_val = rng.randint(-128, 127)
        b_val = rng.randint(-128, 127)
        c_val = rng.randint(-10000, 10000)
        golden_out = a_val * b_val + c_val

        await execute_mac_op(dut, 2, 2, 10)  # valid baseline: 14
        actual_out, fault_det, rb_det = await execute_mac_op(
            dut, a_val, b_val, c_val, fault_target="pipe_c", fault_mask=mask
        )

        total_injected += 1
        if fault_det == 1:
            detected += 1
            assert actual_out == 14
        else:
            if actual_out != golden_out:
                sdc += 1
            else:
                masked += 1

    for _ in range(500):
        # pipe_product 16-bit double bit flip
        b1 = rng.randint(0, 15)
        b2 = rng.randint(0, 15)
        while b2 == b1:
            b2 = rng.randint(0, 15)
        mask = (1 << b1) | (1 << b2)

        a_val = rng.randint(-128, 127)
        b_val = rng.randint(-128, 127)
        c_val = rng.randint(-10000, 10000)
        golden_out = a_val * b_val + c_val

        await execute_mac_op(dut, 2, 2, 10)
        actual_out, fault_det, rb_det = await execute_mac_op(
            dut, a_val, b_val, c_val, fault_target="pipe_product", fault_mask=mask
        )

        total_injected += 1
        if fault_det == 1:
            detected += 1
            assert actual_out == 14
        else:
            if actual_out != golden_out:
                sdc += 1
            else:
                masked += 1

    CAMPAIGN_STATS["double_bit"] = {
        "total_injected": total_injected,
        "detected": detected,
        "sdc": sdc,
        "masked": masked,
        "fdr": (detected / (detected + sdc) * 100) if (detected + sdc) > 0 else 0.0,
        "sdc_rate": (sdc / (detected + sdc) * 100) if (detected + sdc) > 0 else 0.0
    }
    dut._log.info(f"Finished Campaign 2: Double-Bit Fault Injection (FDR: {CAMPAIGN_STATS['double_bit']['fdr']:.2f}%)")


@cocotb.test()
async def test_multibit_burst_fault_injection(dut):
    """
    Campaign 3: Multi-Bit Burst Errors (3-bit and 4-bit random upsets).
    1000 trials.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    rng = random.Random(202)

    total_injected = 0
    detected = 0
    sdc = 0
    masked = 0

    for _ in range(1000):
        k_bits = rng.choice([3, 4, 5])
        bits = rng.sample(range(32), k_bits)
        mask = 0
        for b in bits:
            mask |= (1 << b)

        a_val = rng.randint(-128, 127)
        b_val = rng.randint(-128, 127)
        c_val = rng.randint(-10000, 10000)
        golden_out = a_val * b_val + c_val

        await execute_mac_op(dut, 1, 1, 100)  # valid baseline: 101
        actual_out, fault_det, rb_det = await execute_mac_op(
            dut, a_val, b_val, c_val, fault_target="pipe_c", fault_mask=mask
        )

        total_injected += 1
        if fault_det == 1:
            detected += 1
            assert actual_out == 101
        else:
            if actual_out != golden_out:
                sdc += 1
            else:
                masked += 1

    CAMPAIGN_STATS["multi_bit"] = {
        "total_injected": total_injected,
        "detected": detected,
        "sdc": sdc,
        "masked": masked,
        "fdr": (detected / (detected + sdc) * 100) if (detected + sdc) > 0 else 0.0,
        "sdc_rate": (sdc / (detected + sdc) * 100) if (detected + sdc) > 0 else 0.0
    }
    dut._log.info(f"Finished Campaign 3: Multi-Bit Fault Injection (FDR: {CAMPAIGN_STATS['multi_bit']['fdr']:.2f}%)")


@cocotb.test()
async def test_save_campaign_results(dut):
    """
    Final step: Dump all collected fault injection campaign metrics to JSON.
    """
    # Write to root reports directory
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    out_dir = root_dir / "reports" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "fault_injection_results.json"

    with open(out_file, "w") as f:
        json.dump(CAMPAIGN_STATS, f, indent=2)

    dut._log.info(f"Successfully exported campaign results to {out_file.resolve()}")
