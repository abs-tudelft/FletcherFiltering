#!/usr/bin/env bash

docker run --rm -v `pwd`/fletcherfiltering_test_workspace/Simple:/source -v `pwd`/snap_fletcher/hw:/output -it --entrypoint /bin/bash fletchgen:develop -c "cd /output && fletchgen -i /source/in.fbs /source/out.fbs --axi -f -n FletcherSimple"