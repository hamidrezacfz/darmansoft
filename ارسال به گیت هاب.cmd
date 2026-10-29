@echo off
setlocal
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

if not exist ".git" (
  echo ERROR: Git repository was not found in this folder.
  pause
  exit /b 1
)

echo.
echo Current changes:
git status --short
echo.
set /p "COMMIT_MESSAGE=Commit message: "

if "%COMMIT_MESSAGE%"=="" (
  echo No message entered. Nothing was sent.
  pause
  exit /b 0
)

git add -A
git diff --cached --quiet
if not errorlevel 1 (
  echo No changes found. Nothing was sent.
  pause
  exit /b 0
)

git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
  echo Commit failed. Nothing was sent.
  pause
  exit /b 1
)

git push origin main
if errorlevel 1 (
  echo Push failed. The local commit was kept.
  pause
  exit /b 1
)

echo.
echo Changes were sent to GitHub successfully.
pause
