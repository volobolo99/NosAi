@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>&1
if %errorlevel%==0 (
    py scripts\launch_nosai.py
) else (
    python scripts\launch_nosai.py
)
if errorlevel 1 pause
endlocal
