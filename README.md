# Fault-Resilient RISC-V SoC with Modulo-3 Secure Neural MAC Accelerator

[![RTL Linter](https://img.shields.io/badge/PySlang%20Linter-Passed%20(15%20files)-brightgreen.svg)](#)
[![Verification](https://img.shields.io/badge/Cocotb%20Tests-32%2F32%20PASS%20(100%25)-brightgreen.svg)](#)
[![Fault Injection](https://img.shields.io/badge/Fault%20Injection-81%2C000%20Trials%20Verified-blue.svg)](#)
[![Single-Bit FDR](https://img.shields.io/badge/Single--Bit%20FDR-100.00%25-success.svg)](#)
[![Rollback Accuracy](https://img.shields.io/badge/State%20Rollback-100.00%25-success.svg)](#)
[![FPGA Target](https://img.shields.io/badge/FPGA-Xilinx%20Zynq--7020%20%40%20100MHz-orange.svg)](#)

---

## 📌 Tổng quan dự án (Project Overview)

Dự án nghiên cứu và hiện thực hóa một hệ thống trên chip (**SoC hoàn chỉnh**) tích hợp **Lõi vi xử lý RISC-V 32-bit (RV32I 5 tầng pipeline)** với **Bộ tăng tốc phần cứng Secure MAC** (Multiply-Accumulate) có khả năng tự phát hiện và tự khôi phục trước các cuộc **Tấn công Tiêm lỗi (Fault Injection Attacks - FIA)** và lỗi bức xạ vật lý (Single Event Upsets - SEU) trong quá trình suy luận mạng nơ-ron (Edge AI Inference).

### 💡 Ý tưởng cốt lõi (Core Innovations):
1. **Kiểm tra sai số số học đồng thời (Concurrent Error Detection - CED):** Ứng dụng mã thặng dư số học **Modulo-3 Arithmetic Residue Code** để phát hiện lỗi tính toán $A \times B + C$ trong thời gian thực với overhead phần cứng siêu nhỏ ($< 15\%$).
2. **Khôi phục trạng thái tức thời (Hardware State Rollback):** Tích hợp **Shadow Accumulator** lưu trữ trạng thái hợp lệ gần nhất. Khi phát hiện xung lỗi, mạch ngay lập tức kích hoạt cờ `rollback` để phục hồi dữ liệu gốc, ngăn chặn triệt để hiện tượng Silent Data Corruption (SDC).
3. **Tích hợp SoC & Điều khiển ngắt (Hardware/Software Co-design):** Bộ tăng tốc MAC được kết nối vào bus bộ nhớ CPU thông qua **MMIO** (`0x8000_0000`) và đường ngắt cứng (`irq`), cho phép phần mềm thực thi lớp mạng nơ-ron Fully Connected an toàn.

---

## 🏗️ Kiến trúc Hệ thống (System Architecture)

```
                       +-------------------------------------------------------------+
                       |                        top_module                           |
                       |                                                             |
                       |  +-------------------+      +----------------------------+  |
                       |  |     riscv_cpu     |      |         secure_mac         |  |
                       |  |  5-Stage Pipeline |      |  (Mod-3 Checker + Rollback)|  |
                       |  |                   |      |                            |  |
                       |  |  [IF] [ID] [EX]   |      |  - 8-bit x 8-bit + 32-bit  |  |
                       |  |      [MEM] [WB]   |      |  - Pipelined Mod-3 Encoder |  |
                       |  +---------+---------+      |  - Shadow Accumulator      |  |
                       |            |                +--------------+-------------+  |
                       |            | Memory Bus                    |                |
                       |            v (MMIO / RAM)                  |                |
                       |     +--------------+                       |                |
                       |     | Address Mux  |-----------------------+                |
                       |     +-------+------+       (0x8000_0000..0x8000_0014)       |
                       |             |                                               |
                       |             v (0x0000_0000..0x0000_03FF)                    |
                       |      +-------------+                                        |
                       |      | dmem (RAM)  |                                        |
                       |      +-------------+                                        |
                       |             |                                               |
                       +-------------+-----------------------------------------------+
                                     |
                                     v IRQ (Hardware Fault Interrupt)
```

---

## 📁 Cấu trúc Thư mục Dự án (Project Directory Layout)

```
D:\NCKH
├── docs/                 # Tài liệu kỹ thuật, đặc tả cổng I/O và phân cấp hệ thống
│   ├── README.md
│   ├── rtl_summary_tables.md     # Bảng tra cứu cổng 15 modules RTL
│   ├── hierarchy_data.json       # Cây phân cấp phần cứng trích xuất từ PySlang
├── reports/              # Báo cáo thực nghiệm, ma trận heatmap và datasets
│   ├── README.md
│   ├── exhaustive_fault_injection_report.md  # Báo cáo tổng kết 81,000 ca tiêm lỗi
│   ├── data/                 # Raw datasets (CSV, JSON)
│   └── figures/              # Publication-ready charts and heatmaps
├── rtl/                  # Mã nguồn phần cứng RTL (SystemVerilog / Verilog)
│   ├── cpu/              # Lõi RISC-V 5 tầng (ALU, Control, Forwarding, Hazard, DMEM, IMEM)
│   ├── mac/              # Secure MAC với Modulo-3 Encoders & Rollback
│   ├── top/              # top_module.v (SoC Top) và alu_top.sv (ALU Wrapper)
│   └── filelists/        # Filelist tổng hợp cho trình mô phỏng
├── sw/                   # Phần mềm nhúng, firmware C và mã máy Assembly
│   ├── README.md
│   ├── src/              # Source code (C, Assembly)
│   └── bin/              # Compiled hex machine code (mac_program.hex)
├── synth/                # Cấu hình tổng hợp Vivado (Xilinx Zynq-7020)
│   ├── README.md
│   ├── constraints/      # File XDC ràng buộc xung nhịp 100 MHz
│   ├── fpga_reports/     # Báo cáo FPGA Vivado (Utilization, Timing STA, Power)
│   └── scripts/          # TCL scripts tổng hợp tự động
├── tb/                   # Môi trường kiểm chứng (Verification Suite)
│   ├── README.md
│   ├── cocotb/           # Cocotb 2.0 Testbenches (Python + Icarus Verilog)
│   └── sv_tb/            # SystemVerilog testbench truyền thống
├── tools/                # Bộ công cụ tự động hóa, linter và tiêm lỗi
│   ├── README.md
│   ├── analysis/         # Plotting and RTL inspection (plot_results.py, etc.)
│   ├── fault_injection/  # Fault injection engines (exhaustive_fault_injection.py)
│   └── linting/          # Static analysis (run_full_linter.py, detailed_sv_lint.py)
└── run_all_tests.py      # Master Test Runner (Chạy toàn bộ 5 test suites)
```

---

## 🗺️ Bản đồ Bộ nhớ & Thanh ghi MMIO (Memory Map)

| Dải địa chỉ (Hex) | Tên thanh ghi | Chức năng |
| :--- | :--- | :--- |
| `0x0000_0000` – `0x0000_03FF` | **Data Memory (DMEM)** | Bộ nhớ RAM 1KB lưu trữ biến, mảng trọng số và kết quả |
| `0x8000_0000` | `REG_MAC_A` (8-bit) | Toán hạng $A$ (Trọng số Weight, INT8 signed) |
| `0x8000_0004` | `REG_MAC_B` (8-bit) | Toán hạng $B$ (Đầu vào Activation, INT8 signed) |
| `0x8000_0008` | `REG_MAC_C` / `MAC_OUT` (32-bit) | Nạp giá trị cộng dồn $C$ hoặc đọc kết quả $A \times B + C$ (INT32) |
| `0x8000_000C` | `REG_MAC_START` (1-bit) | Ghi `1` để kích hoạt chu trình tính toán MAC |
| `0x8000_0014` | `REG_MAC_STATUS` (32-bit) | Bit 1: `valid` (tính xong), Bit 0: `fault_detected` (phát hiện lỗi) |

---

## 📊 Kết quả Thực nghiệm Tiêm lỗi (Fault Injection Results)

Kết quả từ chiến dịch tiêm lỗi toàn diện (**81,000 thử nghiệm**):

| Mô hình lỗi (Fault Model) | Vị trí tiêm | Số lượng tiêm | Phát hiện & Rollback | SDC (Bỏ sót) | Tỷ lệ phát hiện (**FDR %**) | Tỷ lệ Rollback thành công |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Single-Bit SEU (Exhaustive)** | `pipe_product` (16b) | 1,600 | 1,600 | 0 | **100.00%** | **100.00%** |
| **Single-Bit SEU (Exhaustive)** | `pipe_c` (32b) | 3,200 | 3,200 | 0 | **100.00%** | **100.00%** |
| **Double-Bit MBU (Tất cả 616 cặp)** | `pipe_product` + `pipe_c` | 61,600 | 30,348 | 31,252 | **49.27%** | **100.00%** |
| **Stuck-At-0 / Stuck-At-1** | `pipe_product` + `pipe_c` | 9,600 | 4,800 | 0 | **100.00%** | **100.00%** |
| **Multi-Bit Bursts (3–6 bit)** | `pipe_c` (32b) | 5,000 | 3,434 | 1,566 | **68.68%** | **100.00%** |
| **TỔNG CỘNG TOÀN CHIẾN DỊCH** | — | **81,000** | **43,382** | **32,818** | — | **100.00%** |

> 📐 **Đóng góp lý thuyết:** Dự án chứng minh định lý **Bit-Pair Parity Theorem**, giải thích chính xác tại sao tỷ lệ phát hiện lỗi 2-bit luôn tiệm cận $50.0\%$ dựa trên tính chẵn lẻ của vị trí bit trong hệ thặng dư modulo 3.

---

## ⚡ Kết quả Tổng hợp Phần cứng (FPGA Synthesis Results)

Kết quả hiện thực hóa trên chip FPGA **Xilinx Zynq-7020** (`xc7z020clg400-1`):

| Thông số (Metric) | Kết quả SoC `top_module` | Kết quả Khối `secure_mac` | Đánh giá |
| :--- | :---: | :---: | :--- |
| **Clock Frequency** | **100.00 MHz** | 200.00 MHz | Tần số vận hành danh định |
| **Worst Negative Slack (WNS)** | **+0.694 ns** (MET ✅) | -1.820 ns | Đạt chuẩn timing ở 100 MHz |
| **Slice LUTs** | **614** (1.15% utilization) | 671 (1.26%) | Diện tích cực kỳ nhỏ gọn |
| **Slice Registers (FFs)** | **657** (0.62% utilization) | 660 (0.62%) | Tiết kiệm flip-flop |
| **DSP Blocks** | **0** (0.00%) | 0 (0.00%) | Nhân 8x8 thuần LUT fabric, tính khả chuyển cao |
| **Block RAM (BRAM)** | **0** (0.00%) | 0 (0.00%) | Không chiếm BRAM chuyên dụng |
| **Dynamic Power** | **0.017 W** (17 mW) | 0.022 W (22 mW) | Tiêu thụ năng lượng cực thấp cho Edge AI |
| **Total On-Chip Power** | **0.120 W** (120 mW) | 0.127 W (127 mW) | Bao gồm 103 mW static power của chip FPGA |

---

## 🚀 Hướng dẫn Chạy & Tái tạo Kết quả (Quick Start)

### 1. Cài đặt môi trường Python & Trình mô phỏng
```bash
pip install cocotb cocotb-tools pyslang pytest
```
*Đảm bảo máy đã cài đặt **Icarus Verilog (`iverilog`)** và đã thêm vào biến môi trường PATH.*

### 2. Chạy toàn bộ Test Suites của Dự án (1 Lệnh duy nhất)
```bash
python run_all_tests.py
```

### 3. Chạy chiến dịch Tiêm lỗi Toàn diện (81,000 Thử nghiệm trong 2 giây)
```bash
python tools/exhaustive_fault_injection.py
```

---


