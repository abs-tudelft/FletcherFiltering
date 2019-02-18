import typed_ast.ast3 as ast
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from .. import debug
from ..exceptions import *


class WhereTransform(BaseTransform):

    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema

    def visit_Query(self, node: ast_nodes.Query) -> ast_nodes.Query:
        debug(node)
        if isinstance(node.q,ast_nodes.ASTNode):
            if not isinstance(node.q, ast_nodes.Where):
                node.q = [node.q, ast_nodes.Where(condition=ast_nodes.TrueValue())]
        elif isinstance(node.q, list):
            type_list = map(type, node.q)
            if ast_nodes.Where not in type_list:
                node.q.append(ast_nodes.Where(condition=ast_nodes.TrueValue()))
        return node
