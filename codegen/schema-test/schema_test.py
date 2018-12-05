import numpy as np

import pandas as pd

import pyarrow as pa

import pyarrow.parquet as parquet
 

  
if __name__ == "__main__":
    my_schema = pa.schema([('id', pa.int32(), False),
                           ('int1', pa.int32(), False),
                           ('int2', pa.int32()),
                           ('string1', pa.string()),
                           ('timestamp1',pa.timestamp('ms'), False)])

    with open("schema.fbs",'wb') as file:
        s_serialized = my_schema.serialize()
        file.write(s_serialized)

    schema = pa.read_schema("schema.fbs")

    for col in schema:
        print(col)

    
