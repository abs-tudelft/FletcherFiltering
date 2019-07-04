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

from ast import *
import pyarrow as pa
from .ctypes_type_mapper import CTypesTypeMapper


def get_class_ast(schema: pa.Schema, class_name: str = 'StructQueryIn'):
    type_map = CTypesTypeMapper()
    col_asts = []
    for col in schema:
        col_asts.append(
            Tuple(
                elts=[
                    Str(s=col.name),
                    Attribute(
                        value=Name(id='ctypes', ctx=Load()), attr=type_map.resolve(col.type).__name__, ctx=Load()
                    )
                ],
                ctx=Load()
            )
        )

    return fix_missing_locations(
        Module(
            body=[
                Import(names=[alias(name='ctypes', asname=None)]),
                ClassDef(
                    name=class_name,
                    bases=[
                        Attribute(value=Name(id='ctypes', ctx=Load()), attr='Structure', ctx=Load())
                    ],
                    keywords=[],
                    body=[
                        Assign(
                            targets=[Name(id='_fields_', ctx=Store())],
                            value=List(
                                elts=col_asts,
                                ctx=Load()
                            )
                        )
                    ],
                    decorator_list=[]
                )
            ]
        )
    )
