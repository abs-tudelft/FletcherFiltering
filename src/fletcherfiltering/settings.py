import pyarrow as pa

DEBUG = False

MINIMAL_QUERY_LENGTH = len('SELECT *')

VAR_LENGTH_TYPES = [pa.string()]
VAR_LENGTH = 32
PORT_TYPE = 'axis' # axis would be proper, but it has weird reserved named resulting in TID suffixes. And has longer latency.
BLOCK_LEVEL_IO_TYPE = 'ap_ctrl_hs' # ap_ctrl_chained if backpressure is required.
PASS_VAR_NAME = '__pass_record'
LENGTH_SUFFIX = '_len'
TEST_SUFFIX = '_test'
DATA_SUFFIX = '_data'
TESTBENCH_SUFFIX = '_tb'
OUTPUT_SUFFIX = '_o'
INPUT_NAME = 'in'
OUTPUT_NAME = 'out'
INPORT_PREFIX = 'i_'
OUTPORT_PREFIX = 'o_'
LENGTH_TYPE = pa.int32()
PART_NAME = 'xc7z020clg400-1' # 'xa7a12tcsg325-1q' 40/40/16k/8k