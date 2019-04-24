from tests.helpers.xsim_output_reader import XSIMOutputReader
import pyarrow as pa

if __name__ == '__main__':
    in_schema = pa.schema([('id', pa.int32(), False),
                                ('string1', pa.string(), False),
                                ('half1', pa.float16(), False),
                                ('float1', pa.float32(), False),
                                ('double1', pa.float64(), False)])

    in_schema_pk = 'id'

    out_schema = pa.schema([('concat', pa.string(), False),
                                 ('concat2', pa.string(), False)])

    xor = XSIMOutputReader(in_schema, out_schema)

    data = xor.read('fletcherfiltering_test_workspace/Combination2/Combination2/automated_tests/sim/tv','Combination2')
    #print("Transactions: ", num)
    print(data)
