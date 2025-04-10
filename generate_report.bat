@echo off
setlocal

:: Configure Python path - Uses Python from PATH if available
set PYTHON_PATH=python

:: Check if Python exists
where %PYTHON_PATH% > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found in PATH
    echo Please install Python 3.10 or later
    pause
    exit /b 1
)

:: Install required packages if needed
echo Installing required packages...
%PYTHON_PATH% -m pip install -r requirements.txt

:: Generate sample data and report
echo Generating API test report...
%PYTHON_PATH% generate_api_report.py --generate-data --output-file reports/api_report.html --force

if %ERRORLEVEL% equ 0 (
    echo Report generated successfully!
    echo Opening report...
    start reports\api_report.html
) else (
    echo Failed to generate report.
    pause
)

endlocal 