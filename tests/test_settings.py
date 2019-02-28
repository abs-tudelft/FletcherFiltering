import platform

DEFAULT_DATA_SIZE = 1000
WORKSPACE_NAME = 'fletcherfiltering_test_workspace'
BUILD_CONFIG = 'Release'
if platform.system() == "Windows":
    CMAKE_GENERATOR = 'Visual Studio 15 2017 Win64'
    HLS_INCLUDE_PATH = 'C:/Xilinx/Vivado/2018.3/include'
    HLS_LINK_PATH = 'C:/Xilinx/Vivado/2018.3/win64/tools/fpo_v7_0'
    HLS_LIBS = 'libgmp libmpfr libIp_floating_point_v7_0_bitacc_cmodel'
else:
    CMAKE_GENERATOR = 'Ninja'
    HLS_INCLUDE_PATH = '/Users/erwin/Xilinx/Vivado/2018.3/include'
    HLS_LINK_PATH = ''
    HLS_LIBS = ''
