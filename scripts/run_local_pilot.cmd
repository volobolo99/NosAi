@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_local_pilot.ps1"
if errorlevel 1 (
  echo.
  echo NosAi Test Pilot failed. Review the error above.
  pause
  exit /b 1
)
echo.
echo NosAi Test Pilot completed successfully.
pause
