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

import pyarrow as pa

import typed_ast.ast3 as ast

import horast as horast

import moz_sql_parser as msp

import string
import os
from pathlib import Path, PurePath
from typing import List

from moz_sql_parser import ast_nodes
import transpyle

from shutil import copyfile

from fletcherfiltering import settings
from fletcherfiltering.common import debug

from .transformations.WhereTransform import WhereTransform
from .transformations.WildcardTransform import WildcardTransform
from .transformations.ConcatTransform import ConcatTransform
from .transformations.ConstantPropagationTransform import ConstantPropagationTransform
from .transformations.PythonASTTransform import PythonASTTransform

from .exceptions import MetaLengthColumnError, FletchgenError, VivadoHLSError

from ..common.helpers.process_runner import ProcessRunner, VivadoHLSProcessRunner


from collections import namedtuple

import platform

# These templates are all formatted, so double up curly braces.
source_header_header = """#pragma once
#if _MSC_VER && !__INTEL_COMPILER
    #include <iso646.h>
#endif
#include "hls_stream.h"
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

TemplateData = namedtuple('TemplateData', ['source', 'destination'])


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
        pass

    def __call__(self, query_str: str, output_dir: Path = Path('.'), query_name: str = 'query',
                 include_build_system: bool = True, include_test_system: bool = True,
                 include_fletcher_wrapper: bool = True,
                 run_fletchgen_in_docker: bool = False,
                 include_snap_project: bool = True,
                 run_vivado_hls: bool = True,
                 meta_length_source: str = 'pkid',
                 extra_include_dirs: List[PurePath] = '',
                 hls_include_dirs: List[PurePath] = '',
                 extra_link_dirs: List[PurePath] = '',
                 extra_link_libraries: List[str] = '', part_name: str = settings.PART_NAME):
        assert isinstance(query_str, str)

        queries = self.parse(query_str)

        if len(queries):
            if not output_dir.exists():
                output_dir.mkdir(parents=True)

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

        tb_new = 'out.{0} = new {2}[{1}];'

        out_str_columns = [x.name if not x.nullable else x.name + '.data' for x in self.out_schema if
                           x.type == pa.string()]

        template_data = {
            'VAR_LENGTH': settings.VAR_LENGTH,
            'query_name': query_name,
            'generated_files': " ".join(generated_files),
            'extra_include_dirs': ' '.join([d.as_posix() for d in extra_include_dirs]),
            'hls_include_dirs': ' '.join(['-I' + d.as_posix() for d in hls_include_dirs]),
            'extra_link_dirs': ' '.join([d.as_posix() for d in extra_link_dirs]),
            'extra_link_libraries': ' '.join(extra_link_libraries),
            'test_suffix': settings.TEST_SUFFIX,
            'data_suffix': settings.DATA_SUFFIX,
            'testbench_suffix': settings.TESTBENCH_SUFFIX,
            'part_name': part_name,
            'out_columns_tb_delete': "\n    ".join([tb_delete.format(x) for x in out_str_columns]),
            'out_columns_tb_new': "\n    ".join(
                [tb_new.format(x, settings.VAR_LENGTH + 1, settings.STRING_BASE_TYPE_TEST) for x in out_str_columns]),
        }

        build_system_files = [
            TemplateData(self.template_path / Path('template.fletcherfiltering.cpp'),
                         output_dir / Path('fletcherfiltering.cpp')),
            TemplateData(self.template_path / Path('template.fletcherfiltering.h'),
                         output_dir / Path('fletcherfiltering.h')),
            TemplateData(self.template_path / Path('template.CMakeLists.txt'),
                         output_dir / Path('CMakeLists.txt')),
        ]

        test_system_files = [
            TemplateData(self.template_path / Path('template.hls_run_complete.tcl'),
                         output_dir / Path('hls_run_complete.tcl')),
            TemplateData(self.template_path / Path('template.hls_build_ip_only.tcl'),
                         output_dir / Path('hls_build_ip_only.tcl')),
            TemplateData(self.template_path / Path('template.testbench.cpp'),
                         output_dir / Path('{0}{1}.cpp'.format(query_name, settings.TESTBENCH_SUFFIX)))
        ]

        snap_output_dir = output_dir / '{0}SnapAction'.format(query_name)

        snap_project_files = [
            TemplateData(self.template_path / Path('template.snap_main.Makefile'),
                         snap_output_dir / 'Makefile'),
            TemplateData(self.template_path / Path('template.snap_sw.Makefile'),
                         snap_output_dir / 'sw' / 'Makefile'),
            TemplateData(self.template_path / Path('template.snap_hw.Makefile'),
                         snap_output_dir / 'hw' / 'Makefile'),
            TemplateData(self.template_path / Path('template.snap_action_wrapper.vhd'),
                         snap_output_dir / 'hw' / 'action_wrapper.vhd'),
            TemplateData(self.template_path / Path('template.snap_action_fletcher.vhd'),
                         snap_output_dir / 'hw' / 'action_fletcher.vhd')
        ]

        fletcher_wrapper_output_dir = output_dir / 'fletcher'

        if include_snap_project:
            fletcher_wrapper_output_dir = snap_output_dir / 'hw'

        fletcher_wrapper_file = TemplateData(self.template_path / Path('template.wrapper_architecture.vhd.j2'),
                                             fletcher_wrapper_output_dir / Path(
                                                 '{0}_wrapper_architecture.vhdt'.format(query_name)))

        if settings.OVERWRITE_DATA:
            test_system_files.append(TemplateData(self.template_path / Path('template.data.h'),
                                                  output_dir / Path(
                                                      '{0}{1}.h'.format(query_name, settings.DATA_SUFFIX))))

        if include_build_system:
            for file in build_system_files:
                with open(file.source, 'r') as template_file:
                    output_data = string.Template(template_file.read())
                    with open(file.destination, 'w') as output_file:
                        output_file.write(output_data.safe_substitute(template_data))

            # Add metadata for fletchgen
            self.in_schema.add_metadata({'fletcher_mode': 'read', 'fletcher_name': settings.INPUT_NAME})
            self.out_schema.add_metadata({'fletcher_mode': 'write', 'fletcher_name': settings.OUTPUT_NAME})
            with open((output_dir / "{}.fbs".format(settings.INPUT_NAME)), 'wb') as file:
                s_serialized = self.in_schema.serialize()
                file.write(s_serialized)

            with open((output_dir / "{}.fbs".format(settings.OUTPUT_NAME)), 'wb') as file:
                s_serialized = self.out_schema.serialize()
                file.write(s_serialized)

        if include_test_system:
            for file in test_system_files:
                with open(file.source, 'r') as template_file:
                    output_data = string.Template(template_file.read())
                    with open(file.destination, 'w') as output_file:
                        output_file.write(output_data.safe_substitute(template_data))

        if run_vivado_hls:
            if platform.system() == 'Darwin':
                raise VivadoHLSError("Vivado is not supported on macOS.")

            if settings.VIVADO_BIN_DIR == '':
                raise VivadoHLSError("No Vivado install configured.")

            vivado_env = os.environ.copy()
            vivado_env["PATH"] = str(settings.VIVADO_BIN_DIR) + os.pathsep + vivado_env["PATH"]
            vivado_env["XILINX_VIVADO"] = str(settings.VIVADO_DIR)

            vivado_printer = lambda val: print("Vivado HLS:", val)

            result, sim_result = VivadoHLSProcessRunner(vivado_printer,
                                                        [str(settings.VIVADO_HLS_EXEC), '-f',
                                                         str((
                                                                         output_dir / 'hls_build_ip_only.tcl').resolve())],
                                                        shell=False, cwd=str(output_dir),
                                                        env=vivado_env)

            if result != 0:
                raise VivadoHLSError("Failed to run Vivado. Exited with code {}.".format(result))

        if include_snap_project:
            if not snap_output_dir.exists():
                snap_output_dir.mkdir(parents=True)
            for file in snap_project_files:
                if not file.destination.parent.exists():
                    file.destination.parent.mkdir(parents=True)

                copyfile(str(file.source),
                         str(file.destination))
            hls_ip_link_path = snap_output_dir / 'hw' / 'hls_ip'
            if not hls_ip_link_path.exists() and not hls_ip_link_path.is_symlink():
                hls_ip_path = output_dir / query_name / 'automated_tests' / 'impl' / 'ip' / 'hdl'
                if hls_ip_path.exists() and hls_ip_path.is_dir():
                    hls_ip_link_path.symlink_to(hls_ip_path.resolve(), target_is_directory=True)
            fletcher_link_path = snap_output_dir / 'hw' / 'fletcher'
            if not fletcher_link_path.exists() and not fletcher_link_path.is_symlink():
                fletcher_hardware_path = settings.FLETCHER_DIR / 'hardware'
                if fletcher_hardware_path.exists() and fletcher_hardware_path.is_dir():
                    fletcher_link_path.symlink_to(fletcher_hardware_path.resolve(), target_is_directory=True)

        if include_fletcher_wrapper:
            if not fletcher_wrapper_output_dir.exists():
                fletcher_wrapper_output_dir.mkdir(parents=True)

            from .kernel_wrapper_generator import generate_kernel_wrapper

            if self.in_schema.get_field_index(meta_length_source) < 0:
                raise MetaLengthColumnError(
                    "Column \'{}\' for meta length source does not exist in the input schema.".format(
                        meta_length_source))

            generate_kernel_wrapper(fletcher_wrapper_file, self.in_schema, self.out_schema, query_name,
                                    meta_length_source)

            fletcher_kernel_path = fletcher_wrapper_output_dir / 'vhdl' / 'Fletcher{}.vhd'.format(query_name)

            # Bug in fletchgen for not respecting the force flag:
            if fletcher_kernel_path.exists():
                fletcher_kernel_path.unlink()

            # Bug in fletchgen for not existing srec files:
            if not (output_dir / "{}{}.srec".format(query_name, settings.DATA_SUFFIX)).resolve().exists():
                (output_dir / "{}{}.srec".format(query_name, settings.DATA_SUFFIX)).resolve().touch()

            if run_fletchgen_in_docker:
                command_line = ['docker', 'run', '--rm', '-v', '{}:/source'.format(output_dir.resolve()), '-v',
                                '{}:/output'.format(fletcher_wrapper_output_dir.resolve()),
                                '-t', 'fletchgen:develop',
                                '-o', '/output', '-i', "/source/{}.fbs".format(settings.INPUT_NAME),
                                "/source/{}.fbs".format(settings.OUTPUT_NAME), '-l', 'vhdl', '--axi', '--sim',
                                '-r', "/source/{}{}.rb".format(query_name, settings.DATA_SUFFIX), '-s',
                                "/source/{}{}.srec".format(query_name, settings.DATA_SUFFIX), '--force', '-n',
                                'Fletcher{}'.format(query_name)]
            else:
                command_line = ['fletchgen', '-o', str(fletcher_wrapper_output_dir.resolve()), '-i',
                                str((output_dir / "{}.fbs".format(settings.INPUT_NAME)).resolve()),
                                str((output_dir / "{}.fbs".format(settings.OUTPUT_NAME)).resolve()), '-l', 'vhdl', '--axi', '--sim',
                                '-r', str((output_dir / "{}{}.rb".format(query_name, settings.DATA_SUFFIX)).resolve()), '-s',
                                str((output_dir / "{}{}.srec".format(query_name, settings.DATA_SUFFIX)).resolve()), '--force', '-n',
                                'Fletcher{}'.format(query_name)]
            debug("COMMAND: {}".format(" ".join(command_line)))
            fletchgen_printer = lambda val: print("Fletchgen:", val)
            result = ProcessRunner(fletchgen_printer, command_line, shell=False)
            if result != 0:
                raise FletchgenError("Fletchgen failed. Build exited with code {}".format(result))

            # Apply the generated architecture to the kernel file.
            if fletcher_kernel_path.exists():
                contents = []
                with open(fletcher_kernel_path, 'r') as fletcher_kernel_file:
                    contents = fletcher_kernel_file.readlines()
                with open(fletcher_kernel_path, 'w') as fletcher_kernel_file:
                    if 'end entity;\n' in contents:
                        start_index = contents.index('end entity;\n') + 1
                        with open(fletcher_wrapper_file.destination, 'r') as arch_file:
                            fletcher_kernel_file.writelines(contents[:start_index])
                            fletcher_kernel_file.writelines(arch_file.readlines())
                    else:
                        raise FletchgenError("Could not patch the fletchgen generated kernel.".format(result))

            if run_fletchgen_in_docker:
                fletcher_simtop_path = fletcher_wrapper_output_dir / 'vhdl' / 'SimTop_tc.vhd'
                if fletcher_simtop_path.exists():
                    with open(fletcher_simtop_path, 'r') as fletcher_simtop_file:
                        simtop_contents = fletcher_simtop_file.read()
                    with open(fletcher_simtop_path, 'w') as fletcher_simtop_file:
                        srec_path_docker = "/source/{}{}.srec".format(query_name, settings.DATA_SUFFIX)
                        srec_path_host = output_dir / "{}{}.srec".format(query_name, settings.DATA_SUFFIX)
                        fletcher_simtop_file.write(
                            simtop_contents.replace(
                                '"{}"'.format(srec_path_docker),
                                '"{}"'.format(srec_path_host.resolve())
                            )
                        )


    def copy_files(self, source_dir: PurePath, output_dir: PurePath, file_list: List[Path]):
        if source_dir == output_dir:
            return
        for file in file_list:
            copyfile(str(source_dir / file),
                     str(output_dir / file))

    def parse(self, query_str: str):
        return msp.parse(query_str, json=False)

    def transform(self, query: ast_nodes.Query, query_name: str):
        assert isinstance(query, ast_nodes.Query)
        query = self.where_transform.transform(query)
        query = self.wildcard_transform.transform(query)
        query = self.constant_propagation_transform.transform(query, skip_functions=True)
        query = self.concat_transform.transform(query)
        query = self.constant_propagation_transform.transform(query)

        header_ast, general_ast, header_test_ast, general_test_ast = self.python_ast_transform.transform(query,
                                                                                                         query_name=query_name)

        # header_ast = self.nullables_transform.transform(header_ast)
        # general_ast = self.nullables_transform.transform(general_ast)
        # header_test_ast = self.nullables_transform.transform(header_ast)
        # general_test_ast = self.nullables_transform.transform(general_test_ast)

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
        unparser = transpyle.Cpp14Unparser(headers=False)
        unparser_header = transpyle.Cpp14Unparser(headers=True)

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
