#pragma once
#include <inttypes.h>
#include <fletcher/api.h>
#define VAR_LENGTH ${VAR_LENGTH}


bool __sql_builtin_like(char* data, int len, const char* pattern_name);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, f_base_length_type length);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, f_base_length_type length, bool valid);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, nullable<f_int32> length);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, f_int32 length);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, f_base_length_type length, bool valid);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, f_base_length_type length);
