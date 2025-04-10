@echo off
setlocal enabledelayedexpansion

:: Configure Python path
set PYTHON_PATH=C:\Users\bened\AppData\Local\Programs\Python\Python313\python.exe
set TEST_TIMEOUT=90
set DEBUG_LOG=test-logs\test_debug_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log

:: Replace spaces in log filename
set DEBUG_LOG=%DEBUG_LOG: =0%

:: Create timestamp function
call :log "==================== API TEST DEBUG SESSION ===================="
call :log "Starting API test debugging session"

:: Process arguments
set API_BASE_URL=http://localhost:8000
set EMAIL=test@example.com
set PASSWORD=password123
set VERBOSE=true
set DEBUG_MODE=true

call :log "Checking Python installation..."
:: Check if Python exists at the specified path
if exist "%PYTHON_PATH%" (
    call :log "Using Python at: %PYTHON_PATH%"
    :: Export the Python path as an environment variable
    set "PYTHON_PATH=%PYTHON_PATH%"
) else (
    call :log "Python not found at %PYTHON_PATH%"
    call :log "Checking if Python is available in PATH..."
    where python > nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set PYTHON_PATH=python
        call :log "Using Python from PATH"
    ) else (
        call :log "ERROR: Python not found. Please install Python 3.10+ first"
        call :log "Visit: https://www.python.org/downloads/"
        pause
        exit /b 1
    )
)

:: Check Python version
call :log "Checking Python version..."
"%PYTHON_PATH%" --version > test-logs\python_version.txt 2>&1
type test-logs\python_version.txt
call :log "Python version output saved to test-logs\python_version.txt"

:: Create test-logs directory if it doesn't exist
if not exist "test-logs" mkdir test-logs

:: Install debugging dependencies
call :log "Installing required dependencies..."
"%PYTHON_PATH%" -m pip install requests pytest psutil pytest-timeout pytest-html colorama memory_profiler > test-logs\pip_install.log 2>&1
if !ERRORLEVEL! neq 0 (
    call :log "ERROR: Failed to install dependencies"
    type test-logs\pip_install.log
    pause
    exit /b 1
)
call :log "Dependencies installed successfully"

:: Check network connectivity to API
call :log "Checking network connectivity to API server..."
call :log "Running curl to test health endpoint..."
curl -s -o test-logs\health_check.json -w "Status: %%{http_code}, Time: %%{time_total}s\n" %API_BASE_URL%/health

if !ERRORLEVEL! neq 0 (
    call :log "ERROR: Failed to connect to API server with curl. Network issue detected."
    netstat -ano | findstr ":8000" > test-logs\port_check.txt
    call :log "Network port check saved to test-logs\port_check.txt"
) else (
    call :log "Basic connectivity test with curl succeeded"
    type test-logs\health_check.json
)

:: Verify Python can connect to the API
call :log "Verifying Python can connect to the API..."
"%PYTHON_PATH%" -c "import requests,sys,time; start=time.time(); print('Connecting to %API_BASE_URL%/health...'); try: response=requests.get('%API_BASE_URL%/health', timeout=5); print(f'Status: {response.status_code}, Time: {time.time()-start:.2f}s, Content: {response.text[:100]}'); sys.exit(0 if response.status_code == 200 else 1); except Exception as e: print(f'Error: {str(e)}'); sys.exit(1)" > test-logs\python_connectivity.txt 2>&1

if !ERRORLEVEL! neq 0 (
    call :log "ERROR: Python connectivity test failed!"
    type test-logs\python_connectivity.txt
    call :log "Checking for potential firewall issues..."
    netsh advfirewall show allprofiles state > test-logs\firewall_status.txt
    call :log "Firewall status saved to test-logs\firewall_status.txt"
    pause
) else (
    call :log "Python connectivity test passed"
)

:: Check for running processes that might interfere
call :log "Checking for running Python processes..."
tasklist /FI "IMAGENAME eq python*" /FO LIST > test-logs\running_python.txt
call :log "Python processes saved to test-logs\running_python.txt"

:: Run diagnostics to identify test performance issues
call :log "Running API test diagnostics..."
"%PYTHON_PATH%" api_test_debug.py --url "%API_BASE_URL%" --email "%EMAIL%" --password "%PASSWORD%" --verbose > test-logs\diagnostics_output.txt 2>&1

:: Check diagnostic results
if !ERRORLEVEL! equ 0 (
    call :log "Diagnostics completed successfully"
    type test-logs\diagnostics_output.txt | findstr /B "API Test Summary"
    call :log "Full diagnostics report saved to test-logs\diagnostics_output.txt"
) else (
    call :log "ERROR: Diagnostics failed with code !ERRORLEVEL!"
    type test-logs\diagnostics_output.txt
)

:: Run benchmark tests
call :log "Running benchmark tests on critical endpoints..."
"%PYTHON_PATH%" api_test_debug.py --url "%API_BASE_URL%" --benchmark --verbose > test-logs\benchmark_output.txt 2>&1

:: Run individual endpoint tracing for problematic endpoints
call :log "Tracing health endpoint..."
"%PYTHON_PATH%" api_test_debug.py --url "%API_BASE_URL%" --trace "/health" > test-logs\health_trace.txt 2>&1

call :log "Tracing authentication endpoint..."
"%PYTHON_PATH%" api_test_debug.py --url "%API_BASE_URL%" --trace "/auth/login" > test-logs\auth_trace.txt 2>&1

:: Run the actual tests with memory profiling
call :log "Running actual API tests with memory profiling and timeout..."
"%PYTHON_PATH%" -m memory_profiler api_test.py --url "%API_BASE_URL%" --email "%EMAIL%" --password "%PASSWORD%" --verbose > test-logs\test_output.txt 2>&1

:: Check test results
set TEST_EXIT_CODE=!ERRORLEVEL!
if !TEST_EXIT_CODE! equ 0 (
    call :log "API tests completed successfully"
) else if !TEST_EXIT_CODE! equ 124 (
    call :log "ERROR: Tests timed out after %TEST_TIMEOUT% seconds"
    call :log "Collecting diagnostic information for hanging processes..."
    tasklist /FI "IMAGENAME eq python*" /FO TABLE > test-logs\hanging_processes.txt
    wmic process where "name like '%%python%%'" get processid,commandline > test-logs\python_process_details.txt
    netstat -ano | findstr ":8000" > test-logs\open_connections.txt
    call :log "Process information saved to test-logs directory"
    
    call :log "Attempting to kill hanging processes..."
    taskkill /F /FI "IMAGENAME eq python*" /T
) else (
    call :log "ERROR: API tests failed with code !TEST_EXIT_CODE!"
    type test-logs\test_output.txt
)

:: Run simplified test for comparison
call :log "Running simplified health check for comparison..."
"%PYTHON_PATH%" -c "import requests,time,json; start=time.time(); print('Testing /health endpoint directly...'); response=requests.get('%API_BASE_URL%/health'); elapsed=time.time()-start; print(f'Response time: {elapsed:.4f}s, Status: {response.status_code}')" > test-logs\simple_test.txt 2>&1

:: Compare outcome
call :log "Comparing test approaches..."
type test-logs\simple_test.txt

:: Summarize findings
call :log "==================== TEST SUMMARY ===================="
call :log "API Base URL: %API_BASE_URL%"
call :log "Test timeout: %TEST_TIMEOUT% seconds"
call :log "Diagnostic logs saved to: test-logs directory"

if exist test-logs\benchmark_analysis.json (
    call :log "Performance analysis is available in benchmark_analysis.json"
    type test-logs\benchmark_analysis.json | findstr "recommendations"
) 

call :log "==================== TEST COMPLETE ===================="
pause
exit /b 0

:log
echo [%DATE% %TIME%] %~1
echo [%DATE% %TIME%] %~1 >> "%DEBUG_LOG%"
goto :eof 