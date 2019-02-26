import pyarrow as pa

import typed_ast.ast3 as ast


class MySQLTypeMapper(object):

    @staticmethod
    def make_method_name(arrow_type: pa.DataType) -> str:
        return 'type_' + str(arrow_type).replace("[", "_").replace("]", "_")

    def resolve(self, arrow_type: pa.DataType):
        """Dispatch method"""
        method_name = self.make_method_name(arrow_type)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, self.unknown_type)
        # Call the method as we return it
        return method(arrow_type)


    def type_bool(self, arrow_type):
        return "BOOLEAN"

    def type_int8(self, arrow_type):
        return "TINYINT"

    def type_uint8(self, arrow_type):
        return "TINYINT UNSIGNED"

    def type_int16(self, arrow_type):
        return "SMALLINT"

    def type_uint16(self, arrow_type):
        return "SMALLINT UNSIGNED"

    def type_int32(self, arrow_type):
        return "INT"

    def type_uint32(self, arrow_type):
        return "INT UNSIGNED"

    def type_int64(self, arrow_type):
        return "BIGINT"

    def type_uint64(self, arrow_type):
        return "BIGINT UNSIGNED"

    def type_timestamp_ms_(self, arrow_type):
        return "BIGINT UNSIGNED"

    # TODO: figure out a way to deal with the 32-bitness of TIMESTAMP columns in SQL (UNIX standard)
    def type_timestamp_s_(self, arrow_type):
        return "TIMESTAMP"

    def type_string(self, arrow_type):
        return "VARCHAR(255)"

    # TODO: Maybe replace with the correct decimal column
    def type_halffloat(self, arrow_type):
        return "FLOAT"

    def type_float(self, arrow_type):
        return "FLOAT"

    def type_double(self, arrow_type):
        return "DOUBLE"

    def unknown_type(self, arrow_type):
        raise NotImplementedError('{} cannot be processed'.format(arrow_type))
