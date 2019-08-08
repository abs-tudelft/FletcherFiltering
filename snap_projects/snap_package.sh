#!/bin/bash
ROOT_DIR=$(dirname $(readlink -f "$BASH_SOURCE"))

set -e

## project, compile_path, action
package(){
    ACTION_ROOT=`pwd`/$3
    PACKAGE_ROOT=`pwd`/${3}_pkg
    COMPILE_PATH=`realpath $2`
    IP_PATH=$COMPILE_PATH/$1/automated_tests/impl/ip/hdl/vhdl
    FLETCHER_HARDWARE_PATH=$FLETCHER_DIR/hardware
    
    rm -f package.tar.gz 2>/dev/null  # remove tar if there    
    rm -rf $PACKAGE_ROOT

    mkdir -p $PACKAGE_ROOT/hw/deps
    mkdir -p $PACKAGE_ROOT/data
    mkdir -p $PACKAGE_ROOT/src

    cp $COMPILE_PATH/*.rb $PACKAGE_ROOT/data
    cp $COMPILE_PATH/*.fbs $PACKAGE_ROOT/data
    cp $COMPILE_PATH/*.cpp $PACKAGE_ROOT/src
    cp $COMPILE_PATH/*.h $PACKAGE_ROOT/src
    cp $COMPILE_PATH/*.tcl $PACKAGE_ROOT/src
    cp $COMPILE_PATH/CMakeLists.txt $PACKAGE_ROOT/src

    cp -R $ACTION_ROOT/* $PACKAGE_ROOT
    cp $ROOT_DIR/snap_script.sh $PACKAGE_ROOT
    find $PACKAGE_ROOT -type l -delete;

    FILES=`vhdeps -i $FLETCHER_HARDWARE_PATH -i $IP_PATH -i $PACKAGE_ROOT/hw dump SimTop_tc | awk '{print $NF}'`
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
            mkdir -p $PACKAGE_ROOT/hw/deps/$DEST
            cp $file $PACKAGE_ROOT/hw/deps/$DEST
        fi
    done    
    echo "Creating $1_pkg.tar.gz"
    tar -czvaf $1_pkg.tar.gz ${3}_pkg -C $PACKAGE_ROOT
    #rm -rf $PACKAGE_ROOT
}

usage()
{
    echo "usage: $(basename $BASH_SOURCE) -p project -o ../fletcherfiltering_test_workspace/<project> -a projectSnapAction | [-h]]"
}

action=SimpleSnapAction
project=Simple
action=${project}SnapAction
compile_path=../fletcherfiltering_test_workspace/$project

while [ "$1" != "" ]; do
    case $1 in
        -a | --action )         shift
                                action=$1
                                ;;
        -p | --project )        shift
                                project=$1
                                ;;
        -o | --compile_path )   shift
                                compile_path=$1
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
package $project $compile_path $action