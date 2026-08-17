r"""
Detailed SystemVerilog & Verilog Linter, Syntax & Elaboration Checker
Powered by pyslang.
Scans all design units and testbenches in D:\NCKH.
"""

import os
import json
import pyslang

workspace = r"D:\NCKH"

# Collect all HDL files
hdl_files = []
for root, dirs, files in os.walk(workspace):
    if any(ignore in root for ignore in ['.vscode', '.git', '.Xil', 'sim_build', '__pycache__', 'synth']):
        continue
    for f in files:
        if f.endswith('.v') or f.endswith('.sv'):
            hdl_files.append(os.path.join(root, f))

hdl_files = sorted(hdl_files)

print("=" * 80)
print("1. FILE-BY-FILE SYNTAX & PREPROCESSOR PARSE CHECK")
print("=" * 80)

syntax_errors = 0
for f in hdl_files:
    rel_path = os.path.relpath(f, workspace)
    tree = pyslang.SyntaxTree.fromFile(f)
    diags = tree.diagnostics
    if diags:
        print(f"[FAILED] {rel_path}: {len(diags)} diagnostic(s)")
        for d in diags:
            print(f"    Line {d.location}: {d.message}")
            syntax_errors += 1
    else:
        print(f"[CLEAN ] {rel_path}")

print(f"\nTotal Syntax / Local Parse Errors: {syntax_errors}\n")

print("=" * 80)
print("2. MULTI-MODULE ELABORATION, TYPE & DECLARATION CHECK")
print("=" * 80)

# Target 1: Full SoC (top_module)
print("\n--- Target 1: SoC Integration (top_module) ---")
soc_files = [
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

comp_soc = pyslang.Compilation()
for fn in soc_files:
    if os.path.exists(fn):
        comp_soc.addSyntaxTree(pyslang.SyntaxTree.fromFile(fn))

diags_soc = comp_soc.getAllDiagnostics()
rep_soc = pyslang.DiagnosticEngine.reportAll(comp_soc.sourceManager, diags_soc)
if rep_soc and rep_soc.strip():
    print(rep_soc)
else:
    print("  CLEAN: 0 errors, 0 warnings across all SoC modules!")

# Target 2: ALU Standalone Wrapper (alu_top)
print("\n--- Target 2: ALU Top Wrapper (alu_top) ---")
comp_alu = pyslang.Compilation()
comp_alu.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\top\alu_top.sv")))
comp_alu.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\cpu\alu.sv")))
comp_alu.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\cpu\control_unit.sv")))
diags_alu = comp_alu.getAllDiagnostics()
rep_alu = pyslang.DiagnosticEngine.reportAll(comp_alu.sourceManager, diags_alu)
if rep_alu and rep_alu.strip():
    print(rep_alu)
else:
    print("  CLEAN: 0 errors, 0 warnings in alu_top!")

# Target 3: Secure MAC SystemVerilog Testbench (tb_secure_mac)
print("\n--- Target 3: Secure MAC SV Testbench (tb_secure_mac) ---")
comp_tb = pyslang.Compilation()
comp_tb.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"rtl\mac\secure_mac.v")))
comp_tb.addSyntaxTree(pyslang.SyntaxTree.fromFile(os.path.join(workspace, r"tb\sv_tb\tb_secure_mac.sv")))
diags_tb = comp_tb.getAllDiagnostics()
rep_tb = pyslang.DiagnosticEngine.reportAll(comp_tb.sourceManager, diags_tb)
if rep_tb and rep_tb.strip():
    print(rep_tb)
else:
    print("  CLEAN: 0 errors, 0 warnings in tb_secure_mac!")
