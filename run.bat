@echo off
setlocal

cd /d "%~dp0"

python packager.py
if errorlevel 1 (
    echo.
    echo Clean Script Exporter exited with an error.
    pause
)

endlocal
