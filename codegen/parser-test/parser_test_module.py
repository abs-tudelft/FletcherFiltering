import pyarrow as pa

from codegen.compiler import Compiler

if __name__ == "__main__":
    in_schema = pa.read_schema("../schema-test/in_schema.fbs")
    out_schema = pa.read_schema("../schema-test/out_schema.fbs")

    compiler = Compiler(in_schema, out_schema)

    compiler(query_str="select int1+int2 as int1, CONCAT(string1,1<<4,'NULL') as concat, CONCAT('123456',string1,True,False) as concat2 FROM a WHERE int1 > 4 AND int2 < 18",
             query_name="query",
             output_dir="../../codegen-cpp/")