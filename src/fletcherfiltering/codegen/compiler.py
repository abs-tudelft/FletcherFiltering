import pyarrow as pa

import typed_ast.ast3 as ast

import horast as horast

import moz_sql_parser as msp

from moz_sql_parser import ast_nodes
import os.path
import transpyle

from shutil import copyfile

from . import debug, settings

from .transformations.WhereTransform import WhereTransform
from .transformations.WildcardTransform import WildcardTransform
from .transformations.ConcatTransform import ConcatTransform
from .transformations.ConstantPropagationTransform import ConstantPropagationTransform
from .transformations.PythonASTTransform import PythonASTTransform

# These templates are all formatted, so double up curly braces.
source_header_header = """#pragma once
#if _MSC_VER && !__INTEL_COMPILER
    #include <iso646.h>
#endif
#include "hls_stream.h"
#include "hls_half.h"
#include "fletcherfiltering.h" """

source_code_header = """#include "{}.h" """

source_code_test_header = """#include "{}_test.h" 
extern "C" {{"""

source_code_test_footer = """}}"""

source_header_test_header = """#pragma once
#include "hls_stream.h"
#include "{}.h" 

extern "C" {{"""

source_header_test_footer = """}}"""


class Compiler(object):
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        self.in_schema = in_schema
        self.out_schema = out_schema
        self.where_transform = WhereTransform(self.in_schema, self.out_schema)
        self.wildcard_transform = WildcardTransform(self.in_schema, self.out_schema)
        self.constant_propagation_transform = ConstantPropagationTransform(self.in_schema, self.out_schema)
        self.concat_transform = ConcatTransform(self.in_schema, self.out_schema)
        self.python_ast_transform = PythonASTTransform(self.in_schema, self.out_schema)

        self.verify_schemas()

    def verify_schemas(self):
        for col in self.in_schema:
            if col.nullable:
                raise ValueError("Nullable columns in the input schema are not supported at this time.")
        for col in self.out_schema:
            if col.nullable:
                raise ValueError("Nullable columns in the output schema are not supported at this time.")

    def __call__(self, query_str: str, output_dir: str = '.', query_name: str = 'query',
                 include_build_system: bool = True, extra_include_dirs: str = '', extra_link_dirs: str = '',
                 extra_link_libraries: str = ''):
        assert isinstance(query_str, str)

        queries = self.parse(query_str)

        generated_files = []
        counter = 0
        for query in queries:
            current_query_name = query_name
            if len(queries) > 1:
                current_query_name += str(counter)
            header_ast, general_ast, header_test_ast, general_test_ast = self.transform(query, current_query_name)
            self.output(header_ast, general_ast, header_test_ast, general_test_ast, output_dir, current_query_name)
            generated_files.append(current_query_name)
            generated_files.append(current_query_name + settings.TEST_SUFFIX)
            counter += 1

        if include_build_system:
            source_dir = os.path.realpath(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../codegen-cpp'))

            self.copy_files(source_dir, os.path.realpath(output_dir), ['fletcherfiltering.cpp', 'fletcherfiltering.h'])

            cmake_list = "cmake_minimum_required(VERSION 3.12)\n" \
                         "project(codegen-{0})\n" \
                         "set(CMAKE_CXX_STANDARD 14)\n" \
                         "include_directories(AFTER SYSTEM {2})\n" \
                         "link_directories(AFTER SYSTEM {3})\n" \
                         "add_library(codegen-{0} SHARED fletcherfiltering.cpp {1})\n" \
                         "set_target_properties(codegen-{0} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS true)\n" \
                         "target_link_libraries(codegen-{0} {4})\n" \
                         "".format(query_name, " ".join(generated_files), extra_include_dirs, extra_link_dirs,
                                   extra_link_libraries)

            with open(os.path.join(output_dir, 'CMakeLists.txt'), 'w') as cmake_file:
                cmake_file.write(cmake_list)

    def copy_files(self, source_dir, output_dir, file_list):
        if source_dir == output_dir:
            return
        for file in file_list:
            copyfile(os.path.join(source_dir, file),
                     os.path.join(output_dir, file))

    def parse(self, query_str: str):
        return msp.parse(query_str)

    def transform(self, query: ast_nodes.Query, query_name: str):
        assert isinstance(query, ast_nodes.Query)
        query = self.where_transform.transform(query)
        query = self.wildcard_transform.transform(query)
        query = self.constant_propagation_transform.transform(query, skip_functions=True)
        query = self.concat_transform.transform(query)
        query = self.constant_propagation_transform.transform(query)

        header_ast, general_ast, header_test_ast, general_test_ast = self.python_ast_transform.transform(query,
                                                                                                         query_name=query_name)

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

        if isinstance(header_test_ast, ast.AST):
            debug(horast.dump(header_test_ast))
        elif isinstance(header_test_ast, list):
            for item in header_test_ast:
                debug(horast.dump(item))
        else:
            debug(header_test_ast)

        if isinstance(general_test_ast, ast.AST):
            debug(horast.dump(general_test_ast))
        elif isinstance(general_test_ast, list):
            for item in general_test_ast:
                debug(horast.dump(item))
        else:
            debug(general_test_ast)

        return header_ast, general_ast, header_test_ast, general_test_ast

    def output(self, header_ast: ast.AST, general_ast: ast.AST, header_test_ast: ast.AST, general_test_ast: ast.AST,
               output_dir: str, query_name: str):
        to_language = transpyle.Language.find('C++')
        unparser = transpyle.Unparser.find(to_language)(headers=False)
        unparser_header = transpyle.Unparser.find(to_language)(headers=True)

        cpp_code = unparser.unparse(general_ast)
        cpp_test_code = unparser.unparse(general_test_ast)
        cpp_test_header = unparser_header.unparse(header_test_ast)
        cpp_header = unparser_header.unparse(header_ast)

        debug("C++ header:")
        debug(cpp_header)
        debug("C++ code:")
        debug(cpp_code)
        debug("C++ test header:")
        debug(cpp_test_header)
        debug("C++ test code:")
        debug(cpp_test_code)

        with open(os.path.join(output_dir, query_name + ".cpp"), 'w') as source_file:
            source_file.write(source_code_header.format(query_name))
            source_file.write(str(cpp_code))

        with open(os.path.join(output_dir, query_name + settings.TEST_SUFFIX + ".cpp"), 'w') as source_file:
            source_file.write(source_code_test_header.format(query_name))
            source_file.write(str(cpp_test_code))
            source_file.write(source_code_test_footer.format(query_name))

        with open(os.path.join(output_dir, query_name + ".h"), 'w') as header_file:
            header_file.write(source_header_header.format(query_name))
            header_file.write(str(cpp_header))

        with open(os.path.join(output_dir, query_name + settings.TEST_SUFFIX + ".h"), 'w') as header_file:
            header_file.write(source_header_test_header.format(query_name))
            header_file.write(str(cpp_test_header))
            header_file.write(source_header_test_footer.format(query_name))
