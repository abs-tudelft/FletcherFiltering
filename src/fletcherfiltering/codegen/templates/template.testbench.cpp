/*
 * Copyright (c) 2019 Erwin de Haan. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *  This file is part of the FletcherFiltering project
 */

#include "${query_name}${test_suffix}.h"
#include "${query_name}${data_suffix}.h"
#include <iostream>

int main(){
	in_schema${test_suffix} in;
	out_schema${test_suffix} out;
	RecordBatchMeta meta;
	meta.length = ${query_name}_data_N;
	bool passed;
    std::cout << "==================== Start ====================" << std::endl;
    ${out_columns_tb_new}

    for(int i=0; i<${query_name}${data_suffix}_N;i++){
        in = ${query_name}${data_suffix}[i];
        passed = ${query_name}${test_suffix}(meta, in, out);
        if(passed){
            std::cout << 'o';
        } else {
            std::cout << 'x';
        }
    }

    ${out_columns_tb_delete}

    std::cout << std::endl << "===================== End =====================" << std::endl;
}