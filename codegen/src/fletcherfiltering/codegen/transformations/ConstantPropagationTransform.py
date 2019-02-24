import typed_ast.ast3 as ast
from typing import Union, Tuple
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from .. import debug, settings
from ..exceptions import *
from .helpers import grouped


class ConstantPropagationTransform(BaseTransform):

    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema
        self.skip_functions = False

    def transform(self, node, skip_functions=False):
        self.skip_functions = skip_functions
        return self.visit(node)

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

    def visit_BinOp(self, node: ast_nodes.BinOp) -> Union[ast_nodes.BinOp, ast_nodes.IntValue, ast_nodes.DoubleValue]:
        node = self.generic_visit(node)
        debug(node)
        if isinstance(node.rhs,ast_nodes.Value) and isinstance(node.lhs,ast_nodes.Value):
            method_name = self.make_binop_name(node.op.__class__.__name__)
            # Get the method from 'self'. Default to a lambda.
            method = getattr(self, method_name, lambda x: x)
            # Call the method as we return it
            return method(node)
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
