`timescale 1ns/1ps
module hazard_unit (
    input  logic [4:0] rs1_addr_EX,
    input  logic [4:0] rs2_addr_EX,
    input  logic [4:0] rd_addr_MEM,
    input  logic       RegWrite_MEM,
    input  logic [4:0] rd_addr_WB,
    input  logic       RegWrite_WB,
    
    input  logic       MemRead_EX,
    input  logic [4:0] rd_addr_EX,
    input  logic [4:0] rs1_addr_ID,
    input  logic [4:0] rs2_addr_ID,
    input  logic       branch_taken_ID,
    input  logic       jump_ID,
    
    output logic [1:0] forwardA_EX,
    output logic [1:0] forwardB_EX,
    
    output logic       stall_IF,
    output logic       stall_ID,
    output logic       flush_ID,
    output logic       flush_EX
);

    // Logic chuyển tiếp dữ liệu (Forwarding) cho ngõ vào ALU tại tầng EX
    // 00: Lấy từ thanh ghi (tầng ID/EX)
    // 01: Lấy từ tầng WB (Giá trị ghi lại)
    // 10: Lấy từ tầng MEM (Kết quả ALU)
    always_comb begin
        if (RegWrite_MEM && (rd_addr_MEM != 5'd0) && (rd_addr_MEM == rs1_addr_EX)) begin
            forwardA_EX = 2'b10;
        end else if (RegWrite_WB && (rd_addr_WB != 5'd0) && (rd_addr_WB == rs1_addr_EX)) begin
            forwardA_EX = 2'b01;
        end else begin
            forwardA_EX = 2'b00;
        end
        
        if (RegWrite_MEM && (rd_addr_MEM != 5'd0) && (rd_addr_MEM == rs2_addr_EX)) begin
            forwardB_EX = 2'b10;
        end else if (RegWrite_WB && (rd_addr_WB != 5'd0) && (rd_addr_WB == rs2_addr_EX)) begin
            forwardB_EX = 2'b01;
        end else begin
            forwardB_EX = 2'b00;
        end
    end

    // Phát hiện lỗi Load-Use Hazard
    // Nếu lệnh ở EX là LOAD và nó ghi vào thanh ghi mà lệnh ở ID đang cần đọc
    logic load_use_hazard;
    assign load_use_hazard = MemRead_EX && (rd_addr_EX != 5'd0) && ((rd_addr_EX == rs1_addr_ID) || (rd_addr_EX == rs2_addr_ID));

    // Logic Tạm dừng (Stall) và Xóa đường ống (Flush)
    always_comb begin
        stall_IF = 1'b0;
        stall_ID = 1'b0;
        flush_ID = 1'b0;
        flush_EX = 1'b0;

        if (load_use_hazard) begin
            // Dừng tầng IF và ID, chèn bong bóng vào tầng EX (flush)
            stall_IF = 1'b1;
            stall_ID = 1'b1;
            flush_EX = 1'b1;
        end else if (branch_taken_ID || jump_ID) begin
            // Xóa tầng ID để hủy lệnh bị nạp sai do nhảy nhánh
            flush_ID = 1'b1;
        end
    end

endmodule
