# ==============================================================================
# Vivado TCL Script for Synthesizing secure_mac.v
# Run using: vivado -mode batch -source run_synth.tcl
# ==============================================================================

# 1. Configuration
# Target a popular Edge AI FPGA (Zynq-7000 series, e.g., PYNQ-Z2 board)
set part "xc7z020clg400-1"
set top_module "secure_mac"

puts "========================================================"
puts "  STARTING SYNTHESIS FOR: $top_module"
puts "  TARGET PART: $part"
puts "========================================================"

# 2. Read Source Files
read_verilog secure_mac.v

# 3. Constraints (Clock definition for Timing and Power analysis)
# Define a 200 MHz clock (5.0 ns period) to challenge the critical path
create_clock -name clk -period 5.0 [get_ports clk]

# 4. Synthesis
puts ">>> Running Synthesis..."
synth_design -top $top_module -part $part -mode out_of_context
write_checkpoint -force post_synth.dcp

# 5. Implementation (Place & Route for accurate Area and Power estimates)
puts ">>> Running Implementation..."
opt_design
place_design
route_design
write_checkpoint -force post_route.dcp

# 6. Generate PPA Reports
puts ">>> Generating Reports..."
report_utilization -file report_utilization.txt
report_timing_summary -file report_timing.txt
report_power -file report_power.txt

puts "========================================================"
puts "  BUILD COMPLETE!"
puts "  Check report_utilization.txt, report_timing.txt, and report_power.txt"
puts "========================================================"
