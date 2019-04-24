import pyarrow as pa

import typed_ast.ast3 as ast

import horast as horast

import moz_sql_parser as msp

import string

from pathlib import Path, PurePath
from typing import List

from moz_sql_parser import ast_nodes
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

        self.template_path = Path(__file__).resolve().parent / 'templates'

    def verify_schemas(self):
        for col in self.in_schema:
            if col.nullable:
                raise ValueError("Nullable columns in the input schema are not supported at this time.")
        for col in self.out_schema:
            if col.nullable:
                raise ValueError("Nullable columns in the output schema are not supported at this time.")

    def __call__(self, query_str: str, output_dir: Path = Path('.'), query_name: str = 'query',
                 include_build_system: bool = True, include_test_system: bool = True,
                 extra_include_dirs: List[PurePath] = '',
                 extra_link_dirs: List[PurePath] = '',
                 extra_link_libraries: List[str] = '', part_name: str = 'xa7a12tcsg325-1q'):
        assert isinstance(query_str, str)

        queries = self.parse(query_str)

        generated_files = []
        counter = 0
        for query in queries:
            current_query_name = query_name
            if len(queries) > 1:
                current_query_name += str(counter)
            header_ast, general_ast, header_test_ast, general_test_ast = self.transform(query, current_query_name)
            self.output(header_ast, general_ast, header_test_ast, general_test_ast, output_dir, current_query_name,
                        include_test_system=include_test_system)
            generated_files.append(current_query_name + '.cpp')
            generated_files.append(current_query_name + settings.TEST_SUFFIX + '.cpp')
            counter += 1

        tb_delete = 'delete[] out.{0};'

        tb_new = 'out.{0} = new char[{1}];'

        out_str_columns = [x.name for x in self.out_schema if x.type == pa.string()]

        template_data = {
            'query_name': query_name,
            'generated_files': " ".join(generated_files),
            'extra_include_dirs': ' '.join([d.as_posix() for d in extra_include_dirs]),
            'extra_link_dirs': ' '.join([d.as_posix() for d in extra_link_dirs]),
            'extra_link_libraries': ' '.join(extra_link_libraries),
            'test_suffix': settings.TEST_SUFFIX,
            'data_suffix': settings.DATA_SUFFIX,
            'testbench_suffix': settings.TESTBENCH_SUFFIX,
            'part_name': part_name,
            'out_columns_tb_delete': "\n    ".join([tb_delete.format(x) for x in out_str_columns]),
            'out_columns_tb_new': "\n    ".join([tb_new.format(x, settings.VAR_LENGTH + 1) for x in out_str_columns]),
        }

        if include_build_system:
            self.copy_files(self.template_path, output_dir.resolve(),
                            [Path('fletcherfiltering.cpp'), Path('fletcherfiltering.h')])

            with open(self.template_path / 'template.CMakeLists.txt', 'r') as template_file:
                cmake_list = string.Template(template_file.read())
                with open(output_dir / Path('CMakeLists.txt'), 'w') as cmake_file:
                    cmake_file.write(cmake_list.safe_substitute(template_data))

        if include_test_system:
            with open(self.template_path / 'template.run_complete_hls.tcl', 'r') as template_file:
                hls_tcl = string.Template(template_file.read())
                with open(output_dir / Path('run_complete_hls.tcl'), 'w') as hls_tcl_file:
                    hls_tcl_file.write(hls_tcl.safe_substitute(template_data))

            with open(self.template_path / 'template.testbench.cpp', 'r') as template_file:
                teshbench_cpp = string.Template(template_file.read())
                with open(output_dir / Path('{0}{1}.cpp'.format(query_name, settings.TESTBENCH_SUFFIX)),
                          'w') as teshbench_cpp_file:
                    teshbench_cpp_file.write(teshbench_cpp.safe_substitute(template_data))

            with open(self.template_path / 'template.data.h', 'r') as template_file:
                data_cpp = string.Template(template_file.read())
                with open(output_dir / Path('{0}{1}.h'.format(query_name, settings.DATA_SUFFIX)),
                          'w') as data_cpp_file:
                    data_cpp_file.write(data_cpp.safe_substitute(template_data))

    def copy_files(self, source_dir: PurePath, output_dir: PurePath, file_list: List[Path]):
        if source_dir == output_dir:
            return
        for file in file_list:
            copyfile(str(source_dir / file),
                     str(output_dir / file))

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
               output_dir: PurePath, query_name: str, include_test_system: bool = True):
        to_language = transpyle.Language.find('C++')
        unparser = transpyle.Unparser.find(to_language)(headers=False)
        unparser_header = transpyle.Unparser.find(to_language)(headers=True)

        cpp_code = unparser.unparse(general_ast)
        cpp_header = unparser_header.unparse(header_ast)
        debug("C++ header:")
        debug(cpp_header)
        debug("C++ code:")
        debug(cpp_code)

        if include_test_system:
            cpp_test_code = unparser.unparse(general_test_ast)
            cpp_test_header = unparser_header.unparse(header_test_ast)
            debug("C++ test header:")
            debug(cpp_test_header)
            debug("C++ test code:")
            debug(cpp_test_code)

        with open(output_dir / Path(query_name + ".cpp"), 'w') as source_file:
            source_file.write(source_code_header.format(query_name))
            source_file.write(str(cpp_code))

        with open(output_dir / Path(query_name + ".h"), 'w') as header_file:
            header_file.write(source_header_header.format(query_name))
            header_file.write(str(cpp_header))

        if include_test_system:
            with open(output_dir / Path(query_name + settings.TEST_SUFFIX + ".h"), 'w') as header_file:
                header_file.write(source_header_test_header.format(query_name))
                header_file.write(str(cpp_test_header))
                header_file.write(source_header_test_footer.format(query_name))
            with open(output_dir / Path(query_name + settings.TEST_SUFFIX + ".cpp"), 'w') as source_file:
                source_file.write(source_code_test_header.format(query_name))
                source_file.write(str(cpp_test_code))
                source_file.write(source_code_test_footer.format(query_name))
