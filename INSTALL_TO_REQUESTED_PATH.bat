@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Install-To-Requested-Path.ps1"
if errorlevel 1 (
    echo.
    echo Installation stopped. No existing destination was overwritten.
    pause
    exit /b 1
)

echo.
pause
