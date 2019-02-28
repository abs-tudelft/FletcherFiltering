from tests.helpers.base_query import BaseQuery
import pyarrow as pa


class QueryFloat(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base='/tmp'):
        super().__init__(printer, cnx, working_dir_base, self.__class__.__name__, False)
        self.in_schema = pa.schema([('id', pa.int32(), False),
                                    ('half1', pa.float16(), False),
                                    ('float1', pa.float32(), False),
                                    ('double1', pa.float64(), False)])

        self.in_schema_pk = 'id'

        self.out_schema = pa.schema([('id', pa.int32(), False),
                                     ('half', pa.float16(), False),
                                     ('float', pa.float32(), False),
                                     ('double', pa.float64(), False),
                                     ('half1x2', pa.float16(), False),
                                     ('float1x2', pa.float32(), False),
                                     ('double1x2', pa.float64(), False)])

        self.query = """select *, `half1` * 2 as half1x2, `float1` * 2 as float1x2, `double1` * 2 as double1x2 FROM `{0}`""".format(self.name)
