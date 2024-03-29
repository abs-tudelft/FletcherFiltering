#  Copyright (c) 2019 Erwin de Haan. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This file is part of the FletcherFiltering project
from fletcherfiltering.common.data_generation import generate_random_data
import pyarrow as pa
import time
import numpy as np
from pathlib import Path
from fletcherfiltering import settings
from math import ceil,floor

DATA_SIZE = 1*1000*1000*1000


#name = 'Simple'
name = 'Float'

#schema = pa.schema([('pkid', pa.int32(), False)])
schema = pa.schema([('pkid', pa.int32(), False),
                    ('half1', pa.float16(), False),
                    ('float1', pa.float32(), False),
                    ('double1', pa.float64(), False)])
schema_size = 0
schema_size_bits = 0
for col in schema:
    schema_size += ceil(col.type.bit_width/8)
    schema_size_bits += col.type.bit_width

print("One row in the schema takes {} bytes or {} bits ({} bytes).".format(schema_size, schema_size_bits, schema_size_bits/8))

SIZE_PER_RECORD = schema_size

DATA_COUNT = floor(DATA_SIZE/SIZE_PER_RECORD)

print("Generating {} rows of size {} for a total size of {} ({})".format(DATA_COUNT, SIZE_PER_RECORD, DATA_COUNT*SIZE_PER_RECORD, DATA_SIZE))

metadata_in = {b'fletcher_mode': b'read',
               b'fletcher_name': settings.INPUT_NAME.encode('ascii')}
# Add the metadata to the schema
schema = schema.add_metadata(metadata_in)

schema_pk = 'pkid'

start = time.time()

data = generate_random_data(schema, schema_pk, DATA_COUNT, columnar=True)



rb_data = []
for col in schema:
    type_func = (lambda x: x)

    if col.type == pa.float16():
        type_func = np.float16
    elif col.type == pa.float32():
        type_func = np.float32
    elif col.type == pa.float64():
        type_func = np.float64
    elif col.type == pa.int8():
        type_func = np.int8
    elif col.type == pa.uint8():
        type_func = np.uint8
    elif col.type == pa.int16():
        type_func = np.int16
    elif col.type == pa.uint16():
        type_func = np.uint16
    elif col.type == pa.int32():
        type_func = np.int32
    elif col.type == pa.uint32():
        type_func = np.uint32
    elif col.type == pa.int64():
        type_func = np.int64
    elif col.type == pa.uint64():
        type_func = np.uint64
    elif pa.types.is_timestamp(col.type):
        type_func = 'datetime64[{}]'.format(col.type.unit)

    rb_data.append(pa.array(np.asarray(data[col.name], dtype=type_func), col.type))


# Create a RecordBatch from the Arrays.
recordbatch = pa.RecordBatch.from_arrays(rb_data, schema)

# Create an Arrow RecordBatchFileWriter.
writer = pa.RecordBatchFileWriter(Path('{0}{1}.rb'.format(name, settings.DATA_SUFFIX)),
                                  schema)
# Write the RecordBatch.
writer.write(recordbatch)

writer.close()

end = time.time()

print(end - start)
