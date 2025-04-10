@echo off
REM Run load tests for the 3&7 Training Platform

REM Set default values
set HOST=http://localhost:8000
set USERS=10
set SPAWN_RATE=1
set RUN_TIME=1m
set USER_CLASS=TrainingPlatformUser

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--users" (
    set USERS=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--spawn-rate" (
    set SPAWN_RATE=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--run-time" (
    set RUN_TIME=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--user-class" (
    set USER_CLASS=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    echo Usage: %0 [options]
    echo Options:
    echo   --host HOST         Host to test (default: http://localhost:8000^)
    echo   --users USERS       Number of users to simulate (default: 10^)
    echo   --spawn-rate RATE   Spawn rate in users per second (default: 1^)
    echo   --run-time TIME     Run time in minutes (default: 1m^)
    echo   --user-class CLASS  User class to use (default: TrainingPlatformUser^)
    echo   --help              Show this help message
    exit /b 0
)
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1
:end_parse_args

REM Check if locust is installed
where locust >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Locust is not installed. Installing...
    pip install locust
)

REM Run the load test
echo Running load test with the following parameters:
echo   Host: %HOST%
echo   Users: %USERS%
echo   Spawn rate: %SPAWN_RATE%
echo   Run time: %RUN_TIME%
echo   User class: %USER_CLASS%
echo.

locust -f locustfile.py --headless -u %USERS% -r %SPAWN_RATE% --run-time %RUN_TIME% --host %HOST% -c %USER_CLASS%

REM Check if the load test was successful
if %ERRORLEVEL% equ 0 (
    echo Load test completed successfully.
) else (
    echo Load test failed.
    exit /b 1
) 