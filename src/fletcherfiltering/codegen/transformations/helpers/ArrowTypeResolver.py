import pyarrow as pa

import typed_ast.ast3 as ast


class ArrowTypeResolver(object):

    @staticmethod
    def make_method_name(arrow_type: pa.DataType) -> str:
        return 'type_' + str(arrow_type).replace("[", "_").replace("]", "_")

    def resolve(self, arrow_type: pa.DataType, as_stream: bool = False, as_pointer: bool = False,
                as_const: bool = False):
        """Dispatch method"""
        method_name = self.make_method_name(arrow_type)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, self.unknown_type)
        # Call the method as we return it
        if as_stream:
            return self.wrap_in_stream(method(arrow_type, as_pointer), as_const)
        else:
            return method(arrow_type, as_pointer, as_const)

    def wrap_in_stream(self, type_ast, as_const: bool = False):
        return ast.Subscript(
            value=ast.Name(
                id=("const " if as_const else "") + 'hls::stream',
                ctx=ast.Load()),
            slice=type_ast
        )

    def type_bool(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "bool" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_int8(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "int8_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_uint8(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint8_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_int16(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "int16_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_uint16(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint16_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_int32(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "int32_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_uint32(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint32_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_int64(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "int64_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_uint64(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint64_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_timestamp_s_(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint64_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_timestamp_ms_(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint64_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_timestamp_us_(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint64_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_timestamp_ns_(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "uint64_t" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_string(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "char" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_halffloat(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "half" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_float(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "float" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def type_double(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        return ast.Name(
            id=("const " if as_const else "") + "double" + ("*" if as_pointer else ''),
            ctx=ast.Load()
        )

    def unknown_type(self, arrow_type, as_pointer: bool = False, as_const: bool = False):
        raise NotImplementedError('{}{}{} cannot be processed'.format(arrow_type, ' as pointer' if as_pointer else '',
                                                                      ' as constant' if as_const else ''))
