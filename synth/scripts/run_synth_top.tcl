# ==============================================================================
# Vivado Batch Synthesis Script for Entire SoC: top_module
# Run using: vivado -mode batch -source run_synth_top.tcl
# ==============================================================================

# 1. Project Configuration
set part "xc7z020clg400-1"
set top_module "top_module"
set proj_dir [file normalize [file dirname [info script]]/../..]

puts "========================================================"
puts "  STARTING SYNTHESIS FOR SOC TOP: $top_module"
puts "  TARGET FPGA PART: $part"
puts "  PROJECT ROOT: $proj_dir"
puts "========================================================"

# 2. Read RTL Sources
puts ">>> Reading RTL Sources..."
read_verilog -sv [glob "$proj_dir/rtl/cpu/*.sv"]
read_verilog     "$proj_dir/rtl/mac/secure_mac.v"
read_verilog     "$proj_dir/rtl/top/top_module.v"

# 3. Read Timing & Physical Constraints
puts ">>> Reading Constraints..."
read_xdc "$proj_dir/synth/constraints/top_module.xdc"

# 4. Synthesis
puts ">>> Running Synthesis..."
synth_design -top $top_module -part $part -mode out_of_context
write_checkpoint -force "$proj_dir/synth/checkpoints/post_synth.dcp"

# 5. Implementation (Place & Route)
puts ">>> Running Implementation..."
opt_design
place_design
route_design
write_checkpoint -force "$proj_dir/synth/checkpoints/post_route.dcp"

# 6. Generate PPA Reports
puts ">>> Generating PPA Reports..."
file mkdir "$proj_dir/synth/fpga_reports"
report_utilization     -file "$proj_dir/synth/fpga_reports/top_module_utilization.txt"
report_timing_summary -file "$proj_dir/synth/fpga_reports/top_module_timing.txt"
report_power          -file "$proj_dir/synth/fpga_reports/top_module_power.txt"
report_clocks         -file "$proj_dir/synth/fpga_reports/top_module_clockInfo.txt"

puts "========================================================"
puts "  BUILD COMPLETE FOR top_module!"
puts "  Reports saved in: $proj_dir/synth/fpga_reports/"
puts "========================================================"
