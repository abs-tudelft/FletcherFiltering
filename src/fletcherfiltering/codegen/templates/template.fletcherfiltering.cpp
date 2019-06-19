#include "fletcherfiltering.h"

bool __sql_builtin_like(char* data, int len, const char* pattern_name){
    //pass to vhdre module
    return true;
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, int length, bool valid){
    if(!valid)
        return;
    __sql_builtin_concat(buffer, offset, value, length);
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, int length){
    for(int i = 0, j = *offset; i < length && j < VAR_LENGTH; i++, (j)++){
        #pragma HLS PIPELINE II=1
        buffer[j].data = value[i].data;
    }
    *offset += length;
    buffer[*offset].data = '\0';
    buffer[*offset].last = true;
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, int length, bool valid){
    if(!valid)
        return;
    __sql_builtin_concat(buffer, offset, value, length);
}

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, int length){
    for(int i = 0, j = *offset; i < length && j < VAR_LENGTH; i++, (j)++){
        #pragma HLS PIPELINE II=1
        buffer[j].data = value[i];
    }
    *offset += length;
    buffer[*offset].data = '\0';
    buffer[*offset].last = true;
}

