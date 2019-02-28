import pyarrow as pa

import typed_ast.ast3 as ast

import horast as horast

import moz_sql_parser as msp

from moz_sql_parser import ast_nodes

import transpyle

from fletcherfiltering.codegen.transformations.WhereTransform import WhereTransform
from fletcherfiltering.codegen.transformations.ConcatTransform import ConcatTransform
from fletcherfiltering.codegen.transformations.ConstantPropagationTransform import ConstantPropagationTransform
from fletcherfiltering.codegen.transformations.PythonASTTransform import PythonASTTransform

STRING_LEN = 255

global_unique_counter = 0

source_header_header = """#pragma once
#include "hls_stream.h"
#include "fletcherfiltering.h" """

source_code_header = """#include "query.h" """

if __name__ == "__main__":
    in_schema = pa.read_schema("../schema-test/in_schema.fbs")
    out_schema = pa.read_schema("../schema-test/out_schema.fbs")

    in_col_reg = {}
    out_col_reg = {}

    obj = msp.parse("select (16 >> 4) as int1, CONCAT(string1,1<<4,'NULL') as concat, CONCAT('123456',string1,True,False) as concat2 FROM a")

    # Grab the first query in the result.
    query = obj[0]
    print(query)

    assert isinstance(query, ast_nodes.Query)
    where_transform = WhereTransform(in_schema, out_schema)
    constant_propagation_transform_first = ConstantPropagationTransform(in_schema, out_schema, True)
    concat_transform = ConcatTransform(in_schema, out_schema)
    constant_propagation_transform_second = ConstantPropagationTransform(in_schema, out_schema)
    transform = PythonASTTransform(in_schema, out_schema)

    query = where_transform.visit(query)
    query = constant_propagation_transform_first.visit(query)
    query = concat_transform.visit(query)
    query = constant_propagation_transform_second.visit(query)

    print(query)

    header_ast, general_ast = transform.visit(query)

    if isinstance(header_ast, ast.AST):
        print(horast.dump(header_ast))
    elif isinstance(header_ast, list):
        for item in header_ast:
            print(horast.dump(item))
    else:
        print(header_ast)

    if isinstance(general_ast, ast.AST):
        print(horast.dump(general_ast))
    elif isinstance(general_ast, list):
        for item in general_ast:
            print(horast.dump(item))
    else:
        print(general_ast)

    to_language = transpyle.Language.find('C++')
    unparser = transpyle.Unparser.find(to_language)(headers=False)
    unparser_header = transpyle.Unparser.find(to_language)(headers=True)

    cpp_code = unparser.unparse(general_ast)
    cpp_header = unparser_header.unparse(header_ast)
    print("C++ header:")
    print(cpp_header)
    print("C++ code:")
    print(cpp_code)

    with open("../../codegen-cpp/query.cpp", 'w') as source_file:
        source_file.write(source_code_header)
        source_file.write(str(cpp_code))

    with open("../../codegen-cpp/query.h", 'w') as header_file:
        header_file.write(source_header_header)
        header_file.write(str(cpp_header))

    # reverseLevelOrder(obj['where'])
