@echo off
setlocal
codex -C "%~dp0.." %*
exit /b %errorlevel%
