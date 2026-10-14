@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Setup-Environment.ps1"
if errorlevel 1 (
    echo.
    echo Setup failed. Review the error above.
    pause
    exit /b 1
)

"%~dp0.venv\Scripts\pythonw.exe" "%~dp0main.py"
if errorlevel 1 (
    echo.
    echo The converter closed with an error. Review the session log.
    pause
    exit /b 1
)
