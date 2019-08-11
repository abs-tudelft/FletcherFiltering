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

 #include "fletcherfiltering.h"

bool __sql_builtin_like(char* data, int len, const char* pattern_name){
    //pass to vhdre module
    return true;
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, f_base_length_type length, bool valid){
    if(!valid)
        return;
    __sql_builtin_concat(buffer, offset, value, length);
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, nullable<f_int32> length){
    if(!length.valid)
        return;
    __sql_builtin_concat(buffer, offset, value, length.data);
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, f_int32 length){
    __sql_builtin_concat(buffer, offset, value, length.data);
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, f_base_length_type length){
    for(int i = 0, j = *offset; i < length && j < VAR_LENGTH; i++, (j)++){
        #pragma HLS PIPELINE II=1
        buffer[j].data = value[i].data;
    }
    if(*offset>0){
        buffer[*offset].last = false;
    }
    *offset += length;
    if(*offset>=0){
    	buffer[*offset].last = true;
    }
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, f_base_length_type length, bool valid){
    if(!valid)
        return;
    __sql_builtin_concat(buffer, offset, value, length);
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, f_base_length_type length){
    for(int i = 0, j = *offset; i < length && j < VAR_LENGTH; i++, (j)++){
        #pragma HLS PIPELINE II=1
        buffer[j].data = value[i];
    }
    if(*offset>0){
        buffer[*offset].last = false;
    }
    *offset += length;
    if(*offset>=0){
    	buffer[*offset].last = true;
    }
}

