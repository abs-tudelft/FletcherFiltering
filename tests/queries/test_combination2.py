from tests.helpers.base_query import BaseQuery
import pyarrow as pa
from pathlib import Path


class Combination2(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base=Path('/tmp'), **kwargs):
        super().__init__(printer, cnx, working_dir_base, name=self.__class__.__name__, has_data_file=False, separate_work_dir=True, **kwargs)
        self.in_schema = pa.schema([('pkid', pa.int32(), False),
                                    ('string1', pa.string(), False),
                                    ('half1', pa.float16(), False),
                                    ('float1', pa.float32(), False),
                                    ('double1', pa.float64(), False)])

        metadata_in = {b'fletcher_mode': b'read',
                    b'fletcher_name': b'in'}

        # Add the metadata to the schema
        self.in_schema = self.in_schema.add_metadata(metadata_in)

        self.in_schema_pk = 'pkid'

        self.out_schema = pa.schema([('concat', pa.string(), False),
                                     ('concat2', pa.string(), False)])

        metadata_out = {b'fletcher_mode': b'write',
                        b'fletcher_name': b'out'}

        # Add the metadata to the schema
        self.out_schema = self.out_schema.add_metadata(metadata_out)

        self.query = """select CONCAT(0.5,`string1`,0.3) as concat, CONCAT(3.453345,`string1`,3.12e4) as concat2 FROM `{0}` WHERE `half1` > 0 AND `float1` > 0 and `double1` > 0""".format(
            self.name)

