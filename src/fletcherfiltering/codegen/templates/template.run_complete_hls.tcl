############################################################
## This file is generated automatically by FletcherFiltering.
############################################################
open_project ${query_name}
set_top ${query_name}
add_files ${query_name}.cpp
add_files ${query_name}.h
add_files fletcherfiltering.cpp
add_files fletcherfiltering.h
add_files -tb ${query_name}${test_suffix}.cpp
add_files -tb ${query_name}${test_suffix}.h
add_files -tb ${query_name}${data_suffix}.h
add_files -tb ${query_name}${testbench_suffix}.cpp
open_solution "automated_tests"
set_part {${part_name}}
create_clock -period 10 -name default
csim_design -O
csynth_design
cosim_design -trace_level all -rtl vhdl
#export_design -rtl vhdl -format ip_catalog
exit