"""
Test Configuration

This module contains configuration settings for the API tests.
It supports loading configuration from environment variables and 
provides default values for development environments.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class Environment(str, Enum):
    """Supported testing environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class PerformanceThresholds:
    """Performance thresholds for different types of requests."""
    fast_endpoint_max_ms: int
    average_endpoint_max_ms: int
    slow_endpoint_max_ms: int
    
    @classmethod
    def for_environment(cls, env: Environment) -> 'PerformanceThresholds':
        """Return performance thresholds appropriate for the given environment."""
        if env == Environment.DEVELOPMENT:
            return cls(
                fast_endpoint_max_ms=200,
                average_endpoint_max_ms=500,
                slow_endpoint_max_ms=1000
            )
        elif env == Environment.STAGING:
            return cls(
                fast_endpoint_max_ms=150,
                average_endpoint_max_ms=300,
                slow_endpoint_max_ms=800
            )
        elif env == Environment.PRODUCTION:
            return cls(
                fast_endpoint_max_ms=100,
                average_endpoint_max_ms=250,
                slow_endpoint_max_ms=600
            )
        else:
            raise ValueError(f"Unsupported environment: {env}")


@dataclass
class TestConfig:
    """Configuration for API tests."""
    # Environment settings
    environment: Environment = field(
        default_factory=lambda: Environment(
            os.environ.get("TEST_ENVIRONMENT", Environment.DEVELOPMENT)
        )
    )
    
    # API Base URL
    base_url: str = field(
        default_factory=lambda: os.environ.get(
            "API_BASE_URL", "http://localhost:8000"
        )
    )
    
    # Authentication
    test_email: str = field(
        default_factory=lambda: os.environ.get(
            "TEST_EMAIL", "test@example.com"
        )
    )
    test_password: str = field(
        default_factory=lambda: os.environ.get(
            "TEST_PASSWORD", "password123"
        )
    )
    auth_endpoint: str = field(default="/api/auth/login")
    
    # Timeout settings
    request_timeout: int = field(
        default_factory=lambda: int(os.environ.get("REQUEST_TIMEOUT", "10"))
    )
    security_scan_timeout: int = field(
        default_factory=lambda: int(os.environ.get("SECURITY_SCAN_TIMEOUT", "120"))
    )
    
    # Performance thresholds
    performance_thresholds: PerformanceThresholds = field(default=None)
    
    # Security test settings
    required_security_headers: List[str] = field(default_factory=lambda: [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-XSS-Protection",
    ])
    
    # Paths for security scans
    security_scan_paths: List[str] = field(default_factory=lambda: [
        "tests",
        "utils",
    ])
    
    # Logging settings
    log_directory: str = field(
        default_factory=lambda: os.environ.get("TEST_LOGS_DIR", "test-logs")
    )
    verbose: bool = field(
        default_factory=lambda: os.environ.get("VERBOSE", "false").lower() == "true"
    )
    
    # Test categories
    skip_security_tests: bool = field(
        default_factory=lambda: os.environ.get("SKIP_SECURITY_TESTS", "false").lower() == "true"
    )
    skip_performance_tests: bool = field(
        default_factory=lambda: os.environ.get("SKIP_PERFORMANCE_TESTS", "false").lower() == "true"
    )
    skip_functional_tests: bool = field(
        default_factory=lambda: os.environ.get("SKIP_FUNCTIONAL_TESTS", "false").lower() == "true"
    )
    
    # Endpoints - organized by category
    endpoints: Dict[str, str] = field(default_factory=lambda: {
        # Auth endpoints
        "login": "/api/auth/login",
        "logout": "/api/auth/logout",
        "refresh": "/api/auth/refresh",
        
        # User endpoints
        "user_profile": "/api/users/profile",
        "user_update": "/api/users/update",
        
        # Content endpoints
        "content_list": "/api/content",
        "content_detail": "/api/content/{id}",
        
        # Search endpoints
        "search": "/api/search",
    })
    
    # Fast endpoints (expected to respond quickly)
    fast_endpoints: List[str] = field(default_factory=lambda: [
        "login",
        "logout",
        "refresh",
    ])
    
    # Slow endpoints (may take longer to respond)
    slow_endpoints: List[str] = field(default_factory=lambda: [
        "search",
        "content_list",
    ])
    
    def __post_init__(self):
        """Initialize the performance thresholds based on the environment."""
        if self.performance_thresholds is None:
            self.performance_thresholds = PerformanceThresholds.for_environment(
                self.environment
            )
    
    def get_endpoint_url(self, endpoint_name: str, **kwargs) -> str:
        """
        Get the full URL for an endpoint.
        
        Args:
            endpoint_name: The name of the endpoint as defined in the endpoints dict
            **kwargs: Any parameters to format into the endpoint URL
            
        Returns:
            The full URL for the endpoint
            
        Raises:
            KeyError: If the endpoint name is not found in the endpoints dict
        """
        if endpoint_name not in self.endpoints:
            raise KeyError(f"Unknown endpoint: {endpoint_name}")
        
        endpoint = self.endpoints[endpoint_name]
        
        # Format the endpoint if it contains parameters
        if kwargs:
            endpoint = endpoint.format(**kwargs)
            
        return f"{self.base_url}{endpoint}"
    
    def get_performance_threshold(self, endpoint_name: str) -> int:
        """
        Get the performance threshold for an endpoint in milliseconds.
        
        Args:
            endpoint_name: The name of the endpoint
            
        Returns:
            The threshold in milliseconds
        """
        if endpoint_name in self.fast_endpoints:
            return self.performance_thresholds.fast_endpoint_max_ms
        elif endpoint_name in self.slow_endpoints:
            return self.performance_thresholds.slow_endpoint_max_ms
        else:
            return self.performance_thresholds.average_endpoint_max_ms
    
    @property
    def auth_url(self) -> str:
        """Get the full URL for the authentication endpoint."""
        return f"{self.base_url}{self.auth_endpoint}"


# Create a default config instance for importing
config = TestConfig()


# Helper function to get a fresh config instance
def get_config() -> TestConfig:
    """Return a fresh instance of TestConfig with values from environment variables."""
    return TestConfig() 