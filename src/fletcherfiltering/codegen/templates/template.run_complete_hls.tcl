############################################################
## This file is generated automatically by FletcherFiltering.
############################################################
open_project ${query_name}
set_top ${query_name}
add_files ${query_name}.cpp -cflags "-std=c++11 ${hls_include_dirs}"
add_files ${query_name}.h -cflags "-std=c++11 ${hls_include_dirs}"
add_files fletcherfiltering.cpp -cflags "-std=c++11 ${hls_include_dirs}"
add_files fletcherfiltering.h -cflags "-std=c++11 ${hls_include_dirs}"
add_files -tb ${query_name}${test_suffix}.cpp -cflags "-std=c++11 ${hls_include_dirs} -Wno-unknown-pragmas"
add_files -tb ${query_name}${test_suffix}.h -cflags "-std=c++11 ${hls_include_dirs} -Wno-unknown-pragmas"
add_files -tb ${query_name}${data_suffix}.h -cflags "-std=c++11 ${hls_include_dirs} -Wno-unknown-pragmas"
add_files -tb ${query_name}${testbench_suffix}.cpp -cflags "-std=c++11 ${hls_include_dirs} -Wno-unknown-pragmas"
open_solution "automated_tests"
set_part {${part_name}}
create_clock -period 10 -name default
config_export -format ip_catalog -rtl vhdl
csim_design -O
csynth_design
cosim_design -O -trace_level all -rtl vhdl
#export_design -rtl vhdl -format ip_catalog
exit