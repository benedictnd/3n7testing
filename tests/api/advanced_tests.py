import pytest
import requests
import logging
import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from test_config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.advanced
class TestAdvancedAPIScenarios:
    """Advanced API test scenarios including security, performance, and edge cases"""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.base_url = config.BASE_URL
        self.email = config.TEST_EMAIL
        self.password = config.TEST_PASSWORD
        self.auth_token = None
        self.login()
        logger.info(f"Setting up advanced API tests with base URL: {self.base_url}")
    
    def login(self) -> bool:
        """Authenticate with the API and get an auth token."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.auth_token}"}
                logger.info("Successfully authenticated with API")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False
    
    @pytest.mark.security
    def test_rate_limiting(self):
        """Verify API rate limiting functionality."""
        endpoint = "/auth/login"
        successful = 0
        rate_limited = 0
        responses = []
        
        # Burst of requests to trigger rate limiting
        logger.info("Testing rate limiting with a burst of requests")
        for i in range(50):
            try:
                random_password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
                response = requests.post(
                    f"{self.base_url}{endpoint}", 
                    json={"email": self.email, "password": random_password},
                    timeout=5
                )
                responses.append(response.status_code)
                
                if response.status_code == 200:
                    successful += 1
                elif response.status_code == 429:
                    rate_limited += 1
                    # Verify that rate limit headers are present
                    assert "Retry-After" in response.headers, "Rate limit response missing Retry-After header"
                    assert "X-RateLimit-Limit" in response.headers, "Rate limit response missing X-RateLimit-Limit header"
                    assert "X-RateLimit-Remaining" in response.headers, "Rate limit response missing X-RateLimit-Remaining header"
                
                # Don't hammer the server too hard
                time.sleep(0.1)
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error during rate limit test: {str(e)}")
        
        logger.info(f"Rate limit test results: {successful} successful, {rate_limited} rate limited")
        response_counts = {code: responses.count(code) for code in set(responses)}
        logger.info(f"Response code distribution: {response_counts}")
        
        # Check if rate limiting was properly triggered
        if config.ENV == "development" and config.MOCK_API:
            # If we're using the mock API, rate limiting should be active
            assert rate_limited > 0, "No rate limiting observed"
            assert successful < 50, "All requests succeeded, rate limiting may not be working"
        
    @pytest.mark.security
    def test_security_headers(self):
        """Verify presence of security headers in API responses."""
        endpoints = ["/health", "/auth/login"]
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
        
        for endpoint in endpoints:
            logger.info(f"Testing security headers for endpoint: {endpoint}")
            if endpoint == "/auth/login":
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json={"email": self.email, "password": self.password},
                    timeout=5
                )
            else:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
            
            for header, expected_value in required_headers.items():
                assert header in response.headers, f"Missing {header} header on {endpoint}"
                assert response.headers[header] == expected_value, f"Incorrect {header} value on {endpoint}"
            
            logger.info(f"All security headers verified for {endpoint}")
    
    @pytest.mark.parametrize("malicious_input", [
        "<script>alert('xss')</script>",
        "' OR 1=1;--",
        "../../etc/passwd",
        "email@example.com; rm -rf /",
        "{\"$ne\": null}"
    ])
    @pytest.mark.security
    def test_input_validation(self, malicious_input):
        """Test API's resilience against various types of malicious input."""
        logger.info(f"Testing input validation with payload: {malicious_input}")
        
        # Test malicious input in login endpoint
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": malicious_input, "password": malicious_input},
            timeout=5
        )
        
        # Should reject the input
        assert response.status_code in [400, 401, 403, 422], f"Status code {response.status_code} may indicate successful injection"
        
        # Shouldn't return server errors
        assert response.status_code != 500, "Server error on malicious input"
        
        # Check response doesn't contain sensitive information
        response_text = response.text.lower()
        sensitive_terms = ["exception", "stack trace", "error:", "at line", "syntax error", "invalid sql"]
        for term in sensitive_terms:
            assert term not in response_text, f"Response contains sensitive information: {term}"
    
    @pytest.mark.performance
    def test_response_time_consistency(self):
        """Verify consistent response times for health endpoint."""
        endpoint = "/health"
        response_times = []
        
        logger.info(f"Testing response time consistency for {endpoint}")
        for i in range(10):
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            logger.info(f"Request {i+1}: Response time = {elapsed:.4f}s")
            time.sleep(0.5)  # Small delay between requests
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        sorted_times = sorted(response_times)
        median = sorted_times[len(sorted_times) // 2]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        
        logger.info(f"Response time statistics: Avg={avg_time:.4f}s, Median={median:.4f}s, 95th={p95:.4f}s")
        
        # Verify against thresholds from config
        thresholds = config.performance_thresholds
        assert avg_time < thresholds["acceptable"], f"Average response time ({avg_time:.4f}s) exceeds threshold ({thresholds['acceptable']}s)"
        assert p95 < thresholds["max_response_time"], f"95th percentile response time ({p95:.4f}s) exceeds threshold ({thresholds['max_response_time']}s)"
    
    @pytest.mark.performance
    def test_email_endpoint_performance(self):
        """Test the performance of the email endpoints."""
        if not self.auth_token:
            pytest.skip("Authentication required for this test")
        
        # Test the test email endpoint
        logger.info("Testing performance of /email/send-test endpoint")
        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/email/send-test",
            headers=self.headers,
            timeout=10
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Test email endpoint failed with status {response.status_code}"
        logger.info(f"Test email endpoint response time: {elapsed:.4f}s")
        
        # Test should complete within the threshold
        assert elapsed < config.performance_thresholds["slow"], f"Email test endpoint too slow: {elapsed:.4f}s"
    
    @pytest.mark.auth
    def test_authentication_required(self):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            "/users/me",
            "/training-sessions",
            "/email/send-test"
        ]
        
        for endpoint in protected_endpoints:
            logger.info(f"Testing authentication requirement for {endpoint}")
            response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
            
            # Should require authentication
            assert response.status_code in [401, 403], f"Endpoint {endpoint} did not require authentication"
            
            # Now try with authentication
            if self.auth_token:
                auth_response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=5
                )
                # Should not return auth error
                assert auth_response.status_code not in [401, 403], f"Authentication failed for {endpoint}"
    
    @pytest.mark.auth
    def test_token_expiration(self):
        """Test that expired tokens are properly rejected."""
        # This test is for real APIs with token expiration
        if config.ENV == "development" and config.MOCK_API:
            logger.info("Skipping token expiration test in mock API mode")
            pytest.skip("Token expiration not implemented in mock API")
            
        # For real tests, we would need to use an expired token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = requests.get(f"{self.base_url}/users/me", headers=headers, timeout=5)
        assert response.status_code in [401, 403], "Expired token was not rejected"
    
    def teardown_method(self):
        """Clean up after each test."""
        logger.info("Tearing down test")
        # Any necessary cleanup goes here

if __name__ == "__main__":
    # This allows the tests to be run directly with pytest
    pytest.main(["-v", __file__]) 