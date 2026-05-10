@echo off
:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
) else (
    echo WARNING: This script must be run as Administrator!
    echo Attempting to restart as Administrator...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs"
    exit /b
)

powershell -NoExit -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_network_access.ps1"
