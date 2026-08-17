// ============================================================
// Complete Project Filelist for RISC-V CPU Core & System SoC
// Structure: All paths relative to project root D:/NCKH
// ============================================================

// --- 1. RISC-V CPU Core Modules ---
../../rtl/cpu/alu.sv
../../rtl/cpu/branch_cmp.sv
../../rtl/cpu/control_unit.sv
../../rtl/cpu/hazard_unit.sv
../../rtl/cpu/imem.sv
../../rtl/cpu/dmem.sv
../../rtl/cpu/instruction_decoder.sv
../../rtl/cpu/pipe_if_id.sv
../../rtl/cpu/pipe_id_ex.sv
../../rtl/cpu/pipe_ex_mem.sv
../../rtl/cpu/pipe_mem_wb.sv
../../rtl/cpu/regfile.sv
../../rtl/cpu/riscv_cpu.sv

// --- 2. Secure MAC Accelerator ---
../../rtl/mac/secure_mac.v

// --- 3. Top System & Wrapper Modules ---
../../rtl/top/top_module.v
../../rtl/top/alu_top.sv