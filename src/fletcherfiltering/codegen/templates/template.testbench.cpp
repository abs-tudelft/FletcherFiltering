#include "${query_name}${test_suffix}.h"
#include "${query_name}${data_suffix}.h"
#include <iostream>

int main(){
	in_schema${test_suffix} in;
	out_schema${test_suffix} out;
	bool passed;
    std::cout << "==================== Start ====================" << std::endl;
    ${out_columns_tb_new}

    for(int i=0; i<${query_name}${data_suffix}_N;i++){
        in = ${query_name}${data_suffix}[i];
        passed = ${query_name}${test_suffix}(in, out);
        if(passed){
            std::cout << 'o';
        } else {
            std::cout << 'x';
        }
    }

    ${out_columns_tb_delete}

    std::cout << std::endl << "===================== End =====================" << std::endl;
}