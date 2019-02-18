#pragma once
#define STRING_SIZE 255

template <typename T> 
struct nullable {
    bool valid;
    T value; 
};

bool __sql_builtin_like(char* data, int len, const char* pattern_name);

void __sql_builtin_concat(char* buffer, int* offset, const char* value, int length);
