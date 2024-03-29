#!/bin/bash
ROOT_DIR=$(dirname $(readlink -f "$BASH_SOURCE"))

set -e

## project, target
run_target()
{
    ACTION_ROOT=`pwd`/$1
    sed -i "s;export ACTION_ROOT=.*;export ACTION_ROOT=${ACTION_ROOT};" $SNAP_ROOT/snap_env.sh
    make -C $SNAP_ROOT $2
}

usage()
{
    echo "usage: $(basename $BASH_SOURCE) -p Project [-t Target] | [-h]]"
}


target=sim
project=Simple

while [ "$1" != "" ]; do
    case $1 in
        -p | --project )        shift
                                project=$1
                                ;;
        -t | --target )         shift
                                target=$1
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
echo "Target: $target"
echo "SNAP Root: $SNAP_ROOT"

run_target $project $target