import pytest
import requests
import time
import json
import logging
import statistics
from datetime import datetime
from pathlib import Path
from test_config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Performance history file for tracking trends
PERF_HISTORY_FILE = config.REPORT_DIR / "performance_history.json"

@pytest.mark.performance
class TestAPIPerformance:
    """Test suite for measuring API performance and response times."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.base_url = config.BASE_URL
        self.token = None
        self.thresholds = config.performance_thresholds
        
        logger.info(f"Setting up performance tests with base URL: {self.base_url}")
        logger.info(f"Using thresholds: {self.thresholds}")
        
        # Authenticate to get token for protected endpoints
        self._authenticate()
        
        # Load performance history if available
        self.history = self._load_performance_history()
    
    def _authenticate(self):
        """Authenticate with the API to get an access token."""
        try:
            auth_data = {
                "email": config.TEST_EMAIL,
                "password": config.TEST_PASSWORD
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                logger.info("Authentication successful")
            else:
                logger.warning(f"Authentication failed: {response.status_code}")
                self.headers = {}
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.headers = {}
    
    def _load_performance_history(self):
        """Load previous performance history for trend analysis."""
        try:
            if PERF_HISTORY_FILE.exists():
                with open(PERF_HISTORY_FILE, "r") as f:
                    return json.load(f)
            
            # Initialize empty history if file doesn't exist
            return {"endpoints": {}}
            
        except Exception as e:
            logger.error(f"Error loading performance history: {str(e)}")
            return {"endpoints": {}}
    
    def _save_performance_history(self):
        """Save current performance data to history file."""
        try:
            # Make sure directory exists
            PERF_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Save history with updated timestamp
            self.history["last_updated"] = datetime.now().isoformat()
            
            with open(PERF_HISTORY_FILE, "w") as f:
                json.dump(self.history, f, indent=2)
                
            logger.info(f"Performance history saved to {PERF_HISTORY_FILE}")
            
        except Exception as e:
            logger.error(f"Error saving performance history: {str(e)}")
    
    def _update_history(self, endpoint, method, response_time):
        """Update performance history for an endpoint."""
        endpoint_key = f"{method}:{endpoint}"
        
        if endpoint_key not in self.history["endpoints"]:
            self.history["endpoints"][endpoint_key] = {
                "times": [],
                "baseline": None,
                "last_updated": None
            }
        
        # Add current measurement
        self.history["endpoints"][endpoint_key]["times"].append(response_time)
        
        # Keep only the latest 100 measurements
        if len(self.history["endpoints"][endpoint_key]["times"]) > 100:
            self.history["endpoints"][endpoint_key]["times"] = self.history["endpoints"][endpoint_key]["times"][-100:]
        
        # Update baseline (average of all measurements)
        self.history["endpoints"][endpoint_key]["baseline"] = statistics.mean(self.history["endpoints"][endpoint_key]["times"])
        self.history["endpoints"][endpoint_key]["last_updated"] = datetime.now().isoformat()
    
    @pytest.mark.parametrize("endpoint", [
        "/health",
        "/auth/login",
        "/users/me",
        "/training-sessions"
    ])
    def test_response_times(self, endpoint):
        """Test that API endpoint responses are within acceptable time limits."""
        method = "POST" if endpoint == "/auth/login" else "GET"
        
        logger.info(f"Testing response time for {method} {endpoint}")
        
        # Prepare request parameters
        kwargs = {}
        if self.token and endpoint != "/auth/login" and endpoint != "/health":
            kwargs["headers"] = self.headers
        
        if endpoint == "/auth/login":
            kwargs["json"] = {
                "email": config.TEST_EMAIL,
                "password": config.TEST_PASSWORD
            }
        
        # Measure response time
        start_time = time.perf_counter()
        
        if method == "GET":
            response = requests.get(f"{self.base_url}{endpoint}", **kwargs)
        else:
            response = requests.post(f"{self.base_url}{endpoint}", **kwargs)
            
        elapsed_time = time.perf_counter() - start_time
        
        # Update performance history
        self._update_history(endpoint, method, elapsed_time)
        
        # Check if status code indicates success
        assert response.status_code in [200, 201, 204], \
            f"Request to {endpoint} failed with status code {response.status_code}"
        
        # Verify response time is within thresholds
        logger.info(f"Response time for {endpoint}: {elapsed_time:.4f}s")
        
        assert elapsed_time < self.thresholds["max_response_time"], \
            f"Response time {elapsed_time:.4f}s exceeds maximum threshold of {self.thresholds['max_response_time']}s"
        
        # Categorize the response time
        if elapsed_time <= self.thresholds["fast"]:
            logger.info(f"Response time for {endpoint} is FAST")
        elif elapsed_time <= self.thresholds["acceptable"]:
            logger.info(f"Response time for {endpoint} is ACCEPTABLE")
        elif elapsed_time <= self.thresholds["slow"]:
            logger.warning(f"Response time for {endpoint} is SLOW")
        else:
            logger.error(f"Response time for {endpoint} is VERY SLOW")
    
    def test_multiple_requests_stability(self):
        """Test that the API maintains consistent response times over multiple requests."""
        endpoint = "/health" # Use non-authenticated endpoint for simplicity
        iterations = 10
        
        logger.info(f"Testing response time stability over {iterations} requests to {endpoint}")
        
        response_times = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            response = requests.get(f"{self.base_url}{endpoint}")
            elapsed_time = time.perf_counter() - start_time
            
            assert response.status_code == 200, \
                f"Request {i+1}/{iterations} failed with status code {response.status_code}"
                
            response_times.append(elapsed_time)
            logger.info(f"Request {i+1}/{iterations}: {elapsed_time:.4f}s")
            
            # Small delay to avoid hitting rate limits
            time.sleep(0.1)
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        stdev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        logger.info(f"Average response time: {avg_time:.4f}s")
        logger.info(f"Median response time: {median_time:.4f}s")
        logger.info(f"Standard deviation: {stdev:.4f}s")
        
        # Verify consistency - standard deviation should be relatively small
        assert stdev < (avg_time * 0.5), \
            f"Response times have high variability. StdDev: {stdev:.4f}s, Mean: {avg_time:.4f}s"
    
    def teardown_method(self):
        """Teardown method run after each test."""
        # Save updated performance history
        self._save_performance_history()

if __name__ == "__main__":
    # This allows the tests to be run directly with pytest
    pytest.main(["-v", __file__]) 