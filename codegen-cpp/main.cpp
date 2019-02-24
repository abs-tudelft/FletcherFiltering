#include <iostream>
#include "fletcherfiltering.h"
#include "query_test.h"

int main() {

    in_schema_test in;
    out_schema_test out;

    in.id = 1;
    in.string1 = "abcdefghijk, sdoifghdsfgsbfgshdfbsifgb8sdfjsdif sbf sdbfis df bsdjns kdfs fisbd fjsodnfisnf sbdif sd bsbg";
    in.string2 = "abcdefghijk, sdoifghdsfgsbfgshdfbsifgb8sdfjsdif haohgw8y245bhwe9y713rbi2 25 ghu924y24tbj24t stfgswr tgwerw4t wrt2 45rt2 45625";


    std::cout << "Input:" << std::endl;
    std::cout << "id: " << in.id << std::endl;
    std::cout << "string1 (" << strlen(in.string1) << "): " << in.string1 << std::endl;
    std::cout << "string2 (" << strlen(in.string2) << "): " << in.string2 << std::endl;


    out.string1 = (char*)malloc(sizeof(char)*256);
    out.string2 = (char*)malloc(sizeof(char)*256);

    bool matched = query_test(in, out);


    if(matched) {
        std::cout << "Output:" << std::endl;
        std::cout << "id: " << out.id << std::endl;
        std::cout << "string1 (" << strlen(out.string1) << "): " << out.string1 << std::endl;
        std::cout << "string2 (" << strlen(out.string2) << "): " << out.string2 << std::endl;
    } else {
        std::cout << "Record didn't match." << std::endl;
    }

    free(out.string1);
    free(out.string2);

    return 0;
}