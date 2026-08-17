"""
Master Test Runner for NCKH RISC-V + Secure MAC SoC Project.
Runs all Linters, Unit Tests, and System-Level Cocotb Testbenches.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_step(step_name, cmd, cwd):
    print("\n" + "=" * 80)
    print(f"RUNNING STEP: {step_name}")
    print("=" * 80)
    start_time = time.time()
    
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=False,
    )
    elapsed = time.time() - start_time
    status = "PASSED" if proc.returncode == 0 else "FAILED"
    print(f"\n>>> [{status}] {step_name} (Time: {elapsed:.2f}s)\n")
    return proc.returncode == 0, elapsed


def main():
    root_dir = Path(__file__).resolve().parent
    
    steps = [
        # Linter execution: Analyzes RTL files for syntax and semantic errors using PySlang
        ("1. PySlang RTL Linter & Elaboration Check", [sys.executable, str(root_dir / "tools" / "linting" / "run_full_linter.py")]),
        
        # Runs basic Arithmetic Logic Unit corner cases
        ("2. Cocotb ALU Top Tests (20 Corner-Cases)", [sys.executable, str(root_dir / "tb" / "cocotb" / "alu_top" / "run_tests.py")]),
        
        # Validates normal operation and fault-tolerance (rollback mechanism) of the Secure MAC
        ("3. Cocotb Secure MAC Tests (8 Fault-Tolerance Cases)", [sys.executable, str(root_dir / "tb" / "cocotb" / "secure_mac" / "run_mac_tests.py")]),
        
        # Complete SoC testing running real instructions from sw/bin/mac_program.hex
        ("4. Cocotb SoC System Integration Tests (4 End-to-End Cases)", [sys.executable, str(root_dir / "tb" / "cocotb" / "top_module" / "run_top_tests.py")]),
        
        # Statistical fault injection campaign simulating radiation/glitch attacks
        ("5. Cocotb Fault Injection Campaign (4,400 Trials & Coverage)", [sys.executable, str(root_dir / "tb" / "cocotb" / "secure_mac" / "run_fault_campaign.py")]),
    ]
    
    results = []
    all_passed = True
    
    for name, cmd in steps:
        passed, elapsed = run_step(name, cmd, root_dir)
        results.append((name, passed, elapsed))
        if not passed:
            all_passed = False
            
    print("\n" + "=" * 80)
    print("                      SUMMARY TEST DASHBOARD")
    print("=" * 80)
    print(f"{'Test Suite':<60} | {'Status':<8} | {'Time':<8}")
    print("-" * 80)
    for name, passed, elapsed in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        print(f"{name:<60} | {status_str:<8} | {elapsed:>6.2f}s")
    print("=" * 80)
    
    if all_passed:
        print("\n[SUCCESS] ALL TEST SUITES PASSED PERFECTLY (100% SUCCESS)!\n")
        sys.exit(0)
    else:
        print("\n[FAIL] SOME TESTS FAILED. PLEASE CHECK LOGS ABOVE.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
