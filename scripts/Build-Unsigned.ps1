[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$BuildRoot = Join-Path $ProjectRoot "build_output"
$UnsignedRoot = Join-Path $BuildRoot "unsigned"
$WorkRoot = Join-Path $BuildRoot "work"
$ArchiveRoot = Join-Path $BuildRoot "previous"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Set-Location $ProjectRoot

& (Join-Path $PSScriptRoot "Setup-Environment.ps1")
& (Join-Path $PSScriptRoot "Run-Tests.ps1")

if (Test-Path $UnsignedRoot) {
    New-Item -ItemType Directory -Force -Path $ArchiveRoot | Out-Null
    $Archived = Join-Path $ArchiveRoot "unsigned_$Timestamp"
    Move-Item -Path $UnsignedRoot -Destination $Archived
    Write-Host "Preserved previous unsigned build at: $Archived"
}

if (Test-Path $WorkRoot) {
    Remove-Item -Recurse -Force $WorkRoot
}

New-Item -ItemType Directory -Force -Path $UnsignedRoot | Out-Null

Write-Host "Building unsigned Windows executable..."
& $VenvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --distpath $UnsignedRoot `
    --workpath $WorkRoot `
    "build_windows.spec"

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

$Exe = Join-Path $UnsignedRoot "HEIC_to_JPG_Converter_TCDOVERLORD.exe"
if (-not (Test-Path $Exe)) {
    throw "Build completed without the expected executable: $Exe"
}

Copy-Item "README.md" $UnsignedRoot
Copy-Item "LICENSE" $UnsignedRoot
Copy-Item "VERSION" $UnsignedRoot
Copy-Item "docs\SAFETY.md" $UnsignedRoot
Copy-Item "docs\TESTING.md" $UnsignedRoot

$Hash = Get-FileHash -Algorithm SHA256 $Exe
"$($Hash.Hash) *$([System.IO.Path]::GetFileName($Exe))" |
    Set-Content -Encoding ASCII (Join-Path $UnsignedRoot "SHA256SUMS.txt")

Write-Host ""
Write-Host "Unsigned build complete:"
Write-Host $Exe
Write-Host ""
Write-Warning "This executable is not digitally signed. Windows SmartScreen may warn when it is opened."
