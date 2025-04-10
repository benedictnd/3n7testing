#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import argparse
import requests
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime

from test_config import (
    TEST_CONFIG,
    ENDPOINTS,
    RESPONSE_CODES,
    SECURITY_HEADERS,
    PERFORMANCE_THRESHOLDS
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_test.log")
    ]
)
logger = logging.getLogger(__name__)

# Timeout exception
class TestTimeoutError(Exception):
    """Exception raised when a test times out"""
    pass

class TimerContext:
    """Context manager for timeouts using threading.Timer"""
    def __init__(self, seconds, message):
        self.seconds = seconds
        self.message = message
        self.timer = None
        
    def __enter__(self):
        def timeout_handler():
            thread_id = threading.current_thread().ident
            logger.error(f"Test timeout in thread {thread_id}: {self.message}")
            # Raise exception in the main thread
            # In Windows we can't use signal.alarm, so we'll just log the error
            
        self.timer = threading.Timer(self.seconds, timeout_handler)
        self.timer.daemon = True
        self.timer.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer:
            self.timer.cancel()

class APITest:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.test_results: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }

    def __del__(self):
        """Clean up resources when object is destroyed"""
        if hasattr(self, 'session') and self.session:
            self.session.close()

    def login(self) -> bool:
        """Login and get authentication token"""
        try:
            # Use timeout context
            with TimerContext(TEST_CONFIG["TEST_TIMEOUT"] / 5, "Login timed out"):
                logger.info(f"Attempting login to {self.base_url}{ENDPOINTS['auth']['login']}")
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}{ENDPOINTS['auth']['login']}",
                    json={"email": self.email, "password": self.password},
                    timeout=TEST_CONFIG["TEST_TIMEOUT"] / 10  # 10% of total timeout
                )
                
                duration = time.time() - start_time
                logger.info(f"Login request completed in {duration:.2f}s")
                
                if response.status_code == RESPONSE_CODES["success"]:
                    data = response.json()
                    self.token = data.get("token")
                    if not self.token:
                        self.token = data.get("access_token")  # Try alternate token name
                    
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    logger.info("Login successful, token obtained")
                    return True
                else:
                    logger.error(f"Login failed: {response.text}")
                    return False
        except requests.exceptions.Timeout:
            logger.error("Login request timed out")
            return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False

    def check_security_headers(self, response: requests.Response) -> bool:
        """Check if response has required security headers"""
        if not TEST_CONFIG.get("CHECK_SECURITY_HEADERS", True):
            return True
            
        missing_headers = []
        for header, expected_value in SECURITY_HEADERS.items():
            if header not in response.headers:
                missing_headers.append(header)
            elif response.headers[header] != expected_value:
                logger.warning(f"Header {header} has unexpected value: {response.headers[header]}")
                
        if missing_headers:
            logger.error(f"Missing security headers: {', '.join(missing_headers)}")
            return False
        return True

    def check_performance(self, start_time: float, endpoint: str) -> bool:
        """Check if response time is within acceptable limits"""
        duration = time.time() - start_time
        if duration > PERFORMANCE_THRESHOLDS["max_response_time"]:
            logger.error(f"Performance threshold exceeded for {endpoint}: {duration:.2f}s")
            return False
        return True

    def run_test(self, name: str, method: str, endpoint: str, 
                expected_status: int, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Run a single test case with timeout protection"""
        test_result = {
            "name": name,
            "endpoint": endpoint,
            "method": method,
            "status": "failed",
            "duration": 0,
            "error": None
        }
        
        try:
            # Use timeout context
            with TimerContext(TEST_CONFIG["TEST_TIMEOUT"] / 2, f"Test {name} timed out"):
                logger.info(f"Running test: {name} - {method} {endpoint}")
                start_time = time.time()
                url = f"{self.base_url}{endpoint}"
                
                # Create a fresh session for each request to avoid potential connection issues
                with requests.Session() as temp_session:
                    # Copy headers from main session
                    if self.token:
                        temp_session.headers.update({"Authorization": f"Bearer {self.token}"})
                    
                    response = temp_session.request(
                        method=method,
                        url=url,
                        json=data,
                        timeout=TEST_CONFIG["TEST_TIMEOUT"] / 4  # 25% of total timeout
                    )
                
                test_result["duration"] = time.time() - start_time
                logger.info(f"Test {name} completed in {test_result['duration']:.2f}s")
                
                # Check response status
                if response.status_code != expected_status:
                    test_result["error"] = f"Expected status {expected_status}, got {response.status_code}"
                    logger.error(f"Test failed: {name} - {test_result['error']}")
                    return test_result
                
                # Check security headers if enabled
                if TEST_CONFIG.get("CHECK_SECURITY_HEADERS", True) and not self.check_security_headers(response):
                    test_result["error"] = "Security headers check failed"
                    return test_result
                
                # Check performance
                if not self.check_performance(start_time, endpoint):
                    test_result["error"] = "Performance threshold exceeded"
                    return test_result
                
                test_result["status"] = "passed"
                logger.info(f"Test passed: {name}")
                return test_result
                
        except TestTimeoutError as te:
            test_result["error"] = f"Test timed out: {str(te)}"
            logger.error(f"Test timeout: {name} - {str(te)}")
            return test_result
        except requests.exceptions.Timeout:
            test_result["error"] = "Request timed out"
            logger.error(f"Request timeout: {name}")
            return test_result
        except Exception as e:
            test_result["error"] = str(e)
            logger.error(f"Test error: {name} - {str(e)}")
            return test_result

    def run_all_tests(self) -> bool:
        """Run all test cases"""
        if not self.login():
            logger.error("Login failed, aborting tests")
            return False
        
        # Set list of tests to run (can be filtered by command line args)
        test_cases = self.get_test_cases()
        
        for test_case in test_cases:
            try:
                result = self.run_test(**test_case)
                self.test_results["tests"].append(result)
                self.test_results["summary"]["total"] += 1
                
                if result["status"] == "passed":
                    self.test_results["summary"]["passed"] += 1
                else:
                    self.test_results["summary"]["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Test case execution error: {test_case['name']} - {str(e)}")
                self.test_results["summary"]["failed"] += 1
                self.test_results["summary"]["total"] += 1
        
        return self.test_results["summary"]["failed"] == 0

    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Get test cases to run, can be filtered by command line args"""
        # Default test cases
        test_cases = [
            {
                "name": "Health Check",
                "method": "GET",
                "endpoint": ENDPOINTS["health"],
                "expected_status": RESPONSE_CODES["success"]
            },
            {
                "name": "Get User Profile",
                "method": "GET",
                "endpoint": ENDPOINTS["user"]["profile"],
                "expected_status": RESPONSE_CODES["success"]
            },
            {
                "name": "Update User Profile",
                "method": "PUT",
                "endpoint": ENDPOINTS["user"]["profile"],
                "expected_status": RESPONSE_CODES["success"],
                "data": {"name": "Test User"}
            },
            {
                "name": "Get Training Sessions",
                "method": "GET",
                "endpoint": ENDPOINTS["training"]["sessions"],
                "expected_status": RESPONSE_CODES["success"]
            },
            {
                "name": "Create Training Session",
                "method": "POST",
                "endpoint": ENDPOINTS["training"]["sessions"],
                "expected_status": RESPONSE_CODES["created"],
                "data": {
                    "title": "Test Session",
                    "description": "Test Description",
                    "date": datetime.now().isoformat()
                }
            }
        ]
        
        return test_cases

def main():
    parser = argparse.ArgumentParser(description="Run API tests for the 3&7 Training Platform")
    parser.add_argument("--url", default=os.getenv("API_BASE_URL", TEST_CONFIG["API_BASE_URL"]), 
                       help="API Base URL")
    parser.add_argument("--email", default=os.getenv("TEST_EMAIL", TEST_CONFIG["TEST_EMAIL"]), 
                       help="Test email")
    parser.add_argument("--password", default=os.getenv("TEST_PASSWORD", TEST_CONFIG["TEST_PASSWORD"]), 
                       help="Test password")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--test-case", help="Comma-separated list of test cases to run (e.g. auth,email)")
    parser.add_argument("--no-security-scan", action="store_true", help="Skip security header checks")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.no_security_scan:
        TEST_CONFIG["CHECK_SECURITY_HEADERS"] = False
    
    logger.info(f"Starting API tests against {args.url}")
    
    try:
        # Use a global timeout context for the entire test run
        with TimerContext(TEST_CONFIG["TEST_TIMEOUT"] * 2, "Complete test run timed out"):
            tester = APITest(args.url, args.email, args.password)
            success = tester.run_all_tests()
            
            if success:
                logger.info("All tests passed successfully!")
                sys.exit(0)
            else:
                logger.error("Some tests failed!")
                sys.exit(1)
                
    except TestTimeoutError:
        logger.critical("Test execution timed out completely")
        sys.exit(2)
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main() 