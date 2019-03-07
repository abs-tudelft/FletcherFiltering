import mysql.connector
import mysql.connector.errorcode as errorcode
import os.path
from fletcherfiltering.codegen.compiler import Compiler

from fletcherfiltering.codegen.transformations.helpers import grouped

from fletcherfiltering import settings

from ..data_generation.SentenceGenerator import SentenceGenerator
from ..data_generation.UIntGenerator import UIntGenerator
from ..data_generation.IntGenerator import IntGenerator
from ..data_generation.FloatGenerator import FloatGenerator

from .mysql_type_mapper import MySQLTypeMapper
from .ctypes_type_mapper import CTypesTypeMapper

from .. import test_settings

from . import python_class_generator

import pyarrow as pa
import shutil
import subprocess
import ctypes
import copy
import pytest
import sys
import platform
import struct


class BaseQuery:
    def __init__(self, printer, cnx, working_dir_base, name='query', has_data_file=False, separate_work_dir=False,
                 clean_workdir=False):
        self.printer = printer
        self.cnx = cnx
        assert os.path.isdir(working_dir_base)
        assert os.access(working_dir_base, os.W_OK)
        self.data = []
        self.cursor = cnx.cursor(dictionary=True, buffered=True)
        self.name = name
        self.has_data_file = has_data_file
        self.in_schema = pa.schema([])
        self.out_schema = pa.schema([])
        self.in_schema_pk = None
        self.query = None
        self.clean_workdir = clean_workdir
        self.swallow_build_output = False
        if separate_work_dir:
            self.working_dir = os.path.join(working_dir_base, test_settings.WORKSPACE_NAME, self.name)
        else:
            self.working_dir = os.path.join(working_dir_base, test_settings.WORKSPACE_NAME)

    def setup(self):
        if not self.create_table():
            if not self.drop_table():
                pytest.fail("Could not drop table successfully.")
            if not self.create_table():
                pytest.fail("Could not create table successfully on second try.")

        if not os.path.exists(self.working_dir):
            self.printer("Creating workspace directory '{}'".format(self.working_dir))
            os.makedirs(self.working_dir)
        else:
            if self.clean_workdir:
                self.printer("Re-creating workspace directory '{}'".format(self.working_dir))
                shutil.rmtree(self.working_dir)
                os.makedirs(self.working_dir)
            else:
                self.printer("Using workspace directory '{}'".format(self.working_dir))

        if not self.has_data_file:
            self.generate_random_data()

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

    def generate_random_data(self):
        str_gen = SentenceGenerator()
        uint_gen = UIntGenerator()
        int_gen = IntGenerator()
        float_gen = FloatGenerator()
        self.data.clear()
        for i in range(test_settings.DEFAULT_DATA_SIZE):
            record = {}
            for col in self.in_schema:
                if col.name == self.in_schema_pk:
                    if col.type == pa.string():
                        record[col.name] = str(i)
                    elif col.type == pa.int32() or col.type == pa.uint32() or col.type == pa.int64() or col.type == pa.uint64():
                        record[col.name] = i
                    else:
                        pytest.fail("Unsupported PK column type {} for {}".format(col.type, col.name))
                else:
                    if col.type == pa.string():
                        record[col.name] = str_gen.generate(maxlength=128)
                    elif col.type == pa.int8():
                        record[col.name] = int_gen.generate(8)
                    elif col.type == pa.uint8():
                        record[col.name] = uint_gen.generate(8)
                    elif col.type == pa.int16():
                        record[col.name] = int_gen.generate(16)
                    elif col.type == pa.uint16():
                        record[col.name] = uint_gen.generate(16)
                    elif col.type == pa.int32():
                        record[col.name] = int_gen.generate(32)
                    elif col.type == pa.uint32():
                        record[col.name] = uint_gen.generate(32)
                    elif col.type == pa.int64():
                        record[col.name] = int_gen.generate(64)
                    elif col.type == pa.uint64():
                        record[col.name] = uint_gen.generate(64)
                    elif col.type == pa.timestamp('ms'):
                        record[col.name] = uint_gen.generate(64)
                    elif col.type == pa.float16():
                        record[col.name] = float_gen.generate(16)
                    elif col.type == pa.float32():
                        record[col.name] = float_gen.generate(32)
                    elif col.type == pa.float64():
                        record[col.name] = float_gen.generate(64)
                    else:
                        pytest.fail("Unsupported column type {} for {}".format(col.type, col.name))
            self.data.append(record)

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

    def compile(self):

        self.printer("Compiling SQL to HLS C++...")
        compiler = Compiler(self.in_schema, self.out_schema)

        compiler(query_str=self.query, query_name=self.name, output_dir=self.working_dir,
                 extra_include_dirs=test_settings.HLS_INCLUDE_PATH, extra_link_dirs=test_settings.HLS_LINK_PATH,
                 extra_link_libraries=test_settings.HLS_LIBS)

        with open(os.devnull, "w") as f:
            redir = f
            if not self.swallow_build_output:
                redir = None

            self.printer("Running CMake Generate...")
            subprocess.run('cmake -G "{}" -DCMAKE_BUILD_TYPE={} .'.format(test_settings.CMAKE_GENERATOR,
                                                                          test_settings.BUILD_CONFIG), shell=True,
                           check=True, cwd=self.working_dir, stdout=redir)
            self.printer("Running CMake Build...")
            subprocess.run("cmake --build . --config {}".format(test_settings.BUILD_CONFIG), shell=True, check=True,
                           cwd=self.working_dir, stdout=redir)

    def build_schema_class(self, schema: pa.Schema, suffix: str):
        schema_name = "Struct{}{}".format(self.name, suffix)
        schema_ast = python_class_generator.get_class_ast(schema, schema_name)
        schema_local_scope = {}
        schema_object = compile(schema_ast, filename='<dynamic_ast>', mode='exec')
        exec(schema_object, None, schema_local_scope)
        return schema_local_scope[schema_name]

    def run_fletcherfiltering(self):

        in_schema_type = self.build_schema_class(self.in_schema, 'In')

        out_schema_type = self.build_schema_class(self.out_schema, 'Out')

        if platform.system() == 'darwin':
            lib = ctypes.CDLL(os.path.join(self.working_dir, 'libcodegen-{}.dylib'.format(self.name)))
        elif platform.system() == 'Windows':
            lib = ctypes.WinDLL(
                os.path.join(self.working_dir, test_settings.BUILD_CONFIG, 'codegen-{}.dll'.format(self.name)))
        else:
            lib = ctypes.CDLL(os.path.join(self.working_dir, 'libcodegen-{}.so'.format(self.name)))
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
                            ctypes.cast(ctypes.create_string_buffer(data_item[col.name].encode('ascii', 'replace'),
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
                            out_data[col.name] = copy.copy(getattr(out_schema, col.name)).decode('ascii')
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
        if test_settings.VIVADO_BIN_DIR == '':
            pytest.fail("No Vivado install configured.")

        vivado_env = {
            'PATH': test_settings.VIVADO_BIN_DIR
        }
        with open(os.devnull, "w") as f:
            redir = f
            if not self.swallow_build_output:
                redir = None
            subprocess.run("vivado_hls -f run_complete_hls.tcl", shell=True, check=True, cwd=self.working_dir,
                           stdout=redir, env={**os.environ, **vivado_env})

        #TODO read output file transactions

        return []

    def run_sql(self):

        result_data = []

        self.cursor.execute(self.query)

        result_data = self.cursor.fetchall()

        return result_data

    def run(self):
        self.compile()

        self.printer("Executing query on MySQL...")
        sql_data = self.run_sql()
        self.printer("Executing query on FletcherFiltering...")
        fletcher_data = self.run_fletcherfiltering()
        self.printer("Executing query on Vivado XSIM...")
        vivado_data = self.run_vivado()

        self.printer("Verifying the returned data...")

        if len(fletcher_data) > len(sql_data):
            pytest.fail(
                "FlechterFiltering let too many records through {} vs {}".format(len(fletcher_data), len(sql_data)))
        elif len(fletcher_data) < len(sql_data):
            pytest.fail(
                "FlechterFiltering let too few records through {} vs {}".format(len(fletcher_data), len(sql_data)))
        else:
            for record_set in zip(sql_data, fletcher_data):
                assert record_set[0] == record_set[1]

        if len(vivado_data) > len(sql_data):
            pytest.fail(
                "Vivado XSIM let too many records through {} vs {}".format(len(vivado_data), len(sql_data)))
        elif len(vivado_data) < len(sql_data):
            pytest.fail(
                "Vivado XSIM let too few records through {} vs {}".format(len(vivado_data), len(sql_data)))
        else:
            for record_set in zip(sql_data, vivado_data):
                assert record_set[0] == record_set[1]
        return True

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
