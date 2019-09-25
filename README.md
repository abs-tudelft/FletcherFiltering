# FletcherFiltering
SQL to HLS compiler that generates hardware filters and transformations for [Flechter](https://github.com/abs-tudelft/fletcher) streams.


If you want to use the compiler from python, you can call the compile function directly. Here is an excerpt from [\_\_main\_\_.py](src/fletcherfiltering/codegen/__main__.py#L42-L69):
```py
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

compiler(query_str=args.query_str, query_name=args.query_name, output_dir=Path(args.output_dir), meta_length_source=args.meta_length_source)
```
Here `meta_length_source` is the name of the column that is the source for the generated kernel length attribute in it's metadata. By default this is 'pkid'.

If you want to use the compiler without using the parser, you can use it like this the following excerpt from [compiler.py](src/fletcherfiltering/codegen/compiler.py#L121-L123):
```py
header_ast, general_ast, header_test_ast, general_test_ast = self.transform(query, current_query_name)
self.output(header_ast, general_ast, header_test_ast, general_test_ast, output_dir, current_query_name,
            include_test_system=include_test_system)
```
Where `query` is the input `AST`. And `self` is the `Compiler` object as instantiated in the code above.