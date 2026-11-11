@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -B "%~dp0setup_menu.py"
goto done
:usepython
python -B "%~dp0setup_menu.py"
:done
pause
