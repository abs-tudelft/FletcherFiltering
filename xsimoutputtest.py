from tests.helpers.xsim_output_reader import XSIMOutputReader
from tests.queries.test_nullable import Nullable
from tests.queries.test_combination1 import Combination1
import pyarrow as pa
from pathlib import Path


def run_test(q):
    print("Running for {}...".format(q.__class__.__name__))
    xor = XSIMOutputReader(q.in_schema, q.out_schema)

    data = xor.read(Path('fletcherfiltering_test_workspace/{0}/{0}/automated_tests/sim/tv'.format(q.__class__.__name__)),
                    q.__class__.__name__)
    # print("Transactions: ", num)
    print(data)

if __name__ == '__main__':
    #run_test(Combination1(None, None))
    run_test(Nullable(None, None))

