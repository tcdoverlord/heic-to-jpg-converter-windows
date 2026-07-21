@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Build-Unsigned.ps1"
if errorlevel 1 (
    echo.
    echo Build failed. Review the error above.
    pause
    exit /b 1
)

echo.
echo Build finished successfully.
pause
