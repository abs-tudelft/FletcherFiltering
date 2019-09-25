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

import glob
import pyarrow as pa

path = 'fletcherfiltering_test_workspace'
files = [f for f in glob.glob(path + "/**/*_data.rb", recursive=True)]

for file in files:
    print("Reading file {}..".format(file))
    reader = pa.RecordBatchFileReader(file)
    input_batch = reader.get_batch(0)
    str_cols = []
    for col in input_batch.columns:
        if isinstance(col, pa.StringArray):
            print("Found string col avg length: {}".format(sum([len(s.as_py()) if s.as_py() is not None else 0 for s in col])/len(col)))



