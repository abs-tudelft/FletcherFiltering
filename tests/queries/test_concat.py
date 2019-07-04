from tests.helpers.base_query import BaseQuery
import pyarrow as pa
from pathlib import Path


class Concat(BaseQuery):
    def __init__(self, printer, cnx, working_dir_base=Path('/tmp'), **kwargs):
        super().__init__(printer, cnx, working_dir_base, name=self.__class__.__name__, has_data_file=False, separate_work_dir=True, **kwargs)
        self.in_schema = pa.schema([('pkid', pa.int32(), False),
                                    ('string1', pa.string(), False),
                                    ('string2', pa.string(), False)])

        metadata_in = {b'fletcher_mode': b'read',
                    b'fletcher_name': b'in'}

        # Add the metadata to the schema
        self.in_schema = self.in_schema.add_metadata(metadata_in)

        self.in_schema_pk = 'pkid'

        self.out_schema = pa.schema([('pkid', pa.int32(), False),
                                     ('concat', pa.string(), False)])

        metadata_out = {b'fletcher_mode': b'write',
                        b'fletcher_name': b'out'}

        # Add the metadata to the schema
        self.out_schema = self.out_schema.add_metadata(metadata_out)

        self.query = """select pkid, CONCAT(string1, string2) as concat FROM `{0}`""".format(self.name)
