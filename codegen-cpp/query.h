#pragma once
#include "hls_stream.h"
#include "hls_half.h"
#include "fletcherfiltering.h" 


struct in_schema {
    hls::stream<int32_t> id;
    hls::stream<char> string1;
    hls::stream<int32_t> string1_len;
    hls::stream<char> string2;
    hls::stream<int32_t> string2_len;
};


struct out_schema {
    hls::stream<int32_t> id;
    hls::stream<char> string1;
    hls::stream<int32_t> string1_len;
    hls::stream<char> string2;
    hls::stream<int32_t> string2_len;
};
bool query(in_schema& in_data, out_schema& out_data);
