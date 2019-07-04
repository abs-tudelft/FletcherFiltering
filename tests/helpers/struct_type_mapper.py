#  Copyright (c) 2019 Erwin de Haan. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This file is part of the FletcherFiltering project

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
        return 'b',8

    def type_uint8(self, arrow_type):
        return 'B',8

    def type_int16(self, arrow_type):
        return 'h',16

    def type_uint16(self, arrow_type):
        return 'H',16

    def type_int32(self, arrow_type):
        return 'i',32

    def type_uint32(self, arrow_type):
        return 'I',32

    def type_int64(self, arrow_type):
        return 'q',64

    def type_uint64(self, arrow_type):
        return 'Q',64

    def type_timestamp_us_(self, arrow_type):
        return 'Q',64

    def type_timestamp_ns_(self, arrow_type):
        return 'Q',64

    def type_timestamp_ms_(self, arrow_type):
        return 'Q',64

    def type_timestamp_s_(self, arrow_type):
        return 'Q',64

    def type_string(self, arrow_type):
        return '_str_',8

    def type_halffloat(self, arrow_type):
        return 'e',16

    def type_float(self, arrow_type):
        return 'f',32

    def type_double(self, arrow_type):
        return 'd',64

    def unknown_type(self, arrow_type):
        raise NotImplementedError('{} cannot be processed'.format(arrow_type))
