@echo off
setlocal
chcp 65001 >nul

set "PROJECT_DIR=C:\Users\hamidreza\.codex\.chatgpt-projects\g-p-6ad12fa783a08191b382f220c2c6e158\clinita"

if not exist "%PROJECT_DIR%\.git" (
  echo ERROR: The Clinita Git repository was not found.
  echo Expected folder: %PROJECT_DIR%
  pause
  exit /b 1
)

cd /d "%PROJECT_DIR%"

echo.
echo Current changes:
git status --short
echo.
set /p "COMMIT_MESSAGE=Describe this change, then press Enter: "

if "%COMMIT_MESSAGE%"=="" (
  echo No description was entered. Nothing was sent.
  pause
  exit /b 0
)

git add -A
git diff --cached --quiet
if not errorlevel 1 (
  echo No new changes were found. Nothing was sent.
  pause
  exit /b 0
)

git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
  echo Commit failed. Nothing was sent to GitHub.
  pause
  exit /b 1
)

git push
if errorlevel 1 (
  echo Push failed. Your commit was saved locally and can be pushed later.
  pause
  exit /b 1
)

echo.
echo Success: changes were sent to GitHub.
pause
