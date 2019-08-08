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
from typing import Union, Tuple
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from fletcherfiltering import settings
from fletcherfiltering.common import debug
from ..exceptions import *
from .helpers import grouped
import copy

class ConstantPropagationTransform(BaseTransform):

    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema
        self.skip_functions = False

    def transform(self, node, skip_functions=False):
        self.skip_functions = skip_functions
        old_node = copy.deepcopy(node)
        node = self.visit(node)
        while old_node != node:
            old_node = copy.deepcopy(node)
            node = self.visit(node)
        return node

    @staticmethod
    def make_funcprop_name(funcname: str) -> str:
        return 'funcprop_' + str(funcname).upper()

    @staticmethod
    def make_binop_name(classname: str) -> str:
        return 'binop_' + str(classname)

    @staticmethod
    def make_unop_name(classname: str) -> str:
        return 'unop_' + str(classname)

    def visit_FunctionCall(self, node: ast_nodes.FunctionCall) -> ast_nodes.FunctionCall:
        node = self.generic_visit(node)
        debug(node)
        if not self.skip_functions:
            method_name = self.make_funcprop_name(node.func)
            # Get the method from 'self'. Default to a lambda.
            method = getattr(self, method_name, lambda x: x)
            # Call the method as we return it
            return method(node)
        else:
            return node

    def visit_UnOp(self, node: ast_nodes.UnOp) -> ast_nodes.UnOp:
        node = self.generic_visit(node)
        debug(node)
        method_name = self.make_unop_name(node.op.__class__.__name__)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda x: x)
        # Call the method as we return it
        return method(node)

    def visit_BinOp(self, node: ast_nodes.BinOp) -> Union[ast_nodes.BinOp, ast_nodes.IntValue, ast_nodes.DoubleValue, ast_nodes.Reference]:
        node = self.generic_visit(node)
        debug(node)
        if node.rhs is None and node.lhs is None:
            return None
        elif node.rhs is not None and node.lhs is None:
            return node.rhs
        elif node.rhs is None and node.lhs is not None:
            return node.lhs
        elif isinstance(node.rhs,ast_nodes.Value) and isinstance(node.lhs,ast_nodes.Value):
            method_name = self.make_binop_name(node.op.__class__.__name__)
            # Get the method from 'self'. Default to a lambda.
            method = getattr(self, method_name, lambda x: x)
            # Call the method as we return it
            return method(node)
        elif isinstance(node.rhs,ast_nodes.Reference) and isinstance(node.lhs,ast_nodes.Reference):
            if isinstance(node.op, ast_nodes.BoolOperator) and node.rhs.id == node.lhs.id and node.rhs.metadata == node.lhs.metadata:
                return node.lhs
            else:
                return node
        elif (isinstance(node.rhs,ast_nodes.Reference) and isinstance(node.lhs,ast_nodes.BoolValue)) or \
                (isinstance(node.rhs,ast_nodes.BoolValue) and isinstance(node.lhs,ast_nodes.Reference)) or \
                (isinstance(node.rhs,ast_nodes.BinOp) and isinstance(node.lhs,ast_nodes.BoolValue)) or \
                (isinstance(node.rhs,ast_nodes.BoolValue) and isinstance(node.lhs,ast_nodes.BinOp)):
            if isinstance(node.op, ast_nodes.BoolOperator):
                method_name = self.make_binop_name(node.op.__class__.__name__)
                # Get the method from 'self'. Default to a lambda.
                method = getattr(self, method_name, lambda x: x)
                # Call the method as we return it
                return method(node)
            else:
                return node
        else:
            return node

    def funcprop_CONCAT(self, node: ast_nodes.FunctionCall):
        new_params = []
        current_param = -1
        for param, param_len in grouped(node.params, 2):
            if isinstance(param, ast_nodes.StringValue) and isinstance(param_len, ast_nodes.IntValue):
                if current_param > 0:
                    if isinstance(new_params[current_param - 1], ast_nodes.StringValue) and isinstance(
                            new_params[current_param], ast_nodes.IntValue):
                        new_params[current_param - 1].value += param.value
                        new_params[current_param].value += param_len.value
                        continue

            new_params.append(param)
            new_params.append(param_len)
            current_param += 2
        node.params = new_params
        return node

    def binop_MulOperator(self, node: ast_nodes.BinOp) -> Union[ast_nodes.DoubleValue, ast_nodes.IntValue]:
        types = (type(node.rhs), type(node.lhs))
        value = node.lhs.value * node.rhs.value
        if ast_nodes.DoubleValue in types:
            return ast_nodes.DoubleValue(value)

        return ast_nodes.IntValue(value)

    def binop_DivOperator(self, node: ast_nodes.BinOp) -> Union[ast_nodes.DoubleValue, ast_nodes.IntValue]:
        types = (type(node.rhs), type(node.lhs))
        value = node.lhs.value / node.rhs.value
        if ast_nodes.DoubleValue in types:
            return ast_nodes.DoubleValue(value)

        return ast_nodes.IntValue(value)

    def binop_AddOperator(self, node: ast_nodes.BinOp) -> Union[ast_nodes.DoubleValue, ast_nodes.IntValue]:
        types = (type(node.rhs), type(node.lhs))
        value = node.lhs.value + node.rhs.value
        if ast_nodes.DoubleValue in types:
            return ast_nodes.DoubleValue(value)

        return ast_nodes.IntValue(value)

    def binop_SubOperator(self, node: ast_nodes.BinOp) -> Union[ast_nodes.DoubleValue, ast_nodes.IntValue]:
        types = (type(node.rhs), type(node.lhs))
        value = node.lhs.value - node.rhs.value
        if ast_nodes.DoubleValue in types:
            return ast_nodes.DoubleValue(value)

        return ast_nodes.IntValue(value)

    def binop_LShiftOperator(self, node: ast_nodes.BinOp) -> ast_nodes.IntValue:
        value = int(node.lhs.value) << int(node.rhs.value)
        return ast_nodes.IntValue(value)

    def binop_RShiftOperator(self, node: ast_nodes.BinOp) -> ast_nodes.IntValue:
        value = int(node.lhs.value) >> int(node.rhs.value)
        return ast_nodes.IntValue(value)

    def binop_AndOperator(self, node: ast_nodes.BinOp) -> Union[ast_nodes.TrueValue, ast_nodes.FalseValue, ast_nodes.BinOp]:
        if isinstance(node.lhs, ast_nodes.BoolValue) and isinstance(node.rhs, ast_nodes.BoolValue):
            value = bool(node.lhs) and bool(node.rhs)
            return ast_nodes.TrueValue() if value else ast_nodes.FalseValue()
        elif isinstance(node.lhs, ast_nodes.BoolValue):
            value = bool(node.lhs)
            return ast_nodes.FalseValue() if not value else node.rhs  # false and x = false and true and x = x
        elif isinstance(node.rhs, ast_nodes.BoolValue):
            value = bool(node.rhs)
            return ast_nodes.FalseValue() if not value else node.lhs  # false and x = false and true and x = x
        return node

    def binop_OrOperator(self, node: ast_nodes.BinOp) -> Union[ast_nodes.TrueValue, ast_nodes.FalseValue, ast_nodes.BinOp]:
        if isinstance(node.lhs, ast_nodes.BoolValue) and isinstance(node.rhs, ast_nodes.BoolValue):
            value = bool(node.lhs) or bool(node.rhs)
            return ast_nodes.TrueValue() if value else ast_nodes.FalseValue()
        elif isinstance(node.lhs, ast_nodes.BoolValue):
            value = bool(node.lhs)
            return ast_nodes.TrueValue() if value else node.rhs  # true or x = true and false or x = x
        elif isinstance(node.rhs, ast_nodes.BoolValue):
            value = bool(node.rhs)
            return ast_nodes.TrueValue() if value else node.lhs  # true or x = true and false or x = x
        return node

    def binop_BitAndOperator(self, node: ast_nodes.BinOp) -> ast_nodes.IntValue:
        value = int(node.lhs.value) & int(node.rhs.value)
        return ast_nodes.IntValue(value)

    def binop_BitOrOperator(self, node: ast_nodes.BinOp) -> ast_nodes.IntValue:
        value = int(node.lhs.value) | int(node.rhs.value)
        return ast_nodes.IntValue(value)

    def binop_BitXorOperator(self, node: ast_nodes.BinOp) -> ast_nodes.IntValue:
        value = int(node.lhs.value) ^ int(node.rhs.value)
        return ast_nodes.IntValue(value)

    def unop_BitNotOperator(self, node: ast_nodes.UnOp) -> ast_nodes.IntValue:
        value = ~int(node.rhs.value)
        return ast_nodes.IntValue(value)

