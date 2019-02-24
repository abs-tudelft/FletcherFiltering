import pyarrow as pa

from fletcherfiltering.codegen.compiler import Compiler

if __name__ == "__main__":
    in_schema = pa.schema([('id', pa.int32(), False),
                           ('string1', pa.string(), False),
                           ('string2', pa.string(), False)])

    out_schema = pa.schema([('id', pa.int32(), False),
                            ('string1', pa.string(), False),
                            ('string2', pa.string(), False)])

    compiler = Compiler(in_schema, out_schema)

    compiler(query_str="select a.* from a",
             query_name="query",
             output_dir="../../codegen-cpp/", include_build_system=False)
