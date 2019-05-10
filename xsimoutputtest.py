from tests.helpers.xsim_output_reader import XSIMOutputReader
import pyarrow as pa
from pathlib import Path

if __name__ == '__main__':
    in_schema = pa.schema([('pkid', pa.int32(), False),
                                ('nullint', pa.int32(), True),
                                ('string1', pa.string(), True)])

    in_schema_pk = 'pkid'

    out_schema = pa.schema([('pkid', pa.int32(), False),
                                 ('nullint', pa.int32(), True),
                                 ('string1', pa.string(), True),
                                 ('pkid2', pa.int32(), False),
                                 ('nullint2', pa.int32(), True),
                                 ('concat', pa.string(), True)])

    xor = XSIMOutputReader(in_schema, out_schema)

    data = xor.read(Path('fletcherfiltering_test_workspace/Nullable/Nullable/automated_tests/sim/tv'),'Nullable')
    #print("Transactions: ", num)
    print(data)
