# Software Stack & Assembly Firmware

Thư mục chứa mã nguồn phần mềm, driver điều khiển phần cứng qua MMIO, và chương trình mã máy mẫu chạy trên SoC RISC-V.

## Danh mục File

| Tên File | Ngôn ngữ | Chức năng |
| :--- | :--- | :--- |
| [`src/fully_connected_layer.c`](file:///d:/NCKH/sw/src/fully_connected_layer.c) | C (Embedded) | Driver C điều khiển bộ tăng tốc Secure MAC thực thi lớp Fully Connected trong mạng nơ-ron: định nghĩa cấu trúc thanh ghi MMIO, hàm nạp trọng số, kích hoạt phép nhân cộng dồn, và hàm xử lý ngắt lỗi (ISR). |
| [`src/mac_program.s`](file:///d:/NCKH/sw/src/mac_program.s) | RISC-V Assembly (RV32I) | Chương trình Assembly mẫu: khởi tạo thanh ghi, nạp giá trị $A=10, B=5, C=100$, ghi vào địa chỉ MMIO `0x8000_0000..0x8000_000C`, đợi cờ `valid`, đọc kết quả $150$ và lưu vào RAM `0x0000_0010`. |
| [`bin/mac_program.hex`](file:///d:/NCKH/sw/bin/mac_program.hex) | Verilog Hex (Mem format) | File mã máy hex (256-word format) được nạp trực tiếp vào [`rtl/cpu/imem.sv`](file:///d:/NCKH/rtl/cpu/imem.sv) khi mô phỏng SoC. |

---

## Bản đồ Thanh ghi MMIO (Hardware MMIO Offsets)

```c
#define SECURE_MAC_BASE     0x80000000
#define REG_MAC_A           (*(volatile uint32_t*)(SECURE_MAC_BASE + 0x00))
#define REG_MAC_B           (*(volatile uint32_t*)(SECURE_MAC_BASE + 0x04))
#define REG_MAC_C           (*(volatile uint32_t*)(SECURE_MAC_BASE + 0x08))
#define REG_MAC_START       (*(volatile uint32_t*)(SECURE_MAC_BASE + 0x0C))
#define REG_MAC_STATUS      (*(volatile uint32_t*)(SECURE_MAC_BASE + 0x14))
```
