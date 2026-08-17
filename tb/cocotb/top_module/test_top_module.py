"""
Comprehensive System-Level Cocotb Testbench for top_module (SoC Integration).
Integrates:
- RV32I 5-stage CPU
- Instruction Memory (IMEM)
- Data Memory (DMEM)
- Secure MAC Accelerator (with Modulo-3 Checker & State Rollback)
- Memory-Mapped I/O (MMIO) Address Decoder
- Interrupt Line (IRQ)

Tests:
1. Reset verification
2. Data Memory (RAM) Read/Write isolation
3. End-to-end MAC execution via MMIO and storage to RAM (10 * 5 + 100 = 150)
4. Hardware Fault Injection & Interrupt (IRQ) triggering
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from cocotb.clock import Clock
from pathlib import Path


async def reset_dut(dut, cycles=5):
    """Apply active-low reset to the SoC."""
    dut.rst_n.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


def load_hex_into_imem(dut, hex_filepath):
    """Load machine code instructions from a .hex file into imem.RAM."""
    with open(hex_filepath, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#") and not line.startswith("//")]
    
    for i, hex_str in enumerate(lines):
        val = int(hex_str, 16)
        dut.u_cpu.u_imem.RAM[i].value = val
    
    dut._log.info(f"Loaded {len(lines)} instructions into IMEM from {hex_filepath}")


# ==============================================================================
# TEST 1: Reset behavior
# ==============================================================================
@cocotb.test()
async def test_system_reset(dut):
    """Verify reset state of SoC top module."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    assert int(dut.irq.value) == 0, "IRQ should be 0 on reset"
    assert int(dut.u_mac.fault_detected.value) == 0, "MAC fault_detected should be 0"
    assert int(dut.u_mac.valid.value) == 0, "MAC valid should be 0"
    assert int(dut.u_cpu.PC_IF.value) == 0, "CPU PC should start at 0"
    dut._log.info("PASS: System reset verified cleanly")


# ==============================================================================
# TEST 2: Data Memory (RAM) Read/Write
# ==============================================================================
@cocotb.test()
async def test_dmem_read_write(dut):
    """
    Test CPU executing standard SW / LW instructions to Data Memory.
    Program:
      0: ADDI x1, x0, 0x10   (address 16)
      1: ADDI x2, x0, 1234   (data 1234)
      2: SW   x2, 0(x1)      (RAM[16] = 1234)
      3: LW   x3, 0(x1)      (x3 = RAM[16])
      4: JAL  x0, 0          (halt)
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Program machine code
    program = [
        0x01000093,  # addi x1, x0, 16
        0x4D200113,  # addi x2, x0, 1234
        0x0020A023,  # sw   x2, 0(x1)
        0x0000A183,  # lw   x3, 0(x1)
        0x0000006F,  # jal  x0, 0
    ]

    for i, instr in enumerate(program):
        dut.u_cpu.u_imem.RAM[i].value = instr

    # Pulse reset so CPU starts executing from PC=0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Run for 25 clock cycles to let pipeline complete execution
    await ClockCycles(dut.clk, 25)

    # Check RAM content at word index (16 >> 2) = 4
    ram_val = int(dut.u_dmem.RAM[4].value)
    assert ram_val == 1234, f"Expected RAM[4]=1234, got {ram_val}"

    # Check register file x3 content
    reg_val = int(dut.u_cpu.u_regfile.registers[3].value)
    assert reg_val == 1234, f"Expected x3=1234, got {reg_val}"

    dut._log.info("PASS: Data Memory SW and LW operations verified successfully")


# ==============================================================================
# TEST 3: End-to-End Secure MAC Acceleration via MMIO
# ==============================================================================
@cocotb.test()
async def test_end_to_end_mac_execution(dut):
    """
    Execute full mac_program.hex:
    - Writes A=10, B=5, C=100 to MAC MMIO registers
    - Triggers start pulse
    - Polls status register until valid
    - Reads MAC result (150)
    - Stores 150 into DMEM at address 0x00000040
    - Reads back into register x10
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent
    hex_path = root_dir / "sw" / "bin" / "mac_program.hex"

    load_hex_into_imem(dut, hex_path)

    # Re-apply reset to start execution from PC=0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Run execution for 60 cycles (plenty of time for MMIO polling and writeback)
    await ClockCycles(dut.clk, 60)

    # Check register x8 (MAC result from MMIO)
    x8_val = int(dut.u_cpu.u_regfile.registers[8].value)
    assert x8_val == 150, f"Expected x8 (MAC result) = 150, got {x8_val}"

    # Check RAM content at address 0x40 (word index 16)
    ram_result = int(dut.u_dmem.RAM[16].value)
    assert ram_result == 150, f"Expected RAM[16] = 150, got {ram_result}"

    # Check register x10 (Read back from RAM)
    x10_val = int(dut.u_cpu.u_regfile.registers[10].value)
    assert x10_val == 150, f"Expected x10 = 150, got {x10_val}"

    # IRQ should remain 0 (no hardware faults)
    assert int(dut.irq.value) == 0, "IRQ should not be asserted in normal execution"

    dut._log.info(f"PASS: End-to-end SoC execution verified: 10 * 5 + 100 = {ram_result} in RAM!")


# ==============================================================================
# TEST 4: Hardware Fault Detection & IRQ Triggering
# ==============================================================================
@cocotb.test()
async def test_system_fault_injection_irq(dut):
    """
    Test fault injection at system level:
    - Execute MAC operation
    - Inject bitflip fault on internal MAC pipeline
    - Verify SoC IRQ pin asserts to 1 to notify the CPU
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent
    hex_path = root_dir / "sw" / "bin" / "mac_program.hex"

    load_hex_into_imem(dut, hex_path)

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Wait until MAC start signal is pulsed (around cycle 10-15)
    fault_injected = False
    for _ in range(50):
        await RisingEdge(dut.clk)
        if int(dut.mac_start.value) == 1:
            # Wait 1 cycle into MAC pipeline stage 2, then inject fault
            await RisingEdge(dut.clk)
            dut.u_mac.pipe_product.value = int(dut.u_mac.pipe_product.value) ^ 0x1
            fault_injected = True
            dut._log.info("Injected bit-flip fault into u_mac.pipe_product")
            break

    assert fault_injected, "mac_start was not asserted by CPU!"

    # Wait for MAC valid / fault output
    for _ in range(10):
        await RisingEdge(dut.clk)
        if int(dut.irq.value) == 1:
            break

    # Verify IRQ signal and fault flags
    assert int(dut.irq.value) == 1, "SoC IRQ output was NOT asserted upon hardware fault!"
    assert int(dut.u_mac.fault_detected.value) == 1, "u_mac.fault_detected was not set"
    assert int(dut.u_mac.rollback.value) == 1, "u_mac.rollback was not set"

    dut._log.info("PASS: System-level Fault Injection successfully triggered IRQ interrupt!")
