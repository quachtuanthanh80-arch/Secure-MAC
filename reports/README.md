# Experimental Reports & Fault Injection Datasets

Thư mục chứa toàn bộ dữ liệu thực nghiệm, báo cáo phân tích độ phủ lỗi (Fault Coverage) và ma trận tương quan cho bài báo khoa học.

## Danh mục File Báo cáo & Dữ liệu
| Tên File | Loại | Mô tả |
| :--- | :--- | :--- |
| [`exhaustive_fault_injection_report.md`](file:///d:/NCKH/reports/exhaustive_fault_injection_report.md) | Markdown | **Báo cáo tổng kết 81,000 thử nghiệm tiêm lỗi**: Phân tích Single-Bit (100%), Double-Bit (49.3%), Stuck-At (100%), Multi-Bit Bursts (68.7%), định lý chẵn lẻ Bit-Pair Parity Theorem. |
| [`data/double_bit_heatmap_32b.csv`](file:///d:/NCKH/reports/data/double_bit_heatmap_32b.csv) | CSV | **Ma trận 2D $32 \times 32$**: Tỷ lệ phát hiện lỗi cho tất cả $\binom{32}{2} = 496$ cặp bit trong thanh ghi Accumulator `pipe_c`. Dùng để vẽ Heatmap biểu đồ bài báo. |
| [`data/double_bit_heatmap_16b.csv`](file:///d:/NCKH/reports/data/double_bit_heatmap_16b.csv) | CSV | **Ma trận 2D $16 \times 16$**: Tỷ lệ phát hiện lỗi cho tất cả $\binom{16}{2} = 120$ cặp bit trong thanh ghi Multiplier `pipe_product`. |
| [`data/stuck_at_coverage.csv`](file:///d:/NCKH/reports/data/stuck_at_coverage.csv) | CSV | Bảng chi tiết kết quả kiểm thử mô hình lỗi Stuck-At-0 (SA0) và Stuck-At-1 (SA1) theo từng bit vị trí. |
| [`data/fault_injection_coverage.csv`](file:///d:/NCKH/reports/data/fault_injection_coverage.csv) | CSV | Dataset phân tích lỗi đơn theo vị trí bit từ $0$ đến $31$. |
| [`data/fault_injection_results.json`](file:///d:/NCKH/reports/data/fault_injection_results.json) | JSON | Dữ liệu thô định dạng JSON xuất trực tiếp từ Cocotb runner. |

---

## 🖼️ Danh mục Đồ thị Khoa học (300+ DPI Figures for IEEE Paper)

Trong thư mục [`reports/figures/`](file:///d:/NCKH/reports/figures):
1. **[`fig1_single_bit_fdr.png`](file:///d:/NCKH/reports/figures/fig1_single_bit_fdr.png)**: Biểu đồ cột độ phủ lỗi đơn (100.00% across all 32 bits) và độ chính xác State Rollback (100.00%).
2. **[`fig2_double_bit_heatmap_32b.png`](file:///d:/NCKH/reports/figures/fig2_double_bit_heatmap_32b.png)**: Bản đồ nhiệt 2D ($32 \times 32$) ma trận phát hiện lỗi 2-bit cho thanh ghi `pipe_c`.
3. **[`fig3_double_bit_heatmap_16b.png`](file:///d:/NCKH/reports/figures/fig3_double_bit_heatmap_16b.png)**: Bản đồ nhiệt 2D ($16 \times 16$) ma trận phát hiện lỗi 2-bit cho thanh ghi `pipe_product`.
4. **[`fig4_multibit_burst_scaling.png`](file:///d:/NCKH/reports/figures/fig4_multibit_burst_scaling.png)**: Biểu đồ đường phân tích lỗi nhiều bit (3–6 bits) tiệm cận ngưỡng lý thuyết $2/3 \approx 66.67\%$.

---

## Cách tái tạo dữ liệu (How to Reproduce)

1. **Chạy bộ thử nghiệm Exhaustive Suite (81,000 ca, ~2 giây)**:
   ```bash
   python tools/exhaustive_fault_injection.py
   ```
2. **Chạy bộ mô phỏng RTL Cocotb (4,400 ca, ~7 giây)**:
   ```bash
   python tb/cocotb/secure_mac/run_fault_campaign.py
   ```
