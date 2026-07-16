[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$repositoryRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
& python (Join-Path $repositoryRoot "scripts/install_skills.py") @RemainingArgs
exit $LASTEXITCODE
