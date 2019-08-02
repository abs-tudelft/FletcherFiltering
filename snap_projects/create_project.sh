#!/bin/bash

set -e

## project
create(){
    ACTION_ROOT=`pwd`/$1
    BASE_PATH=`pwd`/_base

    mkdir -p $ACTION_ROOT/hw
    mkdir -p $ACTION_ROOT/sw

    cp $BASE_PATH/action_*.vhd $ACTION_ROOT/hw
    cp $BASE_PATH/Kernel.vhd $ACTION_ROOT/hw/Fletcher$1.vhd
    cp $BASE_PATH/sw.Makefile $ACTION_ROOT/sw/Makefile
    cp $BASE_PATH/hw.Makefile $ACTION_ROOT/hw/Makefile
    cp $BASE_PATH/Makefile $ACTION_ROOT/Makefile./
}

usage()
{
    echo "usage: $(basename $BASH_SOURCE) -p project | [-h]]"
}

project=New

while [ "$1" != "" ]; do
    case $1 in
        -p | --project )        shift
                                project=$1
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
create $project