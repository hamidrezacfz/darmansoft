@echo off
setlocal EnableExtensions

rem Build the time-limited demo executable, then package it with Inno Setup.
cd /d "%~dp0"

set "PYTHON=.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo ERROR: Project virtual environment was not found: %PYTHON%
    echo Create or restore .venv before building the demo.
    pause
    exit /b 1
)

set "DARMANSOFT_DEMO_BUILD=1"
echo.
echo [1/2] Building DarmanSoft Demo executable...
"%PYTHON%" -m PyInstaller --noconfirm --clean installer\Clinita.spec --workpath installer\work --distpath installer\dist
if errorlevel 1 goto :build_failed

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo ERROR: Inno Setup 6 was not found.
    echo Install Inno Setup 6 and run this file again.
    pause
    exit /b 1
)

echo.
echo [2/2] Building demo installer...
"%ISCC%" "installer\darmansoft-demo.iss"
if errorlevel 1 goto :build_failed

echo.
echo Demo setup created in: output\demo
start "" explorer "output\demo"
exit /b 0

:build_failed
echo.
echo ERROR: Demo build failed. Review the messages above.
pause
exit /b 1
