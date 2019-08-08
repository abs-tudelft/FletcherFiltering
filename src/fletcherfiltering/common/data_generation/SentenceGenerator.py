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

from fletcherfiltering.common.data_generation.BaseGenerator import BaseGenerator
import lipsum
from fletcherfiltering import settings
import random

class SentenceGenerator(BaseGenerator):

    def generate(self, maxlength: int = settings.VAR_LENGTH) -> str:
        if random.random() < settings.EMPTYSTRINGPROBABILITY:
            return ""
        sentence = lipsum.generate_sentences(1)
        if len(sentence) > maxlength:
            indexes = [pos for pos, char in enumerate(sentence) if char == ' ' and pos < maxlength]
            if len(indexes) == 0:
                sentence = sentence[:maxlength]
            else:
                sentence = sentence[:indexes[-1]]
        return sentence
