"""
Pytest Configuration File

This conftest.py configures pytest for the API testing framework, including:
- Setting up flaky test handling
- Configuring test fixtures
- Defining pytest hooks for test reporting
- Setting up logging and environment configuration
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import pytest

# Import test configuration
try:
    from test_config import TEST_CONFIG
except ImportError:
    # Default configuration if test_config.py is not found
    TEST_CONFIG = {
        "BASE_URL": "http://localhost:8000",
        "TEST_LOGS_DIR": "test-logs",
        "ENVIRONMENT": "development",
        "PERFORMANCE_THRESHOLDS": {
            "RESPONSE_TIME_THRESHOLD": 500,  # ms
            "MAX_CPU_USAGE": 80,  # percentage
            "MAX_MEMORY_USAGE": 500,  # MB
        }
    }

# Add pytest-flaky plugin
pytest_plugins = ["pytest_flaky"]

# Configure logging
@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for test execution."""
    log_dir = Path(TEST_CONFIG.get("TEST_LOGS_DIR", "test-logs"))
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"pytest_run_{timestamp}.log"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("pytest_api_tests")
    logger.info(f"Test run started at {timestamp}")
    logger.info(f"Using environment: {TEST_CONFIG.get('ENVIRONMENT', 'unknown')}")
    
    return logger

# API client fixture
@pytest.fixture(scope="session")
def api_client():
    """Create an API client for testing."""
    from api_test import APIClient
    
    base_url = TEST_CONFIG.get("BASE_URL", "http://localhost:8000")
    client = APIClient(base_url=base_url)
    
    return client

# Authentication fixture
@pytest.fixture(scope="session")
def auth_token(api_client):
    """Get an authentication token for API requests."""
    # Get credentials from environment or config
    email = os.environ.get("TEST_EMAIL", TEST_CONFIG.get("TEST_EMAIL", "test@example.com"))
    password = os.environ.get("TEST_PASSWORD", TEST_CONFIG.get("TEST_PASSWORD", "password"))
    
    # Login to get token
    response = api_client.login(email, password)
    
    # Extract token from response
    if not response or "token" not in response:
        pytest.skip("Could not obtain authentication token")
    
    return response["token"]

# Test metrics collection
class TestMetrics:
    """Collect and store test metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.tests_flaky = 0
        self.performance_data = {}
        
    def add_performance_data(self, test_name: str, data: Dict[str, Any]):
        """Add performance data for a test."""
        self.performance_data[test_name] = data
        
    def get_report(self) -> Dict[str, Any]:
        """Generate a report of test metrics."""
        duration = time.time() - self.start_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "tests_skipped": self.tests_skipped,
            "tests_flaky": self.tests_flaky,
            "pass_rate": (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0,
            "performance_data": self.performance_data,
            "environment": TEST_CONFIG.get("ENVIRONMENT", "unknown")
        }

@pytest.fixture(scope="session")
def test_metrics():
    """Provide test metrics collection."""
    return TestMetrics()

# Register test result hooks
@pytest.hookimpl(trylast=True)
def pytest_runtest_protocol(item, nextitem):
    """Record test start in metrics."""
    # Get test metrics
    metrics = item.session.test_metrics if hasattr(item.session, "test_metrics") else None
    if metrics:
        metrics.tests_run += 1
    
    # Continue with normal test execution
    return None

@pytest.hookimpl(trylast=True)
def pytest_runtest_makereport(item, call):
    """Process test results for metrics."""
    # Only process test call phase (not setup/teardown)
    if call.when != "call":
        return
    
    # Get test metrics
    metrics = item.session.test_metrics if hasattr(item.session, "test_metrics") else None
    if not metrics:
        return
    
    # Check test result and update metrics
    if call.excinfo is None:
        metrics.tests_passed += 1
    elif call.excinfo.typename == "Skipped":
        metrics.tests_skipped += 1
    else:
        metrics.tests_failed += 1
        
    # Check if test is flaky
    if hasattr(item.function, "_is_flaky") or item.get_closest_marker("flaky"):
        metrics.tests_flaky += 1

@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session):
    """Called before the test session starts."""
    # Add test metrics to session
    session.test_metrics = TestMetrics()

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Called after the test session finishes."""
    # Get test metrics
    metrics = session.test_metrics if hasattr(session, "test_metrics") else None
    if not metrics:
        return
    
    # Generate and save report
    report = metrics.get_report()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(TEST_CONFIG.get("TEST_LOGS_DIR", "test-logs"))
    log_dir.mkdir(exist_ok=True)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = log_dir / f"test_report_{timestamp}.json"
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Log report summary
    logger = logging.getLogger("pytest_api_tests")
    logger.info(f"Test run completed with exit status: {exitstatus}")
    logger.info(f"Tests run: {report['tests_run']}, "
                f"Passed: {report['tests_passed']}, "
                f"Failed: {report['tests_failed']}, "
                f"Skipped: {report['tests_skipped']}, "
                f"Flaky: {report['tests_flaky']}")
    logger.info(f"Pass rate: {report['pass_rate']:.2f}%")
    logger.info(f"Report saved to {report_file}")

# Add command line options
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--environment",
        action="store",
        default=TEST_CONFIG.get("ENVIRONMENT", "development"),
        help="Specify environment to run tests against (development, staging, production)"
    )
    
    parser.addoption(
        "--api-url",
        action="store",
        default=TEST_CONFIG.get("BASE_URL", "http://localhost:8000"),
        help="Base URL for API testing"
    )
    
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="Run performance tests"
    )

# Update config from command line options
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure pytest with command line options."""
    # Update test config from command line options
    TEST_CONFIG["ENVIRONMENT"] = config.getoption("--environment")
    TEST_CONFIG["BASE_URL"] = config.getoption("--api-url")
    
    # Register flaky marker
    config.addinivalue_line(
        "markers", 
        "flaky(reruns=3, reason=None): mark test as flaky and retry on failure"
    )
    
    # Register performance marker
    config.addinivalue_line(
        "markers",
        "performance: mark test as a performance test"
    )
    
    # Filter performance tests if requested
    if not config.getoption("--performance"):
        # Skip performance tests unless --performance is passed
        skip_performance = pytest.mark.skip(reason="Performance tests only run with --performance flag")
        for item in config.getini("markers"):
            if item.startswith("performance"):
                config.addinivalue_line("markers", "performance: skipped")
                break 