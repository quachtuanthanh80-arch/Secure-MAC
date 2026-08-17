# ==============================================================================
# Constraints for top_module (SoC Integration) on Xilinx Zynq-7000 (xc7z020)
# ==============================================================================

# 1. Primary Clock Definition (100 MHz, Period = 10.0 ns)
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports clk]

# 2. Asynchronous Signals False Path
# Reset (rst_n) and Interrupt Output (irq) are asynchronous to the clock domain
set_false_path -from [get_ports rst_n]
set_false_path -to   [get_ports irq]

# 3. Output Load
set_load 5.000 [get_ports irq]
