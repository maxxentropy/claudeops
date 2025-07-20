@echo off
REM Test suite wrapper for Windows

echo Claude Code Sync Script Test Suite
echo ==================================
echo.

REM Check if we're in Git Bash
if defined MSYSTEM (
    echo Running tests in Git Bash environment...
    bash test-sync.sh %*
    exit /b %errorlevel%
)

REM Find Git Bash
set "GIT_BASH="
if exist "%PROGRAMFILES%\Git\bin\bash.exe" (
    set "GIT_BASH=%PROGRAMFILES%\Git\bin\bash.exe"
) else if exist "%PROGRAMFILES(x86)%\Git\bin\bash.exe" (
    set "GIT_BASH=%PROGRAMFILES(x86)%\Git\bin\bash.exe"
) else if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    set "GIT_BASH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
)

if not defined GIT_BASH (
    echo Error: Git Bash not found. Please install Git for Windows.
    echo.
    echo You can also run the tests manually from Git Bash:
    echo   ./test-sync.sh
    pause
    exit /b 1
)

echo Starting tests using Git Bash...
"%GIT_BASH%" -c "./test-sync.sh %*"

if "%COMSPEC%" == "%CMDCMDLINE%" (
    echo.
    pause
)