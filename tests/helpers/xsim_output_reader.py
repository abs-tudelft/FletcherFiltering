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
from pathlib import Path, PurePath
import typing
from fletcherfiltering.common.helpers.struct_type_mapper import StructTypeMapper
import re
import struct
from fletcherfiltering import settings
import bitstring
import math


class XSIMOutputReader():
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        self.in_schema = in_schema
        self.out_schema = out_schema

    def collapse_length_valid_column(self, d: dict, col_name: str, full_output: bool = False):
        source_name = col_name + settings.LENGTH_SUFFIX
        assert source_name in d

        if full_output:
            d[col_name] = {'len_data': d[source_name], 'data': d[col_name]}
        elif d[source_name] is None:
            d[col_name] = None

        return d

    def read(self, data_path: PurePath, query_name: str, full_output: bool = False):
        # print("Reading....")

        ref_filename = Path('cdatafile/ref.tcl')
        cdata_in_filename_template = 'cdatafile/c.{0}.autotvin_{1}.dat'
        cdata_out_filename_template = 'cdatafile/c.{0}.autotvout_{1}.dat'
        rtldata_out_filename_template = 'rtldatafile/rtl.{0}.autotvout_{1}.dat'

        trans_num_regex = re.compile(r"set trans_num ([0-9]+)")
        depth_num_regex = re.compile(r"\{([a-zA-Z_0-9]+) ([0-9]+)\}")
        columns = []
        total_transactions = 0
        with open(data_path / ref_filename, 'r') as ref_file:
            for line in ref_file:
                if line:
                    if "trans_num" in line:
                        matches = trans_num_regex.match(line)
                        if matches:
                            total_transactions = int(matches.group(1))
                    else:
                        matches = depth_num_regex.match(line)
                        if matches:
                            columns.append((matches.group(1), int(matches.group(2))))
        out_data = [None] * total_transactions
        if len(columns) > 0:
            struct_type_mapper = StructTypeMapper()
            for column in columns:
                col_name = 'ap_return'
                length_column = False
                col_type = pa.bool_()
                if column[0] is not col_name:
                    if not column[0].startswith(settings.INPUT_NAME):
                        colname_regex = re.compile(r"{0}_([a-zA-Z0-9_]+?)(_len)?_V?".format(settings.OUTPUT_NAME))
                        matches = colname_regex.match(column[0])
                        if matches:
                            col_name = matches.group(1)
                            col = self.out_schema.field_by_name(col_name)
                            if matches.group(2) == settings.LENGTH_SUFFIX:
                                col_type = settings.LENGTH_TYPE
                                length_column = True
                            else:
                                col_type = col.type
                    # else:
                    # print("Input column {}, skipping.".format(column))

                suffix = ''
                if length_column:
                    suffix += settings.LENGTH_SUFFIX

                #c_data_out_file = data_path / Path(cdata_out_filename_template.format(query_name, column[0]))
                rtl_data_out_file = data_path / Path(rtldata_out_filename_template.format(query_name, column[0]))
                if rtl_data_out_file.is_file():
                    with open(rtl_data_out_file, 'r') as rtl_datafile:
                        data = self.read_datafile(rtl_datafile, num_transactions=total_transactions,
                                                  type=struct_type_mapper.resolve(col_type),
                                                  nullable=col.nullable and col_name!='ap_return',
                                                  simple=col_name=='ap_return',
                                                  full_output=full_output)
                        out_data = self.merge_column(out_data, data, col_name + suffix)

            if not full_output:
                for col in self.out_schema:
                    if col.nullable and col.type in settings.VAR_LENGTH_TYPES:
                        out_data = list(
                            map(lambda d: self.collapse_length_valid_column(d, col.name, full_output), out_data))

                # Remove LENGTH columns from output and also filter on the query return value.
                out_data = [{k: v for (k, v) in d.items() if k != 'ap_return' and not k.endswith(settings.LENGTH_SUFFIX)}
                            for d in out_data if d['ap_return']]
            else:
                out_data = [
                    #{k: v for (k, v) in d.items() if k != 'ap_return'}
                    d
                    for d in out_data if d['ap_return']]


        return out_data

    def merge_column(self, data, extra_data, column_name):
        for extra_data_idx, extra_data_row in extra_data.items():
            if len(data) <= extra_data_idx:
                raise ValueError("Transaction ID {} does not exists in target data structure.".format(extra_data_idx))
            if data[extra_data_idx] is None:
                data[extra_data_idx] = {}
            data[extra_data_idx][column_name] = extra_data_row
        return data

    def handle_data_hex(self, hex: str, type: typing.Tuple[str, int], nullable: bool = False, simple: bool = False):
        base_bits = 2
        extra_bits = base_bits if not nullable else base_bits+1
        if simple:
            base_bits = 0
            extra_bits = 0
        total_bits = type[1] + extra_bits
        total_bytes = math.ceil(total_bits/4)
        hex_value = hex.zfill(total_bytes)
        bs = bitstring.BitArray(hex=hex_value)[-total_bits:]
        fmt = '{2}bits:{0}{1}'.format(type[1], ',bool' * base_bits, 'bool,' if nullable else '')
        data = bs.unpack(fmt)

        if simple:
            dvalid = True
            last = False
            valid = True
            data = data[0].tobytes()
        elif nullable:
            dvalid = data[3]
            last = data[2]
            valid = data[0]
            data = data[1].tobytes()
        else:
            dvalid = data[2]
            last = data[1]
            valid = True
            data = data[0].tobytes()
        if type[0] != '_str_':
            unpacked = struct.unpack('>' + type[0], data)
            if isinstance(unpacked, tuple):
                unpacked = unpacked[0]
        else:
            unpacked = data
        return {'data': unpacked, 'dvalid': dvalid, 'last': last, 'valid': valid}

    def read_datafile(self, filestream: typing.TextIO, num_transactions: int, type: typing.Tuple[str, int], nullable: bool = False, simple: bool = False, full_output: bool = False):
        trans_num_regex = re.compile(r"\[\[transaction\]\]\s+([0-9]+)")
        in_runtime = False
        in_transaction = False
        current_transaction = None
        transactions = {}
        for line in filestream:
            if '[[[runtime]]]' in line:
                in_runtime = True
            elif in_runtime and '[[transaction]]' in line:
                in_transaction = True
                matches = trans_num_regex.match(line)
                if matches:
                    current_transaction = int(matches.group(1))
                    if current_transaction > num_transactions:
                        raise ValueError("Read a transaction ID larger that the total number of transactions.")

                    if current_transaction not in transactions:
                        if type[0] == '_str_':
                            transactions[current_transaction] = b"" if not full_output else []
                        else:
                            transactions[current_transaction] = None if not full_output else {'data': None,
                                                                                              'dvalid': None,
                                                                                              'last': None,
                                                                                              'valid': None}

            elif in_runtime and not in_transaction and '[[[/runtime]]]' in line:
                in_runtime = False
            elif in_runtime and in_transaction and '[[/transaction]]' in line:
                in_transaction = False
                current_transaction = None
            elif in_runtime and in_transaction:
                # Data
                hex_value = line.strip()[2:]
                unpacked = self.handle_data_hex(hex_value, type, nullable and type[0] != '_str_', simple)

                if unpacked['valid']:
                    if type[0] == '_str_':
                        if full_output:
                            transactions[current_transaction].append(unpacked)
                        else:
                            transactions[current_transaction] += unpacked['data']
                    else:
                        transactions[current_transaction] = unpacked['data'] if not full_output else unpacked
                else:
                    transactions[current_transaction] = None if not full_output else unpacked

            else:
                raise ValueError("Read line '{}' data that is not supported in this spot.".format(line))
        if type[0] == '_str_' and not full_output:
            # Decode from UTF-8 bytes
            transactions = {k: v.decode('utf-8') if v is not None else None for k, v in transactions.items()}
        return transactions
