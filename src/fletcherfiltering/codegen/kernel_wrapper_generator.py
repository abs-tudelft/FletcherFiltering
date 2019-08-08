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

import jinja2 as j2
import pyarrow as pa
from .compiler import TemplateData
from collections import namedtuple
from fletcherfiltering import settings

from fletcherfiltering.common.helpers.struct_type_mapper import StructTypeMapper

VHDLSignalData = namedtuple('VHDLSignalData', ['schema_name', 'stream_name', 'data_size', 'nullable', 'total_size'])

def generate_kernel_wrapper(template: TemplateData, in_schema: pa.Schema, out_schema: pa.Schema, query_name: str, primary_key: str):
    stm = StructTypeMapper()

    in_signals = []
    out_signals = []

    for col in in_schema:
        _, data_size = stm.resolve(col.type)
        in_signals.append(VHDLSignalData(
            settings.INPUT_NAME,
            col.name,
            data_size,
            col.nullable,
            data_size+(3 if col.nullable else 2)
        ))

    for col in out_schema:
        _, data_size = stm.resolve(col.type)
        out_signals.append(VHDLSignalData(
            settings.OUTPUT_NAME,
            col.name,
            data_size,
            col.nullable,
            data_size+(3 if col.nullable else 2)
        ))

    with open(template.source, 'r') as template_file:
        output_data = j2.Template(template_file.read())
        with open(template.destination, 'w') as output_file:
            output_file.write(output_data.render(settings=settings, in_signals=in_signals, out_signals=out_signals, query_name=query_name, primary_key=primary_key))
