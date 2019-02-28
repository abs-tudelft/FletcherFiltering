from tests.helpers.base_query import BaseQuery
import pyarrow as pa


class QueryCombination2(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base='/tmp'):
        super().__init__(printer, cnx, working_dir_base, self.__class__.__name__, False)
        self.in_schema = pa.schema([('id', pa.int32(), False),
                                    ('string1', pa.string(), False),
                                    ('half1', pa.float16(), False),
                                    ('float1', pa.float32(), False),
                                    ('double1', pa.float64(), False)])

        self.in_schema_pk = 'id'

        self.out_schema = pa.schema([('concat', pa.string(), False),
                                     ('concat2', pa.string(), False)])

        self.query = """select CONCAT(0.5,`string1`,0.3) as concat, CONCAT(3.453345,`string1`,3.12e4) as concat2 FROM `{0}` WHERE `half1` > 0 AND `float1` > 0 and `double1` > 0""".format(
            self.name)

