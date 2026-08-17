"""
Pytest runner for Secure_MAC cocotb tests.
Uses cocotb_tools.runner (Cocotb 2.0) with Icarus Verilog.
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
            self.log.info("Running command %s in directory %s", " ".join(str(c) for c in cmd), cwd)
            proc = subprocess.run(cmd, cwd=cwd, env=self.env, capture_output=True, text=True)
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)
            if proc.returncode != 0:
                has_real_error = any('error:' in line.lower() and 'sorry:' not in line.lower() for line in (proc.stderr or "").split('\n'))
                vvp_path = cwd / "sim.vvp" if cwd else None
                if has_real_error or (vvp_path and not vvp_path.exists()):
                    raise subprocess.CalledProcessError(proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr)


def test_secure_mac_runner():
    """Build and run all cocotb tests for secure_mac."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH
    
    sources = [root_dir / "rtl" / "mac" / "secure_mac.v"]
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"
        
    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="secure_mac",
        build_args=["-g2012"],
        always=True,
    )
    runner.test(
        hdl_toplevel="secure_mac",
        test_module="test_secure_mac",
    )


if __name__ == "__main__":
    test_secure_mac_runner()
