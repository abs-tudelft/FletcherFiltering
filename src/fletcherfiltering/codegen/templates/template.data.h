#pragma once
#include "${query_name}${test_suffix}.h"

int ${query_name}_data_N = ${data_N_placeholder};

in_schema${test_suffix} ${query_name}${data_suffix}[] = {
    ${data_placeholder},
};
