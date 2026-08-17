# ==============================================================================
# RISC-V RV32I Assembly Program: Secure MAC Hardware Accelerator Demo
# 
# Demonstrates:
# 1. Loading weights & activations and writing to MAC MMIO registers
# 2. Triggering hardware computation
# 3. Polling status until MAC calculation finishes (valid bit = 1)
# 4. Reading back 16-bit MAC result (10 * 5 + 100 = 150)
# 5. Storing final result into Data Memory (dmem) at address 0x00000040
# 6. Reading back from Data Memory to verify system end-to-end
# ==============================================================================

.text
.globl _start

_start:
    # 1. Base MMIO address for Secure MAC (0x80000000)
    lui     x1, 0x80000         # x1 = 0x80000000 (MAC_BASE)

    # 2. Setup MAC Operands
    addi    x2, x0, 10          # x2 = 10  (Operand A, weight)
    addi    x3, x0, 5           # x3 = 5   (Operand B, activation)
    addi    x4, x0, 100         # x4 = 100 (Operand C, accumulator)

    # 3. Write operands to MAC MMIO registers
    sw      x2, 0(x1)           # MAC_A_REG  (0x80000000) = 10
    sw      x3, 4(x1)           # MAC_B_REG  (0x80000004) = 5
    sw      x4, 8(x1)           # MAC_C_REG  (0x80000008) = 100

    # 4. Trigger MAC calculation (Start pulse)
    addi    x5, x0, 1           # x5 = 1
    sw      x5, 12(x1)          # MAC_START_REG (0x8000000C) = 1

    # 5. Poll MAC_STATUS_REG (0x80000014) until valid (bit 1) == 1
poll_valid:
    lw      x6, 20(x1)          # x6 = *MAC_STATUS_REG
    andi    x7, x6, 2           # check bit 1 (valid)
    beq     x7, x0, poll_valid  # if (valid == 0) wait and loop

    # 6. Read MAC result from MAC_C_REG (0x80000008)
    lw      x8, 8(x1)           # x8 = MAC output (Expected: 150)

    # 7. Store result into Data Memory (RAM) at address 0x00000040
    addi    x9, x0, 64          # x9 = 64 (0x40)
    sw      x8, 0(x9)           # RAM[0x40] = 150

    # 8. Read back from Data Memory to verify RAM
    lw      x10, 0(x9)          # x10 = RAM[0x40] (Expected: 150)

    # 9. Finished successfully -> loop infinitely
done:
    jal     x0, done            # spin loop
