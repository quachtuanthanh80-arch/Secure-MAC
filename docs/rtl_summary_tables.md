# RTL Module Interface Specification

Total Unique RTL Modules: 18

### Module: `alu`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `alu_op` | **In** | `logic[3:0]` |
| `a` | **In** | `logic[31:0]` |
| `b` | **In** | `logic[31:0]` |
| `result` | **Out** | `logic[31:0]` |
| `zero` | **Out** | `logic` |
| `carry` | **Out** | `logic` |

---

### Module: `alu_top`
**Parameters:**
- `S_IDLE` (logic[2:0])
- `S_DECODE` (logic[2:0])
- `S_EXECUTE` (logic[2:0])
- `S_DONE` (logic[2:0])
- `S_ERROR` (logic[2:0])

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `opcode` | **In** | `logic[6:0]` |
| `funct3` | **In** | `logic[2:0]` |
| `funct7` | **In** | `logic[6:0]` |
| `operand_a` | **In** | `logic[31:0]` |
| `operand_b` | **In** | `logic[31:0]` |
| `alu_result` | **Out** | `reg[31:0]` |
| `zero_flag` | **Out** | `reg` |
| `carry_flag` | **Out** | `reg` |
| `RegWrite` | **Out** | `reg` |
| `ResultSrc` | **Out** | `reg[1:0]` |
| `MemWrite` | **Out** | `reg` |
| `MemRead` | **Out** | `reg` |
| `Branch` | **Out** | `reg` |
| `Jump` | **Out** | `reg` |
| `ALUSrcA` | **Out** | `reg[1:0]` |
| `ALUSrcB` | **Out** | `reg[1:0]` |
| `ALUOp` | **Out** | `reg[3:0]` |
| `ImmSrc` | **Out** | `reg[2:0]` |
| `MacStart` | **Out** | `reg` |
| `fsm_state` | **Out** | `logic[2:0]` |

---

### Module: `branch_cmp`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `a` | **In** | `logic[31:0]` |
| `b` | **In** | `logic[31:0]` |
| `funct3` | **In** | `logic[2:0]` |
| `branch_en` | **In** | `logic` |
| `branch_taken` | **Out** | `logic` |

---

### Module: `control_unit`
**Parameters:**
- `RType` (logic[6:0])
- `IType` (logic[6:0])
- `LOAD` (logic[6:0])
- `STORE` (logic[6:0])
- `BRANCH` (logic[6:0])
- `LUI` (logic[6:0])
- `AUIPC` (logic[6:0])
- `JAL` (logic[6:0])
- `JALR` (logic[6:0])
- `MacOp` (logic[6:0])

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `opcode` | **In** | `logic[6:0]` |
| `funct3` | **In** | `logic[2:0]` |
| `funct7` | **In** | `logic[6:0]` |
| `RegWrite` | **Out** | `logic` |
| `ResultSrc` | **Out** | `logic[1:0]` |
| `MemWrite` | **Out** | `logic` |
| `MemRead` | **Out** | `logic` |
| `Branch` | **Out** | `logic` |
| `Jump` | **Out** | `logic` |
| `ALUSrcA` | **Out** | `logic[1:0]` |
| `ALUSrcB` | **Out** | `logic[1:0]` |
| `ALUOp` | **Out** | `logic[3:0]` |
| `ImmSrc` | **Out** | `logic[2:0]` |
| `MacStart` | **Out** | `logic` |

---

### Module: `dmem`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `we` | **In** | `logic` |
| `a` | **In** | `logic[31:0]` |
| `wd` | **In** | `logic[31:0]` |
| `rd` | **Out** | `logic[31:0]` |

---

### Module: `hazard_unit`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `rs1_addr_EX` | **In** | `logic[4:0]` |
| `rs2_addr_EX` | **In** | `logic[4:0]` |
| `rd_addr_MEM` | **In** | `logic[4:0]` |
| `RegWrite_MEM` | **In** | `logic` |
| `rd_addr_WB` | **In** | `logic[4:0]` |
| `RegWrite_WB` | **In** | `logic` |
| `MemRead_EX` | **In** | `logic` |
| `rd_addr_EX` | **In** | `logic[4:0]` |
| `rs1_addr_ID` | **In** | `logic[4:0]` |
| `rs2_addr_ID` | **In** | `logic[4:0]` |
| `branch_taken_ID` | **In** | `logic` |
| `jump_ID` | **In** | `logic` |
| `forwardA_EX` | **Out** | `logic[1:0]` |
| `forwardB_EX` | **Out** | `logic[1:0]` |
| `stall_IF` | **Out** | `logic` |
| `stall_ID` | **Out** | `logic` |
| `flush_ID` | **Out** | `logic` |
| `flush_EX` | **Out** | `logic` |

---

### Module: `imem`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `a` | **In** | `logic[31:0]` |
| `rd` | **Out** | `logic[31:0]` |

---

### Module: `instruction_decoder`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `instr` | **In** | `logic[31:0]` |
| `opcode` | **Out** | `logic[6:0]` |
| `funct3` | **Out** | `logic[2:0]` |
| `funct7` | **Out** | `logic[6:0]` |
| `rs1` | **Out** | `logic[4:0]` |
| `rs2` | **Out** | `logic[4:0]` |
| `rd_addr` | **Out** | `logic[4:0]` |
| `imm_i` | **Out** | `logic[31:0]` |
| `imm_s` | **Out** | `logic[31:0]` |
| `imm_b` | **Out** | `logic[31:0]` |
| `imm_u` | **Out** | `logic[31:0]` |
| `imm_j` | **Out** | `logic[31:0]` |

---

### Module: `mod3_encoder_32b`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `in` | **In** | `logic[31:0]` |
| `out` | **Out** | `reg[1:0]` |

---

### Module: `mod3_encoder_8b`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `in` | **In** | `logic[7:0]` |
| `out` | **Out** | `reg[1:0]` |

---

### Module: `pipe_ex_mem`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `RegWrite_in` | **In** | `logic` |
| `ResultSrc_in` | **In** | `logic[1:0]` |
| `MemWrite_in` | **In** | `logic` |
| `MemRead_in` | **In** | `logic` |
| `alu_result_in` | **In** | `logic[31:0]` |
| `rs2_data_in` | **In** | `logic[31:0]` |
| `rd_addr_in` | **In** | `logic[4:0]` |
| `pc_plus_4_in` | **In** | `logic[31:0]` |
| `RegWrite_out` | **Out** | `logic` |
| `ResultSrc_out` | **Out** | `logic[1:0]` |
| `MemWrite_out` | **Out** | `logic` |
| `MemRead_out` | **Out** | `logic` |
| `alu_result_out` | **Out** | `logic[31:0]` |
| `rs2_data_out` | **Out** | `logic[31:0]` |
| `rd_addr_out` | **Out** | `logic[4:0]` |
| `pc_plus_4_out` | **Out** | `logic[31:0]` |

---

### Module: `pipe_id_ex`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `flush` | **In** | `logic` |
| `RegWrite_in` | **In** | `logic` |
| `ResultSrc_in` | **In** | `logic[1:0]` |
| `MemWrite_in` | **In** | `logic` |
| `MemRead_in` | **In** | `logic` |
| `Branch_in` | **In** | `logic` |
| `Jump_in` | **In** | `logic` |
| `ALUSrcA_in` | **In** | `logic[1:0]` |
| `ALUSrcB_in` | **In** | `logic[1:0]` |
| `ALUOp_in` | **In** | `logic[3:0]` |
| `pc_in` | **In** | `logic[31:0]` |
| `rs1_data_in` | **In** | `logic[31:0]` |
| `rs2_data_in` | **In** | `logic[31:0]` |
| `imm_in` | **In** | `logic[31:0]` |
| `rs1_addr_in` | **In** | `logic[4:0]` |
| `rs2_addr_in` | **In** | `logic[4:0]` |
| `rd_addr_in` | **In** | `logic[4:0]` |
| `RegWrite_out` | **Out** | `logic` |
| `ResultSrc_out` | **Out** | `logic[1:0]` |
| `MemWrite_out` | **Out** | `logic` |
| `MemRead_out` | **Out** | `logic` |
| `Branch_out` | **Out** | `logic` |
| `Jump_out` | **Out** | `logic` |
| `ALUSrcA_out` | **Out** | `logic[1:0]` |
| `ALUSrcB_out` | **Out** | `logic[1:0]` |
| `ALUOp_out` | **Out** | `logic[3:0]` |
| `pc_out` | **Out** | `logic[31:0]` |
| `rs1_data_out` | **Out** | `logic[31:0]` |
| `rs2_data_out` | **Out** | `logic[31:0]` |
| `imm_out` | **Out** | `logic[31:0]` |
| `rs1_addr_out` | **Out** | `logic[4:0]` |
| `rs2_addr_out` | **Out** | `logic[4:0]` |
| `rd_addr_out` | **Out** | `logic[4:0]` |

---

### Module: `pipe_if_id`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `stall` | **In** | `logic` |
| `flush` | **In** | `logic` |
| `pc_in` | **In** | `logic[31:0]` |
| `instr_in` | **In** | `logic[31:0]` |
| `pc_out` | **Out** | `logic[31:0]` |
| `instr_out` | **Out** | `logic[31:0]` |

---

### Module: `pipe_mem_wb`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `RegWrite_in` | **In** | `logic` |
| `ResultSrc_in` | **In** | `logic[1:0]` |
| `alu_result_in` | **In** | `logic[31:0]` |
| `mem_rdata_in` | **In** | `logic[31:0]` |
| `rd_addr_in` | **In** | `logic[4:0]` |
| `pc_plus_4_in` | **In** | `logic[31:0]` |
| `RegWrite_out` | **Out** | `logic` |
| `ResultSrc_out` | **Out** | `logic[1:0]` |
| `alu_result_out` | **Out** | `logic[31:0]` |
| `mem_rdata_out` | **Out** | `logic[31:0]` |
| `rd_addr_out` | **Out** | `logic[4:0]` |
| `pc_plus_4_out` | **Out** | `logic[31:0]` |

---

### Module: `regfile`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `rs1_addr` | **In** | `logic[4:0]` |
| `rs1_data` | **Out** | `logic[31:0]` |
| `rs2_addr` | **In** | `logic[4:0]` |
| `rs2_data` | **Out** | `logic[31:0]` |
| `reg_write` | **In** | `logic` |
| `rd_addr` | **In** | `logic[4:0]` |
| `rd_data` | **In** | `logic[31:0]` |

---

### Module: `riscv_cpu`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `mem_addr` | **Out** | `logic[31:0]` |
| `mem_write` | **Out** | `logic` |
| `mem_wdata` | **Out** | `logic[31:0]` |
| `mem_valid` | **Out** | `logic` |
| `mem_ready` | **In** | `logic` |
| `mem_rdata` | **In** | `logic[31:0]` |
| `mac_start` | **Out** | `logic` |
| `mac_a` | **Out** | `logic[7:0]` |
| `mac_b` | **Out** | `logic[7:0]` |
| `mac_c` | **Out** | `logic[15:0]` |
| `mac_out` | **In** | `logic[15:0]` |
| `mac_fault` | **In** | `logic` |
| `mac_valid` | **In** | `logic` |
| `mac_rollback` | **In** | `logic` |
| `irq` | **In** | `logic` |
| `reg_write` | **Out** | `logic` |
| `rd_addr` | **Out** | `logic[4:0]` |
| `rs1_addr` | **Out** | `logic[4:0]` |
| `rs2_addr` | **Out** | `logic[4:0]` |
| `alu_out` | **Out** | `logic[31:0]` |
| `pc` | **Out** | `logic[31:0]` |
| `mem_read` | **Out** | `logic` |
| `pc_next` | **Out** | `logic[31:0]` |

---

### Module: `secure_mac`
**Parameters:**
- `IN_WIDTH` (logic signed[31:0])
- `OUT_WIDTH` (logic signed[31:0])

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `a` | **In** | `logic signed[7:0]` |
| `b` | **In** | `logic signed[7:0]` |
| `c` | **In** | `logic signed[15:0]` |
| `start` | **In** | `logic` |
| `out` | **Out** | `reg signed[15:0]` |
| `fault_detected` | **Out** | `reg` |
| `valid` | **Out** | `reg` |
| `rollback` | **Out** | `reg` |

---

### Module: `top_module`
**Parameters:** *(None)*

**Ports Table:**
| Port | Direction | Type / Width |
| :--- | :--- | :--- |
| `clk` | **In** | `logic` |
| `rst_n` | **In** | `logic` |
| `irq` | **Out** | `logic` |

---
