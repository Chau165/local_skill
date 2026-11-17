@echo off
setlocal
set HYPERFRAMES_SKIP_SKILLS=1
set HYPERFRAMES_NO_UPDATE_CHECK=1
set DO_NOT_TRACK=1
node "%USERPROFILE%\.agents\skills\hyperframes\scripts\plugin-cli.mjs" %*
exit /b %errorlevel%
