from typing import Union

import typed_ast.ast3 as ast
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .BaseTransform import BaseTransform
from .. import debug,settings
from ..exceptions import *


class WildcardTransform(BaseTransform):

    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        super().__init__()
        self.in_schema = in_schema
        self.out_schema = out_schema

    # TODO log the ignored TableReference
    def visit_SelectColumn(self, node: ast_nodes.SelectColumn) -> Union[list, ast_nodes.SelectColumn]:
        debug(node)
        if isinstance(node.value, ast_nodes.ColumnReference):
            if isinstance(node.value.id, ast_nodes.Wildcard):
                cols = []
                for col in self.in_schema:
                    cols.append(
                        ast_nodes.SelectColumn(
                            ast_nodes.ColumnReference(
                                id=col.name
                            )
                        )
                    )
                return cols
        return node
