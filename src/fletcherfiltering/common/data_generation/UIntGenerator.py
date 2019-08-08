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


class UIntGenerator:
    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)
        pass

    def generate(self, size: int = 32, limit_to_signed: bool = False):
        # Because numpy datetime64 is signed.
        if limit_to_signed:
            size = size - 1
        return self.random.randint(0, 2 ** size - 1)


