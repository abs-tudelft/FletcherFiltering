#include <iostream>
#include "fletcherfiltering.h"
#include "query.h"

int main() {

    in_schema in;
    out_schema out;

    int id = 1;
    int int1 = 2347645;
    int int2 = 123325;
    int string1_len = 11;
    char string1[STRING_SIZE] = "abcdefghijk";
    unsigned long long timestamp1 = 1544620718000ul;


    in.id.write(id);
    in.int1.write(int1);
    in.int2.write(int2);
    in.string1_len.write(string1_len);
    for(int i = 0; i<string1_len; i++) {
        in.string1.write(string1[i]);
    }
    in.timestamp1.write(timestamp1);

    query(in,out);

    if(!out.int1.empty()) {
        int int1_o = out.int1.read();
        int concat_o_len = out.concat_len.read();
        char concat_o[STRING_SIZE];
        for (int i = 0; i < concat_o_len; i++)
            concat_o[i] = out.concat.read();

        concat_o[concat_o_len] = '\0';

        int concat2_o_len = out.concat2_len.read();
        char concat2_o[STRING_SIZE];
        for (int i = 0; i < concat2_o_len; i++)
            concat2_o[i] = out.concat2.read();

        concat2_o[concat2_o_len] = '\0';

        std::cout << "int1: " << int1_o << std::endl;
        std::cout << "concat (" << concat_o_len << "): " << concat_o << std::endl;
        std::cout << "concat2 (" << concat2_o_len << "): " << concat2_o << std::endl;
    } else {
        std::cout << "Record didn't match." << std::endl;
    }
    return 0;
}