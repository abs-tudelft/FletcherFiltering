import pyarrow as pa

import ctypes


class CTypesTypeMapper(object):

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
        return ctypes.c_bool

    def type_int8(self, arrow_type):
        return ctypes.c_int8

    def type_uint8(self, arrow_type):
        return ctypes.c_uint8

    def type_int16(self, arrow_type):
        return ctypes.c_int16

    def type_uint16(self, arrow_type):
        return ctypes.c_uint16

    def type_int32(self, arrow_type):
        return ctypes.c_int32

    def type_uint32(self, arrow_type):
        return ctypes.c_uint32

    def type_int64(self, arrow_type):
        return ctypes.c_int64

    def type_uint64(self, arrow_type):
        return ctypes.c_uint64

    def type_timestamp_ns_(self, arrow_type):
        return ctypes.c_uint64

    def type_timestamp_us_(self, arrow_type):
        return ctypes.c_uint64

    def type_timestamp_ms_(self, arrow_type):
        return ctypes.c_uint64

    def type_timestamp_s_(self, arrow_type):
        return ctypes.c_uint64

    def type_string(self, arrow_type):
        return ctypes.c_char_p

    def type_halffloat(self, arrow_type):
        return ctypes.c_short

    def type_float(self, arrow_type):
        return ctypes.c_float

    def type_double(self, arrow_type):
        return ctypes.c_double

    def unknown_type(self, arrow_type):
        raise NotImplementedError('{} cannot be processed'.format(arrow_type))
