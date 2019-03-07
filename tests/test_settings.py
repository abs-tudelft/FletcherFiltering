import platform
import os.path

DEFAULT_DATA_SIZE = 1000
WORKSPACE_NAME = 'fletcherfiltering_test_workspace'
BUILD_CONFIG = 'Release'
if platform.system() == "Windows":
    CMAKE_GENERATOR = 'Visual Studio 15 2017 Win64'
    VIVADO_DIR = 'C:/Xilinx/Vivado/2018.3'
    VIVADO_BIN_DIR = os.path.join(VIVADO_DIR, 'bin')
    HLS_INCLUDE_PATH = os.path.join(VIVADO_DIR, 'include')
    HLS_LINK_PATH = os.path.join(VIVADO_DIR, 'win64/tools/fpo_v7_0')
    HLS_LIBS = 'libgmp libmpfr libIp_floating_point_v7_0_bitacc_cmodel'
elif platform.system() == "Darwin":
    CMAKE_GENERATOR = 'Ninja'
    VIVADO_DIR = '/Users/erwin/Xilinx/Vivado/2018.3'
    VIVADO_BIN_DIR = ''
    HLS_INCLUDE_PATH = os.path.join(VIVADO_DIR, 'include')
    HLS_LINK_PATH = ''
    HLS_LIBS = ''
else:
    CMAKE_GENERATOR = 'Ninja'
    VIVADO_DIR = '/opt/Xilinx/Vivado/2018.3'
    VIVADO_BIN_DIR = os.path.join(VIVADO_DIR, 'bin')
    HLS_INCLUDE_PATH = os.path.join(VIVADO_DIR, 'include')
    HLS_LINK_PATH = os.path.join(VIVADO_DIR, 'linux64/tools/fpo_v7_0')
    HLS_LIBS = 'gmp mpfr Ip_floating_point_v7_0_bitacc_cmodel'
