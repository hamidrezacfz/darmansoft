@echo off
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%.venv\Scripts\python.exe"

rem If the program is already running, just open it.
netstat -ano | findstr /R /C:"127.0.0.1:8001 .*LISTENING" >nul
if not errorlevel 1 goto open_browser

if not exist "%PYTHON_EXE%" (
  echo Python environment was not found.
  echo Expected: %PYTHON_EXE%
  pause
  exit /b 1
)

start "Clinita Server" /min "%PYTHON_EXE%" "%PROJECT_DIR%manage.py" runserver 127.0.0.1:8001 --noreload
timeout /t 3 /nobreak >nul

:open_browser
set "EDGE_EXE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE_EXE%" set "EDGE_EXE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
if exist "%EDGE_EXE%" (
  start "Clinita" "%EDGE_EXE%" "http://127.0.0.1:8001/login/"
) else (
  start "" "http://127.0.0.1:8001/login/"
)

