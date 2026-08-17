# Automation Tools & Analysis Scripts

Thư mục chứa các công cụ Python phục vụ tự động hóa kiểm tra RTL, linting, phân tích AST, và thực thi chiến dịch tiêm lỗi.

## Danh mục Công cụ

| Tên Script | Mục đích | Cách sử dụng |
| :--- | :--- | :--- |
| [`plot_results.py`](file:///d:/NCKH/tools/plot_results.py) | **Vẽ đồ thị khoa học (300+ DPI Figures)**: Tự động đọc dữ liệu từ các file CSV và vẽ 4 biểu đồ / bản đồ nhiệt chất lượng cao cho bài báo IEEE. | `python tools/plot_results.py` |
| [`exhaustive_fault_injection.py`](file:///d:/NCKH/tools/exhaustive_fault_injection.py) | **Chiến dịch tiêm lỗi toàn diện (81,000 ca)**: Đo lường Single-bit, Double-bit, Stuck-at, Multi-bit, xuất ma trận Heatmap 2D CSV và báo cáo Markdown. | `python tools/exhaustive_fault_injection.py` |
| [`run_full_linter.py`](file:///d:/NCKH/tools/run_full_linter.py) | **Kiểm tra cú pháp & Elaboration RTL bằng PySlang**: Quét toàn bộ 15 file RTL để tìm lỗi cú pháp, vi phạm kiểu dữ liệu hoặc xung đột cổng. | `python tools/run_full_linter.py` |
| [`inspect_rtl.py`](file:///d:/NCKH/tools/inspect_rtl.py) | **Trích xuất cây phân cấp thiết kế**: Quét AST và xuất ra file JSON phân cấp phần cứng. | `python tools/inspect_rtl.py` |
| [`dump_tables.py`](file:///d:/NCKH/tools/dump_tables.py) | **Tự động sinh tài liệu cổng I/O**: Đọc file JSON phân cấp và sinh file [`docs/rtl_summary_tables.md`](file:///d:/NCKH/docs/rtl_summary_tables.md). | `python tools/dump_tables.py` |
| [`detailed_sv_lint.py`](file:///d:/NCKH/tools/detailed_sv_lint.py) | **Linter chi tiết theo từng module**: Báo cáo cảnh báo và gợi ý tối ưu hóa code SystemVerilog. | `python tools/detailed_sv_lint.py` |
