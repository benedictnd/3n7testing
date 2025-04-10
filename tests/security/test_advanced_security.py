import pytest
import requests
import logging
import json
import time
from datetime import datetime, timedelta
from test_config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@pytest.mark.security
class TestAdvancedSecurityFeatures:
    """Advanced security test suite for the 3&7 Training Platform API."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.base_url = config.BASE_URL
        self.email = config.TEST_EMAIL
        self.password = config.TEST_PASSWORD
        self.token = self._get_auth_token()
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        logger.info(f"Setting up advanced security tests with base URL: {self.base_url}")
    
    def _get_auth_token(self):
        """Get authentication token for testing."""
        try:
            auth_data = {
                "email": self.email,
                "password": self.password
            }
            response = requests.post(f"{self.base_url}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    @pytest.mark.auth
    def test_jwt_token_invalidation(self):
        """Test that invalidated JWT tokens are properly rejected."""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        # First request should succeed with valid token
        response1 = requests.get(f"{self.base_url}/users/me", headers=self.headers)
        assert response1.status_code == 200, "Valid token request failed"
        
        # Simulate token invalidation (typically by logout)
        logout_response = requests.post(
            f"{self.base_url}/auth/logout", 
            headers=self.headers
        )
        assert logout_response.status_code in [200, 204], "Logout failed"
        
        # Second request with same token should fail
        time.sleep(1)  # Ensure token invalidation has propagated
        response2 = requests.get(f"{self.base_url}/users/me", headers=self.headers)
        assert response2.status_code == 401, "Invalidated token was not rejected"
        
        logger.info("JWT token invalidation works correctly")
    
    @pytest.mark.auth
    def test_token_expiration(self):
        """Test that expired tokens are properly rejected."""
        if not self.token:
            pytest.skip("Authentication token not available")
            
        # This test is more difficult to automate since we can't force token expiration
        # We could check the JWT payload to verify the expiration time is set properly
        
        # Decode JWT token payload (without verification)
        token_parts = self.token.split('.')
        if len(token_parts) != 3:
            pytest.skip("Token doesn't appear to be a valid JWT")
            
        import base64
        payload = token_parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded_payload = base64.b64decode(payload)
        token_data = json.loads(decoded_payload)
        
        # Check that token has an expiration claim
        assert 'exp' in token_data, "Token missing expiration claim"
        
        # Verify expiration is in the future
        expiration = datetime.fromtimestamp(token_data['exp'])
        now = datetime.now()
        assert expiration > now, "Token already expired"
        
        # Calculate token lifetime
        lifetime = expiration - now
        logger.info(f"Token lifetime: {lifetime}")
        
        # Verify token lifetime is reasonable (not too long)
        assert lifetime < timedelta(days=1), "Token lifetime too long"
        
        logger.info("Token expiration correctly configured")
    
    @pytest.mark.security
    def test_mass_assignment_protection(self):
        """Test that the API is protected against mass assignment vulnerabilities."""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        # Attempt to update user with a privileged field that shouldn't be updatable
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "is_admin": True,  # This should be ignored
            "role": "admin"    # This should be ignored
        }
        
        # Make the update request
        response = requests.put(
            f"{self.base_url}/users/me",
            headers=self.headers,
            json=update_data
        )
        
        # Verify request was accepted
        assert response.status_code in [200, 201, 204], "User update failed"
        
        # Check if the user data was updated correctly
        user_response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
        assert user_response.status_code == 200, "Couldn't retrieve user data"
        
        user_data = user_response.json()
        
        # Verify name was updated
        assert user_data.get('name') == "Updated Name", "Name was not updated"
        
        # Verify privileged fields were not updated
        assert user_data.get('role') != "admin", "Mass assignment protection failed - role was updated"
        assert not user_data.get('is_admin', False), "Mass assignment protection failed - is_admin was updated"
        
        logger.info("Mass assignment protection is working correctly")
    
    @pytest.mark.security
    def test_content_security_policy(self):
        """Test that Content-Security-Policy header is properly set."""
        response = requests.get(f"{self.base_url}/health")
        
        assert response.status_code == 200, "Health check failed"
        assert "Content-Security-Policy" in response.headers, "CSP header missing"
        
        csp = response.headers["Content-Security-Policy"]
        
        # Check for essential CSP directives
        assert "default-src 'self'" in csp, "CSP missing default-src directive"
        
        logger.info("Content Security Policy is properly configured")
    
    @pytest.mark.security
    def test_csrf_protection(self):
        """Test Cross-Site Request Forgery protection."""
        if not self.token:
            pytest.skip("Authentication token not available")
        
        # For APIs using JWT in Authorization header, CSRF isn't typically an issue
        # But we can test that state-changing operations require proper Authorization
        
        # Try to send a test email without authentication
        email_data = {
            "to_email": "test@example.com",
            "subject": "Test Subject",
            "html_content": "<p>Test Content</p>"
        }
        
        response = requests.post(
            f"{self.base_url}/email/send",
            json=email_data
        )
        
        # Expect authentication error
        assert response.status_code in [401, 403], f"CSRF protection failed - unauthenticated request returned {response.status_code}"
        
        logger.info("CSRF protection is working correctly")
    
    def teardown_method(self):
        """Clean up after each test."""
        logger.info("Completed advanced security test")

if __name__ == "__main__":
    # This allows the tests to be run directly with pytest
    pytest.main(["-v", __file__]) 