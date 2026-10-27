@echo off
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%.venv\Scripts\python.exe"

rem Start the local development server on the address used during development.
netstat -ano | findstr /R /C:"127.0.0.1:8000 .*LISTENING" >nul
if not errorlevel 1 goto open_browser

start "DarmanSoft Development Server" /min "%PYTHON_EXE%" "%PROJECT_DIR%manage.py" runserver 127.0.0.1:8000
timeout /t 3 /nobreak >nul

:open_browser
start "" "http://127.0.0.1:8000/login/"
