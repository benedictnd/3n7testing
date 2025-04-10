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

:: Install dependencies
echo Installing required packages...
"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install requests

:: Run the mock API server
echo Starting mock API server...
start "Mock API Server" cmd /c "%PYTHON_PATH% mock_api.py"

:: Wait for the server to start
timeout /t 2 /nobreak > nul

:: Check if the server is running
echo Checking if mock API is running...
"%PYTHON_PATH%" check_api.py http://localhost:8000

if %ERRORLEVEL% equ 0 (
    echo Mock API server is running successfully!
    echo Press Ctrl+C in the server window to stop the server when done.
) else (
    echo Failed to start the mock API server.
    echo Check the server window for errors.
)

echo.
echo You can now run API tests against the mock server:
echo run_api_tests.bat
echo. 