import pytest
import os
import logging
from pathlib import Path
from test_config import config

# Configure logging for pytest
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test-logs/pytest-run.log")
    ]
)
logger = logging.getLogger(__name__)

def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--url",
        action="store",
        default=config.BASE_URL,
        help="Base URL for API tests (default: %(default)s)"
    )
    parser.addoption(
        "--email",
        action="store",
        default=config.TEST_EMAIL,
        help="Email for authentication (default: %(default)s)"
    )
    parser.addoption(
        "--password",
        action="store",
        default=config.TEST_PASSWORD,
        help="Password for authentication (default: %(default)s)"
    )
    parser.addoption(
        "--env",
        action="store",
        default=config.ENV,
        choices=["development", "staging", "production"],
        help="Environment to run tests against (default: %(default)s)"
    )
    parser.addoption(
        "--skip-security",
        action="store_true",
        default=False,
        help="Skip security tests"
    )
    parser.addoption(
        "--skip-performance",
        action="store_true",
        default=False,
        help="Skip performance tests"
    )
    parser.addoption(
        "--skip-integration",
        action="store_true",
        default=False,
        help="Skip integration tests"
    )

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(request):
    """Setup the test environment at the beginning of the test session."""
    # Create log directory if it doesn't exist
    log_dir = Path("test-logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get configuration from command line or use defaults
    base_url = request.config.getoption("--url")
    email = request.config.getoption("--email")
    password = request.config.getoption("--password")
    env = request.config.getoption("--env")
    
    # Update config with command line values
    config.BASE_URL = base_url
    config.TEST_EMAIL = email
    config.TEST_PASSWORD = password
    config.ENV = env
    
    # Log test configuration
    logger.info(f"Starting test session with configuration:")
    logger.info(f"  Base URL: {config.BASE_URL}")
    logger.info(f"  Environment: {config.ENV}")
    logger.info(f"  Test Email: {config.TEST_EMAIL}")
    
    # Return configuration for tests to use
    return {
        "base_url": config.BASE_URL,
        "email": config.TEST_EMAIL,
        "password": config.TEST_PASSWORD,
        "env": config.ENV
    }

@pytest.fixture(scope="class")
def authenticated_session(request, setup_test_environment):
    """Fixture to provide an authenticated session for test classes."""
    import requests
    
    # Get configuration
    base_url = setup_test_environment["base_url"]
    email = setup_test_environment["email"]
    password = setup_test_environment["password"]
    
    logger.info(f"Authenticating session with {email} against {base_url}")
    
    # Try to authenticate
    try:
        auth_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(f"{base_url}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            
            logger.info(f"Authentication successful for {email}")
            
            # Create session with auth headers
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {token}"
            })
            
            # Add user info to session for tests to use
            session.user = user
            return session
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            # Return unauthenticated session
            return requests.Session()
            
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return requests.Session()

@pytest.fixture(scope="function")
def logger_fixture(request):
    """Fixture to provide a logger for test functions."""
    return logger

@pytest.fixture(scope="session")
def performance_history():
    """Fixture to manage performance history data."""
    history_file = config.REPORT_DIR / "performance_history.json"
    
    # Create history object
    history = {
        "endpoints": {},
        "last_updated": None
    }
    
    # Yield history for use in tests
    yield history
    
    # Save history at the end
    import json
    from datetime import datetime
    
    history["last_updated"] = datetime.now().isoformat()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
        
    logger.info(f"Performance history saved to {history_file}")

def pytest_collection_modifyitems(config, items):
    """Modify test items based on command line options."""
    skip_security = pytest.mark.skip(reason="Security tests skipped via --skip-security")
    skip_performance = pytest.mark.skip(reason="Performance tests skipped via --skip-performance")
    skip_integration = pytest.mark.skip(reason="Integration tests skipped via --skip-integration")
    
    for item in items:
        if config.getoption("--skip-security") and "security" in item.keywords:
            item.add_marker(skip_security)
        if config.getoption("--skip-performance") and "performance" in item.keywords:
            item.add_marker(skip_performance)
        if config.getoption("--skip-integration") and "integration" in item.keywords:
            item.add_marker(skip_integration)

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "security: mark a test as a security test")
    config.addinivalue_line("markers", "performance: mark a test as a performance test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "rate_limit: mark a test as a rate limiting test")
    config.addinivalue_line("markers", "auth: mark a test as an authentication test") 