#!/bin/bash

#source activate FletcherFiltering

PYTHONPATH="$PYTHONPATH:`pwd`/src:`pwd`/../fletcher/codegen" python3 -m pytest -rxXs --show-progress --print-relative-time --verbose --cov=fletcherfiltering "$@" tests/
