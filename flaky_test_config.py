#!/usr/bin/env python3
"""
Flaky Test Configuration

This module defines configuration, decorators, and utilities for handling flaky tests
across the project. It works with the pytest_flaky.py plugin to provide consistent
handling of intermittently failing tests.
"""

import functools
import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("flaky_tests")

# Default configuration for flaky tests
CONFIG = {
    # Global settings
    "enabled": True,
    "max_retries": 3,
    "retry_delay": 1.0,
    "backoff_factor": 1.2,
    "flakiness_threshold": 0.3,  # 30% failure rate to be considered flaky
    
    # Patterns for auto-detection of flaky tests
    "error_patterns": [
        r"Connection refused",
        r"timed? ?out",
        r"429 Too Many Requests",
        r"500 Internal Server Error",
        r"temporarily unavailable",
        r"ConnectionResetError",
        r"ConnectionError"
    ],
    
    # Test-specific overrides - updated during runtime
    "test_overrides": {},
    
    # Reporting
    "report_path": os.path.join("test-reports", "flaky-tests"),
    "history_retention_days": 30,
}

# Initialize stats tracking
STATS = {
    "flaky_tests": {},
    "run_start_time": None,
    "run_end_time": None,
    "total_tests": 0,
    "flaky_tests_count": 0,
    "retried_tests_count": 0,
    "total_retries": 0,
}

def is_test_flaky(test_name: str, error_message: str) -> bool:
    """
    Check if a test failure matches patterns that indicate flakiness.
    
    Args:
        test_name: Name of the test that failed
        error_message: Error message from the test failure
        
    Returns:
        bool: True if the error matches flaky patterns, False otherwise
    """
    # Check if the test is in the overrides list
    if test_name in CONFIG["test_overrides"]:
        return True
        
    # Check if the error message matches any flaky patterns
    for pattern in CONFIG["error_patterns"]:
        if re.search(pattern, error_message, re.IGNORECASE):
            return True
            
    return False

def retry_flaky_test(func: Callable) -> Callable:
    """
    Decorator to mark a test as flaky and retry it on failure.
    This is used directly in test files as an alternative to pytest.mark.flaky.
    
    Args:
        func: The test function to decorate
        
    Returns:
        Callable: The decorated function with retry logic
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not CONFIG["enabled"]:
            return func(*args, **kwargs)
            
        test_name = func.__name__
        # Get test-specific config or use defaults
        test_config = CONFIG["test_overrides"].get(test_name, {})
        max_retries = test_config.get("max_retries", CONFIG["max_retries"])
        retry_delay = test_config.get("retry_delay", CONFIG["retry_delay"])
        backoff_factor = test_config.get("backoff_factor", CONFIG["backoff_factor"])
        
        # Track this test in stats
        if test_name not in STATS["flaky_tests"]:
            STATS["flaky_tests"][test_name] = {
                "total_runs": 0,
                "failures": 0,
                "retries": 0,
                "last_failure_time": None,
                "last_success_time": None,
                "last_error": None
            }
        
        attempts = 0
        current_delay = retry_delay
        
        while attempts <= max_retries:
            attempts += 1
            STATS["flaky_tests"][test_name]["total_runs"] += 1
            
            try:
                result = func(*args, **kwargs)
                
                # Update stats on success
                STATS["flaky_tests"][test_name]["last_success_time"] = datetime.now().isoformat()
                
                # Only log retries if we had to retry
                if attempts > 1:
                    logger.info(f"Test '{test_name}' passed on attempt {attempts}/{max_retries+1}")
                
                return result
                
            except Exception as e:
                STATS["flaky_tests"][test_name]["failures"] += 1
                STATS["flaky_tests"][test_name]["last_failure_time"] = datetime.now().isoformat()
                STATS["flaky_tests"][test_name]["last_error"] = str(e)
                
                # If this is the last attempt, re-raise the exception
                if attempts > max_retries:
                    logger.warning(f"Test '{test_name}' failed after {attempts} attempts: {str(e)}")
                    raise
                
                # Log retry attempt
                logger.info(f"Retrying '{test_name}' after failure: {str(e)} (Attempt {attempts}/{max_retries+1})")
                STATS["flaky_tests"][test_name]["retries"] += 1
                STATS["total_retries"] += 1
                
                # Wait before retrying with exponential backoff
                time.sleep(current_delay)
                current_delay *= backoff_factor
    
    # Mark as a flaky test for pytest plugin discovery
    wrapper._is_flaky = True
    return wrapper

def generate_flaky_report(output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a report of flaky test results.
    
    Args:
        output_path: Optional path to save the report JSON
        
    Returns:
        Dict containing the flaky test report data
    """
    # Use default path if none provided
    if output_path is None:
        output_path = CONFIG["report_path"]
        
    # Ensure the directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # Calculate statistics
    flaky_tests = STATS["flaky_tests"]
    total_tests = STATS["total_tests"]
    flaky_tests_count = len(flaky_tests)
    
    # Generate the report
    report = {
        "timestamp": datetime.now().isoformat(),
        "run_start_time": STATS["run_start_time"],
        "run_end_time": STATS["run_end_time"],
        "duration": None,
        "total_tests": total_tests,
        "flaky_tests_count": flaky_tests_count,
        "flaky_test_percentage": (flaky_tests_count / total_tests * 100) if total_tests > 0 else 0,
        "total_retries": STATS["total_retries"],
        "average_retries_per_flaky_test": (STATS["total_retries"] / flaky_tests_count) if flaky_tests_count > 0 else 0,
        "tests": {}
    }
    
    # Calculate run duration if we have both start and end times
    if STATS["run_start_time"] and STATS["run_end_time"]:
        start = datetime.fromisoformat(STATS["run_start_time"])
        end = datetime.fromisoformat(STATS["run_end_time"])
        report["duration"] = (end - start).total_seconds()
    
    # Add individual test data
    for test_name, test_data in flaky_tests.items():
        # Calculate flakiness percentage
        total_runs = test_data["total_runs"]
        failures = test_data["failures"]
        flakiness_percentage = (failures / total_runs * 100) if total_runs > 0 else 0
        
        report["tests"][test_name] = {
            "total_runs": total_runs,
            "failures": failures,
            "retries": test_data["retries"],
            "flakiness_percentage": flakiness_percentage,
            "last_failure_time": test_data["last_failure_time"],
            "last_success_time": test_data["last_success_time"],
            "last_error": test_data["last_error"],
            "is_flaky": flakiness_percentage >= (CONFIG["flakiness_threshold"] * 100)
        }
    
    # Save the report to file
    if output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_path, f"flaky_report_{timestamp}.json")
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Flaky test report saved to {report_file}")
    
    return report

def register_test_start():
    """Register the start of a test run for timing purposes."""
    STATS["run_start_time"] = datetime.now().isoformat()

def register_test_end():
    """Register the end of a test run for timing purposes."""
    STATS["run_end_time"] = datetime.now().isoformat()

def update_flaky_patterns(new_patterns: List[str]):
    """
    Add new patterns to the list of flaky error patterns.
    
    Args:
        new_patterns: List of regex patterns to add
    """
    for pattern in new_patterns:
        if pattern not in CONFIG["error_patterns"]:
            CONFIG["error_patterns"].append(pattern)

# Initialize at import time
if CONFIG["report_path"]:
    os.makedirs(CONFIG["report_path"], exist_ok=True) 