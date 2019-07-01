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
        buffer[*offset-1].last = false;
    }
    *offset += length;
    buffer[*offset-1].last = true;
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
        buffer[*offset-1].last = false;
    }
    *offset += length;
    buffer[*offset-1].last = true;
}

