#!/bin/bash

## project, compile_path
run_fetchgen_docker(){
    ACTION_ROOT=`pwd`/$1
    COMPILE_PATH=`realpath $2`

    docker run --rm -v $COMPILE_PATH:/source -v $ACTION_ROOT/hw:/output -it --entrypoint /bin/bash fletchgen:develop -c "cd /output && fletchgen -i /source/ff_in.fbs /source/ff_out.fbs -l vhdl --axi --sim -r /source/$1_data.rb -s /source/$1_data.srec -f -n Fletcher$1"
}

## project, compile_path
run_fetchgen(){
    ACTION_ROOT=`pwd`/$1
    COMPILE_PATH=`realpath $2`
    pushd $ACTION_ROOT/hw
    fletchgen -i $COMPILE_PATH/ff_in.fbs $COMPILE_PATH/ff_out.fbs -l vhdl --axi --sim -r $COMPILE_PATH/$1_data.rb -s $COMPILE_PATH/$1_data.srec -f -n Fletcher$1
    popd
}

usage()
{
    echo "usage: $(basename $BASH_SOURCE) -p project -o ../fletcherfiltering_test_workspace/<project> | [-h]]"
}

docker=
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
        -d | --docker )         docker=1
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

if [ "$docker" = "1" ]; then
	echo "Running in docker..."
    run_fetchgen_docker $project $compile_path
else
	echo "Running directly..."
    run_fetchgen $project $compile_path
fi

