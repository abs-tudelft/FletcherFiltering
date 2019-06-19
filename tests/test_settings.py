import platform
from pathlib import Path

DEFAULT_DATA_SIZE = 1000
WORKSPACE_NAME = 'fletcherfiltering_test_workspace'
BUILD_CONFIG = 'Release'
CLEAN_WORKDIR = False
SWALLOW_OUTPUT = False

REL_TOL_FLOAT16 = 1e-2 # digits for half float: 3.31
REL_TOL_FLOAT32 = 1e-5 # digits for single float: 7.22
REL_TOL_FLOAT64 = 1e-9 # digits for double float: 15.95

FLOAT16_MAX = 65504.0
FLOAT16_MIN = 0.000061035

NULLPROBABILITY = 0.10

MYSQL_USER='fletcherfiltering'
MYSQL_PASSWORD='pfUcFN4S9Qq7X6NDBMHk'
MYSQL_HOST='127.0.0.1'
MYSQL_DATABASE='fletcherfiltering'

if platform.system() == "Windows":
    TEST_PARTS = ['sql', 'vivado']
    CMAKE_GENERATOR = 'Visual Studio 15 2017 Win64'
    VIVADO_DIR = Path('C:/Xilinx/Vivado/2018.3')
    VIVADO_BIN_DIR = VIVADO_DIR / 'bin'
    VIVADO_HLS_EXEC = VIVADO_BIN_DIR / 'vivado_hls.bat'
    HLS_INCLUDE_PATH = [VIVADO_DIR / 'include']
    HLS_LINK_PATH = [VIVADO_DIR / Path('win64/tools/fpo_v7_0')]
    HLS_LIBS = ['libgmp', 'libmpfr', 'libIp_floating_point_v7_0_bitacc_cmodel']
elif platform.system() == "Darwin":
    TEST_PARTS = ['sql']
    CMAKE_GENERATOR = 'Ninja'
    VIVADO_DIR = Path('/Users/erwin/Xilinx/Vivado/2018.3')
    VIVADO_BIN_DIR = VIVADO_DIR / 'bin'
    VIVADO_HLS_EXEC = VIVADO_BIN_DIR / 'vivado_hls.bat'
    HLS_INCLUDE_PATH = [VIVADO_DIR / 'include']
    HLS_LINK_PATH = []
    HLS_LIBS = ''
else:
    TEST_PARTS = ['sql', 'fletcherfiltering', 'vivado']
    CMAKE_GENERATOR = 'Ninja'
    VIVADO_DIR = Path('/opt/Xilinx/Vivado/2018.3')
    VIVADO_BIN_DIR = VIVADO_DIR / 'bin'
    VIVADO_HLS_EXEC = VIVADO_BIN_DIR / 'vivado_hls.bat'
    HLS_INCLUDE_PATH = [VIVADO_DIR / 'include']
    HLS_LINK_PATH = [VIVADO_DIR / Path('linux64/tools/fpo_v7_0')]
    HLS_LIBS = 'gmp', 'mpfr', 'Ip_floating_point_v7_0_bitacc_cmodel'
