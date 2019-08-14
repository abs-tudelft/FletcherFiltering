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

import typed_ast.ast3 as ast
import horast
import copy
from typing import Union, Tuple
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from fletcherfiltering import settings
from fletcherfiltering.common import debug
from .helpers import make_comment, ReferenceMetadata
from .helpers.ArrowTestTypeResolver import ArrowTestTypeResolver
from .helpers.ArrowTypeResolver import ArrowTypeResolver
from .helpers.FunctionResolver import FunctionResolver, PrePostAST, FunctionMetadata
from ..exceptions import *
from .AuxSignalTransform import AuxSignalTransform
from .ConstantPropagationTransform import ConstantPropagationTransform


class PythonASTTransform(BaseTransform):
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema
        self.type_resolver = ArrowTypeResolver()
        self.test_type_resolver = ArrowTestTypeResolver()
        self.func_resolver = FunctionResolver()
        self.aux_signal_transform = AuxSignalTransform(self.in_schema, self.out_schema)
        self.constant_propagation_transform = ConstantPropagationTransform(self.in_schema, self.out_schema)
        self.query_name = 'query'

    def transform(self, node, query_name: str = 'query'):
        self.query_name = query_name
        return self.visit(node)

    # region Basic Helpers
    # def apply_value_reference(self, node):
    #     if isinstance(node, ast_nodes.ColumnReference):
    #         if not node.is_valid_reference:
    #             col_name = node.id
    #             col = self.in_schema.field_by_name(col_name)
    #             if col.nullable and col.type not in settings.VAR_LENGTH_TYPES:
    #                 node.is_value_reference = True
    #
    #
    #     elif isinstance(node, ast_nodes.IntermediaryReference):
    #         if not node.is_valid_reference:
    #             col_name = node.id
    #             length_stream = False
    #             if col_name.endswith(settings.LENGTH_SUFFIX):
    #                 col_name = col_name[0:-len(settings.LENGTH_SUFFIX)]
    #                 length_stream = True
    #
    #             col = self.in_schema.field_by_name(col_name)
    #             if col.nullable and (col.type not in settings.VAR_LENGTH_TYPES or length_stream):
    #                 node.is_value_reference = True
    #     return node

    # endregion

    # region Schema Helpers

    def get_schema_ast(self, schema: pa.Schema, schema_name: str = "schema", test_data=False,
                       is_input=False) -> ast.Expr:
        schema_ast = []

        type_resolver = self.type_resolver
        if test_data:
            type_resolver = self.test_type_resolver

        for col in schema:
            col_def = ast.AnnAssign(
                target=ast.Name(
                    id=col.name,
                    ctx=ast.Store()),
                annotation=type_resolver.resolve(arrow_type=col.type, as_stream=not test_data,
                                                 as_nullable=col.nullable and (
                                                         col.type not in settings.VAR_LENGTH_TYPES or test_data),
                                                 as_pointer=(test_data and col.type in settings.VAR_LENGTH_TYPES),
                                                 as_const=col.type == pa.string() and test_data and is_input),
                value=None,
                simple=1)
            schema_ast.append(col_def)

            if col.type in settings.VAR_LENGTH_TYPES and not test_data:
                col_def_len = ast.AnnAssign(
                    target=ast.Name(
                        id=col.name + settings.LENGTH_SUFFIX,
                        ctx=ast.Store()),
                    annotation=type_resolver.resolve(arrow_type=settings.LENGTH_TYPE, as_nullable=col.nullable,
                                                     as_stream=not test_data),
                    value=None,
                    simple=1)
                schema_ast.append(col_def_len)

        return ast.ClassDef(
            name=schema_name,
            bases=[],
            keywords=[],
            body=schema_ast,
            decorator_list=[ast.Name(
                id='struct',
                ctx=ast.Load())])

    def get_load_schema_ast(self, schema: pa.Schema):
        schema_ast = []
        for col in schema:
            if col.type in settings.VAR_LENGTH_TYPES:
                col_tmp_def = ast.AnnAssign(
                    target=ast.Subscript(
                        value=ast.Name(
                            id=col.name,
                            ctx=ast.Store()
                        ),
                        slice=ast.Index(ast.Name(id="VAR_LENGTH", ctx=ast.Load())),
                        ctx=ast.Store()
                    ),
                    annotation=self.type_resolver.resolve(arrow_type=col.type),
                    value=None,
                    simple=1)
            else:
                col_tmp_def = ast.AnnAssign(
                    target=ast.Name(
                        id=col.name,
                        ctx=ast.Store()),
                    annotation=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                    value=None,
                    simple=1)

            col_tmp_def_len = ast.AnnAssign(
                target=ast.Name(
                    id=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                annotation=self.type_resolver.resolve(arrow_type=settings.LENGTH_TYPE, as_nullable=col.nullable),
                value=None,
                simple=1)
            if col.type in settings.VAR_LENGTH_TYPES:
                col_len_var = ast.Attribute(
                    value=ast.Name(
                        id=col.name + settings.LENGTH_SUFFIX,
                        ctx=ast.Load()
                    ),
                    attr='data',
                    ctx=ast.Load())
                if col.nullable:
                    col_len_var_valid = ast.Attribute(
                        value=ast.Name(
                            id=col.name + settings.LENGTH_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr='valid',
                        ctx=ast.Load())
                else:
                    col_len_var_valid = col_len_var

                col_load = [ast.For(
                    target=ast.Name(id='i', ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Name(
                            id='range',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Num(0),
                            col_len_var
                        ],
                        keywords=[]
                    ),
                    body=[make_comment("pragma HLS PIPELINE"),
                          ast.Expr(ast.BinOp(
                              left=ast.Attribute(
                                  value=ast.Name(
                                      id=settings.INPUT_NAME,
                                      ctx=ast.Load()),
                                  attr=col.name,
                                  ctx=ast.Load()),
                              op=ast.RShift(),
                              right=ast.Subscript(
                                  value=ast.Name(
                                      id=col.name,
                                      ctx=ast.Load()
                                  ),
                                  slice=ast.Index(ast.Name(
                                      id='i',
                                      ctx=ast.Load()
                                  )),
                                  ctx=ast.Store()
                              ),
                              type_comment=None)
                          )],
                    orelse=None,
                    type_comment=ast.Name(
                        id='int',
                        ctx=ast.Load()
                    )
                ),
                    ast.If(
                        test=ast.Compare(
                            left=col_len_var,
                            ops=[ast.Eq()],
                            comparators=[
                                ast.Num(0)
                            ]
                        ),
                        body=[
                            ast.Expr(ast.BinOp(
                                left=ast.Attribute(
                                    value=ast.Name(
                                        id=settings.INPUT_NAME,
                                        ctx=ast.Load()),
                                    attr=col.name,
                                    ctx=ast.Load()),
                                op=ast.RShift(),
                                right=ast.Subscript(
                                    value=ast.Name(
                                        id=col.name,
                                        ctx=ast.Load()
                                    ),
                                    slice=ast.Index(ast.Num(0)),
                                    ctx=ast.Store()
                                ),
                                type_comment=None)
                            )
                        ],
                        orelse=[]
                    )
                ]
                if col.nullable:
                    col_load = [ast.If(
                        test=col_len_var_valid,
                        body=col_load,
                        orelse=[]
                    )]
            else:
                col_load = [ast.Expr(ast.BinOp(
                    left=ast.Attribute(
                        value=ast.Name(
                            id=settings.INPUT_NAME,
                            ctx=ast.Load()),
                        attr=col.name,
                        ctx=ast.Load()),
                    op=ast.RShift(),
                    right=ast.Name(
                        id=col.name,
                        ctx=ast.Store()),
                    type_comment=None))]
            col_load_len = ast.Expr(ast.BinOp(
                left=ast.Attribute(
                    value=ast.Name(
                        id=settings.INPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()),
                op=ast.RShift(),
                right=ast.Name(
                    id=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                type_comment=None))

            if col.type in settings.VAR_LENGTH_TYPES:
                schema_ast.append(col_tmp_def_len)
                schema_ast.append(col_load_len)

            schema_ast.append(col_tmp_def)
            schema_ast.extend(col_load)
        return schema_ast

    def get_load_test_ast(self, schema: pa.Schema):
        schema_ast = []
        for col in schema:
            if col.nullable:
                col_var_value = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(
                            id=settings.INPUT_NAME + settings.TEST_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr=col.name,
                        ctx=ast.Load()),
                    attr='data',
                    ctx=ast.Load())
                col_var_valid = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(
                            id=settings.INPUT_NAME + settings.TEST_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr=col.name,
                        ctx=ast.Load()),
                    attr='valid',
                    ctx=ast.Load())
            else:
                col_var_valid = col_var_value = ast.Attribute(
                    value=ast.Name(
                        id=settings.INPUT_NAME + settings.TEST_SUFFIX,
                        ctx=ast.Load()
                    ),
                    attr=col.name,
                    ctx=ast.Load())

            if col.type in settings.VAR_LENGTH_TYPES:

                if col.nullable:
                    col_len_var = ast.Attribute(
                        value=ast.Name(
                            id=col.name + settings.LENGTH_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr='data',
                        ctx=ast.Load())
                else:
                    col_len_var = ast.Attribute(
                        value=ast.Name(
                            id=col.name + settings.LENGTH_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr='data',
                        ctx=ast.Load())

                col_load = [
                    ast.For(
                        target=ast.Name(id='i', ctx=ast.Store()),
                        iter=ast.Call(
                            func=ast.Name(
                                id='range',
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Num(0),
                                col_len_var
                            ],
                            keywords=[]
                        ),
                        body=[make_comment("pragma HLS PIPELINE"),
                              ast.Expr(ast.BinOp(
                                  left=ast.Attribute(
                                      value=ast.Name(
                                          id=settings.INPUT_NAME,
                                          ctx=ast.Load()),
                                      attr=col.name,
                                      ctx=ast.Load()),
                                  op=ast.LShift(),
                                  right=ast.Call(
                                      func=self.type_resolver.resolve(arrow_type=col.type,
                                                                      as_nullable=col.nullable and col.type not in settings.VAR_LENGTH_TYPES),
                                      args=[
                                          ast.Subscript(
                                              value=col_var_value,
                                              slice=ast.Index(ast.Name(
                                                  id='i',
                                                  ctx=ast.Load()
                                              )),
                                              ctx=ast.Store()
                                          ),
                                          ast.NameConstant('True'),  # dvalid
                                          ast.Compare(
                                              left=ast.Name(
                                                  id='i',
                                                  ctx=ast.Load()
                                              ),
                                              ops=[ast.Eq()],
                                              comparators=[
                                                  ast.BinOp(
                                                      left=col_len_var,
                                                      op=ast.Sub(),
                                                      right=ast.Num(1)
                                                  )
                                              ]
                                          )  # last
                                      ],
                                      keywords=[]
                                  ),
                                  type_comment=None)
                              )],
                        orelse=None,
                        type_comment=ast.Name(
                            id='int',
                            ctx=ast.Load()
                        )
                    ),
                    ast.If(
                        test=ast.Compare(
                            left=col_len_var,
                            ops=[ast.Eq()],
                            comparators=[
                                ast.Num(0)
                            ]
                        ),
                        body=[
                            ast.Expr(ast.BinOp(
                                left=ast.Attribute(
                                    value=ast.Name(
                                        id=settings.INPUT_NAME,
                                        ctx=ast.Load()),
                                    attr=col.name,
                                    ctx=ast.Load()),
                                op=ast.LShift(),
                                right=ast.Call(
                                    func=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                                    args=[
                                        ast.Num(0),
                                        ast.NameConstant('False'),  # dvalid
                                        ast.NameConstant('True'),  # last
                                    ],
                                    keywords=[]
                                ),
                                type_comment=None))
                        ],
                        orelse=[]
                    )
                ]
                if col.nullable:
                    col_load[1].body[0].value.right.args.insert(0, ast.NameConstant('False'))
                    col_load = [ast.If(
                        test=col_var_valid,
                        body=col_load,
                        orelse=[]
                    )]
            else:
                col_load = [
                    ast.Expr(ast.BinOp(
                        left=ast.Attribute(
                            value=ast.Name(
                                id=settings.INPUT_NAME,
                                ctx=ast.Load()),
                            attr=col.name,
                            ctx=ast.Load()),
                        op=ast.LShift(),
                        right=ast.Call(
                            func=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                            args=[
                                ast.Attribute(
                                    value=ast.Name(
                                        id=settings.INPUT_NAME + settings.TEST_SUFFIX,
                                        ctx=ast.Load()),
                                    attr=col.name,
                                    ctx=ast.Load()),
                                ast.NameConstant('True'),  # dvalid
                                ast.Compare(
                                    left=ast.Name(
                                        id=settings.CURRENT_RECORD_VAR_NAME,
                                        ctx=ast.Load()
                                    ),
                                    ops=[ast.Eq()],
                                    comparators=[
                                        ast.Attribute(
                                            value=ast.Name(
                                                id=settings.META_NAME,
                                                ctx=ast.Load()
                                            ),
                                            attr='length',
                                            ctx=ast.Load())
                                    ]
                                )
                            ],
                            keywords=[]
                        ),
                        type_comment=None))
                ]

            col_def_len_args = [ast.Call(
                func=ast.Name(
                    id='strlen',
                    ctx=ast.Load()
                ),
                args=[
                    col_var_value
                ],
                keywords=[]),
                ast.NameConstant('True'),  # dvalid
                ast.Compare(
                    left=ast.Name(
                        id=settings.CURRENT_RECORD_VAR_NAME,
                        ctx=ast.Load()
                    ),
                    ops=[ast.Eq()],
                    comparators=[
                        ast.Attribute(
                            value=ast.Name(
                                id=settings.META_NAME,
                                ctx=ast.Load()
                            ),
                            attr='length',
                            ctx=ast.Load())
                    ]
                )
            ]

            if col.nullable:
                col_def_len_args.insert(0,
                                        col_var_valid
                                        )

            col_def_len = ast.AnnAssign(
                target=ast.Call(
                    func=ast.Name(id=col.name + settings.LENGTH_SUFFIX, ctx=ast.Load()),
                    args=col_def_len_args,
                    keywords=[]
                ),
                annotation=self.type_resolver.resolve(arrow_type=settings.LENGTH_TYPE, as_nullable=col.nullable),
                value=None,
                simple=1)

            col_load_len = ast.Expr(ast.BinOp(
                left=ast.Attribute(
                    value=ast.Name(
                        id=settings.INPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()),
                op=ast.LShift(),
                right=ast.Name(
                    id=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()),
                type_comment=None))

            if col.type in settings.VAR_LENGTH_TYPES:
                schema_ast.append(col_def_len)
                schema_ast.append(col_load_len)

            schema_ast.extend(col_load)
        return schema_ast

    def get_store_schema_ast(self, schema: pa.Schema):
        schema_ast = []
        for col in schema:
            col_name_code = col.name + settings.OUTPUT_SUFFIX

            if col.type in settings.VAR_LENGTH_TYPES:

                col_empty_element_args = [ast.Num(0), ast.NameConstant('False'),
                                          ast.NameConstant('True')]  # Data = 0, dvalid = 0, last = 1

                col_empty_element = ast.Expr(ast.BinOp(
                    left=
                    ast.Attribute(
                        value=ast.Name(
                            id=settings.OUTPUT_NAME,
                            ctx=ast.Load()),
                        attr=col.name,
                        ctx=ast.Store()),
                    op=ast.LShift(),
                    right=ast.Call(
                        func=self.type_resolver.resolve(arrow_type=col.type),
                        args=col_empty_element_args,
                        keywords=[]
                    ),
                    type_comment=None))
                col_len_var = ast.Attribute(
                    value=ast.Name(
                        id=col_name_code + settings.LENGTH_SUFFIX,
                        ctx=ast.Load()
                    ),
                    attr='data',
                    ctx=ast.Load())
                if col.nullable:
                    col_len_var_valid = ast.Attribute(
                        value=ast.Name(
                            id=col_name_code + settings.LENGTH_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr='valid',
                        ctx=ast.Load())
                else:
                    col_len_var_valid = col_len_var

                output_col_ast = [ast.For(
                    target=ast.Name(id='i', ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Name(
                            id='range',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Num(0),
                            col_len_var
                        ],
                        keywords=[]
                    ),
                    body=[make_comment("pragma HLS PIPELINE"),
                          ast.Expr(ast.BinOp(
                              left=
                              ast.Attribute(
                                  value=ast.Name(
                                      id=settings.OUTPUT_NAME,
                                      ctx=ast.Load()),
                                  attr=col.name,
                                  ctx=ast.Store()),
                              op=ast.LShift(),
                              right=ast.Subscript(
                                  value=ast.Name(
                                      id=col_name_code,
                                      ctx=ast.Load()
                                  ),
                                  slice=ast.Index(ast.Name(
                                      id='i',
                                      ctx=ast.Load()
                                  )),
                                  ctx=ast.Load()
                              ),
                              type_comment=None))
                          ],
                    orelse=None,
                    type_comment=ast.Name(
                        id='int',
                        ctx=ast.Load()
                    )
                ),
                    ast.If(
                        test=ast.Compare(
                            left=col_len_var,
                            ops=[ast.Eq()],
                            comparators=[
                                ast.Num(0)
                            ]
                        ),
                        body=[
                            ast.Expr(ast.BinOp(
                                left=ast.Attribute(
                                    value=ast.Name(
                                        id=settings.OUTPUT_NAME,
                                        ctx=ast.Load()),
                                    attr=col.name,
                                    ctx=ast.Load()),
                                op=ast.LShift(),
                                right=ast.Call(
                                    func=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                                    args=[
                                        ast.Num(0),
                                        ast.NameConstant('False'),  # dvalid
                                        ast.NameConstant('True'),  # last
                                    ],
                                    keywords=[]
                                ),
                                type_comment=None))
                        ],
                        orelse=[]
                    )
                ]
                if col.nullable:
                    output_col_ast[1].body[0].value.right.args.insert(0, ast.NameConstant('False'))
                    output_col_ast = [ast.If(
                        test=col_len_var_valid,
                        body=output_col_ast,
                        orelse=[col_empty_element]
                    )]
            else:
                output_col_ast = [ast.Expr(ast.BinOp(
                    left=
                    ast.Attribute(
                        value=ast.Name(
                            id=settings.OUTPUT_NAME,
                            ctx=ast.Load()),
                        attr=col.name,
                        ctx=ast.Store()),
                    op=ast.LShift(),
                    right=ast.Name(
                        id=col_name_code,
                        ctx=ast.Load()
                    ),
                    type_comment=None))]

            output_col_ast_len = ast.Expr(ast.BinOp(
                left=
                ast.Attribute(
                    value=ast.Name(
                        id=settings.OUTPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                op=ast.LShift(),
                right=ast.Name(
                    id=col_name_code + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()
                ),
                type_comment=None))

            if col.type in settings.VAR_LENGTH_TYPES:
                schema_ast.append(output_col_ast_len)

            schema_ast.extend(output_col_ast)
        return schema_ast

    def get_store_test_ast(self, schema: pa.Schema):
        schema_ast = []
        for col in schema:
            col_name_code = col.name + settings.OUTPUT_SUFFIX
            if col.nullable:
                col_var_value = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(
                            id=settings.OUTPUT_NAME + settings.TEST_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr=col.name,
                        ctx=ast.Load()),
                    attr='data',
                    ctx=ast.Load())
                col_var_valid = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(
                            id=settings.OUTPUT_NAME + settings.TEST_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr=col.name,
                        ctx=ast.Load()),
                    attr='valid',
                    ctx=ast.Load())
            else:
                col_var_valid = col_var_value = ast.Attribute(
                    value=ast.Name(
                        id=settings.OUTPUT_NAME + settings.TEST_SUFFIX,
                        ctx=ast.Load()
                    ),
                    attr=col.name,
                    ctx=ast.Load())
            if col.type in settings.VAR_LENGTH_TYPES:
                col_len_var = ast.Attribute(
                    value=ast.Name(
                        id=col_name_code + settings.LENGTH_SUFFIX,
                        ctx=ast.Load()
                    ),
                    attr='data',
                    ctx=ast.Load())
                if col.nullable:
                    col_len_var_valid = ast.Attribute(
                        value=ast.Name(
                            id=col_name_code + settings.LENGTH_SUFFIX,
                            ctx=ast.Load()
                        ),
                        attr='valid',
                        ctx=ast.Load())
                else:
                    col_len_var_valid = col_len_var

                output_col_read_empty_element = [
                    ast.Expr(ast.BinOp(
                        left=
                        ast.Attribute(
                            value=ast.Name(
                                id=settings.OUTPUT_NAME,
                                ctx=ast.Load()),
                            attr=col.name,
                            ctx=ast.Store()),
                        op=ast.RShift(),
                        right=ast.Name(
                            id=col_name_code,
                            ctx=ast.Load()
                        ),
                        type_comment=None)),
                    ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=col_var_value,
                                slice=ast.Index(ast.Num(0)),
                                ctx=ast.Load()
                            )
                        ],
                        value=
                        ast.Attribute(
                            value=ast.Name(
                                id=col_name_code,
                                ctx=ast.Load()),
                            attr='data',
                            ctx=ast.Store()),
                    )
                ]
                output_col_ast = [ast.For(
                    target=ast.Name(id='i', ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Name(
                            id='range',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Num(0),
                            col_len_var
                        ],
                        keywords=[]
                    ),
                    body=[make_comment("pragma HLS PIPELINE"),
                          ast.Expr(ast.BinOp(
                              left=
                              ast.Attribute(
                                  value=ast.Name(
                                      id=settings.OUTPUT_NAME,
                                      ctx=ast.Load()),
                                  attr=col.name,
                                  ctx=ast.Store()),
                              op=ast.RShift(),
                              right=ast.Name(
                                  id=col_name_code,
                                  ctx=ast.Load()
                              ),
                              type_comment=None)),
                          ast.Assign(
                              targets=[
                                  ast.Subscript(
                                      value=col_var_value,
                                      slice=ast.Index(ast.Name(
                                          id='i',
                                          ctx=ast.Load()
                                      )),
                                      ctx=ast.Load()
                                  )
                              ],
                              value=
                              ast.Attribute(
                                  value=ast.Name(
                                      id=col_name_code,
                                      ctx=ast.Load()),
                                  attr='data',
                                  ctx=ast.Store()),
                          )
                          ],
                    orelse=None,
                    type_comment=ast.Name(
                        id='int',
                        ctx=ast.Load()
                    )
                ),
                    ast.If(
                        test=ast.Compare(
                            left=col_len_var,
                            ops=[ast.Eq()],
                            comparators=[
                                ast.Num(0)
                            ]
                        ),
                        body=[
                            ast.Expr(ast.BinOp(
                                left=
                                ast.Attribute(
                                    value=ast.Name(
                                        id=settings.OUTPUT_NAME,
                                        ctx=ast.Load()),
                                    attr=col.name,
                                    ctx=ast.Store()),
                                op=ast.RShift(),
                                right=ast.Name(
                                    id=col_name_code,
                                    ctx=ast.Load()
                                ),
                                type_comment=None)),
                            ast.Assign(
                                targets=[
                                    ast.Subscript(
                                        value=col_var_value,
                                        slice=ast.Index(ast.Num(0)),
                                        ctx=ast.Load()
                                    )
                                ],
                                value=
                                ast.Attribute(
                                    value=ast.Name(
                                        id=col_name_code,
                                        ctx=ast.Load()),
                                    attr='data',
                                    ctx=ast.Store()),
                            )
                        ],
                        orelse=[]
                    )
                ]

                output_col_null_term = ast.Assign(
                    targets=[
                        ast.Subscript(
                            value=col_var_value,
                            slice=ast.Index(
                                col_len_var
                            ),
                            ctx=ast.Load()
                        )
                    ],
                    value=ast.Bytes(s='\0')
                )

                if col.type in settings.VAR_LENGTH_TYPES:
                    output_col_ast.append(output_col_null_term)

                if col.nullable:
                    output_col_ast = [ast.If(
                        test=col_var_valid,
                        body=output_col_ast,
                        orelse=[output_col_read_empty_element]
                    )]

                output_col_valid = ast.Assign(
                    targets=[col_var_valid],
                    value=col_len_var_valid
                )

            else:
                output_col_ast = [ast.Expr(ast.BinOp(
                    left=
                    ast.Attribute(
                        value=ast.Name(
                            id=settings.OUTPUT_NAME,
                            ctx=ast.Load()),
                        attr=col.name,
                        ctx=ast.Store()),
                    op=ast.RShift(),
                    right=ast.Name(
                        id=col_name_code,
                        ctx=ast.Load()),
                    type_comment=None)),
                    ast.Assign(
                        targets=[col_var_value],
                        value=ast.Attribute(
                            value=ast.Name(
                                id=col_name_code,
                                ctx=ast.Load()),
                            attr='data',
                            ctx=ast.Load()),
                    )
                ]

                col_var_valid_src = ast.Attribute(
                    value=ast.Name(
                        id=col_name_code,
                        ctx=ast.Load()
                    ),
                    attr='valid',
                    ctx=ast.Load())

                output_col_valid = ast.Assign(
                    targets=[col_var_valid],
                    value=col_var_valid_src
                )

            output_col_ast_len = ast.Expr(ast.BinOp(
                left=
                ast.Attribute(
                    value=ast.Name(
                        id=settings.OUTPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                op=ast.RShift(),
                right=ast.Name(
                    id=col_name_code + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()
                ),
                type_comment=None))

            output_col_def = ast.AnnAssign(
                target=ast.Name(
                    id=col_name_code,
                    ctx=ast.Store()),
                annotation=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                value=None,
                simple=1)

            output_col_def_len = ast.AnnAssign(
                target=ast.Name(
                    id=col_name_code + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                annotation=self.type_resolver.resolve(arrow_type=settings.LENGTH_TYPE, as_nullable=col.nullable),
                value=None,
                simple=1)

            schema_ast.append(output_col_def)
            if col.type in settings.VAR_LENGTH_TYPES:
                schema_ast.append(output_col_def_len)
                schema_ast.append(output_col_ast_len)

                if col.nullable:
                    schema_ast.append(output_col_valid)

            schema_ast.extend(output_col_ast)

            if col.type not in settings.VAR_LENGTH_TYPES:
                if col.nullable:
                    schema_ast.append(output_col_valid)

        return schema_ast

    def get_in_schema_ast(self, test_data=False) -> ast.Expr:
        return self.get_schema_ast(self.in_schema, "in_schema" if not test_data else "in_schema" + settings.TEST_SUFFIX,
                                   test_data, True)

    def get_out_schema_ast(self, test_data=False) -> ast.Expr:
        return self.get_schema_ast(self.out_schema,
                                   "out_schema" if not test_data else "out_schema" + settings.TEST_SUFFIX,
                                   test_data, False)

    def get_input_ast(self) -> list:
        return [
                   ast.AnnAssign(
                       target=ast.Name(
                           id=settings.CURRENT_RECORD_VAR_NAME,
                           ctx=ast.Store()),
                       annotation=ast.Name(id='static unsigned int', ctx=ast.Load()),
                       value=ast.Num(0),
                       simple=1),
                   make_comment('pragma HLS reset variable={}'.format(settings.CURRENT_RECORD_VAR_NAME)),
                   ast.AugAssign(
                       target=ast.Name(
                           id=settings.CURRENT_RECORD_VAR_NAME,
                           ctx=ast.AugLoad()),
                       op=ast.Add(),
                       value=ast.Num(1)
                   )
               ] + self.get_load_schema_ast(self.in_schema)

    def get_port_pragma_ast(self) -> list:
        port_pragma_ast = []
        port_pragma_ast.append(make_comment('pragma HLS INTERFACE {} port=return'.format(settings.BLOCK_LEVEL_IO_TYPE)))
        port_pragma_ast.append(
            make_comment(
                'pragma HLS INTERFACE {0} port={1}.{2}'.format(settings.META_PORT_TYPE, settings.META_NAME, 'length')))
        port_pragma_ast.append(
            make_comment('pragma HLS DATA_PACK variable={0}'.format(settings.META_NAME)))

        # TODO Add name={2}{1} back in
        for col in self.in_schema:
            port_pragma_ast.append(
                make_comment(
                    'pragma HLS INTERFACE {0} port={3}.{1}'.format(settings.PORT_TYPE, col.name,
                                                                   settings.INPORT_PREFIX,
                                                                   settings.INPUT_NAME)))
            port_pragma_ast.append(
                make_comment(
                    'pragma HLS DATA_PACK variable={2}.{0}'.format(col.name,
                                                                   settings.INPORT_PREFIX,
                                                                   settings.INPUT_NAME)))
            # pragma HLS DATA_PACK variable=st_in
            if col.type in settings.VAR_LENGTH_TYPES:
                port_pragma_ast.append(
                    make_comment(
                        'pragma HLS INTERFACE {0} port={3}.{1}'.format(settings.PORT_TYPE,
                                                                       col.name + settings.LENGTH_SUFFIX,
                                                                       settings.INPORT_PREFIX,
                                                                       settings.INPUT_NAME)))
                port_pragma_ast.append(
                    make_comment(
                        'pragma HLS DATA_PACK variable={2}.{0}'.format(col.name + settings.LENGTH_SUFFIX,
                                                                       settings.INPORT_PREFIX,
                                                                       settings.INPUT_NAME)))

        for col in self.out_schema:
            port_pragma_ast.append(
                make_comment(
                    'pragma HLS INTERFACE {0} port={3}.{1}'.format(settings.PORT_TYPE, col.name,
                                                                   settings.OUTPORT_PREFIX,
                                                                   settings.OUTPUT_NAME)))
            port_pragma_ast.append(
                make_comment(
                    'pragma HLS DATA_PACK variable={2}.{0}'.format(col.name,
                                                                   settings.OUTPORT_PREFIX,
                                                                   settings.OUTPUT_NAME)))

            if col.type in settings.VAR_LENGTH_TYPES:
                port_pragma_ast.append(
                    make_comment(
                        'pragma HLS INTERFACE {0} port={3}.{1}'.format(settings.PORT_TYPE,
                                                                       col.name + settings.LENGTH_SUFFIX,
                                                                       settings.OUTPORT_PREFIX,
                                                                       settings.OUTPUT_NAME)))
                port_pragma_ast.append(
                    make_comment(
                        'pragma HLS DATA_PACK variable={2}.{0}'.format(col.name + settings.LENGTH_SUFFIX,
                                                                       settings.OUTPORT_PREFIX,
                                                                       settings.OUTPUT_NAME)))

        # port_pragma_ast.append(make_comment('pragma HLS DATAFLOW'.format(settings.BLOCK_LEVEL_IO_TYPE)))

        return port_pragma_ast

    def get_grab_empty_ast(self, schema: pa.Schema) -> list:
        grab_empty_ast = [make_comment('close streams')]
        for col in schema:

            col_name_code = col.name + settings.OUTPUT_SUFFIX

            output_col_def = ast.AnnAssign(
                target=ast.Name(
                    id=col_name_code,
                    ctx=ast.Store()),
                annotation=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                value=None,
                simple=1)

            output_col_def_len = ast.AnnAssign(
                target=ast.Name(
                    id=col_name_code + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                annotation=self.type_resolver.resolve(arrow_type=settings.LENGTH_TYPE, as_nullable=col.nullable),
                value=None,
                simple=1)

            output_col_ast = ast.Expr(ast.BinOp(
                left=
                ast.Attribute(
                    value=ast.Name(
                        id=settings.OUTPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name,
                    ctx=ast.Store()),
                op=ast.RShift(),
                right=ast.Name(
                    id=col_name_code,
                    ctx=ast.Load()
                ),
                type_comment=None))

            output_col_ast_len = ast.Expr(ast.BinOp(
                left=
                ast.Attribute(
                    value=ast.Name(
                        id=settings.OUTPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name + settings.LENGTH_SUFFIX,
                    ctx=ast.Store()),
                op=ast.RShift(),
                right=ast.Name(
                    id=col_name_code + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()
                ),
                type_comment=None))

            if col.type in settings.VAR_LENGTH_TYPES:
                grab_empty_ast.append(output_col_def_len)
                grab_empty_ast.append(output_col_ast_len)
            else:
                grab_empty_ast.append(output_col_def)
                grab_empty_ast.append(output_col_ast)

        return [ast.If(
            test=ast.Compare(
                left=ast.Name(
                    id=settings.CURRENT_RECORD_VAR_NAME,
                    ctx=ast.Load()
                ),
                ops=[ast.Eq()],
                comparators=[
                    ast.Attribute(
                        value=ast.Name(
                            id=settings.META_NAME,
                            ctx=ast.Load()),
                        attr='length',
                        ctx=ast.Store()),
                ]
            ),
            body=grab_empty_ast,
            orelse=[]
        )]

    def get_write_empty_ast(self, schema: pa.Schema) -> list:
        write_empty_ast = [make_comment('close streams')]
        for col in schema:

            col_name_code = col.name + settings.OUTPUT_SUFFIX

            col_load = ast.Expr(ast.BinOp(
                left=ast.Attribute(
                    value=ast.Name(
                        id=settings.OUTPUT_NAME,
                        ctx=ast.Load()),
                    attr=col.name + (settings.LENGTH_SUFFIX if col.type in settings.VAR_LENGTH_TYPES else ''),
                    ctx=ast.Load()),
                op=ast.LShift(),
                right=ast.Call(
                    func=self.type_resolver.resolve(
                        arrow_type=col.type if col.type not in settings.VAR_LENGTH_TYPES else settings.LENGTH_TYPE,
                        as_nullable=col.nullable),
                    args=[
                        ast.Num(0),
                        ast.NameConstant('False'),  # dvalid
                        ast.Attribute(
                            value=ast.Name(
                                id=col_name_code + (
                                    settings.LENGTH_SUFFIX if col.type in settings.VAR_LENGTH_TYPES else ''),
                                ctx=ast.Load()),
                            attr='last',
                            ctx=ast.Load())
                    ],
                    keywords=[]
                ),
                type_comment=None))

            if col.nullable:
                col_load.value.right.args.insert(0, ast.NameConstant('False'))
            write_empty_ast.append(col_load)

        return [ast.If(
            test=ast.Compare(
                left=ast.Name(
                    id=settings.CURRENT_RECORD_VAR_NAME,
                    ctx=ast.Load()
                ),
                ops=[ast.Eq()],
                comparators=[
                    ast.Attribute(
                        value=ast.Name(
                            id=settings.META_NAME,
                            ctx=ast.Load()),
                        attr='length',
                        ctx=ast.Store()),
                ]
            ),
            body=write_empty_ast,
            orelse=[]
        )]

    def get_output_ast(self) -> list:
        grab_empty_ast = []

        return [
            ast.If(
                test=ast.Name(
                    id=settings.PASS_VAR_NAME,
                    ctx=ast.Load()),
                body=self.get_store_schema_ast(self.out_schema),
                orelse=self.get_write_empty_ast(self.out_schema))
        ]

    def get_input_test_ast(self) -> list:
        return [
                   ast.AnnAssign(
                       target=ast.Name(
                           id=settings.INPUT_NAME,
                           ctx=ast.Store()),
                       annotation=ast.Name(id='in_schema', ctx=ast.Load()),
                       value=None,
                       simple=1),
                   ast.AnnAssign(
                       target=ast.Name(
                           id=settings.OUTPUT_NAME,
                           ctx=ast.Store()),
                       annotation=ast.Name(id='out_schema', ctx=ast.Load()),
                       value=None,
                       simple=1),
                   ast.AnnAssign(
                       target=ast.Name(
                           id=settings.CURRENT_RECORD_VAR_NAME,
                           ctx=ast.Store()),
                       annotation=ast.Name(id='static unsigned int', ctx=ast.Load()),
                       value=ast.Num(0),
                       simple=1),
                   ast.AugAssign(
                       target=ast.Name(
                           id=settings.CURRENT_RECORD_VAR_NAME,
                           ctx=ast.AugLoad()),
                       op=ast.Add(),
                       value=ast.Num(1)
                   )

               ] + self.get_load_test_ast(self.in_schema)

    def get_output_test_ast(self) -> list:
        return [
            ast.If(
                test=ast.Name(
                    id=settings.PASS_VAR_NAME,
                    ctx=ast.Load()),
                body=self.get_store_test_ast(self.out_schema),
                orelse=self.get_grab_empty_ast(self.out_schema))
        ]

    # endregion

    # region Function Helpers
    # def getLengthFunction(self, func):
    #     if isinstance(func, ast.Call):
    #         func_name = func.func.id
    #         func_lookup = {functions[x]['name']: x for x in functions.keys()}
    #         if func_name in func_lookup:
    #             return ast.Call(
    #                 func=ast.Name(
    #                     id=functions[func_lookup[func_name]]['name_length'],
    #                     ctx=ast.Load()
    #                 ),
    #                 args=func.args[1::2],
    #                 keywords=[])
    #         else:
    #             raise ValueError("Function {} not found.".format(func_name))
    #     elif isinstance(func, ast.Name):
    #         return func
    #     else:
    #         raise ValueError("Argument was not of type ast.Call or ast.Name but {}.".format(func))

    # endregion

    # region Operator Containers

    def visit_CompOp(self, node: ast_nodes.CompOp) -> ast.Compare:
        debug(node)
        # self.apply_value_reference(node.lhs)
        # self.apply_value_reference(node.rhs)

        return ast.Compare(self.visit(node.lhs), [self.visit(node.op)], [self.visit(node.rhs)])

    def visit_BinOp(self, node: ast_nodes.BinOp) -> Union[ast.BinOp, ast.BoolOp]:
        debug(node)
        # self.apply_value_reference(node.lhs)
        # self.apply_value_reference(node.rhs)

        if isinstance(node.op, ast_nodes.BoolOperator):
            return ast.BoolOp(self.visit(node.op), [self.visit(node.lhs), self.visit(node.rhs)])
        else:
            return ast.BinOp(self.visit(node.lhs), self.visit(node.op), self.visit(node.rhs))

    def visit_UnOp(self, node: ast_nodes.UnOp) -> ast.UnaryOp:
        debug(node)
        # self.apply_value_reference(node.rhs)

        return ast.UnaryOp(self.visit(node.op), self.visit(node.rhs))

    def visit_Not(self, node: ast_nodes.Not) -> ast.UnaryOp:
        debug(node)
        # self.apply_value_reference(node.expr)

        return ast.UnaryOp(ast.Not(), self.visit(node.expr))

    # endregion

    # region Values
    def visit_IntValue(self, node: ast_nodes.IntValue) -> ast.Num:
        debug(node)
        return ast.Num(node.value)

    def visit_DoubleValue(self, node: ast_nodes.DoubleValue) -> ast.Num:
        debug(node)
        return ast.Num(node.value)

    def visit_StringValue(self, node: ast_nodes.StringValue) -> ast.Str:
        debug(node)
        return ast.Str(node.value)

    def visit_TrueValue(self, node: ast_nodes.TrueValue) -> ast.NameConstant:
        debug(node)
        return ast.NameConstant('True')

    def visit_FalseValue(self, node: ast_nodes.TrueValue) -> ast.NameConstant:
        debug(node)
        return ast.NameConstant('False')

    # endregion

    # region Operators
    def visit_AddOperator(self, node: ast_nodes.AddOperator) -> ast.Add:
        debug(node)
        return ast.Add()

    def visit_SubOperator(self, node: ast_nodes.SubOperator) -> ast.Sub:
        debug(node)
        return ast.Sub()

    def visit_MulOperator(self, node: ast_nodes.MulOperator) -> ast.Mult:
        debug(node)
        return ast.Mult()

    def visit_DivOperator(self, node: ast_nodes.DivOperator) -> ast.Div:
        debug(node)
        return ast.Div()

    def visit_BitAndOperator(self, node: ast_nodes.BitAndOperator) -> ast.BitAnd:
        debug(node)
        return ast.BitAnd()

    def visit_BitOrOperator(self, node: ast_nodes.BitOrOperator) -> ast.BitOr:
        debug(node)
        return ast.BitOr()

    def visit_BitXorOperator(self, node: ast_nodes.BitXorOperator) -> ast.BitXor:
        debug(node)
        return ast.BitXor()

    def visit_AndOperator(self, node: ast_nodes.AndOperator) -> ast.And:
        debug(node)
        return ast.And()

    def visit_OrOperator(self, node: ast_nodes.OrOperator) -> ast.Or:
        debug(node)
        return ast.Or()

    def visit_USubOperator(self, node: ast_nodes.USubOperator) -> ast.USub:
        debug(node)
        return ast.USub()

    def visit_UAddOperator(self, node: ast_nodes.UAddOperator) -> ast.UAdd:
        debug(node)
        return ast.UAdd()

    def visit_NEqOperator(self, node: ast_nodes.NEqOperator) -> ast.NotEq:
        debug(node)
        return ast.NotEq()

    def visit_GtOperator(self, node: ast_nodes.GtOperator) -> ast.Gt:
        debug(node)
        return ast.Gt()

    def visit_LtOperator(self, node: ast_nodes.LtOperator) -> ast.Lt:
        debug(node)
        return ast.Lt()

    def visit_GtEOperator(self, node: ast_nodes.GtEOperator) -> ast.GtE:
        debug(node)
        return ast.GtE()

    def visit_LtEOperator(self, node: ast_nodes.UAddOperator) -> ast.LtE:
        debug(node)
        return ast.LtE()

    def visit_EqOperator(self, node: ast_nodes.EqOperator) -> ast.Eq:
        debug(node)
        return ast.Eq()

    def visit_IsOperator(self, node: ast_nodes.IsOperator) -> ast.Is:
        debug(node)
        return ast.Is()

    # endregion

    def visit_FunctionCall(self, node: ast_nodes.FunctionCall) -> Union[ast.Call, PrePostAST]:
        func_metadata = self.func_resolver.resolve(node.func)

        # node.params = list(map(self.apply_value_reference, node.params))

        func_ast = ast.Call(
            func=ast.Name(
                id=func_metadata.resolved_name,
                ctx=ast.Load()
            ),
            args=self.visit(node.params),
            keywords=[])

        if callable(func_metadata.generator):
            debug(func_ast)
            func_ast = func_metadata.generator(func_ast, func_metadata)
            debug(func_ast)

        return func_ast

    def visit_ColumnReference(self, node: ast_nodes.ColumnReference) -> ast.Name:
        if isinstance(node.metadata, ReferenceMetadata):
            if node.metadata.signal is not None:
                return ast.Attribute(
                    value=ast.Name(
                        id=node.id,
                        ctx=ast.Load()
                    ),
                    attr=node.metadata.signal,
                    ctx=ast.Load())
        return ast.Name(
            id=node.id,
            ctx=ast.Load()
        )

    def visit_IntermediaryReference(self, node: ast_nodes.IntermediaryReference) -> ast.Name:
        if isinstance(node.metadata, ReferenceMetadata):
            if node.metadata.signal is not None:
                return ast.Attribute(
                    value=ast.Name(
                        id=node.id,
                        ctx=ast.Load()
                    ),
                    attr=node.metadata.signal,
                    ctx=ast.Load())
        return ast.Name(
            id=node.id,
            ctx=ast.Load()
        )

    def visit_SelectColumn(self, node: ast_nodes.SelectColumn) -> list:
        # self.apply_value_reference(node.value)
        return self.visit(node.value)

    def visit_Select(self, node: ast_nodes.Select) -> list:
        if len(node.columns) != len(self.out_schema.names):
            raise OutSchemaColumnCodegenError()

        select_ast = []

        for select_col in node.columns:
            col_name = 'unknown'
            if isinstance(select_col, ast_nodes.SelectColumn):
                if isinstance(select_col.alias, ast_nodes.Alias):
                    col_name = select_col.alias.id
                elif isinstance(select_col.value, ast_nodes.ColumnReference):
                    col_name = select_col.value.id

            col = self.out_schema.field_by_name(col_name)
            assert (col is not None)
            # TODO Proper error about missing output column
            col_name_code = col.name + settings.OUTPUT_SUFFIX

            select_col_valid = copy.deepcopy(select_col)
            select_col_dvalid = copy.deepcopy(select_col)
            select_col_last = copy.deepcopy(select_col)
            col_value = self.visit(select_col)

            if col.nullable:
                col_value_valid = self.visit(
                    self.constant_propagation_transform.transform(
                        self.aux_signal_transform.transform(select_col_valid, signal='valid', only_nullables=True,
                                                            merge_op=ast_nodes.AndOperator),
                        skip_functions=True
                    )
                )

            col_value_last = self.visit(
                self.constant_propagation_transform.transform(
                    self.aux_signal_transform.transform(select_col_last, signal='last', only_nullables=False,
                                                        merge_op=ast_nodes.OrOperator,
                                                        default_value=ast_nodes.FalseValue),
                    skip_functions=True
                )
            )

            col_value_dvalid = self.visit(
                self.constant_propagation_transform.transform(
                    self.aux_signal_transform.transform(select_col_dvalid, signal='dvalid', only_nullables=False,
                                                        merge_op=ast_nodes.AndOperator),
                    skip_functions=True
                )
            )

            col_len_ast = ast.Name(id="VAR_LENGTH", ctx=ast.Load())

            # Unwrap for lists.
            if col.type in settings.VAR_LENGTH_TYPES and isinstance(col_value, ast.Attribute):
                col_value = col_value.value

            if isinstance(col_value, PrePostAST):
                col_value_ast = col_value.ast
                if isinstance(col_value.len_ast, ast.AST):
                    col_len_ast = col_value.len_ast
            else:
                col_value_ast = col_value
                if isinstance(col_value, ast.Name):
                    col_len_ast = self.visit(
                        ast_nodes.IntermediaryReference(
                            id=col_value.id + settings.LENGTH_SUFFIX
                        )
                    )

            if col.nullable and col.type not in settings.VAR_LENGTH_TYPES:
                args_ast = [col_value_valid, col_value_ast]
            else:
                args_ast = [col_value_ast]

            if col.nullable:
                args_len_ast = [col_value_valid, col_len_ast]
            else:
                args_len_ast = [col_len_ast]

            if isinstance(col_value, PrePostAST):
                if isinstance(col_value.metadata, FunctionMetadata):
                    if col_value.metadata.manual_signal_passthrough:
                        args_len_ast.append(
                            col_value_dvalid
                        )
                        args_len_ast.append(
                            col_value_last
                        )

            target_ast = ast.Call(
                func=ast.Name(
                    id=col_name_code,
                    ctx=ast.Load()
                ),
                args=args_ast,
                keywords=[]
            )

            target_len_ast = ast.Call(
                func=ast.Name(
                    id=col_name_code + settings.LENGTH_SUFFIX,
                    ctx=ast.Load()
                ),
                args=args_len_ast,
                keywords=[]
            )

            if col.type in settings.VAR_LENGTH_TYPES:
                col_ast = ast.AnnAssign(
                    target=target_ast,
                    annotation=self.type_resolver.resolve(arrow_type=col.type, as_nullable=False,
                                                          as_pointer=True),
                    value=None,
                    simple=1)
            else:
                col_ast = ast.AnnAssign(
                    target=target_ast,
                    annotation=self.type_resolver.resolve(arrow_type=col.type, as_nullable=col.nullable),
                    value=None,
                    simple=1)

            col_len = ast.AnnAssign(
                target=target_len_ast,
                annotation=self.type_resolver.resolve(arrow_type=settings.LENGTH_TYPE, as_nullable=col.nullable),
                value=None,
                simple=1)

            if isinstance(col_value, PrePostAST):
                if col_value.pre_ast is not None:
                    if isinstance(col_value.pre_ast, list):
                        select_ast.extend(col_value.pre_ast)
                    else:
                        select_ast.append(col_value.pre_ast)
            select_ast.append(col_ast)
            if col.type in settings.VAR_LENGTH_TYPES:
                select_ast.append(col_len)
            if isinstance(col_value, PrePostAST):
                if col_value.post_ast is not None:
                    select_ast.append(col_value.post_ast)

        return select_ast

        # return [self.visit(col) for col in node.columns]

    def visit_From(self, node: ast_nodes.From) -> None:
        return

    def visit_Where(self, node: ast_nodes.Where) -> ast.AnnAssign:
        return ast.AnnAssign(
            target=ast.Name(
                id=settings.PASS_VAR_NAME,
                ctx=ast.Store()
            ),
            annotation=ast.Name(
                id='bool',
                ctx=ast.Load()
            ),
            value=self.visit(node.condition),
            simple=1
        )

    def visit_Query(self, node: ast_nodes.Query) -> Tuple[list, list, list, list]:
        debug(node)
        function_ast = ast.FunctionDef(
            name=self.query_name,
            args=ast.arguments(
                args=[
                    ast.arg(
                        arg=settings.META_NAME,
                        annotation=ast.Index(ast.Name(
                            id='RecordBatchMeta',
                            ctx=ast.Load())),
                        type_comment=None),
                    ast.arg(
                        arg=settings.INPUT_NAME,
                        annotation=ast.Index(ast.Name(
                            id='in_schema',
                            ctx=ast.Load())),
                        type_comment=None),
                    ast.arg(
                        arg=settings.OUTPUT_NAME,
                        annotation=ast.Index(ast.Name(
                            id='out_schema',
                            ctx=ast.Load())),
                        type_comment=None)
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]),
            body=self.get_port_pragma_ast() + self.get_input_ast() + [
                make_comment("Start of data processing")] + self.visit(node.q) + [
                     make_comment("End of data processing")] + self.get_output_ast() + [
                     ast.Return(
                         value=ast.Name(
                             id=settings.PASS_VAR_NAME,
                             ctx=ast.Load()
                         )
                     )
                 ],
            decorator_list=[],
            returns=ast.Name(
                id='bool',
                ctx=ast.Load()
            ),
            type_comment=None)

        test_function_ast = ast.FunctionDef(
            name=self.query_name + settings.TEST_SUFFIX,
            args=ast.arguments(
                args=[
                    ast.arg(
                        arg=settings.META_NAME,
                        annotation=ast.Index(ast.Name(
                            id='RecordBatchMeta',
                            ctx=ast.Load())),
                        type_comment=None),
                    ast.arg(
                        arg=settings.INPUT_NAME + settings.TEST_SUFFIX,
                        annotation=ast.Index(ast.Name(
                            id='in_schema' + settings.TEST_SUFFIX,
                            ctx=ast.Load())),
                        type_comment=None),
                    ast.arg(
                        arg=settings.OUTPUT_NAME + settings.TEST_SUFFIX,
                        annotation=ast.Index(ast.Name(
                            id='out_schema' + settings.TEST_SUFFIX,
                            ctx=ast.Load())),
                        type_comment=None)
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]),
            body=self.get_input_test_ast() + [
                make_comment("Start of query code"),
                ast.AnnAssign(
                    target=ast.Name(
                        id=settings.PASS_VAR_NAME,
                        ctx=ast.Store()
                    ),
                    annotation=ast.Name(
                        id='bool',
                        ctx=ast.Load()
                    ),
                    value=ast.Call(
                        func=ast.Name(
                            id=self.query_name,
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Name(
                                id=settings.META_NAME,
                                ctx=ast.Load()
                            ),
                            ast.Name(
                                id=settings.INPUT_NAME,
                                ctx=ast.Load()
                            ),
                            ast.Name(
                                id=settings.OUTPUT_NAME,
                                ctx=ast.Load()
                            )
                        ],
                        keywords=[]
                    ),
                    simple=1
                ),
                make_comment("End of query code")
            ] + self.get_output_test_ast() + [
                     ast.Return(
                         value=ast.Name(
                             id=settings.PASS_VAR_NAME,
                             ctx=ast.Load()
                         )
                     )
                 ],
            decorator_list=[],
            returns=ast.Name(
                id='bool',
                ctx=ast.Load()
            ),
            type_comment=None)

        header_ast = [
            self.get_in_schema_ast(),
            self.get_out_schema_ast(),
            function_ast
        ]

        code_ast = [
            function_ast
        ]

        test_header_ast = [
            self.get_in_schema_ast(test_data=True),
            self.get_out_schema_ast(test_data=True),
            test_function_ast
        ]

        test_code_ast = [
            test_function_ast
        ]

        return (header_ast, code_ast, test_header_ast, test_code_ast)
