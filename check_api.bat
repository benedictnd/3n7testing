@echo off
setlocal

:: Configure Python path - Updated with correct path
set PYTHON_PATH=C:\Users\bened\AppData\Local\Programs\Python\Python313\python.exe

:: Check if Python exists at the specified path
if exist "%PYTHON_PATH%" (
    echo Using Python at: %PYTHON_PATH%
) else (
    echo Python not found at %PYTHON_PATH%
    echo Checking if Python is available in PATH...
    where python > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_PATH=python
        echo Using Python from PATH
    ) else (
        echo Python not found. Please install Python 3.10 first
        echo Visit: https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)

:: Install requests if not already installed
echo Installing requests package...
"%PYTHON_PATH%" -m pip install requests

:: Run the API check
echo Checking if the API is running...
"%PYTHON_PATH%" check_api.py http://localhost:8000

if %ERRORLEVEL% equ 0 (
    echo API check completed successfully
) else (
    echo API check failed - server may not be running
    echo Please start the API server and try again
)

pause 