@echo off
rem ------------------------------------------------------------
rem  GestureTracker helper script for Windows
rem ------------------------------------------------------------

rem ---------- Helper: print help ----------
:print_help
echo USAGE:
echo   %~nx0 {OPTIONS}
echo.
echo OPTIONS:
echo   --install    Install all dependencies.
echo   --reinstall  Remove existing environment and reinstall dependencies.
echo   --update     Ensure packages are installed and update them.
echo   --help       Display this help message.
goto :eof

rem ---------- Parse first argument ----------
if "%~1"=="" (
    call :print_help
    exit /b 1
)

if "%~1"=="--install" (
    echo [Activating virtual environment]
    call .\.venv\Scripts\activate.bat >nul 2>&1
    goto :run_main
)

if "%~1"=="--reinstall" (
    echo [Removing existing virtual environment]
    rmdir /s /q .\.venv

    echo [Creating a new virtual environment]
    python -m venv .\.venv

    echo [Installing requirements]
    call .\.venv\Scripts\activate.bat
    python -m pip install -r .\src\requirements.txt
    goto :run_main
)

if "%~1"=="--update" (
    if not exist ".\.venv\" (
        echo [Virtual environment not found. Creating it]
        python -m venv .\.venv

        echo [Installing requirements]
        call .\.venv\Scripts\activate.bat
        python -m pip install -r .\src\requirements.txt
    ) else (
        echo [Activating existing virtual environment]
        call .\.venv\Scripts\activate.bat
    )

    echo [Pulling updated git release]
    git pull

    echo [Updating installed packages]
    python -m pip install --upgrade -r .\src\requirements.txt
    goto :run_main
)

if "%~1"=="--help" (
    call :print_help
    exit /b 0
)

rem ---------- Fallback: unknown option ----------
echo Unknown option: %~1
call :print_help
exit /b 1

rem ---------- Run the main script ----------
:run_main
echo [Running GestureTracker]
python .\src\main.py

