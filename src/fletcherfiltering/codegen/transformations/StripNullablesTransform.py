import typed_ast.ast3 as ast
import horast
from typing import Union, Tuple
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from .. import debug, settings
from .helpers import make_comment
from .helpers.ArrowTypeResolver import ArrowTypeResolver
from .helpers.FunctionResolver import FunctionResolver, PrePostAST
from ..exceptions import *


class StripNullablesTransform(BaseTransform):
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema

    def transform(self, node):
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

    def create_tree_from_flat_list(self, node_list, index=1, value=None):
        if index >= len(node_list) or node_list[index] is None:
            return self.visit(value)
        d = node_list[index]
        l = index * 2
        r = l + 1
        tree = ast_nodes.BinOp(op=ast_nodes.AndOperator(),
                               lhs=self.create_tree_from_flat_list(node_list, l, d),
                               rhs=self.create_tree_from_flat_list(node_list, r, d))
        return tree

    def visit_ColumnReference(self, node: ast_nodes.ColumnReference) -> ast_nodes.ColumnReference:
        #node.is_value_reference = False
        node.is_valid_reference = True
        if not node.id.endswith(settings.LENGTH_SUFFIX) and self.is_varlength_col(node.id):
            node.id += settings.LENGTH_SUFFIX
        return node

    def visit_IntermediaryReference(self, node: ast_nodes.IntermediaryReference) -> ast_nodes.IntermediaryReference:
        #node.is_value_reference = False
        node.is_valid_reference = True
        if not node.id.endswith(settings.LENGTH_SUFFIX) and self.is_varlength_col(node.id):
            node.id += settings.LENGTH_SUFFIX
        return node

    def visit_TrueValue(self, node: ast_nodes.TrueValue) -> ast_nodes.TrueValue:
        return node

    def visit_FalseValue(self, node: ast_nodes.FalseValue) -> ast_nodes.FalseValue:
        return node

    def visit_NullValue(self, node: ast_nodes.NullValue) -> ast_nodes.FalseValue:
        return ast_nodes.FalseValue()

    def visit_StringValue(self, node: ast_nodes.StringValue) -> ast_nodes.TrueValue:
        return ast_nodes.TrueValue()

    def visit_IntValue(self, node: ast_nodes.IntValue) -> ast_nodes.TrueValue:
        return ast_nodes.TrueValue()

    def visit_DoubleValue(self, node: ast_nodes.DoubleValue) -> ast_nodes.TrueValue:
        return ast_nodes.TrueValue()

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
        return self.create_tree_from_flat_list(node.params)

    def visit_SelectColumn(self, node: ast_nodes.SelectColumn) -> list:
        return self.visit(node.value)
