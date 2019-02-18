import pyarrow as pa

import typed_ast.ast3 as ast

import horast as horast

import moz_sql_parser as msp

from moz_sql_parser import ast_nodes
import os.path
import transpyle

from . import debug

from .transformations.WhereTransform import WhereTransform
from .transformations.ConcatTransform import ConcatTransform
from .transformations.ConstantPropagationTransform import ConstantPropagationTransform
from .transformations.PythonASTTransform import PythonASTTransform

source_header_header = """#pragma once
#include "hls_stream.h"
#include "fletcherfiltering.h" """

source_code_header = """#include "query.h" """


class Compiler(object):
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        self.in_schema = in_schema
        self.out_schema = out_schema
        self.where_transform = WhereTransform(self.in_schema, self.out_schema)
        self.constant_propagation_transform = ConstantPropagationTransform(self.in_schema, self.out_schema)
        self.concat_transform = ConcatTransform(self.in_schema, self.out_schema)
        self.python_ast_transform = PythonASTTransform(self.in_schema, self.out_schema)

    def __call__(self, query_str: str, output_dir: str = '.', query_name: str = 'query'):
        assert isinstance(query_str, str)

        queries = self.parse(query_str)

        counter = 0
        for query in queries:
            current_query_name = query_name
            if len(queries) > 1:
                current_query_name += str(counter)
            header_ast, general_ast = self.transform(query, current_query_name)
            self.output(header_ast, general_ast, output_dir, current_query_name)
            counter += 1

    def parse(self, query_str: str):
        return msp.parse(query_str)

    def transform(self, query: ast_nodes.Query, query_name: str):
        assert isinstance(query, ast_nodes.Query)
        query = self.where_transform.transform(query)
        query = self.constant_propagation_transform.transform(query, skip_functions=True)
        query = self.concat_transform.transform(query)
        query = self.constant_propagation_transform.transform(query)

        header_ast, general_ast = self.python_ast_transform.transform(query, query_name=query_name)

        if isinstance(header_ast, ast.AST):
            debug(horast.dump(header_ast))
        elif isinstance(header_ast, list):
            for item in header_ast:
                debug(horast.dump(item))
        else:
            debug(header_ast)

        if isinstance(general_ast, ast.AST):
            debug(horast.dump(general_ast))
        elif isinstance(general_ast, list):
            for item in general_ast:
                debug(horast.dump(item))
        else:
            debug(general_ast)

        return header_ast, general_ast

    def output(self, header_ast: ast.AST, general_ast: ast.AST, output_dir: str, query_name: str):
        to_language = transpyle.Language.find('C++')
        unparser = transpyle.Unparser.find(to_language)(headers=False)
        unparser_header = transpyle.Unparser.find(to_language)(headers=True)

        cpp_code = unparser.unparse(general_ast)
        cpp_header = unparser_header.unparse(header_ast)

        debug("C++ header:")
        debug(cpp_header)
        debug("C++ code:")
        debug(cpp_code)

        with open(os.path.join(output_dir, query_name + ".cpp"), 'w') as source_file:
            source_file.write(source_code_header)
            source_file.write(str(cpp_code))

        with open(os.path.join(output_dir, query_name + ".h"), 'w') as header_file:
            header_file.write(source_header_header)
            header_file.write(str(cpp_header))
