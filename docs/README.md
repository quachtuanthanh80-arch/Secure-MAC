# Documentation & Architecture Specifications

Thư mục chứa các tài liệu kỹ thuật, sơ đồ phân cấp và đặc tả giao tiếp của hệ thống SoC.

## Danh mục tài liệu

| Tên file | Định dạng | Mô tả chi tiết |
| :--- | :--- | :--- |
| [`rtl_summary_tables.md`](file:///d:/NCKH/docs/rtl_summary_tables.md) | Markdown | Bảng tra cứu toàn bộ 15 modules RTL, danh sách cổng vào/ra (I/O ports), độ rộng bit và chức năng từng tín hiệu. |
| [`hierarchy_data.json`](file:///d:/NCKH/docs/hierarchy_data.json) | JSON | Cây phân cấp phần cứng (Hardware Elaboration Hierarchy) trích xuất tự động từ AST của PySlang. |

---

## Sơ đồ Phân cấp Module (Module Hierarchy Tree)

```
top_module (SoC Top)
├── u_cpu: riscv_cpu (RV32I 5-stage CPU)
│   ├── u_if_stage: if_stage (Fetch)
│   ├── u_pipe_if_id: pipe_if_id (Pipeline Reg IF/ID)
│   ├── u_id_stage: id_stage (Decode & Regfile)
│   ├── u_pipe_id_ex: pipe_id_ex (Pipeline Reg ID/EX)
│   ├── u_ex_stage: ex_stage (Execute ALU + Control)
│   │   ├── u_alu: alu
│   │   └── u_control: control_unit
│   ├── u_pipe_ex_mem: pipe_ex_mem (Pipeline Reg EX/MEM)
│   ├── u_mem_stage: mem_stage (Memory Interface)
│   ├── u_pipe_mem_wb: pipe_mem_wb (Pipeline Reg MEM/WB)
│   ├── u_wb_stage: wb_stage (Write-Back)
│   ├── u_hazard: hazard_detection
│   ├── u_forward: forwarding_unit
│   └── u_branch_pred: branch_predictor
├── u_imem: imem (Instruction Memory, 256 words)
├── u_dmem: dmem (Data RAM, 256 words, 0x0000_0000..0x0000_03FF)
└── u_mac: secure_mac (Resilient MAC Accelerator, 0x8000_0000..0x8000_0014)
    ├── u_enc_a: mod3_encoder_8b (Operand A Residue Encoder)
    ├── u_enc_b: mod3_encoder_8b (Operand B Residue Encoder)
    ├── u_enc_c: mod3_encoder_32b (Accumulator Residue Encoder)
    └── u_enc_out: mod3_encoder_32b (Result Residue Encoder)
```
