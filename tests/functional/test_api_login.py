"""
API Login Tests

This module contains tests for the API login functionality.
"""

import json
import logging
import os
import pytest
import sys
from typing import Dict, Any

# Add the parent directory to the Python path to be able to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.api_test_utils import (
    make_request,
    assert_status_code,
    assert_json_response,
    assert_response_time,
    assert_header_present,
    assert_json_schema,
)

# Test configuration - would be moved to test_config.py in a real project
TEST_CONFIG = {
    'BASE_URL': os.environ.get('API_BASE_URL', 'http://localhost:8000'),
    'LOGIN_ENDPOINT': '/api/auth/login',
    'TEST_EMAIL': os.environ.get('TEST_EMAIL', 'test@example.com'),
    'TEST_PASSWORD': os.environ.get('TEST_PASSWORD', 'password123'),
    'MAX_RESPONSE_TIME': 2.0,  # seconds
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger('test_api_login')

# Login response schema for validation
LOGIN_RESPONSE_SCHEMA = {
    'access_token': {'type': 'string', 'required': True},
    'refresh_token': {'type': 'string', 'required': True},
    'user': {
        'type': 'object',
        'required': True,
        'properties': {
            'id': {'type': 'integer', 'required': True},
            'email': {'type': 'string', 'required': True},
            'name': {'type': 'string', 'required': True},
        },
    },
    'expires_in': {'type': 'integer', 'required': True},
}

# Test fixtures
@pytest.fixture
def login_url() -> str:
    """Return the full login URL based on the test configuration."""
    return f"{TEST_CONFIG['BASE_URL']}{TEST_CONFIG['LOGIN_ENDPOINT']}"

@pytest.fixture
def login_payload() -> Dict[str, str]:
    """Return the login payload with test credentials."""
    return {
        'email': TEST_CONFIG['TEST_EMAIL'],
        'password': TEST_CONFIG['TEST_PASSWORD'],
    }

@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Get auth headers by performing a login and returning the token."""
    login_url = f"{TEST_CONFIG['BASE_URL']}{TEST_CONFIG['LOGIN_ENDPOINT']}"
    payload = {
        'email': TEST_CONFIG['TEST_EMAIL'],
        'password': TEST_CONFIG['TEST_PASSWORD'],
    }
    
    response = make_request('POST', login_url, json_data=payload)
    assert_status_code(response, 200)
    
    data = assert_json_response(response)
    token = data.get('access_token')
    
    assert token, "Failed to get access token from login response"
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

# Test cases
def test_login_success(login_url: str, login_payload: Dict[str, str]) -> None:
    """Test successful login with valid credentials."""
    # Make login request
    response = make_request('POST', login_url, json_data=login_payload)
    
    # Verify response status
    assert_status_code(response, 200)
    
    # Verify response time
    assert_response_time(response, TEST_CONFIG['MAX_RESPONSE_TIME'])
    
    # Verify response headers
    assert_header_present(response, 'Content-Type')
    
    # Parse and verify JSON response
    data = assert_json_response(response)
    
    # Validate response schema
    assert_json_schema(data, LOGIN_RESPONSE_SCHEMA)
    
    # Additional assertions
    assert data['user']['email'] == TEST_CONFIG['TEST_EMAIL'], (
        f"Expected email {TEST_CONFIG['TEST_EMAIL']}, got {data['user']['email']}"
    )
    
    logger.info("Login test successful")

def test_login_invalid_credentials(login_url: str) -> None:
    """Test login with invalid credentials."""
    payload = {
        'email': TEST_CONFIG['TEST_EMAIL'],
        'password': 'wrong_password',
    }
    
    # Make login request with invalid credentials
    response = make_request('POST', login_url, json_data=payload)
    
    # Verify response status (expecting unauthorized)
    assert_status_code(response, 401)
    
    # Verify response time
    assert_response_time(response, TEST_CONFIG['MAX_RESPONSE_TIME'])
    
    # Parse and verify JSON response
    data = assert_json_response(response)
    
    # Verify error message
    assert 'error' in data, "Expected 'error' field in response"
    assert 'message' in data, "Expected 'message' field in response"
    
    logger.info("Invalid credentials test successful")

def test_login_missing_fields(login_url: str) -> None:
    """Test login with missing required fields."""
    # Test with missing email
    payload_missing_email = {
        'password': TEST_CONFIG['TEST_PASSWORD'],
    }
    
    response = make_request('POST', login_url, json_data=payload_missing_email)
    assert_status_code(response, 400)
    
    # Test with missing password
    payload_missing_password = {
        'email': TEST_CONFIG['TEST_EMAIL'],
    }
    
    response = make_request('POST', login_url, json_data=payload_missing_password)
    assert_status_code(response, 400)
    
    # Test with empty payload
    response = make_request('POST', login_url, json_data={})
    assert_status_code(response, 400)
    
    logger.info("Missing fields test successful")

def test_login_rate_limiting(login_url: str, login_payload: Dict[str, str]) -> None:
    """Test rate limiting on login endpoint by making multiple rapid requests."""
    # Make multiple rapid requests (adjust number based on rate limit policy)
    num_requests = 10
    responses = []
    
    for i in range(num_requests):
        response = make_request('POST', login_url, json_data=login_payload)
        responses.append(response)
        
        # Log request number and status
        logger.info(f"Request {i+1}: Status {response.status_code}")
        
        # If we hit rate limit, stop and verify
        if response.status_code == 429:
            # Verify rate limit headers
            assert_header_present(response, 'Retry-After')
            logger.info(f"Rate limiting detected after {i+1} requests")
            break
    
    # Check if rate limiting is implemented
    # Note: This test might pass even if rate limiting is not implemented
    # depending on the server configuration
    rate_limited = any(r.status_code == 429 for r in responses)
    
    if rate_limited:
        logger.info("Rate limiting test successful - detected 429 response")
    else:
        logger.info("No rate limiting detected after multiple requests")

if __name__ == '__main__':
    # This allows the tests to be run directly from the command line
    # e.g. python test_api_login.py
    pytest.main(['-v', __file__]) 