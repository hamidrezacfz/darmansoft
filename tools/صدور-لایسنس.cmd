@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%..\.venv\Scripts\python.exe"
set "ISSUER_SCRIPT=%SCRIPT_DIR%issue_license.py"

if not exist "%PYTHON_EXE%" goto :missing_python

echo ==============================================
echo        DarmanSoft Offline License Issuer
echo ==============================================
set /p "MACHINE_ID=Customer Device ID: "
if "%MACHINE_ID%"=="" goto :missing_device
set /p "CUSTOMER=Customer or clinic name: "
set /p "PLAN=Plan (demo / base / support / custom) [base]: "
if "%PLAN%"=="" set "PLAN=base"
set /p "EXPIRY=Expiry date YYYY-MM-DD (leave blank for permanent): "

echo.
echo Activation code - copy ALL of it and send it to the customer:
if "%EXPIRY%"=="" goto :permanent
"%PYTHON_EXE%" "%ISSUER_SCRIPT%" --machine-id "%MACHINE_ID%" --customer "%CUSTOMER%" --plan "%PLAN%" --expires-on "%EXPIRY%"
goto :done

:permanent
"%PYTHON_EXE%" "%ISSUER_SCRIPT%" --machine-id "%MACHINE_ID%" --customer "%CUSTOMER%" --plan "%PLAN%"
goto :done

:missing_python
echo ERROR: Project Python was not found.
echo Expected: "%PYTHON_EXE%"
goto :done

:missing_device
echo ERROR: Device ID cannot be empty.

:done
echo.
pause
