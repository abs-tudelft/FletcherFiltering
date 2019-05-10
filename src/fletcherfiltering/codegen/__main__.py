from .compiler import Compiler
from .. import settings
from pathlib import Path
import os
import os.path

from .exceptions import SchemaFileNotReadable, OutputDirIsNotWritable, QueryTooShort

if __name__ == "__main__":
    import argparse
    import pyarrow as pa

    parser = argparse.ArgumentParser(prog="python3 -m codegen",
                                     description='Compile SQL statements into HLS C++ files.')
    parser.add_argument('-i', '--input-schema', dest='input_schema', help='The input schema flatbuffer file.',
                        default='in_schema.fbs')
    parser.add_argument('-o', '--output-schema', dest='output_schema', help='The output schema flatbuffer file.',
                        default='out_schema.fbs')
    parser.add_argument('query_str', help='The query string to be compiled.', metavar='query-string')
    parser.add_argument('--query-name', help='The query name for both the file and the function.', default='query')
    parser.add_argument('--output-dir', help='The output directory.', default='.')

    args = parser.parse_args()

    if os.path.isfile(args.input_schema):
        if os.access(args.input_schema, os.R_OK):
            in_schema = pa.read_schema(args.input_schema)
        else:
            raise SchemaFileNotReadable()
    else:
        raise FileNotFoundError(args.input_schema)

    if os.path.isfile(args.output_schema):
        if os.access(args.output_schema, os.R_OK):
            out_schema = pa.read_schema(args.output_schema)
        else:
            raise SchemaFileNotReadable()
    else:
        raise FileNotFoundError(args.output_schema)

    if os.path.isdir(args.output_dir):
        if not os.access(args.output_dir, os.W_OK):
            raise OutputDirIsNotWritable()
    else:
        raise NotADirectoryError(args.output_dir)

    compiler = Compiler(in_schema, out_schema)

    if len(args.query_str) < settings.MINIMAL_QUERY_LENGTH:
        raise QueryTooShort()

    compiler(query_str=args.query_str, query_name=args.query_name, output_dir=Path(args.output_dir))
