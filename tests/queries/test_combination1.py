from tests.helpers.base_query import BaseQuery
import pyarrow as pa
from pathlib import Path


class Combination1(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base=Path('/tmp'), **kwargs):
        super().__init__(printer, cnx, working_dir_base, name=self.__class__.__name__, has_data_file=False,
                         separate_work_dir=True, **kwargs)
        self.in_schema = pa.schema([('pkid', pa.int32(), False),
                                    ('int1', pa.int32(), False),
                                    ('int2', pa.int32(), False),
                                    ('string1', pa.string(), False),
                                    ('timestamp1', pa.timestamp('s'), False),
                                    ('timestamp2', pa.timestamp('us'), False),
                                    ('timestamp3', pa.timestamp('ms'), False),
                                    ('timestamp4', pa.timestamp('ns'), False)
                                    ])

        self.in_schema_pk = 'pkid'

        self.out_schema = pa.schema([('int1', pa.int32(), False),
                                     ('concat', pa.string(), False),
                                     ('concat2', pa.string(), False),
                                     ('timestamp1', pa.timestamp('s'), False),
                                     ('timestamp2', pa.timestamp('us'), False),
                                     ('timestamp3', pa.timestamp('ms'), False),
                                     ('timestamp4', pa.timestamp('ns'), False)
                                     ])

        self.query = """select 
            `int1`+`int2` as `int1`,
            CONCAT(string1,1<<4,'NULL') as concat,
            CONCAT('123456',string1,True,False) as concat2,
            timestamp1,
            timestamp2,
            timestamp3,
            timestamp4
            FROM `{0}`
            WHERE `int1` > 4 AND `int2` < 18""".format(
            self.name)
