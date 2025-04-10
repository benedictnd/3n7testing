import pytest
import requests
import logging
from test_config import config, SECURITY_HEADERS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.security
class TestSecurityFeatures:
    """Test suite for verifying API security features like headers and rate limiting."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.base_url = config.BASE_URL
        self.headers = {}
        logger.info(f"Setting up security tests with base URL: {self.base_url}")
    
    @pytest.mark.parametrize("header,expected_value", [
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", "DENY"),
        ("X-XSS-Protection", "1; mode=block")
    ])
    def test_security_headers(self, header, expected_value):
        """Test that API responses contain required security headers."""
        logger.info(f"Testing security header: {header}")
        response = requests.get(f"{self.base_url}/health")
        
        assert response.status_code == 200, f"Failed to connect to API: {response.status_code}"
        assert header in response.headers, f"Missing {header} header"
        assert response.headers[header] == expected_value, \
            f"Incorrect header value. Expected: {expected_value}, Got: {response.headers.get(header, 'MISSING')}"
    
    def test_all_security_headers_present(self):
        """Test that all required security headers are present in API responses."""
        logger.info("Testing all security headers are present")
        endpoints = ["/health", "/auth/login", "/email/send-test"]
        
        for endpoint in endpoints:
            logger.info(f"Checking headers for endpoint: {endpoint}")
            method = "GET" if endpoint != "/auth/login" and endpoint != "/email/send-test" else "POST"
            
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}")
            else:
                # Use minimal data for POST requests
                data = {"email": "test@example.com", "password": "password123"} if endpoint == "/auth/login" else {}
                response = requests.post(f"{self.base_url}{endpoint}", json=data)
            
            # Check if request was successful or returned expected error
            assert response.status_code in [200, 201, 401, 404], \
                f"Unexpected status code {response.status_code} for {endpoint}"
            
            # Check all required headers
            for header, expected_value in SECURITY_HEADERS.items():
                assert header in response.headers, f"Missing {header} header in {endpoint} response"
                assert response.headers[header] == expected_value, \
                    f"Incorrect header value for {header} in {endpoint} response. Expected: {expected_value}, Got: {response.headers.get(header)}"
    
    @pytest.mark.rate_limit
    def test_rate_limiting(self):
        """Test that rate limiting is correctly implemented."""
        logger.info("Testing rate limiting functionality")
        
        # Make multiple requests to trigger rate limiting
        limit_endpoint = f"{self.base_url}/test-rate-limit"
        responses = []
        
        # Make more requests than the limit allows
        for i in range(10):
            logger.info(f"Making request {i+1}/10 to test rate limiting")
            response = requests.get(limit_endpoint)
            responses.append(response)
            
            # Check if we got a rate limit response
            if response.status_code == 429:
                logger.info(f"Rate limit triggered after {i+1} requests")
                # Verify that the Retry-After header is present
                assert "Retry-After" in response.headers, "Rate limit response missing Retry-After header"
                break
        
        # Verify that rate limiting was triggered
        assert any(r.status_code == 429 for r in responses), "Rate limiting was not triggered"
        
    @pytest.mark.auth
    def test_authentication_required(self):
        """Test that protected endpoints require authentication."""
        logger.info("Testing authentication requirements")
        
        # List of endpoints that should require authentication
        protected_endpoints = [
            "/users/me",
            "/training-sessions",
            "/email/send-test"
        ]
        
        for endpoint in protected_endpoints:
            logger.info(f"Testing authentication for endpoint: {endpoint}")
            response = requests.get(f"{self.base_url}{endpoint}")
            
            # Should return 401 Unauthorized or similar
            assert response.status_code in [401, 403], \
                f"Endpoint {endpoint} did not require authentication. Got status code: {response.status_code}"
            logger.info(f"Endpoint {endpoint} correctly requires authentication")

if __name__ == "__main__":
    # This allows the tests to be run directly with pytest
    pytest.main(["-v", __file__]) 