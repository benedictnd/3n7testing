@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM API Test Debugging Batch File
REM This script runs API tests with enhanced debugging and
REM monitoring capabilities to diagnose performance issues
REM ============================================================

REM Initialize environment variables
set "TEST_FILE=%~1"
if "%TEST_FILE%"=="" set "TEST_FILE=api_test.py"

set "TIMEOUT=%~2"
if "%TIMEOUT%"=="" set "TIMEOUT=300"

set "LOG_DIR=%~3"
if "%LOG_DIR%"=="" set "LOG_DIR=test-logs"

REM Set Python path explicitly to the installed version
set "PYTHON_PATH=C:\Users\bened\AppData\Local\Programs\Python\Python313\python.exe"

REM Create timestamp for log files
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set "DATE=%%c-%%a-%%b")
for /f "tokens=1-3 delims=: " %%a in ('time /t') do (set "TIME=%%a-%%b-%%c")
set "TIMESTAMP=%DATE%_%TIME%"

REM Create log directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "LOG_FILE=%LOG_DIR%\debug_test_%TIMESTAMP%.log"

REM Log the start of debugging session
echo =============================================== > "%LOG_FILE%"
echo API TEST DEBUGGING SESSION - %TIMESTAMP% >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Verify test file exists
echo Checking if test file exists: %TEST_FILE% >> "%LOG_FILE%"
if not exist "%TEST_FILE%" (
    echo ERROR: Test file not found: %TEST_FILE% >> "%LOG_FILE%"
    echo ERROR: Test file not found: %TEST_FILE%
    exit /b 1
)
echo Test file found. >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Log Python version
echo Python version: >> "%LOG_FILE%"
"%PYTHON_PATH%" --version >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%"

REM Log system information
echo System information: >> "%LOG_FILE%"
systeminfo | findstr /C:"OS" /C:"System Type" /C:"Total Physical Memory" >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Log network connections before test
echo Network connections before test: >> "%LOG_FILE%"
netstat -ano | findstr /C:"ESTABLISHED" >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Log running processes before test
echo Running processes before test: >> "%LOG_FILE%"
tasklist /FI "IMAGENAME eq python.exe" >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Enable debug environment variables
set "DEBUG_MODE=1"
set "DEBUG_TIMEOUT=1"
set "DEBUG_NETWORK=1"
set "DEBUG_LOGGING=debug"

echo =============================================== >> "%LOG_FILE%"
echo STARTING TEST EXECUTION >> "%LOG_FILE%"
echo Test file: %TEST_FILE% >> "%LOG_FILE%"
echo Timeout: %TIMEOUT% seconds >> "%LOG_FILE%"
echo Debug mode: Enabled >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Record start time
set "START_TIME=%time%"
echo Start time: %START_TIME% >> "%LOG_FILE%"

REM Run the test with timeout monitoring
echo Running test with timeout monitoring... >> "%LOG_FILE%"
"%PYTHON_PATH%" run_test_with_timeout.py --test_file "%TEST_FILE%" --timeout %TIMEOUT% --debug >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%errorlevel%"

REM Record end time
set "END_TIME=%time%"
echo End time: %END_TIME% >> "%LOG_FILE%"

REM Check for orphaned processes
echo. >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
echo CHECKING FOR ORPHANED PROCESSES >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
tasklist /FI "IMAGENAME eq python.exe" >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Log network connections after test
echo =============================================== >> "%LOG_FILE%"
echo NETWORK CONNECTIONS AFTER TEST >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
netstat -ano | findstr /C:"ESTABLISHED" >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Check for locked files
echo =============================================== >> "%LOG_FILE%"
echo CHECKING FOR LOCKED FILES >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
openfiles >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%"

REM Log test execution result
echo =============================================== >> "%LOG_FILE%"
echo TEST EXECUTION COMPLETED >> "%LOG_FILE%"
echo Exit code: %EXIT_CODE% >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"

REM Display results to console
echo.
echo Test execution completed with exit code: %EXIT_CODE%
echo Debug log saved to: %LOG_FILE%

REM Return the test's exit code
exit /b %EXIT_CODE% 