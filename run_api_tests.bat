@echo off
setlocal enabledelayedexpansion

:: Configure Python path - Updated with correct path
set PYTHON_PATH=C:\Users\bened\AppData\Local\Programs\Python\Python313\python.exe
set TEST_TIMEOUT=60

:: Add timestamp logging
echo [%TIME%] Test sequence started

:: Check if Python exists at the specified path
if exist "%PYTHON_PATH%" (
    echo [%TIME%] Using Python at: %PYTHON_PATH%
    :: Export the Python path as an environment variable
    set "PYTHON_PATH=%PYTHON_PATH%"
) else (
    echo [%TIME%] Python not found at %PYTHON_PATH%
    echo [%TIME%] Checking if Python is available in PATH...
    where python > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_PATH=python
        echo [%TIME%] Using Python from PATH
    ) else (
        echo [%TIME%] Python not found. Please install Python 3.10 first
        echo Visit: https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)

:: Bypass full dependency installation for faster testing
echo [%TIME%] Installing minimal dependencies...
"%PYTHON_PATH%" -m pip install requests pytest

:: Create test-logs directory if it doesn't exist
if not exist "test-logs" mkdir test-logs

:: Get command line arguments
set API_BASE_URL=http://localhost:8000
set EMAIL=test@example.com
set PASSWORD=password123
set VERBOSE=true

echo [%TIME%] Running API tests with timeout monitoring...
echo [%TIME%] API URL: %API_BASE_URL%
echo [%TIME%] Timeout set to: %TEST_TIMEOUT% seconds

:: Run single basic test to verify connection before full test
echo [%TIME%] Running basic connectivity test...
"%PYTHON_PATH%" -c "import requests; response = requests.get('%API_BASE_URL%/health', timeout=5); print(f'Basic test: {response.status_code}'); exit(0 if response.status_code == 200 else 1)"

if %ERRORLEVEL% neq 0 (
    echo [%TIME%] Basic connectivity test failed! Check if API server is running.
    pause
    exit /b 1
)

:: Run the actual tests directly (without subprocess wrapper)
echo [%TIME%] Starting full test suite...
"%PYTHON_PATH%" api_test.py --url "%API_BASE_URL%" --email "%EMAIL%" --password "%PASSWORD%" --verbose

if %ERRORLEVEL% equ 0 (
    echo [%TIME%] API tests completed successfully
) else if %ERRORLEVEL% equ 124 (
    echo [%TIME%] Tests timed out after %TEST_TIMEOUT% seconds
    tasklist /FI "IMAGENAME eq python*" /FO TABLE
    netstat -ano | findstr ":8000"
    echo [%TIME%] Killing hanging processes...
    taskkill /F /FI "IMAGENAME eq python*" /T
) else (
    echo [%TIME%] API tests failed with code %ERRORLEVEL%
)

echo [%TIME%] Test execution complete
echo [%TIME%] End timestamp: %DATE% %TIME%
pause 