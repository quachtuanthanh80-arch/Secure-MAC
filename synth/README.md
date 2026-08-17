# FPGA Synthesis & Implementation Results (Xilinx Vivado)

Thư mục chứa cấu hình tổng hợp, file ràng buộc chân & xung nhịp (XDC constraints), và báo cáo tài nguyên/thời gian thực tế trên FPGA **Xilinx Zynq-7020** (`xc7z020clg400-1`).

## 1. Cấu trúc thư mục

* [`constraints/top_constraints.xdc`](file:///d:/NCKH/synth/constraints/top_constraints.xdc): Ràng buộc xung nhịp hệ thống $100\text{ MHz}$ ($10\text{ ns}$ period) và khai báo false paths.
* [`fpga_reports/top_module_utilization.txt`](file:///d:/NCKH/synth/fpga_reports/top_module_utilization.txt): Báo cáo sử dụng tài nguyên phần cứng (LUTs, FFs, BRAM, DSP) của toàn bộ SoC.
* [`fpga_reports/top_module_timing.txt`](file:///d:/NCKH/synth/fpga_reports/top_module_timing.txt): Báo cáo phân tích thời gian tĩnh (STA), Worst Negative Slack (WNS).
* [`fpga_reports/top_module_power.txt`](file:///d:/NCKH/synth/fpga_reports/top_module_power.txt): Báo cáo công suất tiêu thụ động & tĩnh (Power Analysis).
* [`scripts/run_synth_top.tcl`](file:///d:/NCKH/synth/scripts/run_synth_top.tcl): Script TCL tự động hóa quá trình Synthesis & Implementation trên Vivado.

---

## 2. Bảng kết quả tổng hợp thực tế (Synthesis Summary)

| Chỉ số (Metric) | Kết quả SoC `top_module` (@ 100MHz) | Kết quả Khối `secure_mac` (@ 200MHz) | Nhận xét |
| :--- | :---: | :---: | :--- |
| **Target Device** | Xilinx Zynq-7020 (`xc7z020clg400-1`) | Xilinx Zynq-7020 | Chip FPGA thông dụng trong nghiên cứu Edge AI |
| **Clock Frequency** | **100.00 MHz** | 200.00 MHz | Tần số vận hành |
| **Worst Negative Slack (WNS)** | **+0.694 ns** (TIMING MET ✅) | -1.820 ns | Đạt chuẩn timing ở 100 MHz với biên an toàn lớn |
| **Slice LUTs** | **614** (1.15% utilization) | 671 (1.26%) | Diện tích cực nhỏ, fit hoàn toàn trong fabric |
| **Slice Registers (FFs)** | **657** (0.62% utilization) | 660 (0.62%) | Tiết kiệm thanh ghi |
| **DSP Blocks** | **0** (0.00%) | 0 (0.00%) | Multiplier 8x8 thuần LUT fabric, tính khả chuyển cao |
| **Block RAM (BRAM)** | **0** (0.00%) | 0 (0.00%) | IMEM và DMEM dạng Distributed RAM |
| **Dynamic Power** | **0.017 W** (17 mW) | 0.022 W (22 mW) | Tiêu thụ năng lượng cực thấp cho Edge AI |
| **Total On-Chip Power** | **0.120 W** (120 mW) | 0.127 W (127 mW) | Bao gồm 103 mW static power của chip FPGA |
