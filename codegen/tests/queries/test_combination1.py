from tests.helpers.base_query import BaseQuery
import pyarrow as pa


class QueryCombination1(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base='/tmp'):
        super().__init__(printer, cnx, working_dir_base, self.__class__.__name__, False)
        self.in_schema = pa.schema([('id', pa.int32(), False),
                                    ('int1', pa.int32(), False),
                                    ('int2', pa.int32(), False),
                                    ('string1', pa.string(), False),
                                    ('timestamp1', pa.timestamp('ms'), False)])

        self.in_schema_pk = 'id'

        self.out_schema = pa.schema([('int1', pa.int32(), False),
                                     ('concat', pa.string(), False),
                                     ('concat2', pa.string(), False)])

        self.query = """select `int1`+`int2` as `int1`, CONCAT(string1,1<<4,'NULL') as concat, CONCAT('123456',string1,True,False) as concat2 FROM `{0}` WHERE `int1` > 4 AND `int2` < 18""".format(
            self.name)

