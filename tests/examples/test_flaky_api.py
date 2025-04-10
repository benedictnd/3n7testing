#!/usr/bin/env python3
"""
Example Flaky API Tests

This file demonstrates various ways to use the flaky test infrastructure.
The tests in this file are intentionally designed to be flaky for demonstration.
"""

import os
import pytest
import random
import requests
import time
from typing import Dict, Any

import flaky_test_config as ftc
from flaky_test_config import retry_flaky_test

# Base URL for the API
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


class TestFlakyAPI:
    """Test class demonstrating different ways to handle flaky tests."""

    def setup_method(self):
        """Setup before each test method."""
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def teardown_method(self):
        """Teardown after each test method."""
        self.session.close()

    # Example 1: Using the decorator from flaky_test_config
    @retry_flaky_test
    def test_endpoint_with_random_failure(self):
        """Test an endpoint that randomly fails (using decorator)."""
        # Simulate a flaky test with 30% chance of failure
        if random.random() < 0.3:
            raise Exception("Random failure occurred")
        
        # If we got here, the test passes
        assert True

    # Example 2: Using the pytest marker
    @pytest.mark.flaky(reruns=5)
    def test_endpoint_with_occasional_timeout(self):
        """Test an endpoint that occasionally times out (using pytest marker)."""
        # Simulate a flaky test with occasional timeouts
        if random.random() < 0.4:
            time.sleep(0.5)  # Simulate a slow response
            raise TimeoutError("Request timed out")
        
        # If we got here, the test passes
        assert True

    # Example 3: Test with intermittent connection issues
    @retry_flaky_test
    def test_endpoint_with_connection_issues(self):
        """Test an endpoint with intermittent connection issues."""
        # Simulate connection issues with 25% probability
        if random.random() < 0.25:
            raise requests.exceptions.ConnectionError("Connection refused")
        
        # If we got here, the test passes
        response = {"status": "connected"}
        assert response["status"] == "connected"

    # Example 4: Test with rate limiting (needs more retries)
    @retry_flaky_test
    def test_endpoint_with_rate_limiting(self):
        """Test an endpoint that sometimes returns rate limiting errors."""
        # Override retry configuration for this test
        if hasattr(self.test_endpoint_with_rate_limiting, "__name__"):
            test_name = self.test_endpoint_with_rate_limiting.__name__
            ftc.CONFIG["test_overrides"][test_name] = {
                "max_retries": 7,
                "retry_delay": 2.0,
                "backoff_factor": 1.5
            }
        
        # Simulate rate limiting with 20% probability
        if random.random() < 0.2:
            raise requests.exceptions.HTTPError("429 Too Many Requests")
        
        # If we got here, the test passes
        assert True

    # Example 5: Test with network latency
    def test_endpoint_with_network_latency(self):
        """Test an endpoint with variable network latency."""
        # Not marked as flaky, but could still be retried if it fails based on error pattern
        
        # Simulate variable latency
        latency = random.uniform(0.1, 1.0)
        time.sleep(latency)
        
        # Fail if latency is too high (simulating a performance test)
        assert latency < 0.95, f"Latency too high: {latency}s"


# Run this file directly to see retry behavior
if __name__ == "__main__":
    # Setup manually for demonstration
    import sys
    import pytest
    sys.exit(pytest.main(["-v", __file__, "--flaky-enabled"])) 