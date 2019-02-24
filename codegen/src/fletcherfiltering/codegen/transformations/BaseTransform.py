import typed_ast.ast3 as ast
from moz_sql_parser import ast_nodes
import pyarrow as pa
from .. import debug
from .. import settings

class BaseTransform(ast.NodeTransformer):

    def __init__(self):
        super().__init__()

    def visit(self, node):
        if node is None:
            debug('None')
            return None
        debug(node)
        return super().visit(node)


    def transform(self, node):
        return self.visit(node)

#region General
    def visit_(self, node):
        """Transform ."""
        debug(node)
        # raise NotImplementedError('{} cannot be processed'.format(node))
        return

    def visit_list(self, node):
        """Transform list."""
        debug(node)
        new_values = []
        for value in node:
            if isinstance(value, ast_nodes.ASTNode):
                value = self.visit(value)
                if value is None:
                    continue
                elif not isinstance(value, ast.AST):
                    new_values.extend(value)
                    continue
            new_values.append(value)
        node[:] = new_values
        return node

    def generic_visit(self, node):
        debug(node)
        super().generic_visit(node)
        return node
#endregion
