#pragma once
#include "hls_stream.h"
#include "query.h" 

extern "C" {


struct in_schema_test {
    int32_t id;
    char* string1;
    char* string2;
};


struct out_schema_test {
    int32_t id;
    char* string1;
    char* string2;
};
bool query_test(in_schema_test& in_data_test, out_schema_test& out_data_test);
}