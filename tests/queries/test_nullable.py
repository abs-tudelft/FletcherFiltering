from tests.helpers.base_query import BaseQuery
import pyarrow as pa
from pathlib import Path


class Nullable(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base=Path('/tmp'), **kwargs):
        super().__init__(printer, cnx, working_dir_base, name=self.__class__.__name__, has_data_file=False, separate_work_dir=True, **kwargs)
        self.in_schema = pa.schema([('pkid', pa.int32(), False),
                                    ('nullint', pa.int32(), True),
                                    ('string1', pa.string(), True)])

        self.in_schema_pk = 'pkid'

        self.out_schema = pa.schema([('pkid', pa.int32(), False),
                                    ('nullint', pa.int32(), True),
                                    ('string1', pa.string(), True),
                                    ('pkid2', pa.int32(), False),
                                    ('nullint2', pa.int32(), True),
                                    ('concat', pa.string(), True)])

        self.query = """select pkid, nullint, string1, pkid+pkid as pkid2, nullint*2 as nullint2, concat(435,string1,123) as concat FROM `{0}`""".format(self.name)

