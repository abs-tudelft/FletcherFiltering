#  Copyright (c) 2019 Erwin de Haan. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This file is part of the FletcherFiltering project

import pyarrow as pa
import os
import platform
from pathlib import Path
from version_query import predict_version_str

__version__ = predict_version_str()

DEBUG = False

MINIMAL_QUERY_LENGTH = len('SELECT *')

OVERWRITE_DATA = True

VAR_LENGTH_TYPES = [pa.string()]
VAR_LENGTH = 255
PORT_TYPE = 'ap_fifo'  # axis would be proper, but it has weird reserved named resulting in TID suffixes. And has longer latency.
BLOCK_LEVEL_IO_TYPE = 'ap_ctrl_hs'  # ap_ctrl_chained if backpressure is required.
META_PORT_TYPE = 'register'
PASS_VAR_NAME = '__pass_record'
CURRENT_RECORD_VAR_NAME = 'current_record'
LENGTH_SUFFIX = '_len'
TEST_SUFFIX = '_test'
VALID_SUFFIX = '_valid'
DATA_SUFFIX = '_data'
TESTBENCH_SUFFIX = '_tb'
OUTPUT_SUFFIX = '_o'
INPUT_NAME = 'ff_in'
OUTPUT_NAME = 'ff_out'
META_NAME = 'meta'
INPORT_PREFIX = 'i_'
OUTPORT_PREFIX = 'o_'
STRING_BASE_TYPE = 'f_uint8'  # in code
STRING_BASE_TYPE_TEST = 'char'  # in test bench
LENGTH_TYPE = pa.int32()
VALID_TYPE = pa.bool_()
PART_NAME = 'xcku060-ffva1156-2-e'  # 'xa7a12tcsg325-1q' 40/40/16k/8k or alveo: xcu200-fsgd2104-2-e or zynq 700: xc7z020clg400-1 or nimbix: xcku060-ffva1156-2-e

if 'FLETCHER_DIR' in os.environ:
    FLETCHER_DIR = Path(os.environ['FLETCHER_DIR'])
else:
    FLETCHER_DIR = Path('Z:/Documents/GitHub/fletcher')

FLETCHER_HLS_DIR = Path('integrations/vivado_hls/src')

# Test settings
DEFAULT_DATA_SIZE = 2500

WORKSPACE_NAME = 'fletcherfiltering_test_workspace'
BUILD_CONFIG = 'Release'
CLEAN_WORKDIR = True
SWALLOW_OUTPUT = False

REL_TOL_FLOAT16 = 1e-2  # digits for half float: 3.31
REL_TOL_FLOAT32 = 1e-5  # digits for single float: 7.22
REL_TOL_FLOAT64 = 1e-9  # digits for double float: 15.95

FLOAT16_MAX = 65504.0
FLOAT16_MIN = 0.000061035

NULLPROBABILITY = 0.10
EMPTYSTRINGPROBABILITY = 0.01

MYSQL_USER = 'fletcherfiltering'
MYSQL_PASSWORD = 'pfUcFN4S9Qq7X6NDBMHk'
MYSQL_HOST = '127.0.0.1'
MYSQL_DATABASE = 'fletcherfiltering'

TEST_PARTS = []
CMAKE_GENERATOR = 'Ninja'
VIVADO_DIR = Path('/opt/Xilinx/Vivado/2018.1')
VIVADO_BIN_DIR = VIVADO_DIR / 'bin'
VIVADO_EXEC = 'vivado'
VIVADO_HLS_EXEC = 'vivado_hls'
HLS_INCLUDE_PATH = [VIVADO_DIR / 'include']  # For build C++ code outside of Vivado HLS
HLS_LINK_PATH = [VIVADO_DIR / Path('linux64/tools/fpo_v7_0')]
HLS_LIBS = ['gmp', 'mpfr', 'Ip_floating_point_v7_0_bitacc_cmodel']

if platform.system() == "Windows":
    TEST_PARTS = ['sql', 'vivado']
    MYSQL_HOST = '10.211.55.2'
    # CMAKE_GENERATOR = 'Visual Studio 15 2017 Win64'
    VIVADO_DIR = Path('C:/Xilinx/Vivado/2019.1')
    VIVADO_BIN_DIR = VIVADO_DIR / 'bin'
    VIVADO_EXEC = VIVADO_BIN_DIR / 'vivado.bat'
    VIVADO_HLS_EXEC = VIVADO_BIN_DIR / 'vivado_hls.bat'
    HLS_INCLUDE_PATH = [VIVADO_DIR / 'include']
    HLS_LINK_PATH = [VIVADO_DIR / Path('win64/tools/fpo_v7_0')]
    HLS_LIBS = ['libgmp', 'libmpfr', 'libIp_floating_point_v7_0_bitacc_cmodel']
elif platform.system() == "Darwin":
    TEST_PARTS = []
    # CMAKE_GENERATOR = 'Ninja'
    VIVADO_DIR = Path('/Users/erwin/Xilinx/Vivado/2019.1')
    VIVADO_BIN_DIR = VIVADO_DIR / 'bin'
    # VIVADO_HLS_EXEC = VIVADO_BIN_DIR / 'vivado_hls'
    HLS_INCLUDE_PATH = [VIVADO_DIR / 'include']
    HLS_LINK_PATH = []
    HLS_LIBS = ''
