Param(
    [parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Passthrough
)
conda activate FletcherFiltering
$pwd = Get-Location
$env:PYTHONPATH ="$pwd\src;$pwd\..\transpyle;$pwd\..\fletcher\codegen;$pwd\..\moz-sql-parser"

python -m pytest -rxXs --show-progress --print-relative-time --verbose --cov=fletcherfiltering @Passthrough tests/
