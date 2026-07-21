[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    & (Join-Path $PSScriptRoot "Setup-Environment.ps1")
}

Set-Location $ProjectRoot
& $VenvPython -m pytest -q
if ($LASTEXITCODE -ne 0) {
    throw "Tests failed. The build was stopped."
}
