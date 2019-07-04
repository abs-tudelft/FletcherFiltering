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
from .. import debug, settings
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
