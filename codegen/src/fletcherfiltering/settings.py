import pyarrow as pa

DEBUG = False

MINIMAL_QUERY_LENGTH = len('SELECT *')

VAR_LENGTH_TYPES = [pa.string()]
VAR_LENGTH = 255
PASS_VAR_NAME = '__pass_record'
LENGTH_SUFFIX = '_len'
TEST_SUFFIX = '_test'
OUTPUT_SUFFIX = '_o'
LENGTH_TYPE = pa.int32()