`timescale 1ns/1ps
// Secure_MAC – Khối MAC 8-bit × 8-bit + 32-bit có khả năng kháng tấn công tiêm lỗi
// Kiến trúc: Luồng dữ liệu cơ sở + Mã thặng dư số học (Modulo 3)
module secure_mac #(
    parameter IN_WIDTH = 8,
    parameter OUT_WIDTH = 32
)(
    input  wire                 clk,
    input  wire                 rst_n,
    input  wire signed [IN_WIDTH-1:0]  a,
    input  wire signed [IN_WIDTH-1:0]  b,
    input  wire signed [OUT_WIDTH-1:0] c,
    input  wire                 start,
    output reg signed  [OUT_WIDTH-1:0] out,
    output reg                  fault_detected,
    output reg                  valid,
    output reg                  rollback
);

    // Luồng dữ liệu chính (8x8 -> 16, + 32 -> 32)

    reg signed [IN_WIDTH-1:0]  reg_a, reg_b;
    reg signed [OUT_WIDTH-1:0] reg_c;
    reg valid_d1;

    wire signed [2*IN_WIDTH-1:0] product;
    wire signed [OUT_WIDTH-1:0]  mac_result;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_a <= 0;
            reg_b <= 0;
            reg_c <= 0;
            valid_d1 <= 0;
        end else begin
            valid_d1 <= start;
            if (start) begin
                reg_a <= a;
                reg_b <= b;
                reg_c <= c;
            end
        end
    end

    // TẦNG PIPELINE 1.5: Khối tổ hợp 1
    
    assign product = reg_a * reg_b;

    wire [1:0] a_mod3;
    wire [1:0] b_mod3;
    wire [1:0] c_mod3;

    wire [31:0] reg_c_32 = reg_c;
    mod3_encoder_8b  u_enc_a (.in(reg_a), .out(a_mod3));
    mod3_encoder_8b  u_enc_b (.in(reg_b), .out(b_mod3));
    mod3_encoder_32b u_enc_c (.in(reg_c_32), .out(c_mod3));

    wire [3:0] ab_mod3_product = a_mod3 * b_mod3;

    // TẦNG PIPELINE 2: Các thanh ghi trung gian
  
    reg signed [2*IN_WIDTH-1:0] pipe_product;
    reg signed [OUT_WIDTH-1:0]  pipe_c;
    reg [3:0]                   pipe_ab_mod3;
    reg [1:0]                   pipe_c_mod3;
    reg                         valid_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipe_product <= 0;
            pipe_c       <= 0;
            pipe_ab_mod3 <= 0;
            pipe_c_mod3  <= 0;
            valid_d2     <= 0;
        end else begin
            valid_d2 <= valid_d1;
            if (valid_d1) begin
                pipe_product <= product;
                pipe_c       <= reg_c;
                pipe_ab_mod3 <= ab_mod3_product;
                pipe_c_mod3  <= c_mod3;
            end
        end
    end

 
    // TẦNG PIPELINE 2.5: Khối tổ hợp 2
    
    assign mac_result = pipe_product + pipe_c;

    wire [1:0] out_mod3;       
    wire [1:0] expected_mod3;  

    wire [31:0] mac_result_32 = mac_result;
    mod3_encoder_32b u_enc_out (.in(mac_result_32), .out(out_mod3));

    wire [3:0] rns_calc = pipe_ab_mod3 + pipe_c_mod3;
    reg  [1:0] expected_mod3_reg;

    always @(*) begin
        case (rns_calc)
            4'd0, 4'd3, 4'd6, 4'd9: expected_mod3_reg = 2'd0;
            4'd1, 4'd4, 4'd7:       expected_mod3_reg = 2'd1;
            4'd2, 4'd5, 4'd8:       expected_mod3_reg = 2'd2;
            default:                expected_mod3_reg = 2'd0; 
        endcase
    end
    assign expected_mod3 = expected_mod3_reg;

    wire disagreement = (expected_mod3 != out_mod3);

    
    // TẦNG PIPELINE 3: Thanh ghi ngõ ra, Cờ lỗi & Khôi phục trạng thái
   
    reg signed [OUT_WIDTH-1:0] shadow_accumulator;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out                <= 0;
            shadow_accumulator <= 0;
            fault_detected     <= 0;
            rollback           <= 0;
            valid              <= 0;
        end else begin
            valid <= valid_d2;
            if (valid_d2) begin
                if (disagreement) begin
                    // Lỗi được phát hiện -> Kích hoạt Rollback
                    out            <= shadow_accumulator; // Khôi phục giá trị cũ hợp lệ
                    fault_detected <= 1'b1;
                    rollback       <= 1'b1;
                end else begin
                    // Hoạt động bình thường -> Cập nhật out và shadow
                    out                <= mac_result;
                    shadow_accumulator <= mac_result;     // Lưu lại kết quả hợp lệ
                    fault_detected     <= 1'b0;
                    rollback           <= 1'b0;
                end
            end else begin
                fault_detected <= 0;
                rollback       <= 0;
            end
        end
    end

endmodule


// Module hỗ trợ: Bộ mã hóa Modulo 3 cho số 8-bit có dấu

module mod3_encoder_8b (
    input  wire [7:0] in,
    output reg  [1:0] out
);
    wire [3:0] sum_w1 = in[0] + in[2] + in[4] + in[6] + in[7]; // Các bit có trọng số 1 (MSB có trọng số là 1)
    wire [2:0] sum_w2 = in[1] + in[3] + in[5];                 // Các bit có trọng số 2
    
    wire [4:0] total_sum = sum_w1 + (sum_w2 << 1);             // Tối đa 5 + 6 = 11

    always @(*) begin
        case (total_sum)
            5'd0, 5'd3, 5'd6, 5'd9:  out = 2'd0;
            5'd1, 5'd4, 5'd7, 5'd10: out = 2'd1;
            5'd2, 5'd5, 5'd8, 5'd11: out = 2'd2;
            default:                 out = 2'd0;
        endcase
    end
endmodule


// Module hỗ trợ: Bộ mã hóa Modulo 3 cho số 32-bit có dấu

module mod3_encoder_32b (
    input  wire [31:0] in,
    output reg  [1:0]  out
);
    wire [4:0] sum_w1 = in[0] + in[2] + in[4] + in[6] + in[8] + in[10] + 
                        in[12] + in[14] + in[16] + in[18] + in[20] + in[22] + 
                        in[24] + in[26] + in[28] + in[30] + in[31]; // Tối đa 17 bit -> 17
                        
    wire [3:0] sum_w2 = in[1] + in[3] + in[5] + in[7] + in[9] + in[11] + 
                        in[13] + in[15] + in[17] + in[19] + in[21] + in[23] + 
                        in[25] + in[27] + in[29]; // Tối đa 15 bit -> 15

    wire [5:0] total_sum = sum_w1 + (sum_w2 << 1); // Tối đa 17 + 30 = 47

    // Rút gọn tầng thứ 2 để tránh dùng khối case quá lớn
    wire [2:0] red2_w1 = total_sum[0] + total_sum[2] + total_sum[4]; // Tối đa 3
    wire [1:0] red2_w2 = total_sum[1] + total_sum[3] + total_sum[5]; // Tối đa 3
    wire [3:0] total_sum2 = red2_w1 + (red2_w2 << 1); // Tối đa 3 + 6 = 9

    always @(*) begin
        case (total_sum2)
            4'd0, 4'd3, 4'd6, 4'd9: out = 2'd0;
            4'd1, 4'd4, 4'd7:       out = 2'd1;
            4'd2, 4'd5, 4'd8:       out = 2'd2;
            default:                out = 2'd0;
        endcase
    end
endmodule