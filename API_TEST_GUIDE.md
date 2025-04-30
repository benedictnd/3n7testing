# Enhanced API Testing Guide for 3&7 Training Platform

## Overview

This guide describes the comprehensive API testing framework for the 3&7 Training Platform. The framework provides multiple testing approaches:

1. **Security Testing**: Verifies API security headers, rate limiting, and authentication
2. **Performance Testing**: Measures and tracks API performance metrics over time
3. **Integration Testing**: Tests complete API workflows end-to-end
4. **Automated CI/CD**: Implements continuous testing via GitHub Actions

## Prerequisites

Before running the API tests, ensure you have:

1. **Python 3.13+** installed on your system
   - [Download Python](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation

2. **API Server** running
   - Default URL: http://localhost:8000
   - For testing without a real API, use the included Mock API

3. **Required Python packages**
   ```bash
   pip install -r test-requirements.txt
   ```

## Quick Start

### Running the Mock API

The mock API simulates the real API for testing purposes:

```bash
# Start the mock API
python mock_api.py
```

Verify it's running by visiting http://localhost:8000/health in your browser.

### Running Basic Tests

1. **Check API connection**
   ```bash
   python check_api.py http://localhost:8000
   ```

2. **Run all API tests**
   ```bash
   python run_api_tests.py --url http://localhost:8000 --email test@example.com --password password123
   ```

3. **Run tests with batch file (Windows)**
   ```bash
   run_api_tests.bat
   ```

### Running Specific Test Types

Use pytest to run specific test categories:

```bash
# Run security tests only
python -m pytest tests/security -v

# Run performance tests only
python -m pytest tests/performance -v

# Run integration tests only
python -m pytest tests/integration -v
```

## Advanced Testing

### Security Testing

Security tests verify that the API implements proper security measures:

```bash
python -m pytest tests/security/test_security_headers.py -v
```

Features tested:
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Rate limiting functionality
- Authentication requirements

### Performance Testing

Performance tests measure API response times and track changes over time:

```bash
python -m pytest tests/performance/test_api_performance.py -v
```

Features:
- Response time measurements for key endpoints
- Statistical analysis of performance
- Tracking of performance trends over time

### Integration Testing

Integration tests verify complete API workflows:

```bash
python -m pytest tests/integration/test_email_workflow.py -v
```

Features:
- End-to-end workflow testing
- Authentication and token management
- Error handling and retry logic

### Load Testing with Locust

Load testing measures API performance under load:

```bash
# Start Locust web interface
locust -f locustfile.py

# Or run headless with parameters
locust -f locustfile.py --headless -u 10 -r 1 --run-time 1m --host http://localhost:8000
```

## CI/CD Integration

The testing framework integrates with GitHub Actions for continuous testing:

- **Security Scans**: Automated security scanning with Bandit
- **Mock API Tests**: Tests against the mock API
- **Windows Tests**: Tests specific to Windows environments
- **Integration Tests**: Tests against real API environments (staging, production)
- **Performance Tests**: Automated performance benchmarking
- **Reporting**: Automated HTML report generation

## Test Reports

After running tests, reports are available in:

1. **JUnit XML**: `test-logs/*.xml`
2. **JSON Reports**: `test-logs/*.json`
3. **HTML Reports**: `reports/test-report.html`

Generate a HTML report from test results:

```bash
python generate_report.py --input-dir test-logs --output-file reports/my-report.html
```

## Configuration

Customize test behavior by editing:

1. `test_config.py` - Main configuration file
2. `pytest.ini` - Pytest configuration
3. Environment variables:
   ```bash
   set API_ENV=production
   set API_BASE_URL=https://api.production.com
   set TEST_EMAIL=test@example.com
   set TEST_PASSWORD=securepassword
   ```

## Troubleshooting

If you encounter issues:

1. **Check Mock API**
   ```bash
   python check_api.py http://localhost:8000
   ```

2. **Run with debug logging**
   ```bash
   python -m pytest tests/ -v --log-cli-level=DEBUG
   ```

3. **Use the debug batch file**
   ```bash
   run_debug_test.bat api_test.py 60 test-logs
   ```

4. **Check for Python version compatibility**
   ```bash
   python --version
   ```

5. **Verify installed packages**
   ```bash
   pip list
   ```

## Directory Structure

```
├── mock_api.py               # Mock API for testing
├── test_config.py            # Test configuration
├── run_api_tests.py          # Main test runner
├── generate_report.py        # Report generator
├── pytest.ini                # Pytest configuration
├── tests/                    # Test files
│   ├── conftest.py           # Pytest fixtures
│   ├── security/             # Security tests
│   ├── performance/          # Performance tests
│   └── integration/          # Integration tests
├── templates/                # Report templates
├── test-logs/                # Test logs and results
└── reports/                  # Generated reports
``` 