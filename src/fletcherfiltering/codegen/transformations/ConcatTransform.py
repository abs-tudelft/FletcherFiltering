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
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from fletcherfiltering import settings
from fletcherfiltering.common import debug
from ..exceptions import *


class ConcatTransform(BaseTransform):

    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema

    def visit_FunctionCall(self, node: ast_nodes.FunctionCall) -> ast_nodes.FunctionCall:
        debug(node)
        if node.func.lower() == 'concat':
            new_params = []
            for param in node.params:
                method = 'param_' + param.__class__.__name__
                visitor = getattr(self, method, None)
                if callable(visitor):
                    new_params.extend(visitor(param))
                else:
                    raise UnsupportedArgumentTypeError()
            node.params = new_params
        return node

    def param_StringValue(self, node: ast_nodes.StringValue) -> list:
        debug(node)
        return [node, ast_nodes.IntValue(value=len(node.value))]

    def param_IntValue(self, node: ast_nodes.IntValue) -> list:
        debug(node)
        value = str(node.value)
        return [ast_nodes.StringValue(value=value), ast_nodes.IntValue(value=len(value))]

    def param_DoubleValue(self, node: ast_nodes.DoubleValue) -> list:
        debug(node)
        if int(node.value) == node.value:
            value = str(int(node.value))
        else:
            value = str(node.value)
        return [ast_nodes.StringValue(value=value), ast_nodes.IntValue(value=len(value))]

    def param_ColumnReference(self, node: ast_nodes.ColumnReference) -> list:
        debug(node)
        col = self.in_schema.field_by_name(node.id)
        assert (col is not None)
        if col.type != pa.string():
            raise UnsupportedArgumentTypeError()

        if col.type in settings.VAR_LENGTH_TYPES:
            #node.is_data_reference = True
            return [node, ast_nodes.IntermediaryReference(id=col.name + settings.LENGTH_SUFFIX)]

    def param_TrueValue(self, node: ast_nodes.TrueValue) -> list:
        debug(node)
        return [ast_nodes.StringValue(value='1'), ast_nodes.IntValue(value=1)]

    def param_FalseValue(self, node: ast_nodes.FalseValue) -> list:
        debug(node)
        return [ast_nodes.StringValue(value='0'), ast_nodes.IntValue(value=1)]

    def param_NullValue(self, node: ast_nodes.NullValue) -> list:
        debug(node)
        return [ast_nodes.StringValue(value='NULL'), ast_nodes.IntValue(value=4)]
