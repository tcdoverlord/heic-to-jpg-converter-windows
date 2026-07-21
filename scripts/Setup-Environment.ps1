[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{
            Command = "py"
            Prefix = @("-3")
        }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{
            Command = "python"
            Prefix = @()
        }
    }

    throw "Python 3 was not found. Install Python 3.10 or newer, then run this script again."
}

$Python = Get-PythonCommand
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

$VersionCheckArgs = @($Python.Prefix) + @(
    "-c",
    "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
)
& $Python.Command $VersionCheckArgs
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.10 or newer is required."
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating isolated Python environment..."
    $VenvArgs = @($Python.Prefix) + @("-m", "venv", ".venv")
    & $Python.Command $VenvArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Python could not create the virtual environment."
    }
}

Write-Host "Installing project dependencies..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "pip upgrade failed."
}

& $VenvPython -m pip install -r "requirements-build.txt"
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed."
}

Write-Host ""
Write-Host "Environment ready."
Write-Host "Python: $VenvPython"
