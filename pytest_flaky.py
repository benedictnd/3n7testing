#!/usr/bin/env python3
"""
Pytest Plugin for Flaky Tests

This pytest plugin provides functionality for handling flaky tests.
It integrates with the flaky_test_config.py module to provide comprehensive
flaky test detection, retrying, and reporting.

To use this plugin, add the following to your pytest.ini or conftest.py:
    
    pytest_plugins = ["pytest_flaky"]

Or pass it on the command line:
    
    pytest --flaky-enabled --flaky-reruns=3
"""

import logging
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo

# Import our flaky test configuration
try:
    import flaky_test_config
except ImportError:
    print("WARNING: flaky_test_config.py not found. Flaky test plugin disabled.")
    flaky_test_config = None

# Configure logging
logger = logging.getLogger("pytest_flaky")

# Track flaky tests in this session
FLAKY_TESTS: Set[str] = set()
RETRIED_TESTS: Dict[str, int] = {}
TEST_DURATIONS: Dict[str, float] = {}

def pytest_addoption(parser: Parser) -> None:
    """Add flaky test options to pytest command line."""
    group = parser.getgroup("flaky", "flaky test handling")
    group.addoption(
        "--flaky-enabled",
        action="store_true",
        default=False,
        help="Enable flaky test handling",
    )
    group.addoption(
        "--flaky-reruns",
        action="store",
        type=int,
        default=None,
        help="Number of times to retry flaky tests (overrides config)",
    )
    group.addoption(
        "--flaky-report",
        action="store_true",
        default=True,
        help="Generate a flaky test report",
    )
    group.addoption(
        "--flaky-report-path",
        action="store",
        type=str,
        default=None,
        help="Path to store flaky test reports",
    )

def pytest_configure(config: Config) -> None:
    """Configure the plugin based on command line options."""
    if not flaky_test_config:
        return
        
    # Check if flaky test handling is enabled
    enabled = config.getoption("--flaky-enabled")
    if enabled:
        # Update configuration from command line options
        flaky_test_config.CONFIG["enabled"] = True
        
        # Override max retries if specified
        reruns = config.getoption("--flaky-reruns")
        if reruns is not None:
            flaky_test_config.CONFIG["max_retries"] = reruns
            
        # Override report path if specified
        report_path = config.getoption("--flaky-report-path")
        if report_path:
            flaky_test_config.CONFIG["report_path"] = report_path
            # Ensure the directory exists
            os.makedirs(report_path, exist_ok=True)
    else:
        # Disable flaky test handling if not enabled
        flaky_test_config.CONFIG["enabled"] = False

def pytest_sessionstart(session: Session) -> None:
    """Called before the test session starts."""
    if not flaky_test_config or not flaky_test_config.CONFIG["enabled"]:
        return
        
    # Register test start time
    flaky_test_config.register_test_start()
    
    # Initialize tracking variables
    FLAKY_TESTS.clear()
    RETRIED_TESTS.clear()
    TEST_DURATIONS.clear()

def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    """Called after the test session finishes."""
    if not flaky_test_config or not flaky_test_config.CONFIG["enabled"]:
        return
        
    # Register test end time
    flaky_test_config.register_test_end()
    
    # Count total tests
    flaky_test_config.STATS["total_tests"] = len(session.items)
    flaky_test_config.STATS["flaky_tests_count"] = len(FLAKY_TESTS)
    flaky_test_config.STATS["retried_tests_count"] = len(RETRIED_TESTS)
    
    # Generate report if enabled
    if session.config.getoption("--flaky-report"):
        report = flaky_test_config.generate_flaky_report()
        
        # Print summary to console
        print("\n=== Flaky Test Report ===")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Flaky Tests: {report['flaky_tests_count']} ({report['flaky_test_percentage']:.1f}%)")
        print(f"Total Retries: {report['total_retries']}")
        if report['flaky_tests_count'] > 0:
            print(f"Avg Retries per Flaky Test: {report['average_retries_per_flaky_test']:.1f}")
            
            # List flaky tests
            print("\nFlaky Tests:")
            for test_name, test_data in report['tests'].items():
                if test_data['is_flaky']:
                    print(f"- {test_name}: {test_data['flakiness_percentage']:.1f}% flaky "
                          f"({test_data['failures']}/{test_data['total_runs']} failures)")
        print("========================\n")

def get_test_nodeid(item: Item) -> str:
    """Get a clean test node ID."""
    return item.nodeid.replace("::()::", "::")

def pytest_runtest_setup(item: Item) -> None:
    """Called before test setup."""
    if not flaky_test_config or not flaky_test_config.CONFIG["enabled"]:
        return
        
    # Check if the test is marked as flaky
    is_flaky = False
    
    # Check for @pytest.mark.flaky
    flaky_marker = item.get_closest_marker("flaky")
    if flaky_marker:
        is_flaky = True
        
    # Check for @retry_flaky_test decorator
    if hasattr(item.function, "_is_flaky"):
        is_flaky = True
    
    # Add to tracking if it's a flaky test
    if is_flaky:
        FLAKY_TESTS.add(get_test_nodeid(item))

def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> Optional[TestReport]:
    """Called when a test report is generated."""
    if not flaky_test_config or not flaky_test_config.CONFIG["enabled"]:
        return None
        
    # Only process test call phase (not setup/teardown)
    if call.when != "call":
        return None
        
    # Create the report
    report = TestReport.from_item_and_call(item, call)
    
    # Track the test duration
    test_nodeid = get_test_nodeid(item)
    TEST_DURATIONS[test_nodeid] = call.duration
    
    # If the test failed, check if it's flaky and should be retried
    if report.failed:
        should_retry = False
        
        # Check if already identified as flaky
        if test_nodeid in FLAKY_TESTS:
            should_retry = True
        else:
            # Check if the error message indicates a flaky test
            error_message = str(call.excinfo)
            if flaky_test_config.is_test_flaky(item.name, error_message):
                FLAKY_TESTS.add(test_nodeid)
                should_retry = True
        
        # If it should be retried, mark for retry
        if should_retry:
            # Track retry count
            RETRIED_TESTS[test_nodeid] = RETRIED_TESTS.get(test_nodeid, 0) + 1
            
            # Determine if we should retry
            test_config = flaky_test_config.CONFIG["test_overrides"].get(item.name, {})
            max_retries = test_config.get("max_retries", flaky_test_config.CONFIG["max_retries"])
            
            # Only retry if we haven't reached the max retries
            if RETRIED_TESTS[test_nodeid] <= max_retries:
                # Mark the test for rerun
                report.outcome = "rerun"
                
                # Update stats in our config
                if item.name not in flaky_test_config.STATS["flaky_tests"]:
                    flaky_test_config.STATS["flaky_tests"][item.name] = {
                        "total_runs": 0,
                        "failures": 0,
                        "retries": 0,
                        "last_failure_time": None,
                        "last_success_time": None,
                        "last_error": None
                    }
                
                flaky_test_config.STATS["flaky_tests"][item.name]["total_runs"] += 1
                flaky_test_config.STATS["flaky_tests"][item.name]["failures"] += 1
                flaky_test_config.STATS["flaky_tests"][item.name]["retries"] += 1
                flaky_test_config.STATS["total_retries"] += 1
                
                # Log the retry
                logger.info(f"Retrying '{item.name}' after failure: {str(call.excinfo)} "
                           f"(Attempt {RETRIED_TESTS[test_nodeid]}/{max_retries})")
    
    # If the test passed, update stats if it's a flaky test
    elif report.passed and test_nodeid in FLAKY_TESTS:
        if item.name in flaky_test_config.STATS["flaky_tests"]:
            flaky_test_config.STATS["flaky_tests"][item.name]["total_runs"] += 1
    
    return report

# If a test is marked for rerun, add rerunfailures plugin
def pytest_configure_node(node) -> None:
    """Configure node with rerunfailures plugin if needed."""
    # This requires pytest-rerunfailures plugin to be installed
    # It will be used to handle the actual rerunning of tests
    pass

# Register the plugin with pytest
if flaky_test_config:
    @pytest.hookimpl(trylast=True)
    def pytest_configure(config: Config) -> None:
        """Register the plugin with pytest."""
        config.pluginmanager.register(sys.modules[__name__], "flaky_tests") 