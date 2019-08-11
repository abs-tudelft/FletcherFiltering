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

import mysql.connector
import mysql.connector.errorcode as errorcode
from fletcherfiltering.codegen.compiler import Compiler
from fletcherfiltering.common.data_generation import generate_random_data

from .xsim_output_reader import XSIMOutputReader

from fletcherfiltering import settings

from pathlib import Path

from .mysql_type_mapper import MySQLTypeMapper

from . import python_class_generator

from fletcherfiltering.common.helpers.process_runner import ProcessRunner, VivadoHLSProcessRunner

import pyarrow as pa
import numpy as np
import shutil
import os
import ctypes
import copy
import pytest
import platform
import struct
import string
import math


class BaseQuery:
    def __init__(self, printer, cnx, working_dir_base: Path, name='query', has_data_file=False, separate_work_dir=False,
                 clean_workdir=False):
        self.printer = printer
        self.cnx = cnx
        assert working_dir_base.is_dir()
        self.data = []
        if self.cnx:
            self.cursor = cnx.cursor(dictionary=True, buffered=True)
        else:
            self.cursor = None
        self.name = name
        self.has_data_file = has_data_file
        self.in_schema = None
        self.out_schema = None
        self.in_schema_pk = None
        self.query = None
        self.clean_workdir = clean_workdir
        self.swallow_build_output = settings.SWALLOW_OUTPUT
        if separate_work_dir:
            self.working_dir = working_dir_base / settings.WORKSPACE_NAME / self.name
        else:
            self.working_dir = working_dir_base / settings.WORKSPACE_NAME

    def setup(self):
        if 'sql' in settings.TEST_PARTS:
            if not self.create_table():
                if not self.drop_table():
                    pytest.fail("Could not drop table successfully.")
                if not self.create_table():
                    pytest.fail("Could not create table successfully on second try.")

        #if 'fletcherfiltering' in settings.TEST_PARTS or 'vivado' in settings.TEST_PARTS:
        if not self.working_dir.exists():
            self.printer("Creating workspace directory '{}'".format(self.working_dir))
            self.working_dir.mkdir(parents=True, exist_ok=True)
        else:
            if self.clean_workdir:
                self.printer("Re-creating workspace directory '{}'".format(self.working_dir))
                shutil.rmtree(self.working_dir)
                self.working_dir.mkdir(parents=True, exist_ok=True)
            else:
                self.printer("Using workspace directory '{}'".format(self.working_dir))

        if not self.has_data_file:
            self.printer("Generating random data...".format(self.working_dir))
            self.data = generate_random_data(self.in_schema, self.in_schema_pk)

        if 'sql' in settings.TEST_PARTS:
            self.insert_data()

        return True

    def create_table(self):
        assert self.in_schema_pk is not None
        query = """CREATE TABLE `{0}` (
                          {1}
                          PRIMARY KEY (`{2}`)
                          );""".format(self.name, self.get_create_columns(self.in_schema), self.in_schema_pk)
        self.printer("Creating table for test {}".format(self.name))
        if not self.execute_query(query):
            return False

        return True

    def insert_data(self):
        if len(self.data) == 0:
            pytest.fail("There is no data.")

        query = """INSERT INTO `{0}` ({1}) VALUES ({2});""".format(self.name,
                                                                   self.get_insert_columns(
                                                                       self.in_schema),
                                                                   self.get_data_columns(
                                                                       self.in_schema))

        self.printer("Inserting {} records into database...".format(len(self.data)))

        if not self.execute_query(query, self.data):
            return False

        self.cnx.commit()

        return True

    def save_data(self):
        self.printer("Saving {} data records to header and record batch...".format(len(self.data)))
        data_placeholder = []

        for data_item in self.data:
            data_item_lst = []
            for col in self.in_schema:
                if col.type == pa.string():
                    data_item_text = "\"{}\"".format(data_item[col.name])
                elif col.type == pa.bool_():
                    data_item_text = "{}".format('true' if data_item[col.name] else 'false')
                elif col.type == pa.float32():
                    data_item_text = "{}f".format(data_item[col.name])
                elif col.type == pa.uint8() or col.type == pa.uint16() or col.type == pa.uint32():
                    data_item_text = "{}u".format(data_item[col.name])
                elif col.type == pa.int64():
                    data_item_text = "{}ll".format(data_item[col.name])
                elif col.type == pa.uint64():
                    data_item_text = "{}ull".format(data_item[col.name])
                elif pa.types.is_timestamp(col.type):
                    data_item_text = "{}ull".format(data_item[col.name])
                else:
                    data_item_text = "{}".format(data_item[col.name])
                if col.nullable:
                    if data_item[col.name] is not None:
                        data_item_lst.append("{{ .data = {0}, .valid = true}}".format(data_item_text))
                    else:
                        if col.type == pa.string():
                            default_value = "\"\""
                        else:
                            default_value = "0"
                        data_item_lst.append("{{ .data = {0}, .valid = false}}".format(default_value))
                else:
                    data_item_lst.append("{0}".format(data_item_text))

            data_placeholder.append(", ".join(data_item_lst))

        template_data = {
            'data_N_placeholder': len(self.data),
            'data_placeholder': ",\n\t".join(data_placeholder),
        }

        with open(self.working_dir / Path('{0}{1}.h'.format(self.name, settings.DATA_SUFFIX)), 'r+') as data_file:
            data_cpp = string.Template(data_file.read())
            data_file.seek(0)
            data_file.write(data_cpp.safe_substitute(template_data))
            data_file.truncate()

        rb_data = []
        for col in self.in_schema:
            type_func = (lambda x: x)
            
            if col.type == pa.float16():
                type_func = np.float16
            elif col.type == pa.float32():
                type_func = np.float32
            elif col.type == pa.float64():
                type_func = np.float64
            elif col.type == pa.int8():
                type_func = np.int8
            elif col.type == pa.uint8():
                type_func = np.uint8
            elif col.type == pa.int16():
                type_func = np.int16
            elif col.type == pa.uint16():
                type_func = np.uint16
            elif col.type == pa.int32():
                type_func = np.int32
            elif col.type == pa.uint32():
                type_func = np.uint32
            elif col.type == pa.int64():
                type_func = np.int64
            elif col.type == pa.uint64():
                type_func = np.uint64
            elif pa.types.is_timestamp(col.type):
                type_func = (lambda x: np.datetime64(x, col.type.unit))
                
            rb_data.append(pa.array([(type_func(d[col.name]) if d[col.name] is not None else None) for d in self.data], col.type))

        # Create a RecordBatch from the Arrays.
        recordbatch = pa.RecordBatch.from_arrays(rb_data, self.in_schema)

        # Create an Arrow RecordBatchFileWriter.
        writer = pa.RecordBatchFileWriter(self.working_dir / Path('{0}{1}.rb'.format(self.name, settings.DATA_SUFFIX)),
                                      self.in_schema)
        # Write the RecordBatch.
        writer.write(recordbatch)

        writer.close()

    def compile(self):
        self.printer("Compiling SQL to HLS C++...")
        compiler = Compiler(self.in_schema, self.out_schema)

        compiler(query_str=self.query, query_name=self.name, output_dir=self.working_dir,
                 extra_include_dirs=settings.HLS_INCLUDE_PATH, hls_include_dirs=[settings.FLETCHER_DIR / settings.FLETCHER_HLS_DIR], extra_link_dirs=settings.HLS_LINK_PATH,
                 extra_link_libraries=settings.HLS_LIBS,
                 include_fletcher_wrapper=platform.system() == 'Linux',
                 run_vivado_hls=platform.system() == 'Linux', run_fletchgen_in_docker=platform.system() != 'Linux',
                 include_snap_project=platform.system() == 'Linux')

    def build_schema_class(self, schema: pa.Schema, suffix: str):
        schema_name = "Struct{}{}".format(self.name, suffix)
        schema_ast = python_class_generator.get_class_ast(schema, schema_name)
        schema_local_scope = {}
        schema_object = compile(schema_ast, filename='<dynamic_ast>', mode='exec')
        exec(schema_object, None, schema_local_scope)
        return schema_local_scope[schema_name]

    def run_fletcherfiltering(self):

        if not self.swallow_build_output:
            cmake_printer = self.printer
        else:
            cmake_printer = lambda val: None

        self.printer("Running CMake Generate...")
        result = ProcessRunner(cmake_printer, ['cmake', '-G', settings.CMAKE_GENERATOR,
                                               '-DCMAKE_BUILD_TYPE={}'.format(settings.BUILD_CONFIG), '.'],
                               shell=False, cwd=self.working_dir)
        if result != 0:
            pytest.fail("CMake Generate exited with code {}".format(result))
        self.printer("Running CMake Build...")
        result = ProcessRunner(cmake_printer, ['cmake', '--build', '.', '--config', settings.BUILD_CONFIG],
                               shell=False, cwd=self.working_dir)
        if result != 0:
            pytest.fail("CMake Build exited with code {}".format(result))

        in_schema_type = self.build_schema_class(self.in_schema, 'In')

        out_schema_type = self.build_schema_class(self.out_schema, 'Out')

        if platform.system() == 'Darwin':
            lib = ctypes.CDLL(str(self.working_dir / 'libcodegen-{}.dylib'.format(self.name)))
        elif platform.system() == 'Windows':
            lib = ctypes.WinDLL(str(self.working_dir / settings.BUILD_CONFIG / 'codegen-{}.dll'.format(self.name)))
        else:
            lib = ctypes.CDLL(str(self.working_dir / 'libcodegen-{}.so'.format(self.name)))
        fletcherfiltering_test = lib.__getattr__(self.name + settings.TEST_SUFFIX)
        fletcherfiltering_test.restype = ctypes.c_bool
        fletcherfiltering_test.argtypes = [ctypes.POINTER(in_schema_type), ctypes.POINTER(out_schema_type)]

        result_data = []
        in_schema = in_schema_type()
        out_schema = out_schema_type()
        for col in self.out_schema:
            if col.type == pa.string():
                setattr(out_schema, col.name,
                        ctypes.cast(ctypes.create_string_buffer(settings.VAR_LENGTH), ctypes.c_char_p))

        for data_item in self.data:
            for col in self.in_schema:
                if col.type == pa.string():
                    setattr(in_schema, col.name,
                            ctypes.cast(ctypes.create_string_buffer(data_item[col.name].encode('utf-8', 'replace'),
                                                                    size=settings.VAR_LENGTH),
                                        ctypes.c_char_p))
                elif col.type == pa.float16():
                    # Pack the halffloat and unpack it as a short.
                    setattr(in_schema, col.name, struct.unpack('h', struct.pack('e', data_item[col.name]))[0])
                else:
                    setattr(in_schema, col.name, data_item[col.name])
            passed = fletcherfiltering_test(ctypes.byref(in_schema), ctypes.byref(out_schema))

            if passed:
                out_data = {}
                for col in self.out_schema:
                    if col.type == pa.string():
                        try:
                            out_data[col.name] = copy.copy(getattr(out_schema, col.name)).decode('utf-8')
                        except UnicodeDecodeError:
                            print(getattr(out_schema, col.name))
                    elif col.type == pa.float16():
                        # unpack the data as a short and the unpack that as a halffloat
                        out_data[col.name] = \
                            struct.unpack('e', struct.pack('h', copy.copy(getattr(out_schema, col.name))))[0]
                    else:
                        out_data[col.name] = copy.copy(getattr(out_schema, col.name))
                result_data.append(out_data)

        return result_data

    def run_vivado(self):
        if platform.system() == 'Darwin':
            self.printer("Vivado is not supported on macOS.")
            return None

        if settings.VIVADO_BIN_DIR == '':
            pytest.fail("No Vivado install configured.")

        vivado_env = os.environ.copy()
        vivado_env["PATH"] = str(settings.VIVADO_BIN_DIR) + os.pathsep + vivado_env["PATH"]
        vivado_env["XILINX_VIVADO"] = str(settings.VIVADO_DIR)

        if not self.swallow_build_output:
            vivado_printer = self.printer
        else:
            vivado_printer = lambda val: None

        result, sim_result = VivadoHLSProcessRunner(vivado_printer,
                                                    [str(settings.VIVADO_HLS_EXEC), '-f',
                                                     str((self.working_dir / 'hls_run_complete.tcl').resolve())],
                                                    shell=False, cwd=self.working_dir,
                                                    env=vivado_env)

        if result != 0:
            pytest.fail("Failed to run Vivado. Exited with code {}.".format(result))

        self.printer("Vivado reported C/RTL co-simulation result: {}".format(sim_result))

        assert sim_result == 'PASS'

        xor = XSIMOutputReader(self.in_schema, self.out_schema)

        return xor.read(self.working_dir / self.name / 'automated_tests' / 'sim' / 'tv', self.name)

    def run_sql(self):

        result_data = []

        self.cursor.execute(self.query)

        result_data = self.cursor.fetchall()

        return result_data

    def run(self):
        self.compile()

        self.save_data()

        if 'sql' in settings.TEST_PARTS:
            self.printer("Executing query on MySQL...")
            sql_data = self.run_sql()
        else:
            sql_data = None
        if (
                platform.system() == 'Darwin' or platform.system() == 'Linux') and 'fletcherfiltering' in settings.TEST_PARTS:
            self.printer("Executing query on FletcherFiltering...")
            fletcher_data = self.run_fletcherfiltering()
        else:
            fletcher_data = None
        if (platform.system() == 'Windows' or platform.system() == 'Linux') and 'vivado' in settings.TEST_PARTS:
            self.printer("Executing query on Vivado XSIM...")
            vivado_data = self.run_vivado()
        else:
            vivado_data = None

        if sql_data is None:
            pytest.xfail("No MySQL data was gathered. Can not compare results.")

        if fletcher_data is None and vivado_data is None:
            pytest.xfail("No implementation data was gathered. Platform possibly unsupported.")

        if fletcher_data is not None:
            self.printer("Verifying the returned FletcherFiltering data...")
            if len(fletcher_data) > len(sql_data):
                pytest.fail(
                    "FlechterFiltering let too many records through {} vs {}".format(len(fletcher_data), len(sql_data)))
            elif len(fletcher_data) < len(sql_data):
                pytest.fail(
                    "FlechterFiltering let too few records through {} vs {}".format(len(fletcher_data), len(sql_data)))
            else:
                for record_set in zip(sql_data, fletcher_data):
                    if not self.check_record_set(*record_set):
                        pytest.fail("Item from FletcherFiltering is not the same as item from SQL. \n{}\n{}".format(
                            record_set[0], record_set[1]))
        else:
            self.printer("No FletcherFiltering output data, platform not supported.")

        if vivado_data is not None:
            self.printer("Verifying the returned Vivado XSIM data...")
            if len(vivado_data) > len(sql_data):
                pytest.fail(
                    "Vivado XSIM let too many records through {} vs {}".format(len(vivado_data), len(sql_data)))
            elif len(vivado_data) < len(sql_data):
                pytest.fail(
                    "Vivado XSIM let too few records through {} vs {}".format(len(vivado_data), len(sql_data)))
            else:
                for record_set in zip(sql_data, vivado_data):
                    if not self.check_record_set(*record_set):
                        pytest.fail(
                            "Item from Vivado XSIM is not the same as item from SQL. \n{}\n{}".format(record_set[0],
                                                                                                      record_set[1]))
        else:
            self.printer("No Vivado XSIM output data, platform not supported.")
        return True

    def check_record_set(self, reference, candidate):
        errors = 0
        for col in self.out_schema:
            if col.name not in reference:
                self.printer("Column {} does not exist in the reference record.".format(col.name))
                errors += 1
                continue

            if col.name not in candidate:
                self.printer("Column {} does not exist in the candidate record.".format(col.name))
                errors += 1
                continue

            if col.type == pa.int16() or col.type == pa.uint16():
                reference[col.name] = self.clamp_int16(reference[col.name])
                candidate[col.name] = self.clamp_int16(candidate[col.name])
            elif col.type == pa.int8() or col.type == pa.uint8():
                reference[col.name] = self.clamp_int8(reference[col.name])
                candidate[col.name] = self.clamp_int8(candidate[col.name])
            elif col.type == pa.int32() or col.type == pa.uint32():
                reference[col.name] = self.clamp_int32(reference[col.name])
                candidate[col.name] = self.clamp_int32(candidate[col.name])
            elif col.type == pa.int64() or col.type == pa.uint64():
                reference[col.name] = self.clamp_int64(reference[col.name])
                candidate[col.name] = self.clamp_int64(candidate[col.name])

            if col.type == pa.float16():
                reference[col.name] = self.clamp_float16(reference[col.name])
                candidate[col.name] = self.clamp_float16(candidate[col.name])
                if not math.isclose(reference[col.name], candidate[col.name], rel_tol=settings.REL_TOL_FLOAT16):
                    self.printer("Column {} has a larger difference than the configured tolerance: {}.".format(col.name,
                                                                                                               settings.REL_TOL_FLOAT16))
                    errors += 1
            elif col.type == pa.float32():
                if not math.isclose(reference[col.name], candidate[col.name], rel_tol=settings.REL_TOL_FLOAT32):
                    self.printer("Column {} has a larger difference than the configured tolerance: {}.".format(col.name,
                                                                                                               settings.REL_TOL_FLOAT32))
                    errors += 1
            elif col.type == pa.float64():
                if not math.isclose(reference[col.name], candidate[col.name], rel_tol=settings.REL_TOL_FLOAT64):
                    self.printer("Column {} has a larger difference than the configured tolerance: {}.".format(col.name,
                                                                                                               settings.REL_TOL_FLOAT64))
                    errors += 1
            else:
                if not reference[col.name] == candidate[col.name]:
                    self.printer("Column {} does not have the same value in both records.".format(col.name))
                    errors += 1
        if errors > 0:
            self.printer("Record errors: {}".format(errors))
        return errors == 0

    @staticmethod
    def clamp_float16(value):
        if value is None:
            return value
        if value > settings.FLOAT16_MAX:
            return float("inf")
        elif value < -settings.FLOAT16_MAX:
            return float("-inf")
        elif -settings.FLOAT16_MIN < value < settings.FLOAT16_MIN:
            return 0

        return value

    @staticmethod
    def clamp_int64(value):
        if value is None:
            return value
        return value & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def clamp_int32(value):
        if value is None:
            return value
        return value & 0xFFFFFFFF

    @staticmethod
    def clamp_int16(value):
        if value is None:
            return value
        return value & 0xFFFF

    @staticmethod
    def clamp_int8(value):
        if value is None:
            return value
        return value & 0xFF

    def drop_table(self):
        query = """DROP TABLE `{0}`;""".format(self.name)
        self.printer("Dropping table for test {}".format(self.name))
        if not self.execute_query(query):
            return False
        return True

    def cleanup(self):
        # self.drop_table()

        if self.cursor:
            self.cursor.close()

    def get_create_columns(self, schema: pa.Schema):
        cols = ""
        mysql_types = MySQLTypeMapper()
        for col in schema:
            cols += "`{0}` {1} {2}NULL,".format(col.name, mysql_types.resolve(col.type), "" if col.nullable else "NOT ")

        return cols

    def get_insert_columns(self, schema: pa.Schema):
        cols = []
        for col in schema:
            cols.append("`{0}`".format(col.name))

        return ", ".join(cols)

    def get_data_columns(self, schema: pa.Schema):
        cols = []
        for col in schema:
            cols.append("%({0})s".format(col.name))

        return ", ".join(cols)

    def execute_query(self, query, data=None):
        try:
            if isinstance(data, list):
                self.cursor.executemany(query, data)
            elif isinstance(data, tuple) or isinstance(data, dict):
                self.cursor.execute(query, data)
            else:
                self.cursor.execute(query)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.printer("Table already exists.")
            else:
                pytest.fail("Mysql Error: " + err.msg)
        else:
            return True
