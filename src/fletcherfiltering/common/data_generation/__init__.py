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
import random

import pyarrow as pa
import pytest

from fletcherfiltering import settings
from fletcherfiltering.common.data_generation.FloatGenerator import FloatGenerator
from fletcherfiltering.common.data_generation.IntGenerator import IntGenerator
from fletcherfiltering.common.data_generation.SentenceGenerator import SentenceGenerator
from fletcherfiltering.common.data_generation.UIntGenerator import UIntGenerator


def generate_random_data_old(schema: pa.Schema, schema_pk: str, size: int = settings.DEFAULT_DATA_SIZE):
    if schema.get_field_index(schema_pk) < 0:
        raise ValueError("schema_pk must be the name of a column in the schema.")
    str_gen = SentenceGenerator()
    uint_gen = UIntGenerator()
    int_gen = IntGenerator()
    float_gen = FloatGenerator()
    data = []
    for i in range(size):
        record = {}
        for col in schema:
            if col.name == schema_pk:
                if col.type == pa.string():
                    record[col.name] = str(i)
                elif col.type == pa.int32() or col.type == pa.uint32() or col.type == pa.int64() or col.type == pa.uint64():
                    record[col.name] = i
                else:
                    pytest.fail("Unsupported PK column type {} for {}".format(col.type, col.name))
            else:
                if col.type == pa.string():
                    record[col.name] = str_gen.generate(maxlength=int(settings.VAR_LENGTH / 2))
                elif col.type == pa.int8():
                    record[col.name] = int_gen.generate(8)
                elif col.type == pa.uint8():
                    record[col.name] = uint_gen.generate(8)
                elif col.type == pa.int16():
                    record[col.name] = int_gen.generate(16)
                elif col.type == pa.uint16():
                    record[col.name] = uint_gen.generate(16)
                elif col.type == pa.int32():
                    record[col.name] = int_gen.generate(32)
                elif col.type == pa.uint32():
                    record[col.name] = uint_gen.generate(32)
                elif col.type == pa.int64():
                    record[col.name] = int_gen.generate(64)
                elif col.type == pa.uint64():
                    record[col.name] = uint_gen.generate(64)
                elif pa.types.is_timestamp(col.type):
                    record[col.name] = uint_gen.generate(64)
                elif col.type == pa.float16():
                    record[col.name] = float_gen.generate(16)
                elif col.type == pa.float32():
                    record[col.name] = float_gen.generate(32)
                elif col.type == pa.float64():
                    record[col.name] = float_gen.generate(64)
                else:
                    pytest.fail("Unsupported column type {} for {}".format(col.type, col.name))
                if col.nullable:
                    if random.random() < settings.NULLPROBABILITY:
                        record[col.name] = None
        data.append(record)

    #v = [dict(zip(data, t)) for t in zip(*data.values())]
    return data


def generate_random_data(schema: pa.Schema, schema_pk: str, size: int = settings.DEFAULT_DATA_SIZE):
    if schema.get_field_index(schema_pk) < 0:
        raise ValueError("schema_pk must be the name of a column in the schema.")
    str_gen = SentenceGenerator()
    uint_gen = UIntGenerator()
    int_gen = IntGenerator()
    float_gen = FloatGenerator()
    data = {}

    for col in schema:
        if col.name == schema_pk:
            if col.type == pa.string():
                data[col.name] = [str(i) for i in range(size)]
            elif col.type == pa.int32() or col.type == pa.uint32() or col.type == pa.int64() or col.type == pa.uint64():
                data[col.name] = list(range(size))
            else:
                pytest.fail("Unsupported PK column type {} for {}".format(col.type, col.name))
        else:
            if col.type == pa.string():
                data[col.name] = [str_gen.generate(maxlength=int(settings.VAR_LENGTH / 2)) for i in range(size) ]
            elif col.type == pa.int8():
                data[col.name] = [int_gen.generate(8) for i in range(size) ]
            elif col.type == pa.uint8():
                data[col.name] = [uint_gen.generate(8) for i in range(size) ]
            elif col.type == pa.int16():
                data[col.name] = [int_gen.generate(16) for i in range(size) ]
            elif col.type == pa.uint16():
                data[col.name] = [uint_gen.generate(16) for i in range(size) ]
            elif col.type == pa.int32():
                data[col.name] = [int_gen.generate(32) for i in range(size) ]
            elif col.type == pa.uint32():
                data[col.name] = [uint_gen.generate(32) for i in range(size) ]
            elif col.type == pa.int64():
                data[col.name] = [int_gen.generate(64) for i in range(size) ]
            elif col.type == pa.uint64():
                data[col.name] = [uint_gen.generate(64) for i in range(size) ]
            elif pa.types.is_timestamp(col.type):
                data[col.name] = [uint_gen.generate(64) for i in range(size) ]
            elif col.type == pa.float16():
                data[col.name] = [float_gen.generate(16) for i in range(size) ]
            elif col.type == pa.float32():
                data[col.name] = [float_gen.generate(32) for i in range(size) ]
            elif col.type == pa.float64():
                data[col.name] = [float_gen.generate(64) for i in range(size) ]
            else:
                pytest.fail("Unsupported column type {} for {}".format(col.type, col.name))
            if col.nullable:
                indices = random.sample(range(size),round(settings.NULLPROBABILITY*size))
                for i in indices:
                    data[col.name][i] = None

    v = [dict(zip(data, t)) for t in zip(*data.values())]
    return v

