from typing import Dict, Any
from pathlib import Path
import os

class TestConfig:
    """Enhanced test configuration for the 3&7 Training Platform API tests."""
    
    # Environment
    ENV = os.getenv("API_ENV", "development")
    BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # Credentials
    TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password123")
    
    # Paths
    TEST_LOGS_DIR = Path("./test-logs")
    REPORT_DIR = Path("./reports")
    SECURITY_SCAN_PATHS = ["routes/", "middleware/", "dependencies/"]
    
    # Test settings
    RATE_LIMIT = 120  # requests per minute
    TEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    MOCK_API = True  # Set to True to use mock API endpoints
    SKIP_SECURITY_SCAN = True  # Skip security scanning for now
    
    # Performance thresholds (in seconds)
    PERFORMANCE = {
        "development": {  # For mock API
            "max_response_time": 5.0,
            "fast": 1.0,
            "acceptable": 2.5,
            "slow": 4.0
        },
        "production": {   # For real API
            "max_response_time": 2.0,
            "fast": 0.2,
            "acceptable": 0.5,
            "slow": 1.0
        }
    }

    # Get the appropriate performance thresholds based on current environment
    @property
    def performance_thresholds(self):
        return self.PERFORMANCE.get(self.ENV, self.PERFORMANCE["development"])
    
    def __init__(self):
        # Create necessary directories
        self.TEST_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Test endpoints
ENDPOINTS = {
    "health": "/health",
    "auth": {
        "login": "/auth/login",
        "register": "/auth/register",
        "me": "/auth/me",
    },
    "email": {
        "send": "/email/send",
        "send_test": "/email/send-test",
    },
    "user": {
        "profile": "/users/me",
        "update": "/users/me",
    },
    "training": {
        "sessions": "/training-sessions",
        "session": "/training-sessions/{id}",
    },
    "reports": {
        "training": "/reports/training",
        "attendance": "/reports/attendance",
        "feedback": "/reports/feedback",
    },
}

# Expected response codes
RESPONSE_CODES = {
    "success": 200,
    "created": 201,
    "no_content": 204,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "rate_limit": 429,
    "server_error": 500,
}

# Security headers to check
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
}

# Create a global instance of the configuration
config = TestConfig() 