import numpy as np

import pandas as pd

import pyarrow as pa

import pyarrow.parquet as parquet
 

  
if __name__ == "__main__":
    in_schema = pa.schema([('id', pa.int32(), False),
                           ('int1', pa.int32(), False),
                           ('int2', pa.int32()),
                           ('string1', pa.string()),
                           ('timestamp1',pa.timestamp('ms'), False)])

    with open("in_schema.fbs",'wb') as file:
        s_serialized = in_schema.serialize()
        file.write(s_serialized)

    out_schema = pa.schema([('int1', pa.int32(), False),
                           ('concat', pa.string(), False),
                           ('concat2', pa.string(), False)])

    with open("out_schema.fbs", 'wb') as file:
        s_serialized = out_schema.serialize()
        file.write(s_serialized)

