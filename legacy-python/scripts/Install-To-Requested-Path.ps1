[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Source = Split-Path -Parent $PSScriptRoot
$Destination = "C:\DevTools\FullBuilds_Unsigned\heic_to_jpg_convert_TCDOVERLORD"

$SourceFull = [System.IO.Path]::GetFullPath($Source).TrimEnd("\")
$DestinationFull = [System.IO.Path]::GetFullPath($Destination).TrimEnd("\")

if ($SourceFull -ieq $DestinationFull) {
    Write-Host "The project is already in the requested location:"
    Write-Host $Destination
    exit 0
}

if (Test-Path $Destination) {
    throw "The destination already exists. Nothing was overwritten: $Destination"
}

$Parent = Split-Path -Parent $Destination
New-Item -ItemType Directory -Force -Path $Parent | Out-Null

Write-Host "Copying project to:"
Write-Host $Destination

& robocopy.exe `
    $Source `
    $Destination `
    /E `
    /R:2 `
    /W:1 `
    /XD ".venv" ".git" ".pytest_cache" "__pycache__" "build_output" `
    /XF "*.pyc" "*.log"

$RoboCopyExitCode = $LASTEXITCODE
if ($RoboCopyExitCode -ge 8) {
    throw "Copy failed with Robocopy exit code $RoboCopyExitCode."
}

Write-Host ""
Write-Host "Project installed successfully."
Write-Host "Next: open the destination and run RUN_FROM_SOURCE.bat."
