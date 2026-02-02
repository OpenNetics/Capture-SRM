@echo off
setlocal enabledelayedexpansion

rem ------------------------------------------------------------
rem   CaptureSRM helper script for Windows
rem ------------------------------------------------------------

rem ------------------------
rem   Script Arguments
rem ------------------------

if "%~1"=="" (
    if not exist ".\.venv\" (
        call :run_install
    )
    call :run_main

) else if "%~1"=="install" (
    call :run_install

) else if "%~1"=="reinstall" (
    echo [Removing existing virtual environment]
    rmdir /s /q .\.venv

    call :run_install

) else if "%~1"=="update" (
    echo update
    call :run_install

) else if "%~1"=="help" (
    call :print_help

) else (
    call :print_help
)


rem ------------------------
rem   Functions
rem ------------------------

goto :eof

:run_main
    echo [Activating virtual environment]
    call .\.venv\Scripts\activate.bat >nul 2>&1

    echo [Running CaptureSRM]
    python .\src\main.py

    goto :eof


:run_install
    echo [Creating a new virtual environment]
    python -m venv .\.venv
    attrib +h .\.venv

    echo [Installing requirements]
    call .\.venv\Scripts\activate.bat
    python -m pip install -r .\src\requirements.txt

    goto :eof


:print_help
    echo USAGE:
    echo   %~nx0 {OPTIONS}
    echo.
    echo OPTIONS:
    echo   install    Install all dependencies.
    echo   reinstall  Remove existing environment and reinstall dependencies.
    echo   update     Ensure packages are installed and update them.
    echo   help       Display this help message.

    goto :eof

