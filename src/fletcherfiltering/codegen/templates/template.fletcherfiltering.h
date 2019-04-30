#pragma once
#include <inttypes.h>
#define VAR_LENGTH ${VAR_LENGTH}

template <typename T> 
struct nullable {
    bool valid;
    T value; 
};

bool __sql_builtin_like(char* data, int len, const char* pattern_name);

void __sql_builtin_concat(char* buffer, int* offset, const char* value, int length);
