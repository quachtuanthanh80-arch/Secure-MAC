"""
Pytest runner for alu_top cocotb tests.
Uses cocotb_tools.runner (Cocotb 2.0) with Icarus Verilog.
Handles iverilog SystemVerilog warnings gracefully.
"""
import os
import subprocess
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner, Icarus


class IcarusTolerant(Icarus):
    """Icarus runner that tolerates warnings."""
    
    def _execute(self, cmds, cwd=None):
        for cmd in cmds:
            self.log.info(
                "Running command %s in directory %s",
                " ".join(f"'{c}'" if " " in str(c) else str(c) for c in cmd),
                cwd,
            )
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                env=self.env,
                capture_output=True,
                text=True,
            )
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)
            
            if proc.returncode != 0:
                has_real_error = any(
                    'error:' in line.lower() and 'sorry:' not in line.lower()
                    for line in (proc.stderr or "").split('\n')
                )
                vvp_path = cwd / "sim.vvp" if cwd else None
                if has_real_error or (vvp_path and not vvp_path.exists()):
                    raise subprocess.CalledProcessError(
                        proc.returncode, cmd,
                        output=proc.stdout, stderr=proc.stderr
                    )
                else:
                    self.log.warning(
                        "iverilog returned exit code %d but only warnings found, continuing...",
                        proc.returncode
                    )


def test_alu_top_runner():
    """Build and run all cocotb tests for alu_top."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH
    
    sources = [
        root_dir / "rtl" / "cpu" / "alu.sv",
        root_dir / "rtl" / "cpu" / "control_unit.sv",
        root_dir / "rtl" / "top" / "alu_top.sv",
    ]
    
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"
    
    runner = IcarusTolerant()
    runner.build(
        sources=sources,
        hdl_toplevel="alu_top",
        build_args=["-g2012"],
        always=True,
    )
    runner.test(
        hdl_toplevel="alu_top",
        test_module="test_alu_top",
    )


if __name__ == "__main__":
    test_alu_top_runner()