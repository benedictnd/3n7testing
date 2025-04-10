import pytest
import requests
import time
import random
import logging
import os
from typing import Dict, Any, Optional
import json
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the flaky test manager decorators
from tests.utils.flaky_test_manager import track_flaky_test, retry_flaky_test, get_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants - can be overridden by environment variables
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_EMAIL = os.environ.get("API_EMAIL", "test@example.com")
API_PASSWORD = os.environ.get("API_PASSWORD", "password123")


class TestFlakyAPI:
    """Test class to demonstrate different types of flaky behavior."""

    def setup_method(self):
        """Set up the test environment."""
        self.base_url = API_BASE_URL
        self.email = API_EMAIL
        self.password = API_PASSWORD
        self.auth_token = self._get_auth_token()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        })
        
        # Keep track of test outcomes for reporting
        self.test_results = {
            "stable_endpoint": {"runs": 0, "failures": 0},
            "random_failing_endpoint": {"runs": 0, "failures": 0},
            "timing_sensitive_endpoint": {"runs": 0, "failures": 0},
            "intermittent_server_error": {"runs": 0, "failures": 0},
        }
        
        logger.info(f"Set up test environment with base URL: {self.base_url}")

    def _get_auth_token(self) -> str:
        """Get an authentication token from the API."""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": self.email, "password": self.password}
            )
            response.raise_for_status()
            return response.json().get("access_token", "dummy-token-for-testing")
        except requests.RequestException as e:
            logger.warning(f"Failed to get auth token: {e}. Using dummy token for testing.")
            return "dummy-token-for-testing"

    @track_flaky_test
    def test_stable_endpoint(self):
        """Test a stable endpoint that should always pass."""
        try:
            endpoint = f"{self.base_url}/api/stable-endpoint"
            response = self.session.get(endpoint)
            
            # Simulate response validation
            assert response.status_code in [200, 201], f"Expected 200 or 201, got {response.status_code}"
            
            # Always pass this test
            self.test_results["stable_endpoint"]["runs"] += 1
            logger.info("Stable endpoint test passed")
        except Exception as e:
            self.test_results["stable_endpoint"]["failures"] += 1
            logger.error(f"Stable endpoint test failed: {e}")
            raise

    @retry_flaky_test(max_retries=2, delay_seconds=0.5)
    def test_random_failing_endpoint(self):
        """Test an endpoint that fails randomly about 30% of the time."""
        try:
            endpoint = f"{self.base_url}/api/random-failing-endpoint"
            
            # Simulate a random failure (30% chance)
            self.test_results["random_failing_endpoint"]["runs"] += 1
            if random.random() < 0.3:
                self.test_results["random_failing_endpoint"]["failures"] += 1
                logger.warning("Random failure occurred in random failing endpoint test")
                raise AssertionError("Random test failure occurred")
            
            # Simulate a successful response
            logger.info("Random failing endpoint test passed")
        except Exception as e:
            logger.error(f"Random failing endpoint test failed: {e}")
            raise

    @track_flaky_test
    def test_timing_sensitive_endpoint(self):
        """Test an endpoint with timing sensitivity issues."""
        try:
            endpoint = f"{self.base_url}/api/timing-sensitive-endpoint"
            
            # Add random delay to simulate timing issues
            delay = random.uniform(0.1, 0.9)
            time.sleep(delay)
            
            self.test_results["timing_sensitive_endpoint"]["runs"] += 1
            
            # Fail if delay is in a certain range (making it timing sensitive)
            if 0.4 < delay < 0.6:
                self.test_results["timing_sensitive_endpoint"]["failures"] += 1
                logger.warning(f"Timing sensitive failure occurred with delay {delay:.2f}s")
                raise AssertionError(f"Timing-sensitive failure with delay {delay:.2f}s")
            
            logger.info(f"Timing sensitive endpoint test passed with delay {delay:.2f}s")
        except Exception as e:
            logger.error(f"Timing sensitive endpoint test failed: {e}")
            raise

    @retry_flaky_test(max_retries=3, delay_seconds=0.2)
    def test_intermittent_server_error(self):
        """Test an endpoint that occasionally returns a server error."""
        try:
            endpoint = f"{self.base_url}/api/intermittent-error-endpoint"
            
            self.test_results["intermittent_server_error"]["runs"] += 1
            
            # Simulate intermittent server error (10% chance)
            if random.random() < 0.1:
                self.test_results["intermittent_server_error"]["failures"] += 1
                logger.warning("Simulated server error in intermittent server error test")
                raise requests.HTTPError("500 Server Error: Internal Server Error")
            
            logger.info("Intermittent server error test passed")
        except Exception as e:
            logger.error(f"Intermittent server error test failed: {e}")
            raise

    def teardown_method(self):
        """Clean up after test and report flaky tests."""
        self.session.close()
        
        # Generate report from the flaky test manager
        flaky_manager = get_manager()
        flaky_tests = flaky_manager.get_all_flaky_tests()
        
        if flaky_tests:
            logger.warning(f"Detected {len(flaky_tests)} flaky tests:")
            for test_id in flaky_tests:
                status = flaky_manager.get_test_status(test_id)
                logger.warning(
                    f"  - {test_id}: "
                    f"Score: {status['flakiness_score']:.2f}, "
                    f"Pass rate: {status['pass_rate']:.2f}, "
                    f"Runs: {status['total_runs']}"
                )
        else:
            logger.info("No flaky tests detected yet")
            
        # Log results of all tests
        logger.info("Test run summary:")
        for test_name, results in self.test_results.items():
            if results["runs"] > 0:
                fail_rate = results["failures"] / results["runs"] if results["runs"] > 0 else 0
                logger.info(
                    f"  - {test_name}: "
                    f"Runs: {results['runs']}, "
                    f"Failures: {results['failures']}, "
                    f"Failure rate: {fail_rate:.2f}"
                )


def run_tests_multiple_times(iterations=10):
    """Run the flaky tests multiple times to collect flakiness data."""
    logger.info(f"Running flaky tests for {iterations} iterations")
    
    # Aggregate results
    results = {
        "stable_endpoint": {"runs": 0, "failures": 0},
        "random_failing_endpoint": {"runs": 0, "failures": 0},
        "timing_sensitive_endpoint": {"runs": 0, "failures": 0},
        "intermittent_server_error": {"runs": 0, "failures": 0},
    }
    
    # Run tests multiple times
    for i in range(iterations):
        logger.info(f"Iteration {i+1}/{iterations}")
        test_instance = TestFlakyAPI()
        
        # Run each test and track results
        for test_name in ["test_stable_endpoint", "test_random_failing_endpoint", 
                         "test_timing_sensitive_endpoint", "test_intermittent_server_error"]:
            test_method = getattr(test_instance, test_name)
            test_key = test_name.replace("test_", "")
            
            try:
                test_instance.setup_method()
                test_method()
                results[test_key]["runs"] += 1
            except Exception as e:
                results[test_key]["runs"] += 1
                results[test_key]["failures"] += 1
                logger.error(f"Test {test_name} failed: {e}")
            finally:
                test_instance.teardown_method()
    
    # Generate final report
    logger.info("Final test summary after all iterations:")
    for test_name, test_results in results.items():
        fail_rate = test_results["failures"] / test_results["runs"] if test_results["runs"] > 0 else 0
        logger.info(
            f"  - {test_name}: "
            f"Runs: {test_results['runs']}, "
            f"Failures: {test_results['failures']}, "
            f"Failure rate: {fail_rate:.2f}"
        )
    
    # Generate and save flaky test report
    flaky_manager = get_manager()
    report = flaky_manager.generate_report()
    
    # Print detected flaky tests
    if report["flaky_test_count"] > 0:
        logger.warning(f"Detected {report['flaky_test_count']} flaky tests:")
        for test_id in report["flaky_tests"]:
            test_details = report["test_details"][test_id]
            logger.warning(
                f"  - {test_id.split('.')[-1]}: "
                f"Score: {test_details['flakiness_score']:.2f}, "
                f"Pass rate: {test_details['pass_rate']:.2f}, "
                f"Runs: {test_details['total_runs']}"
            )
    

if __name__ == "__main__":
    # Run tests multiple times to collect flakiness data
    run_tests_multiple_times(10) 