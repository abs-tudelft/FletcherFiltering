#!/bin/bash
ROOT_DIR=$(dirname $(readlink -f "$BASH_SOURCE"))

set -e

## project, compile_path, backend
run_vhdeps(){
    ACTION_ROOT=`pwd`/$1
    COMPILE_PATH=`realpath $2`
    IP_PATH=$COMPILE_PATH/$1/automated_tests/impl/ip/hdl/vhdl
    FLETCHER_HARDWARE_PATH=$FLETCHER_DIR/hardware
    
    rm -f package.tar.gz 2>/dev/null  # remove tar if there    
    rm -rf $ACTION_ROOT/hw/deps
    rm -rf $ACTION_ROOT/data
    rm -rf $ACTION_ROOT/src

    mkdir -p $ACTION_ROOT/hw/deps
    mkdir -p $ACTION_ROOT/data
    mkdir -p $ACTION_ROOT/src

    cp $COMPILE_PATH/*.rb $ACTION_ROOT/data
    cp $COMPILE_PATH/*.fbs $ACTION_ROOT/data
    cp $COMPILE_PATH/*.cpp $ACTION_ROOT/src
    cp $COMPILE_PATH/*.h $ACTION_ROOT/src
    cp $COMPILE_PATH/*.tcl $ACTION_ROOT/src
    cp $COMPILE_PATH/CMakeLists.txt $ACTION_ROOT/src

    FILES=`vhdeps -i $FLETCHER_HARDWARE_PATH -i $IP_PATH -i $ACTION_ROOT/hw $3 SimTop_tc | awk '{print $NF}'`
    PREFIX=`printf "%s\n" "${FILES[@]}" | sed -e 'N;s/^\(.*\).*\n\1.*$/\1\n\1/;D'`

    echo "Longest common prefix $PREFIX"

    for file in ${FILES}; do
        if [ "${file##${ACTION_ROOT}}" == "${file}" ]; then
            if [ "${file##${COMPILE_PATH}}" != "${file}" ]; then                
                DEST=ip/$(dirname ${file##${COMPILE_PATH}})                
            elif [ "${file##${FLETCHER_HARDWARE_PATH}}" != "${file}" ]; then                
                DEST=fletcher/$(dirname ${file##${FLETCHER_HARDWARE_PATH}})                
            else
                DEST=$(dirname ${file##${PREFIX}})
            fi
            echo "Collecting ${file} to deps $(dirname ${file##${PREFIX}}) directory."
            mkdir -p $ACTION_ROOT/hw/deps/$DEST
            cp $file $ACTION_ROOT/hw/deps/$DEST
        fi
    done    
    echo "Creating $1_pkg.tar.gz"
    tar -czvaf $1_pkg.tar.gz $1 snap_script.sh -C $ACTION_ROOT
}

usage()
{
    echo "usage: $(basename $BASH_SOURCE) -p project -o ../fletcherfiltering_test_workspace/<project> [-b backend] | [-h]]"
}

backend=ghdl
project=Simple
compile_path=../fletcherfiltering_test_workspace/$project

while [ "$1" != "" ]; do
    case $1 in
        -p | --project )        shift
                                project=$1
                                ;;
        -o | --compile_path )   shift
                                compile_path=$1
                                ;;
        -b | --backend )        shift
                                backend=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

# Test code to verify command line processing
echo "Project: $project"
echo "Compile Path: $compile_path"
echo "Fletcher Path: $FLETCHER_DIR/hardware"
echo "Vhdeps Backend: $FLETCHER_DIR/hardware"
run_vhdeps $project $compile_path $backend