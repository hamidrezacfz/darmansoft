@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

if not exist ".git" (
  echo ERROR: This folder is not a Git repository.
  pause
  exit /b 1
)

set "HAS_CHANGES="
for /f "delims=" %%A in ('git status --porcelain') do set "HAS_CHANGES=1"

if defined HAS_CHANGES (
  echo.
  echo Local changes were found. Nothing was downloaded.
  echo First send your local changes to GitHub, then try again.
  pause
  exit /b 1
)

echo.
echo Receiving the latest changes from GitHub...
git pull --ff-only

if errorlevel 1 (
  echo.
  echo Update failed. Your local files were not changed.
  pause
  exit /b 1
)

echo.
echo Success: this computer now has the latest GitHub version.
pause
