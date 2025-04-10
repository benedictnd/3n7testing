#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced API Test Suite

This script extends the basic API test suite with advanced testing scenarios including:
- Rate limiting tests
- Security tests (headers, auth, CORS)
- Input validation tests
- Edge case handling

Usage:
    python run_advanced_tests.py --base-url http://localhost:3000 --email test@example.com --password securepassword
"""

import argparse
import json
import logging
import os
import sys
import time
import concurrent.futures
import random
import string
import datetime
import requests
from requests.exceptions import RequestException, Timeout
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('test-logs', 'advanced_tests.log'))
    ]
)
logger = logging.getLogger(__name__)

# Default test configuration
TEST_CONFIG = {
    "TEST_LOGS_DIR": "test-logs",
    "RATE_LIMIT_THRESHOLD": 50,  # Requests per minute
    "RATE_LIMIT_DURATION": 60,   # Duration in seconds for rate limit test
    "SECURITY_HEADERS": [
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security"
    ],
    "AUTH_ENDPOINTS": [
        "/api/user/profile",
        "/api/admin",
        "/api/settings"
    ],
    "INPUT_VALIDATION": {
        "endpoint": "/api/items",
        "method": "POST",
        "tests": [
            {"name": "empty_payload", "payload": {}, "expected_status": 400},
            {"name": "invalid_json", "payload": "not_json", "expected_status": 400},
            {"name": "sql_injection", "payload": {"name": "'; DROP TABLE items; --"}, "expected_status": 400},
            {"name": "xss_attack", "payload": {"name": "<script>alert('XSS')</script>"}, "expected_status": 400},
        ]
    }
}

class AdvancedTestRunner:
    """Runs advanced API test scenarios including rate limiting and security tests"""
    
    def __init__(self, base_url, email=None, password=None, verbose=False):
        """
        Initialize the advanced test runner with authentication credentials
        
        Args:
            base_url (str): The base URL of the API
            email (str): Email for authentication
            password (str): Password for authentication
            verbose (bool): Whether to enable verbose logging
        """
        self.base_url = base_url
        self.email = email
        self.password = password
        self.verbose = verbose
        
        # Configure logging level based on verbosity
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        # Create test logs directory if it doesn't exist
        os.makedirs(TEST_CONFIG["TEST_LOGS_DIR"], exist_ok=True)
        
        # Initialize session and results
        self.session = requests.Session()
        self.test_results = {
            "start_time": datetime.datetime.now().isoformat(),
            "base_url": base_url,
            "rate_limit_tests": {},
            "security_tests": {},
            "input_validation_tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        logger.info(f"Advanced test runner initialized with base URL: {base_url}")
    
    def authenticate(self):
        """Authenticate with the API"""
        if not self.email or not self.password:
            logger.warning("No authentication credentials provided, skipping authentication")
            return False
        
        try:
            auth_endpoint = urljoin(self.base_url, "/api/auth/login")
            response = self.session.post(
                auth_endpoint,
                json={"email": self.email, "password": self.password},
                timeout=10
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                if "token" in auth_data:
                    self.session.headers.update({"Authorization": f"Bearer {auth_data['token']}"})
                    logger.info("Authentication successful")
                    return True
                else:
                    logger.error("Authentication response missing token")
            else:
                logger.error(f"Authentication failed with status code: {response.status_code}")
                
            return False
        except RequestException as e:
            logger.error(f"Authentication request failed: {str(e)}")
            return False
    
    def run_rate_limit_tests(self):
        """Test rate limiting by sending many requests in a short time period"""
        logger.info("Starting rate limit tests")
        
        rate_limit_endpoint = urljoin(self.base_url, "/api/items")
        results = {
            "endpoint": rate_limit_endpoint,
            "threshold": TEST_CONFIG["RATE_LIMIT_THRESHOLD"],
            "duration": TEST_CONFIG["RATE_LIMIT_DURATION"],
            "requests_sent": 0,
            "requests_succeeded": 0,
            "requests_limited": 0,
            "rate_limited": False,
            "passed": False
        }
        
        start_time = time.time()
        end_time = start_time + TEST_CONFIG["RATE_LIMIT_DURATION"]
        
        # Track response codes
        response_codes = {}
        
        # Send requests as fast as possible until duration expires
        while time.time() < end_time:
            try:
                results["requests_sent"] += 1
                response = self.session.get(rate_limit_endpoint, timeout=2)
                
                # Track response codes
                status_code = response.status_code
                response_codes[status_code] = response_codes.get(status_code, 0) + 1
                
                if status_code == 200:
                    results["requests_succeeded"] += 1
                elif status_code == 429:  # Too Many Requests
                    results["requests_limited"] += 1
                    results["rate_limited"] = True
                    
                    # If we've confirmed rate limiting, we can stop
                    if results["requests_limited"] >= 3:
                        logger.info("Rate limiting confirmed after 3 limited responses")
                        break
                    
                # Small delay to avoid overwhelming the server unnecessarily
                time.sleep(0.05)
                
            except RequestException as e:
                logger.debug(f"Request failed during rate limit test: {str(e)}")
        
        # Calculate requests per minute
        elapsed_time = time.time() - start_time
        requests_per_minute = (results["requests_sent"] / elapsed_time) * 60
        
        results["elapsed_time"] = elapsed_time
        results["requests_per_minute"] = requests_per_minute
        results["response_codes"] = response_codes
        
        # Determine if the test passed based on whether rate limiting was observed
        # The test passes if either:
        # 1. Rate limiting was observed (429 responses)
        # 2. We couldn't exceed the threshold despite our best efforts
        if results["rate_limited"] or requests_per_minute < TEST_CONFIG["RATE_LIMIT_THRESHOLD"]:
            results["passed"] = True
            logger.info(f"Rate limit test passed: {requests_per_minute:.2f} req/min, limited: {results['rate_limited']}")
            self.test_results["summary"]["passed"] += 1
        else:
            logger.warning(f"Rate limit test failed: Sent {requests_per_minute:.2f} req/min without hitting limits")
            self.test_results["summary"]["failed"] += 1
        
        self.test_results["summary"]["total"] += 1
        self.test_results["rate_limit_tests"] = results
        
        return results["passed"]
    
    def run_security_header_tests(self):
        """Test security headers returned by the API"""
        logger.info("Starting security header tests")
        
        results = {
            "headers_tested": TEST_CONFIG["SECURITY_HEADERS"],
            "endpoints_tested": [],
            "results": {},
            "missing_headers": [],
            "passed": True
        }
        
        # Test the homepage or API root for security headers
        endpoints = ["/", "/api", "/api/health"]
        
        for endpoint in endpoints:
            try:
                full_url = urljoin(self.base_url, endpoint)
                response = self.session.get(full_url, timeout=10)
                
                # Skip endpoints that return 404
                if response.status_code == 404:
                    continue
                    
                results["endpoints_tested"].append(endpoint)
                
                # Check for required security headers
                endpoint_results = {}
                for header in TEST_CONFIG["SECURITY_HEADERS"]:
                    header_present = header.lower() in (h.lower() for h in response.headers.keys())
                    endpoint_results[header] = header_present
                    
                    if not header_present and header not in results["missing_headers"]:
                        results["missing_headers"].append(header)
                        results["passed"] = False
                
                results["results"][endpoint] = endpoint_results
                
            except RequestException as e:
                logger.error(f"Security header test failed for {endpoint}: {str(e)}")
                results["results"][endpoint] = {"error": str(e)}
        
        # Update test summary
        if results["passed"]:
            logger.info("Security header tests passed")
            self.test_results["summary"]["passed"] += 1
        else:
            logger.warning(f"Security header tests failed: Missing headers: {results['missing_headers']}")
            self.test_results["summary"]["failed"] += 1
            
        self.test_results["summary"]["total"] += 1
        self.test_results["security_tests"]["headers"] = results
        
        return results["passed"]
    
    def run_auth_protection_tests(self):
        """Test that protected endpoints require authentication"""
        logger.info("Starting authentication protection tests")
        
        results = {
            "endpoints_tested": TEST_CONFIG["AUTH_ENDPOINTS"],
            "results": {},
            "unprotected_endpoints": [],
            "passed": True
        }
        
        # Create a clean session without auth
        clean_session = requests.Session()
        
        for endpoint in TEST_CONFIG["AUTH_ENDPOINTS"]:
            try:
                full_url = urljoin(self.base_url, endpoint)
                response = clean_session.get(full_url, timeout=10)
                
                # Check if we can access the endpoint without authentication
                # Expected: 401 Unauthorized or 403 Forbidden
                is_protected = response.status_code in (401, 403)
                results["results"][endpoint] = {
                    "status_code": response.status_code,
                    "is_protected": is_protected
                }
                
                if not is_protected:
                    results["unprotected_endpoints"].append(endpoint)
                    results["passed"] = False
                    logger.warning(f"Endpoint {endpoint} is not properly protected. Status code: {response.status_code}")
                
            except RequestException as e:
                logger.error(f"Auth protection test failed for {endpoint}: {str(e)}")
                results["results"][endpoint] = {"error": str(e)}
        
        # Update test summary
        if results["passed"]:
            logger.info("Authentication protection tests passed")
            self.test_results["summary"]["passed"] += 1
        else:
            logger.warning(f"Authentication protection tests failed. Unprotected endpoints: {results['unprotected_endpoints']}")
            self.test_results["summary"]["failed"] += 1
            
        self.test_results["summary"]["total"] += 1
        self.test_results["security_tests"]["auth_protection"] = results
        
        return results["passed"]
    
    def run_input_validation_tests(self):
        """Test input validation by sending malformed data to an endpoint"""
        logger.info("Starting input validation tests")
        
        input_validation = TEST_CONFIG["INPUT_VALIDATION"]
        endpoint = urljoin(self.base_url, input_validation["endpoint"])
        method = input_validation["method"].lower()
        tests = input_validation["tests"]
        
        results = {
            "endpoint": endpoint,
            "method": method,
            "tests": {},
            "passed": True
        }
        
        for test in tests:
            test_name = test["name"]
            payload = test["payload"]
            expected_status = test["expected_status"]
            
            try:
                if method == "post":
                    # Handle special case for sending invalid JSON as a string
                    if test_name == "invalid_json":
                        response = self.session.post(
                            endpoint, 
                            data=payload,  # Send as raw data, not JSON
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                    else:
                        response = self.session.post(endpoint, json=payload, timeout=10)
                elif method == "put":
                    response = self.session.put(endpoint, json=payload, timeout=10)
                else:
                    logger.error(f"Unsupported method for input validation test: {method}")
                    continue
                
                test_passed = response.status_code == expected_status
                results["tests"][test_name] = {
                    "payload": str(payload),  # Convert to string for JSON serialization
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "passed": test_passed
                }
                
                if not test_passed:
                    results["passed"] = False
                    logger.warning(f"Input validation test '{test_name}' failed. "
                                f"Expected status: {expected_status}, "
                                f"Actual status: {response.status_code}")
                
            except RequestException as e:
                logger.error(f"Input validation test '{test_name}' failed with error: {str(e)}")
                results["tests"][test_name] = {
                    "payload": str(payload),
                    "expected_status": expected_status,
                    "error": str(e),
                    "passed": False
                }
                results["passed"] = False
        
        # Update test summary
        if results["passed"]:
            logger.info("Input validation tests passed")
            self.test_results["summary"]["passed"] += 1
        else:
            logger.warning("Input validation tests failed")
            self.test_results["summary"]["failed"] += 1
            
        self.test_results["summary"]["total"] += 1
        self.test_results["input_validation_tests"] = results
        
        return results["passed"]
    
    def run_tests(self, rate_limit_tests=True, security_tests=True, input_validation_tests=True):
        """Run the selected test suites"""
        logger.info("Starting advanced API tests")
        
        # Authenticate if credentials are provided
        if self.email and self.password:
            if not self.authenticate():
                logger.error("Authentication failed, some tests may fail")
        
        # Track passing status
        all_passed = True
        
        # Run rate limit tests
        if rate_limit_tests:
            rate_limit_passed = self.run_rate_limit_tests()
            all_passed = all_passed and rate_limit_passed
        
        # Run security tests
        if security_tests:
            header_tests_passed = self.run_security_header_tests()
            auth_tests_passed = self.run_auth_protection_tests()
            all_passed = all_passed and header_tests_passed and auth_tests_passed
        
        # Run input validation tests
        if input_validation_tests:
            input_validation_passed = self.run_input_validation_tests()
            all_passed = all_passed and input_validation_passed
        
        # Record end time
        self.test_results["end_time"] = datetime.datetime.now().isoformat()
        
        # Calculate duration
        start_time = datetime.datetime.fromisoformat(self.test_results["start_time"])
        end_time = datetime.datetime.fromisoformat(self.test_results["end_time"])
        self.test_results["duration_seconds"] = (end_time - start_time).total_seconds()
        
        logger.info(f"Advanced tests completed in {self.test_results['duration_seconds']:.2f} seconds")
        logger.info(f"Total tests: {self.test_results['summary']['total']}, "
                 f"Passed: {self.test_results['summary']['passed']}, "
                 f"Failed: {self.test_results['summary']['failed']}, "
                 f"Skipped: {self.test_results['summary']['skipped']}")
        
        return all_passed
    
    def save_results(self, output_file):
        """Save test results to a JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"Test results saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save test results: {str(e)}")
            return False

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Run advanced API tests")
    parser.add_argument("--base-url", required=True, help="Base URL of the API")
    parser.add_argument("--email", help="Email for API authentication")
    parser.add_argument("--password", help="Password for API authentication")
    parser.add_argument("--rate-limit-tests", action="store_true", help="Run rate limiting tests")
    parser.add_argument("--security-tests", action="store_true", help="Run security tests")
    parser.add_argument("--input-validation-tests", action="store_true", help="Run input validation tests")
    parser.add_argument("--output", default="test-logs/advanced_tests.json", help="Output file for test results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Ensure at least one test type is selected
    if not any([args.rate_limit_tests, args.security_tests, args.input_validation_tests]):
        # If no specific tests are selected, run all of them
        args.rate_limit_tests = True
        args.security_tests = True
        args.input_validation_tests = True
        logger.info("No specific tests selected, running all advanced tests")
    
    # Create test runner
    test_runner = AdvancedTestRunner(
        base_url=args.base_url,
        email=args.email,
        password=args.password,
        verbose=args.verbose
    )
    
    # Run tests
    tests_passed = test_runner.run_tests(
        rate_limit_tests=args.rate_limit_tests,
        security_tests=args.security_tests,
        input_validation_tests=args.input_validation_tests
    )
    
    # Save results
    test_runner.save_results(args.output)
    
    # Return appropriate exit code
    sys.exit(0 if tests_passed else 1)

if __name__ == "__main__":
    main() 