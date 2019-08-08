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
from typing import Union, Tuple, Callable
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from fletcherfiltering import settings
from fletcherfiltering.common import debug
from .helpers import ReferenceMetadata
from .helpers import make_comment
from .helpers.ArrowTypeResolver import ArrowTypeResolver
from .helpers.FunctionResolver import FunctionResolver, PrePostAST
from ..exceptions import *


class AuxSignalTransform(BaseTransform):
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema
        self.signal = 'valid'
        self.only_nullables = False
        self.merge_op = ast_nodes.AndOperator
        self.default_value = ast_nodes.TrueValue

    def transform(self, node, signal: str = 'valid', only_nullables: bool = False, merge_op: Callable = ast_nodes.AndOperator, default_value: Callable = ast_nodes.TrueValue):
        self.signal = signal
        self.only_nullables = only_nullables
        self.merge_op = merge_op
        self.default_value = default_value
        return self.visit(node)

    def is_input_col(self, name: str):
        if self.in_schema.field_by_name(name):
            return True
        else:
            return False

    def must_apply_valid_reference(self, node):
        if isinstance(node, ast_nodes.ColumnReference):
            col_name = node.id
            type = self.in_schema.field_by_name(col_name)
            if type.nullable and type.type not in settings.VAR_LENGTH_TYPES:
                return True

        elif isinstance(node, ast_nodes.IntermediaryReference):
            col_name = node.id
            length_stream = False
            if col_name.endswith(settings.LENGTH_SUFFIX):
                col_name = col_name[0:-len(settings.LENGTH_SUFFIX)]
                length_stream = True

            type = self.in_schema.field_by_name(col_name)
            if type.nullable and (type.type not in settings.VAR_LENGTH_TYPES or length_stream):
                return True
        return False

    def is_nullable_col(self, name: str):
        return self.in_schema.field_by_name(name).nullable

    def is_varlength_col(self, name: str):
        return self.in_schema.field_by_name(name).type in settings.VAR_LENGTH_TYPES

    def create_tree_from_flat_list(self, node_list):
        if len(node_list) == 1:
            return node_list[0]
        if len(node_list) == 2:
            left = [node_list[0]]
            right = [node_list[1]]
        else:
            left = node_list[:2]
            right = node_list[2:]

        tree = ast_nodes.BinOp(op=self.merge_op(),
                               lhs=self.create_tree_from_flat_list(left),
                               rhs=self.create_tree_from_flat_list(right))
        return tree

    def visit_ColumnReference(self, node: ast_nodes.ColumnReference) -> Union[ast_nodes.ColumnReference, None]:
        if node.metadata is None:
            node.metadata = ReferenceMetadata(signal=self.signal)
        elif isinstance(node.metadata, ReferenceMetadata):
            node.metadata.signal = self.signal
        else:
            raise ValueError('Reference has unsupported metadata. {}'.format(node.metadata))

        if not self.is_nullable_col(node.id) and self.only_nullables:
            return None
        if not node.id.endswith(settings.LENGTH_SUFFIX) and self.is_varlength_col(node.id):
            node.id += settings.LENGTH_SUFFIX
        return node

    def visit_IntermediaryReference(self, node: ast_nodes.IntermediaryReference) -> Union[ast_nodes.IntermediaryReference, None]:
        if node.metadata is None:
            node.metadata = ReferenceMetadata(signal=self.signal)
        elif isinstance(node.metadata, ReferenceMetadata):
            node.metadata.signal = self.signal
        else:
            raise ValueError('Reference has unsupported metadata.')
        if node.id.endswith(settings.LENGTH_SUFFIX):
            if not self.is_nullable_col(node.id[:-len(settings.LENGTH_SUFFIX)]) and self.only_nullables:
                return None
        return node

    def visit_TrueValue(self, node: ast_nodes.TrueValue) -> ast_nodes.TrueValue:
        return node

    def visit_FalseValue(self, node: ast_nodes.FalseValue) -> ast_nodes.FalseValue:
        return node

    def visit_NullValue(self, node: ast_nodes.NullValue) -> ast_nodes.BoolValue:
        if self.signal == 'valid':
            return ast_nodes.FalseValue()
        return self.default_value()

    def visit_StringValue(self, node: ast_nodes.StringValue) -> ast_nodes.BoolValue:
        return self.default_value()

    def visit_IntValue(self, node: ast_nodes.IntValue) -> ast_nodes.BoolValue:
        return self.default_value()

    def visit_DoubleValue(self, node: ast_nodes.DoubleValue) -> ast_nodes.BoolValue:
        return self.default_value()

    def visit_CompOp(self, node: ast_nodes.CompOp) -> ast_nodes.BinOp:
        debug(node)
        return ast_nodes.BinOp(op=ast_nodes.AndOperator(),
                               lhs=self.visit(node.lhs),
                               rhs=self.visit(node.rhs))

    def visit_BinOp(self, node: ast_nodes.BinOp) -> ast_nodes.BinOp:
        debug(node)
        return ast_nodes.BinOp(op=ast_nodes.AndOperator(),
                               lhs=self.visit(node.lhs),
                               rhs=self.visit(node.rhs))

    def visit_UnOp(self, node: ast_nodes.UnOp) -> ast_nodes.BoolValue:
        debug(node)
        return self.visit(self.visit(node.rhs))

    def visit_FunctionCall(self, node: ast_nodes.FunctionCall) -> ast_nodes.BinOp:
        def sort_func(param):
            if isinstance(param, ast_nodes.Reference):
                return param.id
            else:
                return ""
        node.params.sort(key=sort_func, reverse=False)
        node.params = self.visit(node.params)
        return self.create_tree_from_flat_list(node.params)

    def visit_SelectColumn(self, node: ast_nodes.SelectColumn) -> list:
        return self.visit(node.value)
