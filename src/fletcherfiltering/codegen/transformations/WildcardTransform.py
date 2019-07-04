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
