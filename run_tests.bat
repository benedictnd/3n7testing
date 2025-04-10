@echo off
REM ===============================================================
REM Advanced API Test Runner for 3&7 Training Platform
REM ===============================================================
setlocal enabledelayedexpansion

REM Default configuration
set "PYTHON_EXE=python"
set "TEST_ENV=development"
set "TESTS_DIR=tests"
set "BASE_URL=http://localhost:8000/api"
set "REPORT_DIR=test-reports"
set "LOG_LEVEL=INFO"
set "TEST_CATEGORY=all"
set "SECURITY_SCAN=false"
set "PERFORMANCE_TEST=false"
set "DEBUG_MODE=false"
set "TIMEOUT=60"
set "PARALLEL=false"
set "PARALLEL_WORKERS=4"

REM Timestamp for reports
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "TIMESTAMP=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%T%dt:~8,2%-%dt:~10,2%-%dt:~12,2%"
set "LOG_FILE=%REPORT_DIR%\test-run-%TIMESTAMP%.log"

REM Parse command line arguments
:parse_args
if "%1"=="" goto :after_args
if /i "%1"=="--env" (
    set "TEST_ENV=%2"
    shift & shift
    goto :parse_args
)
if /i "%1"=="--url" (
    set "BASE_URL=%2"
    shift & shift
    goto :parse_args
)
if /i "%1"=="--category" (
    set "TEST_CATEGORY=%2"
    shift & shift
    goto :parse_args
)
if /i "%1"=="--security" (
    set "SECURITY_SCAN=true"
    shift
    goto :parse_args
)
if /i "%1"=="--performance" (
    set "PERFORMANCE_TEST=true"
    shift
    goto :parse_args
)
if /i "%1"=="--debug" (
    set "DEBUG_MODE=true"
    set "LOG_LEVEL=DEBUG"
    shift
    goto :parse_args
)
if /i "%1"=="--timeout" (
    set "TIMEOUT=%2"
    shift & shift
    goto :parse_args
)
if /i "%1"=="--log-level" (
    set "LOG_LEVEL=%2"
    shift & shift
    goto :parse_args
)
if /i "%1"=="--parallel" (
    set "PARALLEL=true"
    shift
    goto :parse_args
)
if /i "%1"=="--workers" (
    set "PARALLEL_WORKERS=%2"
    shift & shift
    goto :parse_args
)
if /i "%1"=="--help" (
    call :display_help
    exit /b 0
)
shift
goto :parse_args

:display_help
echo.
echo Advanced API Test Runner for 3^&7 Training Platform
echo =================================================
echo.
echo Options:
echo   --env ^<environment^>       Set test environment (development, staging, production)
echo   --url ^<base_url^>          Set API base URL
echo   --category ^<category^>     Set test category to run (api, security, performance, integration, all)
echo   --security                Run security scans
echo   --performance             Run performance tests
echo   --debug                   Enable debug mode with verbose output
echo   --timeout ^<seconds^>       Set test timeout in seconds
echo   --log-level ^<level^>       Set logging level (DEBUG, INFO, WARNING, ERROR)
echo   --parallel                Enable parallel test execution
echo   --workers ^<number^>        Number of parallel workers (default: 4)
echo   --help                    Display this help message
echo.
exit /b 0

:after_args

REM Create directories if they don't exist
if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"

REM Display configuration
echo =================================================
echo API TEST EXECUTION - %TIMESTAMP%
echo =================================================
echo Environment:    %TEST_ENV%
echo Base URL:       %BASE_URL%
echo Test Category:  %TEST_CATEGORY%
echo Security Scan:  %SECURITY_SCAN%
echo Performance:    %PERFORMANCE_TEST%
echo Debug Mode:     %DEBUG_MODE%
echo Timeout:        %TIMEOUT% seconds
echo Parallel:       %PARALLEL% (%PARALLEL_WORKERS% workers)
echo Log Level:      %LOG_LEVEL%
echo Log File:       %LOG_FILE%
echo =================================================
echo.

REM Create log directory and file
echo Starting test execution at %TIME% > "%LOG_FILE%"
echo Configuration: >> "%LOG_FILE%"
echo   Environment:    %TEST_ENV% >> "%LOG_FILE%"
echo   Base URL:       %BASE_URL% >> "%LOG_FILE%"
echo   Test Category:  %TEST_CATEGORY% >> "%LOG_FILE%"
echo   Security Scan:  %SECURITY_SCAN% >> "%LOG_FILE%"
echo   Performance:    %PERFORMANCE_TEST% >> "%LOG_FILE%"
echo   Debug Mode:     %DEBUG_MODE% >> "%LOG_FILE%"
echo   Timeout:        %TIMEOUT% seconds >> "%LOG_FILE%"
echo   Parallel:       %PARALLEL% (%PARALLEL_WORKERS% workers) >> "%LOG_FILE%"
echo   Log Level:      %LOG_LEVEL% >> "%LOG_FILE%"
echo =================================================>> "%LOG_FILE%"

REM Check Python installation
echo Checking Python installation...
%PYTHON_EXE% --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python or set the correct path.
    echo Error: Python not found. Please install Python or set the correct path. >> "%LOG_FILE%"
    exit /b 1
)
%PYTHON_EXE% --version >> "%LOG_FILE%" 2>&1

REM Export environment variables for the tests
set "TEST_ENVIRONMENT=%TEST_ENV%"
set "API_BASE_URL=%BASE_URL%"
set "API_TEST_TIMEOUT=%TIMEOUT%"
set "API_TEST_LOG_LEVEL=%LOG_LEVEL%"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

REM Run security scan if enabled
if "%SECURITY_SCAN%"=="true" (
    echo.
    echo Running security scan...
    echo Running security scan at %TIME% >> "%LOG_FILE%"
    
    %PYTHON_EXE% -m bandit -r %TESTS_DIR% utils api_test.py run_api_tests.py >> "%LOG_FILE%" 2>&1
    
    if %errorlevel% neq 0 (
        echo Security scan found issues - see %LOG_FILE% for details
        echo Security scan failed with exit code %errorlevel% at %TIME% >> "%LOG_FILE%"
    ) else (
        echo Security scan passed
        echo Security scan passed at %TIME% >> "%LOG_FILE%"
    )
)

REM Prepare pytest command
set "PYTEST_CMD=%PYTHON_EXE% -m pytest"

REM Add verbosity based on debug mode
if "%DEBUG_MODE%"=="true" (
    set "PYTEST_CMD=%PYTEST_CMD% -vv"
) else (
    set "PYTEST_CMD=%PYTEST_CMD% -v"
)

REM Add parallel execution if enabled
if "%PARALLEL%"=="true" (
    set "PYTEST_CMD=%PYTEST_CMD% -n %PARALLEL_WORKERS%"
)

REM Add HTML report generation
set "PYTEST_CMD=%PYTEST_CMD% --html=%REPORT_DIR%/report-%TIMESTAMP%.html --self-contained-html"

REM Add timeout argument
set "PYTEST_CMD=%PYTEST_CMD% --timeout=%TIMEOUT%"

REM Select tests based on category
if "%TEST_CATEGORY%"=="security" (
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/security/"
) else if "%TEST_CATEGORY%"=="performance" (
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/performance/"
) else if "%TEST_CATEGORY%"=="api" (
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/api/"
) else if "%TEST_CATEGORY%"=="integration" (
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/integration/"
) else if "%TEST_CATEGORY%"=="stability" (
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/stability/"
) else if "%TEST_CATEGORY%"=="functional" (
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/functional/"
) else (
    REM Run all tests if category is "all"
    set "PYTEST_CMD=%PYTEST_CMD% %TESTS_DIR%/"
)

REM Run performance tests if enabled (separately from main tests)
if "%PERFORMANCE_TEST%"=="true" (
    echo.
    echo Running performance tests...
    echo Running performance tests at %TIME% >> "%LOG_FILE%"
    
    %PYTHON_EXE% -m pytest %TESTS_DIR%/performance/ -v --html=%REPORT_DIR%/performance-report-%TIMESTAMP%.html --self-contained-html >> "%LOG_FILE%" 2>&1
    
    if %errorlevel% neq 0 (
        echo Performance tests found issues - see %LOG_FILE% for details
        echo Performance tests failed with exit code %errorlevel% at %TIME% >> "%LOG_FILE%"
    ) else (
        echo Performance tests passed
        echo Performance tests passed at %TIME% >> "%LOG_FILE%"
    )
)

REM Run the main tests
echo.
echo Running API tests with command:
echo %PYTEST_CMD%
echo.
echo Running API tests at %TIME% with command: >> "%LOG_FILE%"
echo %PYTEST_CMD% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

%PYTEST_CMD% >> "%LOG_FILE%" 2>&1
set TEST_RESULT=%errorlevel%

REM Check for common errors
findstr /C:"ConnectionError" /C:"urllib3.exceptions" /C:"requests.exceptions" "%LOG_FILE%" > nul
if %errorlevel% equ 0 (
    echo.
    echo WARNING: Connection issues detected. Check if the API server is running.
    echo WARNING: Connection issues detected at %TIME%. Check if the API server is running. >> "%LOG_FILE%"
)

REM Analyze test results
echo.
echo Test execution completed at %TIME% with exit code %TEST_RESULT% >> "%LOG_FILE%"
echo.

if %TEST_RESULT% equ 0 (
    echo =================================================
    echo ✓ All tests passed successfully!
    echo =================================================
    echo All tests passed successfully at %TIME% >> "%LOG_FILE%"
) else (
    echo =================================================
    echo ✗ Tests failed with exit code %TEST_RESULT%
    echo =================================================
    echo Tests failed with exit code %TEST_RESULT% at %TIME% >> "%LOG_FILE%"
    
    REM Extract and display failures
    echo.
    echo Failure summary:
    echo Failure summary: >> "%LOG_FILE%"
    findstr /C:"FAILED" "%LOG_FILE%"
    findstr /C:"FAILED" "%LOG_FILE%" >> "%LOG_FILE%"
)

REM Display report location
echo.
echo Test report available at: %REPORT_DIR%/report-%TIMESTAMP%.html
echo Test log available at: %LOG_FILE%
echo.

endlocal
exit /b %TEST_RESULT% 