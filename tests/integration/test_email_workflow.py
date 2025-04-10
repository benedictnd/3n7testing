import pytest
import requests
import logging
import uuid
import time
from test_config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.integration
class TestEmailWorkflow:
    """Integration tests for email-related API functionality."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.base_url = config.BASE_URL
        self.email = config.TEST_EMAIL
        self.password = config.TEST_PASSWORD
        self.token = None
        self.headers = {}
        
        logger.info(f"Setting up integration tests with base URL: {self.base_url}")
        
        # Authenticate before running tests
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with the API to get an access token."""
        try:
            logger.info(f"Authenticating as {self.email}")
            auth_data = {
                "email": self.email,
                "password": self.password
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user = data.get("user", {})
                self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    def test_send_test_email(self):
        """Test sending a test email through the API."""
        logger.info("Testing send test email endpoint")
        
        # Skip test if authentication failed
        if not self.token:
            pytest.skip("Authentication failed, cannot proceed with test")
        
        response = requests.post(
            f"{self.base_url}/email/send-test",
            headers=self.headers
        )
        
        logger.info(f"Test email response status: {response.status_code}")
        
        # Verify the response
        assert response.status_code == 200, f"Failed to send test email: {response.status_code} - {response.text}"
        assert "status" in response.json(), "Response missing status field"
        assert response.json()["status"] == "success", f"Email status was not success: {response.json()}"
        assert "message_id" in response.json(), "Response missing message_id field"
        
        logger.info(f"Test email sent successfully with message ID: {response.json().get('message_id')}")

    def test_send_custom_email(self):
        """Test sending a custom email through the API."""
        logger.info("Testing send custom email endpoint")
        
        # Skip test if authentication failed
        if not self.token:
            pytest.skip("Authentication failed, cannot proceed with test")
        
        # Generate a unique subject for this test run
        subject = f"Integration Test - {uuid.uuid4()}"
        
        # Create email payload
        email_data = {
            "to_email": self.email,  # Send to self
            "subject": subject,
            "html_content": "<h1>Integration Test</h1><p>This is an integration test email from the 3&7 Training Platform API tests.</p>"
        }
        
        # Send the email
        response = requests.post(
            f"{self.base_url}/email/send",
            json=email_data,
            headers=self.headers
        )
        
        logger.info(f"Custom email response status: {response.status_code}")
        
        # Verify the response
        assert response.status_code == 200, f"Failed to send custom email: {response.status_code} - {response.text}"
        assert "status" in response.json(), "Response missing status field"
        assert response.json()["status"] == "success", f"Email status was not success: {response.json()}"
        assert "message_id" in response.json(), "Response missing message_id field"
        
        logger.info(f"Custom email sent successfully with message ID: {response.json().get('message_id')}")

    def test_email_validation(self):
        """Test that the API properly validates email fields."""
        logger.info("Testing email validation")
        
        # Skip test if authentication failed
        if not self.token:
            pytest.skip("Authentication failed, cannot proceed with test")
        
        # Test cases with invalid data
        test_cases = [
            {"payload": {"subject": "Missing Email", "html_content": "<p>Test</p>"}, 
             "expected_error": "Missing required fields"},
            {"payload": {"to_email": "invalid-email", "subject": "Invalid Email", "html_content": "<p>Test</p>"}, 
             "expected_error": "email"},
            {"payload": {"to_email": self.email, "html_content": "<p>Test</p>"}, 
             "expected_error": "Missing required fields"},
            {"payload": {"to_email": self.email, "subject": "Missing Content"}, 
             "expected_error": "Missing required fields"},
        ]
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"Testing validation case {i+1}: {test_case['payload']}")
            
            response = requests.post(
                f"{self.base_url}/email/send",
                json=test_case["payload"],
                headers=self.headers
            )
            
            # Verify the response indicates an error
            assert response.status_code in [400, 422], \
                f"Expected error status code, got {response.status_code} for payload: {test_case['payload']}"
                
            # Check for error message (implementation may vary)
            response_data = response.json()
            error_msg = response_data.get("detail", response_data.get("error", ""))
            
            assert test_case["expected_error"].lower() in str(error_msg).lower(), \
                f"Expected error message containing '{test_case['expected_error']}', got: {error_msg}"
                
            logger.info(f"Validation case {i+1} - received expected error: {error_msg}")

    def test_email_workflow_with_retry(self):
        """Test complete email workflow with retry logic for production environments."""
        logger.info("Testing email workflow with retry logic")
        
        # Skip test if authentication failed
        if not self.token:
            pytest.skip("Authentication failed, cannot proceed with test")
        
        # Generate a unique subject
        subject = f"Integration Test with Retry - {uuid.uuid4()}"
        
        # Create email payload
        email_data = {
            "to_email": self.email,
            "subject": subject,
            "html_content": "<h1>Integration Test</h1><p>This is a retry test email.</p>"
        }
        
        # Attempt to send email with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending email - attempt {attempt}/{max_retries}")
                
                response = requests.post(
                    f"{self.base_url}/email/send",
                    json=email_data,
                    headers=self.headers,
                    timeout=10  # Set a reasonable timeout
                )
                
                # If successful, break out of the retry loop
                if response.status_code == 200:
                    logger.info(f"Email sent successfully on attempt {attempt}")
                    message_id = response.json().get("message_id", "unknown")
                    logger.info(f"Message ID: {message_id}")
                    break
                    
                # If we get a 429 (rate limit), wait longer before retry
                elif response.status_code == 429:
                    retry_delay = int(response.headers.get("Retry-After", retry_delay * 2))
                    logger.warning(f"Rate limited. Retrying after {retry_delay} seconds")
                    
                else:
                    logger.warning(f"Failed to send email: {response.status_code} - {response.text}. Retrying...")
                    
            except Exception as e:
                logger.error(f"Error during email sending: {str(e)}")
                
            # Wait before retry if not the last attempt
            if attempt < max_retries:
                time.sleep(retry_delay)
                
        # Final verification
        assert response.status_code == 200, \
            f"Email sending failed after {max_retries} attempts. Last status: {response.status_code}"
        assert response.json().get("status") == "success", "Email status was not success"
        
        logger.info("Email workflow with retry completed successfully")

if __name__ == "__main__":
    # This allows the tests to be run directly with pytest
    pytest.main(["-v", __file__]) 