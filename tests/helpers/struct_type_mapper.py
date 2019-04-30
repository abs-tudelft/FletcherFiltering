import pyarrow as pa

import ctypes


class StructTypeMapper(object):

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
        return '?',1

    def type_int8(self, arrow_type):
        return 'b',1

    def type_uint8(self, arrow_type):
        return 'B',1

    def type_int16(self, arrow_type):
        return 'h',2

    def type_uint16(self, arrow_type):
        return 'H',2

    def type_int32(self, arrow_type):
        return 'i',4

    def type_uint32(self, arrow_type):
        return 'I',4

    def type_int64(self, arrow_type):
        return 'q',8

    def type_uint64(self, arrow_type):
        return 'Q',8

    def type_timestamp_us_(self, arrow_type):
        return 'Q',8

    def type_timestamp_ns_(self, arrow_type):
        return 'Q',8

    def type_timestamp_ms_(self, arrow_type):
        return 'Q',8

    def type_timestamp_s_(self, arrow_type):
        return 'Q',8

    def type_string(self, arrow_type):
        return '_str_',1

    def type_halffloat(self, arrow_type):
        return 'e',2

    def type_float(self, arrow_type):
        return 'f',4

    def type_double(self, arrow_type):
        return 'd',8

    def unknown_type(self, arrow_type):
        raise NotImplementedError('{} cannot be processed'.format(arrow_type))
