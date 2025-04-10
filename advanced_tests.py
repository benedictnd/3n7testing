#!/usr/bin/env python3
import requests
import time
import logging
import argparse
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test-logs/advanced_tests.log")
    ]
)
logger = logging.getLogger(__name__)

class AdvancedAPITests:
    """Advanced API test scenarios focused on rate limiting, security, and edge cases"""
    
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None
        self.session = requests.Session()
        
        # Create test logs directory if it doesn't exist
        Path("test-logs").mkdir(exist_ok=True)
        
        # Initialize results dictionary
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
    
    def login(self) -> bool:
        """Authenticate with the API and get token"""
        try:
            logger.info(f"Attempting login to {self.base_url}/auth/login")
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": self.email,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    logger.info("Login successful, token obtained")
                    return True
                else:
                    logger.error("Login response did not contain token")
                    return False
            else:
                logger.error(f"Login failed with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
    
    def _record_test_result(self, name: str, passed: bool, duration: float, details: Dict[str, Any] = None):
        """Record test result in the results dictionary"""
        result = {
            "name": name,
            "passed": passed,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            result["details"] = details
            
        self.results["tests"].append(result)
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
    
    def test_rate_limiting(self, endpoint: str = "/health", requests_per_second: int = 20, duration: int = 5) -> bool:
        """
        Test rate limiting by sending many requests in a short time
        
        Args:
            endpoint: API endpoint to test
            requests_per_second: Number of requests to send per second
            duration: Duration of the test in seconds
            
        Returns:
            bool: True if rate limiting works as expected, False otherwise
        """
        logger.info(f"Testing rate limiting on {endpoint} with {requests_per_second} req/s for {duration}s")
        start_time = time.time()
        
        url = f"{self.base_url}{endpoint}"
        success_count = 0
        rate_limited_count = 0
        total_requests = requests_per_second * duration
        
        async def make_requests():
            nonlocal success_count, rate_limited_count
            
            async def single_request(session, i):
                nonlocal success_count, rate_limited_count
                try:
                    headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            success_count += 1
                        elif response.status == 429:
                            rate_limited_count += 1
                            logger.debug(f"Request {i} was rate limited")
                        return response.status
                except Exception as e:
                    logger.error(f"Error in request {i}: {str(e)}")
                    return 0
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for second in range(duration):
                    # Create batch of requests for this second
                    for i in range(requests_per_second):
                        task = asyncio.ensure_future(single_request(session, second * requests_per_second + i))
                        tasks.append(task)
                    
                    # Wait for 1 second before next batch
                    await asyncio.sleep(1)
                
                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks)
                return results
        
        # Run the async requests
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(make_requests())
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        success_rate = success_count / total_requests * 100
        rate_limited_rate = rate_limited_count / total_requests * 100
        
        logger.info(f"Rate limiting test completed in {duration:.2f}s")
        logger.info(f"Success rate: {success_rate:.2f}% ({success_count}/{total_requests})")
        logger.info(f"Rate limited: {rate_limited_rate:.2f}% ({rate_limited_count}/{total_requests})")
        
        # Test passes if we got some successful requests and some rate limited
        passed = success_count > 0 and rate_limited_count > 0
        
        details = {
            "endpoint": endpoint,
            "requests_per_second": requests_per_second,
            "duration": duration,
            "total_requests": total_requests,
            "success_count": success_count,
            "rate_limited_count": rate_limited_count,
            "success_rate": success_rate,
            "rate_limited_rate": rate_limited_rate
        }
        
        self._record_test_result("Rate Limiting Test", passed, duration, details)
        
        if passed:
            logger.info("Rate limiting test passed: Rate limiting is working correctly")
        else:
            logger.error("Rate limiting test failed: Rate limiting might not be working correctly")
            
        return passed
    
    def test_security_headers(self, endpoints: List[str] = None) -> bool:
        """
        Test security headers on multiple endpoints
        
        Args:
            endpoints: List of endpoints to test, defaults to ["/health", "/users/me"]
            
        Returns:
            bool: True if all endpoints have required security headers, False otherwise
        """
        if endpoints is None:
            endpoints = ["/health", "/users/me"]
            
        logger.info(f"Testing security headers on {len(endpoints)} endpoints")
        
        # Security headers we expect to find
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
        
        all_passed = True
        results = {}
        start_time = time.time()
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Checking security headers for {url}")
            
            try:
                response = self.session.get(url)
                
                # Check if all required headers are present with expected values
                endpoint_passed = True
                missing_headers = []
                incorrect_headers = []
                
                for header, expected_value in required_headers.items():
                    if header not in response.headers:
                        endpoint_passed = False
                        missing_headers.append(header)
                    elif response.headers[header] != expected_value:
                        endpoint_passed = False
                        incorrect_headers.append(f"{header}: expected '{expected_value}', got '{response.headers[header]}'")
                
                if endpoint_passed:
                    logger.info(f"All security headers present for {endpoint}")
                else:
                    if missing_headers:
                        logger.error(f"Missing security headers for {endpoint}: {', '.join(missing_headers)}")
                    if incorrect_headers:
                        logger.error(f"Incorrect security headers for {endpoint}: {', '.join(incorrect_headers)}")
                
                results[endpoint] = {
                    "passed": endpoint_passed,
                    "status_code": response.status_code,
                    "missing_headers": missing_headers,
                    "incorrect_headers": incorrect_headers,
                    "all_headers": dict(response.headers)
                }
                
                all_passed = all_passed and endpoint_passed
                
            except Exception as e:
                logger.error(f"Error checking security headers for {endpoint}: {str(e)}")
                results[endpoint] = {
                    "passed": False,
                    "error": str(e)
                }
                all_passed = False
        
        duration = time.time() - start_time
        
        details = {
            "endpoints": endpoints,
            "required_headers": required_headers,
            "results": results
        }
        
        self._record_test_result("Security Headers Test", all_passed, duration, details)
        
        if all_passed:
            logger.info("Security headers test passed: All required headers are present")
        else:
            logger.error("Security headers test failed: Some headers are missing or incorrect")
            
        return all_passed
    
    def test_input_validation(self) -> bool:
        """
        Test input validation by sending invalid input to various endpoints
        
        Returns:
            bool: True if all endpoints properly validate input, False otherwise
        """
        logger.info("Testing input validation on various endpoints")
        
        test_cases = [
            # Test case format: (endpoint, method, data, expected_status)
            ("/auth/login", "POST", {"email": "invalid", "password": "test"}, 400),  # Invalid email
            ("/auth/login", "POST", {"email": "test@example.com", "password": ""}, 400),  # Empty password
            ("/auth/login", "POST", {}, 400),  # Empty body
            ("/training-sessions", "POST", {"title": "a" * 300}, 400),  # Title too long
            ("/users/me", "PUT", {"email": "invalid"}, 400),  # Invalid email in update
        ]
        
        all_passed = True
        results = {}
        start_time = time.time()
        
        for endpoint, method, data, expected_status in test_cases:
            test_name = f"{method} {endpoint} with {str(data)[:30]}..."
            logger.info(f"Testing input validation: {test_name}")
            
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", params=data)
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                elif method == "PUT":
                    response = self.session.put(f"{self.base_url}{endpoint}", json=data)
                elif method == "DELETE":
                    response = self.session.delete(f"{self.base_url}{endpoint}", json=data)
                else:
                    logger.error(f"Unsupported method: {method}")
                    continue
                
                # Check if status code matches expected
                passed = response.status_code == expected_status
                
                if passed:
                    logger.info(f"Input validation passed for {test_name}: Got expected status {expected_status}")
                else:
                    logger.error(f"Input validation failed for {test_name}: Expected status {expected_status}, got {response.status_code}")
                
                results[test_name] = {
                    "passed": passed,
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "response_body": response.text[:200]  # Truncate long responses
                }
                
                all_passed = all_passed and passed
                
            except Exception as e:
                logger.error(f"Error testing input validation for {test_name}: {str(e)}")
                results[test_name] = {
                    "passed": False,
                    "error": str(e)
                }
                all_passed = False
        
        duration = time.time() - start_time
        
        details = {
            "test_cases": [{"endpoint": tc[0], "method": tc[1], "data": tc[2], "expected_status": tc[3]} for tc in test_cases],
            "results": results
        }
        
        self._record_test_result("Input Validation Test", all_passed, duration, details)
        
        if all_passed:
            logger.info("Input validation test passed: All endpoints properly validate input")
        else:
            logger.error("Input validation test failed: Some endpoints do not properly validate input")
            
        return all_passed
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all advanced tests and return results"""
        logger.info("Starting advanced API tests")
        
        # Login first
        if not self.login():
            logger.error("Login failed, cannot proceed with tests")
            return self.results
        
        # Run all tests
        self.test_rate_limiting()
        self.test_security_headers()
        self.test_input_validation()
        
        # Save results to file
        self.save_results()
        
        return self.results
    
    def save_results(self, filename: str = None) -> None:
        """Save test results to a JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test-logs/advanced_test_results_{timestamp}.json"
            
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
            
        logger.info(f"Test results saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Run advanced API tests")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--email", default="test@example.com", help="Email for authentication")
    parser.add_argument("--password", default="password123", help="Password for authentication")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the tests
    tester = AdvancedAPITests(args.url, args.email, args.password)
    results = tester.run_all_tests()
    
    # Print summary
    print("\nAdvanced API Test Summary:")
    print(f"Total tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    
    return 0 if results["summary"]["failed"] == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 