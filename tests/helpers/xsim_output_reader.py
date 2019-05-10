import pyarrow as pa
from pathlib import Path, PurePath
import typing
from .struct_type_mapper import StructTypeMapper
import re
import struct
from fletcherfiltering import settings


class XSIMOutputReader():
    def __init__(self, in_schema: pa.Schema, out_schema: pa.Schema):
        self.in_schema = in_schema
        self.out_schema = out_schema

    def collapse_valid_column(self, d:dict, col_name: str, grab_from_length_column:bool = False):
        source_name = col_name + (settings.LENGTH_SUFFIX if grab_from_length_column else '') + settings.VALID_SUFFIX
        assert source_name in d

        if d[source_name] == False:
            d[col_name] = None

        del d[source_name]
        return d


    def read(self, data_path: PurePath, query_name: str):
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
                valid_column = False
                nullable_column = True
                col_type = pa.bool_()
                if column[0] is not col_name:
                    if not column[0].startswith(settings.INPUT_NAME):
                        colname_regex = re.compile(r"{0}_([a-zA-Z0-9_]+?)(_len)?_V_?([a-zA-Z]+)?".format(settings.OUTPUT_NAME))
                        matches = colname_regex.match(column[0])
                        if matches:
                            col_name = matches.group(1)
                            col_name_suffix = matches.group(3)
                            if col_name_suffix == 'value':
                                assert self.out_schema.field_by_name(col_name).nullable
                                nullable_column = True
                            if col_name_suffix == 'valid' and matches.group(2) == settings.LENGTH_SUFFIX:
                                col_type = settings.VALID_TYPE
                                valid_column = True
                                length_column = True
                            elif col_name_suffix == 'valid':
                                col_type = settings.VALID_TYPE
                                valid_column = True
                            elif matches.group(2) == settings.LENGTH_SUFFIX:
                                col_type = settings.LENGTH_TYPE
                                length_column = True
                            else:
                                col_type = self.out_schema.field_by_name(col_name).type
                    # else:
                    # print("Input column {}, skipping.".format(column))

                suffix = ''
                if length_column:
                    suffix += settings.LENGTH_SUFFIX
                if valid_column:
                    suffix += settings.VALID_SUFFIX

                #c_data_out_file = data_path / Path(cdata_out_filename_template.format(query_name, column[0]))
                rtl_data_out_file = data_path / Path(rtldata_out_filename_template.format(query_name, column[0]))
                if rtl_data_out_file.is_file():
                    with open(rtl_data_out_file, 'r') as rtl_datafile:
                        data = self.read_datafile(rtl_datafile, total_transactions, struct_type_mapper.resolve(col_type))
                        out_data = self.merge_column(out_data, data, col_name + suffix)

            # Remove LENGTH columns from output and also filter on the query return value.
            out_data = [{k: v for (k, v) in d.items() if k != 'ap_return' and not k.endswith(settings.LENGTH_SUFFIX)}
                        for d in out_data if d['ap_return']]

            for col in self.out_schema:
                if col.nullable:
                    out_data = list(map(lambda d: self.collapse_valid_column(d, col.name, col.type in settings.VAR_LENGTH_TYPES), out_data))


        return out_data

    def merge_column(self, data, extra_data, column_name):
        for extra_data_idx, extra_data_row in extra_data.items():
            if len(data) <= extra_data_idx:
                raise ValueError("Transaction ID {} does not exists in target data structure.".format(extra_data_idx))
            if data[extra_data_idx] is None:
                data[extra_data_idx] = {}
            data[extra_data_idx][column_name] = extra_data_row
        return data

    def read_datafile(self, filestream: typing.TextIO, num_transactions: int, type: typing.Tuple[str, int]):
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

                    if not current_transaction in transactions:
                        if type[0] == '_str_':
                            transactions[current_transaction] = b""
                        else:
                            transactions[current_transaction] = None

            elif in_runtime and not in_transaction and '[[[/runtime]]]' in line:
                in_runtime = False
            elif in_runtime and in_transaction and '[[/transaction]]' in line:
                in_transaction = False
                current_transaction = None
            elif in_runtime and in_transaction:
                # Data

                hex_value = line.strip()[2:]
                hex_value = hex_value.zfill(type[1] * 2)
                if len(hex_value) > type[1] * 2:
                    hex_value = hex_value[-type[1] * 2:]
                # TODO unpack into types.
                raw_value = bytes.fromhex(hex_value)
                if type[0] == '_str_':
                    transactions[current_transaction] += bytes(raw_value)
                else:
                    unpacked = struct.unpack('>' + type[0], raw_value)
                    if isinstance(unpacked, tuple):
                        transactions[current_transaction] = unpacked[0]
                    else:
                        transactions[current_transaction] = unpacked
            else:
                raise ValueError("Read line '{}' data that is not supported in this spot.".format(line))
        if type[0] == '_str_':
            # Decode from UTF-8 bytes
            transactions = {k: v.decode('utf-8') for k, v in transactions.items()}
        return transactions
