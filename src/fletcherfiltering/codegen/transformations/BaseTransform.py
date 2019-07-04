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
