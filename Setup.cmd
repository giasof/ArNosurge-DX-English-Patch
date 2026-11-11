@echo off
setlocal
if not exist "%~dp0runtime\python.exe" goto source
if "%~1"=="" (
    start "" /wait "%~dp0Setup.exe"
) else (
    "%~dp0runtime\python.exe" -I -B -u -X utf8 "%~dp0install.py" %*
)
exit /b %errorlevel%
:source
echo This is the source archive. Download and extract the Windows x64 portable ZIP:
echo https://github.com/giasof/ArNosurge-DX-English-Patch/releases/latest
pause
exit /b 1
