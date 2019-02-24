#include "query.h" 

bool query(in_schema& in_data, out_schema& out_data) {
    int32_t id;
    (in_data.id >> id);
    int32_t string1_len;
    (in_data.string1_len >> string1_len);
    char string1[255];
    for (int i = 0; i < string1_len; i += 1) {
        (in_data.string1 >> string1[i]);
    }
    int32_t string2_len;
    (in_data.string2_len >> string2_len);
    char string2[255];
    for (int i = 0; i < string2_len; i += 1) {
        (in_data.string2 >> string2[i]);
    }
    //Start of data processing
    int32_t id_o = id;
    char* string1_o = string1;
    int string1_o_len = string1_len;
    char* string2_o = string2;
    int string2_o_len = string2_len;
    bool __pass_record = true;
    //End of data processing
    if (__pass_record) {
        (out_data.id << id_o);
        (out_data.string1_len << string1_o_len);
        for (int i = 0; i < string1_o_len; i += 1) {
            (out_data.string1 << string1_o[i]);
        }
        (out_data.string2_len << string2_o_len);
        for (int i = 0; i < string2_o_len; i += 1) {
            (out_data.string2 << string2_o[i]);
        }
    }
    
    return __pass_record;
}
