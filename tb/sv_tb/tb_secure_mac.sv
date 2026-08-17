`timescale 1ns/1ps

module tb_secure_mac();

    // ==========================================
    // 1. Khai báo tham số và tín hiệu
    // ==========================================
    parameter IN_WIDTH = 8;
    parameter OUT_WIDTH = 32;

    reg clk;
    reg rst_n;
    reg signed [IN_WIDTH-1:0] a, b;
    reg signed [OUT_WIDTH-1:0] c;
    reg start;
    
    wire signed [OUT_WIDTH-1:0] out;
    wire fault_detected;
    wire valid;
    wire rollback; // Tín hiệu báo hiệu hệ thống đang tự phục hồi

    integer fd; // File Descriptor để ghi log

    // Tạo xung nhịp 100MHz (Chu kỳ 10ns)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // ==========================================
    // 2. Khởi tạo khối Design Under Test (DUT)
    // ==========================================
    secure_mac #(
        .IN_WIDTH(IN_WIDTH),
        .OUT_WIDTH(OUT_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .a(a),
        .b(b),
        .c(c),
        .start(start),
        .out(out),
        .fault_detected(fault_detected),
        .valid(valid),
        .rollback(rollback)
    );

    // ==========================================
    // 3. Thiết lập xuất file VCD cho GTKWave và File txt
    // ==========================================
    initial begin
        $dumpfile("tb_secure_mac.vcd"); 
        $dumpvars(0, tb_secure_mac);    
        
        // Mở file txt để ghi đè log mô phỏng (Vivado sẽ lưu ở thư mục sim)
        // Dùng toán tử OR bitwise (| 1) để ghi ra cả màn hình Console (fd 1) lẫn file txt
        fd = $fopen("sim_output_vivado.txt") | 1;
    end

    // ==========================================
    // 4. Các kịch bản kiểm tra (Scenarios)
    // ==========================================
    reg signed [OUT_WIDTH-1:0] expected_out;
    reg signed [OUT_WIDTH-1:0] last_valid_out; 

    task drive_inputs(input reg signed [IN_WIDTH-1:0] in_a, input reg signed [IN_WIDTH-1:0] in_b, input reg signed [OUT_WIDTH-1:0] in_c);
        begin
            @(negedge clk);
            a = in_a;
            b = in_b;
            c = in_c;
            start = 1;
            expected_out = in_a * in_b + in_c; 
            
            @(negedge clk);
            start = 0;
        end
    endtask

    initial begin
        // Khởi tạo
        rst_n = 0;
        a = 0; b = 0; c = 0; start = 0;
        last_valid_out = 0;
        #20 rst_n = 1;
        #10;

        $fdisplay(fd, "==================================================================");
        $fdisplay(fd, "   BAT DAU MO PHONG SECURE_MAC (CO TICH HOP STATE ROLLBACK)");
        $fdisplay(fd, "==================================================================");

        // ----------------------------------------------------------------
        // KỊCH BẢN 1: NORMAL OPERATION
        // ----------------------------------------------------------------
        $fdisplay(fd, "\n[SCENARIO 1] Normal Operation (Khong co tan cong)");
        
        drive_inputs(8'd10, 8'd5, 32'd100); // Kỳ vọng: 150
        @(posedge valid); 
        #1; 
        if (out === expected_out && fault_detected === 1'b0) begin
            $fdisplay(fd, "  -> PASS: out = %0d (Dung voi ky vong: %0d)", out, expected_out);
            last_valid_out = out; 
        end else begin
            $fdisplay(fd, "  -> FAIL: out = %0d (Ky vong: %0d)", out, expected_out);
        end
        @(negedge clk);

        // ----------------------------------------------------------------
        // KỊCH BẢN 2 & 3: FAULT INJECTION & KIỂM TRA ROLLBACK
        // ----------------------------------------------------------------
        $fdisplay(fd, "\n[SCENARIO 2 & 3] Fault Injection & Kiem tra State Rollback");
        
        drive_inputs(8'd20, 8'd3, 32'd200); // Kỳ vọng: 260
        
        // --- BẮT ĐẦU CHÍCH LỖI ---
        force dut.mac_result[0] = ~dut.mac_result[0];
        $fdisplay(fd, "  -> [!] DANG TIEM LOI: Dao bit thu 0 cua bo nhan/cong (mac_result)");

        @(posedge valid);
        #1;
        
        if (fault_detected === 1'b1 && rollback === 1'b1) begin
            $fdisplay(fd, "  -> PASS: He thong da phat hien tan cong! fault_detected = 1, rollback = 1");
            if (out === last_valid_out) begin
                $fdisplay(fd, "  -> PASS: STATE ROLLBACK THANH CONG! Ngõ ra 'out' da duoc khoi phuc ve %0d (gia tri hop le gan nhat)", out);
            end else begin
                $fdisplay(fd, "  -> FAIL: STATE ROLLBACK THAT BAI! Ngõ ra 'out' = %0d (Le ra phai la %0d)", out, last_valid_out);
            end
        end else begin
            $fdisplay(fd, "  -> FAIL: He thong KHONG phat hien duoc tan cong hoac rollback khong bat!");
        end
        
        release dut.mac_result;
        @(negedge clk);
        
        $fdisplay(fd, "\n==================================================================");
        $fdisplay(fd, "   KET THUC MO PHONG");
        $fdisplay(fd, "==================================================================");
        
        $fclose(fd); // Đóng file để ghi toàn bộ xuống ổ cứng
        $finish;
    end

endmodule