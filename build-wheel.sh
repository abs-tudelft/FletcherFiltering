#!/usr/bin/env bash

#eval "$(conda shell.bash hook)"

#conda activate FletcherFiltering

PYTHONPATH="$PYTHONPATH:`pwd`/src:" python setup.py bdist_wheel
