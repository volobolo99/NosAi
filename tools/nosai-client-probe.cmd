@echo off
setlocal
python -m app.client %*
exit /b %ERRORLEVEL%
