@echo off
REM Claude Code Configuration Sync Script for Windows
REM This is a wrapper for the bash script to work on Windows

REM Check if Git Bash is available
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in PATH
    echo Please install Git for Windows from https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

REM Check if we're in Git Bash already
if defined MSYSTEM (
    REM We're in Git Bash, run the script directly
    bash "%~dp0sync.sh" %*
    exit /b %errorlevel%
)

REM Find Git Bash executable
set "GIT_BASH="
if exist "%PROGRAMFILES%\Git\bin\bash.exe" (
    set "GIT_BASH=%PROGRAMFILES%\Git\bin\bash.exe"
) else if exist "%PROGRAMFILES(x86)%\Git\bin\bash.exe" (
    set "GIT_BASH=%PROGRAMFILES(x86)%\Git\bin\bash.exe"
) else if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    set "GIT_BASH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
) else (
    REM Try to find bash in PATH
    for %%i in (bash.exe) do (
        set "GIT_BASH=%%~$PATH:i"
    )
)

if not defined GIT_BASH (
    echo Error: Could not find Git Bash
    echo Please ensure Git for Windows is installed
    echo.
    pause
    exit /b 1
)

REM Convert Windows path to Unix path for Git Bash
set "SCRIPT_PATH=%~dp0sync.sh"
set "SCRIPT_PATH=%SCRIPT_PATH:\=/%"

REM Run the sync script in Git Bash
echo Starting Claude Code configuration sync...
"%GIT_BASH%" -c "cd '%~dp0' && ./sync.sh %*"

REM Check if we need to pause (when double-clicked from Explorer)
if "%COMSPEC%" == "%CMDCMDLINE%" (
    echo.
    echo Press any key to close this window...
    pause >nul
)