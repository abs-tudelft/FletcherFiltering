#!/bin/bash

source activate FletcherFiltering

PYTHONPATH="$PYTHONPATH:`pwd`/src:`pwd`/../../transpyle:`pwd`/../../fletcher/codegen:`pwd`/../../moz-sql-parser" python -m pytest -s --show-progress --print-relative-time --verbose --cov=fletcherfiltering "$@" tests/
