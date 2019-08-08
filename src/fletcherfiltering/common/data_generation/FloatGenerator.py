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

import random
import struct

class FloatGenerator:
    ieee_floats = {
        16: {'exp': 5, 'significand': 11, 'digits': 3.31, 'int_struct': 'H', 'float_struct': 'e'},
        32: {'exp': 8, 'significand': 24, 'digits': 7.22, 'int_struct': 'I', 'float_struct': 'f'},
        64: {'exp': 11, 'significand': 53, 'digits': 15.95, 'int_struct': 'Q', 'float_struct': 'd'},
        # 128: {'exp': 15, 'significand': 113, 'digits': 34.02, 'int_struct': 'H', 'float_struct': 'e'}
    }

    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)
        pass

    def generate(self, size: int = 32):
        b = 2
        q = size
        if size in self.ieee_floats:
            emax = 2 ** (self.ieee_floats[size]['exp'] - 1) - 1
            emin = 1 - emax
            p = self.ieee_floats[size]['significand']
            value = self.random.uniform(-2 ** (emin+1), 2 ** emax)
            if size == 16:
                value = struct.unpack(self.ieee_floats[size]['float_struct'],
                              struct.pack(self.ieee_floats[size]['float_struct'], value))[0]
            return value
        else:
            raise ValueError("Size {} is not valid for IEEE floats.".format(size))


# import random
# import struct
#
# class FloatGenerator:
#     ieee_floats = {
#         16: {'exp': 5, 'significand': 11, 'digits': 3.31, 'int_struct': 'H', 'float_struct': 'e'},
#         32: {'exp': 8, 'significand': 24, 'digits': 7.22, 'int_struct': 'I', 'float_struct': 'f'},
#         64: {'exp': 11, 'significand': 53, 'digits': 15.95, 'int_struct': 'Q', 'float_struct': 'd'},
#         #128: {'exp': 15, 'significand': 113, 'digits': 34.02, 'int_struct': 'H', 'float_struct': 'e'}
#     }
#
#     def __init__(self, seed: int = 0):
#         self.random = random.Random(seed)
#         pass
#
#     def generate(self, size: int = 32):
#         b = 2
#         q = size
#         if size in self.ieee_floats:
#             value = 0
#             value |= self.random.getrandbits(1) << size - 1
#             value |= self.random.getrandbits(self.ieee_floats[size]['exp']) << self.ieee_floats[size]['significand']
#             value |= self.random.getrandbits(self.ieee_floats[size]['significand'])
#             result = struct.unpack(self.ieee_floats[size]['float_struct'],struct.pack(self.ieee_floats[size]['int_struct'],value))[0]
#             return result #self.random.uniform(-2 ** (emin+1), 2 ** emax)
#         else:
#             raise ValueError("Size {} is not valid for IEEE floats.".format(size))

