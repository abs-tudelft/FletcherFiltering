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
