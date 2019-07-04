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

from pathlib import Path

from version_query import predict_version_str

__version__ = predict_version_str()

DEBUG = False

MINIMAL_QUERY_LENGTH = len('SELECT *')

OVERWRITE_DATA = True

VAR_LENGTH_TYPES = [pa.string()]
VAR_LENGTH = 32
PORT_TYPE = 'ap_fifo' # axis would be proper, but it has weird reserved named resulting in TID suffixes. And has longer latency.
BLOCK_LEVEL_IO_TYPE = 'ap_ctrl_hs' # ap_ctrl_chained if backpressure is required.
META_PORT_TYPE = 'register'
PASS_VAR_NAME = '__pass_record'
CURRENT_RECORD_VAR_NAME = 'current_record'
LENGTH_SUFFIX = '_len'
TEST_SUFFIX = '_test'
VALID_SUFFIX = '_valid'
DATA_SUFFIX = '_data'
TESTBENCH_SUFFIX = '_tb'
OUTPUT_SUFFIX = '_o'
INPUT_NAME = 'in'
OUTPUT_NAME = 'out'
META_NAME = 'meta'
INPORT_PREFIX = 'i_'
OUTPORT_PREFIX = 'o_'
STRING_BASE_TYPE = 'f_uint8' #in code
STRING_BASE_TYPE_TEST = 'char' #in test bench
LENGTH_TYPE = pa.int32()
VALID_TYPE = pa.bool_()
PART_NAME = 'xcu200-fsgd2104-2-e' # 'xa7a12tcsg325-1q' 40/40/16k/8k or alveo: xcu200-fsgd2104-2-e or zynq 700: xc7z020clg400-1
FLETCHER_DIR = Path('Z:/Documents/GitHub/fletcher')
FLETCHER_HLS_DIR = Path('integrations/vivado_hls/src')