#include "query_test.h" 
extern "C" {

bool query_test(in_schema_test& in_data_test, out_schema_test& out_data_test) {
    in_schema in_data;
    out_schema out_data;
    (in_data.id << in_data_test.id);
    int32_t string1_len = strlen(in_data_test.string1);
    (in_data.string1_len << string1_len);
    for (int i = 0; i < string1_len; i += 1) {
        (in_data.string1 << in_data_test.string1[i]);
    }
    int32_t string2_len = strlen(in_data_test.string2);
    (in_data.string2_len << string2_len);
    for (int i = 0; i < string2_len; i += 1) {
        (in_data.string2 << in_data_test.string2[i]);
    }
    //Start of query code
    bool __pass_record = query(in_data, out_data);
    //End of query code
    if (__pass_record) {
        (out_data.id >> out_data_test.id);
        int32_t string1_o_len;
        (out_data.string1_len >> string1_o_len);
        for (int i = 0; i < string1_o_len; i += 1) {
            (out_data.string1 >> out_data_test.string1[i]);
        }
        out_data_test.string1[string1_o_len] = '\0';
        int32_t string2_o_len;
        (out_data.string2_len >> string2_o_len);
        for (int i = 0; i < string2_o_len; i += 1) {
            (out_data.string2 >> out_data_test.string2[i]);
        }
        out_data_test.string2[string2_o_len] = '\0';
    }
    
    return __pass_record;
}
}