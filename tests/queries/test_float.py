from tests.helpers.base_query import BaseQuery
import pyarrow as pa
from pathlib import Path


class Float(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base=Path('/tmp'), **kwargs):
        super().__init__(printer, cnx, working_dir_base, name=self.__class__.__name__, has_data_file=False, separate_work_dir=True, **kwargs)
        self.in_schema = pa.schema([('pkid', pa.int32(), False),
                                    ('half1', pa.float16(), False),
                                    ('float1', pa.float32(), False),
                                    ('double1', pa.float64(), False)])

        metadata_in = {b'fletcher_mode': b'read',
                    b'fletcher_name': b'in'}

        # Add the metadata to the schema
        self.in_schema = self.in_schema.add_metadata(metadata_in)

        self.in_schema_pk = 'pkid'

        self.out_schema = pa.schema([('pkid', pa.int32(), False),
                                     ('half1', pa.float16(), False),
                                     ('float1', pa.float32(), False),
                                     ('double1', pa.float64(), False),
                                     ('half1x2', pa.float16(), False),
                                     ('float1x2', pa.float32(), False),
                                     ('double1x2', pa.float64(), False)])

        metadata_out = {b'fletcher_mode': b'write',
                        b'fletcher_name': b'out'}

        # Add the metadata to the schema
        self.out_schema = self.out_schema.add_metadata(metadata_out)

        self.query = """select *, `half1` * 2 as half1x2, `float1` * 2 as float1x2, `double1` * 2 as double1x2 FROM `{0}`""".format(self.name)
