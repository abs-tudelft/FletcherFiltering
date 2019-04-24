#include "fletcherfiltering.h"

bool __sql_builtin_like(char* data, int len, const char* pattern_name){
    //pass to vhdre module
    return true;
}

void __sql_builtin_concat(char* buffer, int* offset, const char* value, int length){
    for(int i = 0; i < length && *offset < STRING_SIZE; i++, (*offset)++){
        buffer[*offset] = value[i];
    }
    buffer[*offset] = '\0';
}