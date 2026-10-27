@echo off
setlocal
set "REGISTRY=%~dp0license-registry.csv"
if not exist "%REGISTRY%" (
  echo No license has been issued yet.
  pause
  exit /b 0
)
start "" notepad.exe "%REGISTRY%"
