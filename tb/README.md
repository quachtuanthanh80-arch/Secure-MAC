# Verification & Testbench Suite

Thư mục chứa toàn bộ môi trường kiểm chứng phần cứng dựa trên **Cocotb 2.0 (Python)** và **SystemVerilog Testbench truyền thống**.

## Cấu trúc thư mục

```
tb/
├── cocotb/                   # Môi trường kiểm thử hiện đại với Cocotb 2.0 + Icarus Verilog
│   ├── alu_top/              # Unit test khối ALU & Control Unit (20 test cases)
│   │   ├── test_alu_top.py
│   │   └── run_tests.py
│   ├── secure_mac/           # Unit test khối Secure MAC & Tiêm lỗi Rollback (8 cases) + Campaign (4,400 cases)
│   │   ├── test_secure_mac.py
│   │   ├── run_mac_tests.py
│   │   ├── test_fault_campaign.py
│   │   └── run_fault_campaign.py
│   └── top_module/           # System-level testbench tích hợp toàn bộ SoC (4 test cases)
│       ├── test_top_module.py
│       └── run_top_tests.py
└── sv_tb/                    # SystemVerilog Testbench truyền thống
    └── tb_secure_mac.sv      # Direct Verilog testbench
```

---

## Hướng dẫn chạy kiểm thử

* **Chạy toàn bộ test suites (Khuyến nghị)**:
  ```bash
  python run_all_tests.py
  ```
* **Chạy riêng từng thành phần**:
  * ALU Unit Tests: `python tb/cocotb/alu_top/run_tests.py`
  * MAC Unit Tests: `python tb/cocotb/secure_mac/run_mac_tests.py`
  * System-Level SoC Tests: `python tb/cocotb/top_module/run_top_tests.py`
  * Fault Injection Campaign: `python tb/cocotb/secure_mac/run_fault_campaign.py`
