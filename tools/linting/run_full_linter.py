r"""
SystemVerilog Linter & Syntax Checker using pyslang.
Scans all Verilog and SystemVerilog files in D:\NCKH.
Reports:
- Syntax Errors
- Semantic / Elaboration Diagnostics
- Declaration & Typing Rules (undeclared nets, signedness mismatches, width mismatches)
"""

import os
import pyslang
import json

workspace = r"D:\NCKH"

# Find all .v and .sv files in rtl/ and tb/
all_files = []
for root, dirs, files in os.walk(workspace):
    if any(ignore in root for ignore in ['.vscode', '.git', '.Xil', 'sim_build', '__pycache__', 'synth']):
        continue
    for f in files:
        if f.endswith('.v') or f.endswith('.sv'):
            all_files.append(os.path.join(root, f))

all_files = sorted(all_files)
print(f"Total files to check: {len(all_files)}\n")

# 1. Check each file individually (Isolated Syntax & Preprocessing check)
print("=" * 80)
print("PHASE 1: FILE-BY-FILE SYNTAX & LOCAL PARSE CHECK")
print("=" * 80)

individual_results = {}
for f in all_files:
    rel_path = os.path.relpath(f, workspace)
    try:
        tree = pyslang.SyntaxTree.fromFile(f)
        diags = tree.diagnostics
        diag_list = []
        if diags:
            for d in diags:
                diag_list.append(str(d))
        individual_results[rel_path] = diag_list
        status = "PASSED (Clean)" if not diag_list else f"ISSUES FOUND ({len(diag_list)})"
        print(f"[{status:20s}] {rel_path}")
        for d in diag_list:
            print(f"    -> {d}")
    except Exception as e:
        individual_results[rel_path] = [f"CRITICAL EXCEPTION: {e}"]
        print(f"[ERROR               ] {rel_path}: {e}")

# 2. Comprehensive Multi-File Elaboration Check for each System/Top
print("\n" + "=" * 80)
print("PHASE 2: FULL COMPILATION & ELABORATION CHECK")
print("=" * 80)

# Project 1: System Integration Top (top_module + riscv_cpu + secure_mac + all submodules)
sys_files = [
    os.path.join(workspace, r"rtl\top\top_module.v"),
    os.path.join(workspace, r"rtl\mac\secure_mac.v"),
    os.path.join(workspace, r"rtl\cpu\riscv_cpu.sv"),
    os.path.join(workspace, r"rtl\cpu\imem.sv"),
    os.path.join(workspace, r"rtl\cpu\dmem.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_if_id.sv"),
    os.path.join(workspace, r"rtl\cpu\instruction_decoder.sv"),
    os.path.join(workspace, r"rtl\cpu\control_unit.sv"),
    os.path.join(workspace, r"rtl\cpu\regfile.sv"),
    os.path.join(workspace, r"rtl\cpu\branch_cmp.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_id_ex.sv"),
    os.path.join(workspace, r"rtl\cpu\alu.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_ex_mem.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_mem_wb.sv"),
    os.path.join(workspace, r"rtl\cpu\hazard_unit.sv"),
]

comp_sys = pyslang.Compilation()
for fn in sys_files:
    if os.path.exists(fn):
        comp_sys.addSyntaxTree(pyslang.SyntaxTree.fromFile(fn))

diags_sys = comp_sys.getAllDiagnostics()
report_sys = pyslang.DiagnosticEngine.reportAll(comp_sys.sourceManager, diags_sys)

print("--- System Integration (top_module) Elaboration Diagnostics ---")
if report_sys and report_sys.strip():
    print(report_sys)
else:
    print("  CLEAN: 0 errors, 0 warnings across all 14 interconnected modules!")

# Project 2: Testbench tb_secure_mac.sv
print("\n--- Testbench: tb/sv_tb/tb_secure_mac.sv ---")
comp_tb = pyslang.Compilation()
comp_tb.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\mac\secure_mac.v")))
comp_tb.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"tb\sv_tb\tb_secure_mac.sv")))
diags_tb = comp_tb.getAllDiagnostics()
report_tb = pyslang.DiagnosticEngine.reportAll(comp_tb.sourceManager, diags_tb)
if report_tb and report_tb.strip():
    print(report_tb)
else:
    print("  CLEAN: 0 errors, 0 warnings in tb_secure_mac.sv!")

# Project 3: alu_top wrapper
print("\n--- Module: rtl/top/alu_top.sv ---")
comp_alu = pyslang.Compilation()
comp_alu.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\top\alu_top.sv")))
comp_alu.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\cpu\alu.sv")))
comp_alu.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\cpu\control_unit.sv")))
diags_alu = comp_alu.getAllDiagnostics()
report_alu = pyslang.DiagnosticEngine.reportAll(comp_alu.sourceManager, diags_alu)
if report_alu and report_alu.strip():
    print(report_alu)
else:
    print("  CLEAN: 0 errors, 0 warnings in alu_top.sv!")
