import ctypes

class CStructWrapper(ctypes.Structure):
    _fields_ = [("int1",ctypes.c_uint32),("name",ctypes.c_char_p)]

    # def __init__(self, schema: pa.Schema):
    #     type_map = CTypesTypeMapper()
    #     for col in schema:
    #         self._fields_.append((col.name, type_map.resolve(col.type)))
    #     super().__init__()
