DEFAULT_DATA_SIZE = 1000
WORKSPACE_NAME = 'fletcherfiltering_test_workspace'
BUILD_CONFIG = 'Release'
import platform
if platform.system() == "Windows":
    CMAKE_GENERATOR = 'Visual Studio 15 2017 Win64'
else:
    CMAKE_GENERATOR = 'Ninja'
if platform.system() == "Windows":
    HLS_INCLUDE_PATH = 'C:/Xilinx/Vivado/2018.3/include'
else:
    HLS_INCLUDE_PATH = '/Users/erwin/Xilinx/Vivado/2018.3/include'
