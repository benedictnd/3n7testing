import functools
import json
import os
import time
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
FLAKY_TESTS_DB_PATH = Path("tests/data/flaky_tests.json")
FLAKY_TEST_THRESHOLD = 0.2  # 20% failure rate indicates flaky test

class FlakyTestException(Exception):
    """Exception raised when a test is identified as flaky."""
    pass

# Singleton instance of the FlakyTestManager
_manager_instance = None

def get_manager() -> 'FlakyTestManager':
    """
    Get the singleton instance of the FlakyTestManager.
    
    Returns:
        FlakyTestManager: The singleton instance of the FlakyTestManager.
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = FlakyTestManager()
    return _manager_instance

class FlakyTestManager:
    """
    Manages detection and handling of flaky tests in the test suite.
    
    A flaky test is one that exhibits inconsistent behavior, passing sometimes
    and failing other times with the same code and environment.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the flaky test manager with the database path."""
        self.db_path = db_path or FLAKY_TESTS_DB_PATH
        self.test_history = self._load_history()
        logger.info(f"Initialized FlakyTestManager with DB at {self.db_path}")
    
    def _load_history(self) -> Dict:
        """Load test history from the JSON database file."""
        if not self.db_path.exists():
            # Create directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            return {"tests": {}, "last_updated": datetime.now().isoformat()}
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading flaky test history: {str(e)}")
            return {"tests": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_history(self):
        """Save test history to the JSON database file."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update the last_updated timestamp
            self.test_history["last_updated"] = datetime.now().isoformat()
            
            # Write to file
            with open(self.db_path, 'w') as f:
                json.dump(self.test_history, f, indent=2)
            
            logger.debug(f"Successfully saved flaky test history to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving flaky test history: {str(e)}")
    
    def record_test_run(self, test_id: str, success: bool, duration: float, metadata: Dict = None):
        """
        Record the outcome of a test run.
        
        Args:
            test_id: Unique identifier for the test (typically module_name::class_name::method_name)
            success: Whether the test passed (True) or failed (False)
            duration: The duration of the test run in seconds
            metadata: Additional metadata about the test run (environment variables, etc.)
        """
        if metadata is None:
            metadata = {}
            
        # Initialize test entry if it doesn't exist
        if test_id not in self.test_history["tests"]:
            self.test_history["tests"][test_id] = {
                "runs": [],
                "pass_count": 0,
                "fail_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "is_flaky": False,
                "flaky_since": None
            }
        
        # Update test statistics
        test_entry = self.test_history["tests"][test_id]
        test_entry["last_seen"] = datetime.now().isoformat()
        
        if success:
            test_entry["pass_count"] += 1
        else:
            test_entry["fail_count"] += 1
        
        # Add the current run to the run history
        run_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "duration": duration,
            "metadata": metadata
        }
        
        # Limit the number of stored runs to avoid excessive growth
        max_runs = 100
        test_entry["runs"].append(run_entry)
        if len(test_entry["runs"]) > max_runs:
            test_entry["runs"] = test_entry["runs"][-max_runs:]
        
        # Determine if the test is flaky
        total_runs = test_entry["pass_count"] + test_entry["fail_count"]
        if total_runs >= 5:  # Need enough data to make a determination
            min_count = min(test_entry["pass_count"], test_entry["fail_count"])
            flakiness = min_count / total_runs
            
            # Update flaky status if it crosses the threshold
            if flakiness >= FLAKY_TEST_THRESHOLD and not test_entry["is_flaky"]:
                test_entry["is_flaky"] = True
                test_entry["flaky_since"] = datetime.now().isoformat()
                logger.warning(f"Test {test_id} identified as flaky (flakiness: {flakiness:.2f})")
            elif flakiness < FLAKY_TEST_THRESHOLD and test_entry["is_flaky"]:
                test_entry["is_flaky"] = False
                test_entry["flaky_since"] = None
                logger.info(f"Test {test_id} no longer considered flaky (flakiness: {flakiness:.2f})")
        
        # Save the updated history
        self._save_history()
        
        # Return the updated test entry
        return test_entry
    
    def is_test_flaky(self, test_id: str) -> bool:
        """Check if a test is considered flaky based on historical data."""
        if test_id not in self.test_history["tests"]:
            return False
            
        return self.test_history["tests"][test_id].get("is_flaky", False)
    
    def get_all_flaky_tests(self) -> List[str]:
        """Get a list of all tests currently marked as flaky."""
        return [
            test_id for test_id, test_data in self.test_history["tests"].items()
            if test_data.get("is_flaky", False)
        ]
    
    def get_test_status(self, test_id: str) -> Dict:
        """Get the status and history for a specific test."""
        if test_id not in self.test_history["tests"]:
            return {"error": "Test not found in database"}
            
        return self.test_history["tests"][test_id]
    
    def get_test_flakiness_score(self, test_id: str) -> float:
        """
        Calculate the flakiness score for a test.
        
        A score of 0 means the test always has the same result.
        A score of 0.5 is maximally flaky (50% pass, 50% fail).
        """
        if test_id not in self.test_history["tests"]:
            return 0.0
            
        test_data = self.test_history["tests"][test_id]
        total_runs = test_data["pass_count"] + test_data["fail_count"]
        
        if total_runs == 0:
            return 0.0
            
        pass_ratio = test_data["pass_count"] / total_runs
        
        # Calculate flakiness - 0.5 is maximally flaky (50/50), 0.0 is perfectly stable
        return 1 - abs(0.5 - pass_ratio) * 2
    
    def generate_report(self, output_path: Optional[Path] = None) -> Dict:
        """
        Generate a report of flaky tests.
        
        Args:
            output_path: Optional file path to write the report to
            
        Returns:
            A dictionary containing report data
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_tests": len(self.test_history["tests"]),
            "flaky_tests": self.get_all_flaky_tests(),
            "flaky_test_count": len(self.get_all_flaky_tests()),
            "test_details": {}
        }
        
        # Add details for each flaky test
        for test_id in report["flaky_tests"]:
            test_data = self.test_history["tests"][test_id]
            total_runs = test_data["pass_count"] + test_data["fail_count"]
            
            report["test_details"][test_id] = {
                "flakiness_score": self.get_test_flakiness_score(test_id),
                "pass_rate": test_data["pass_count"] / total_runs if total_runs > 0 else 0,
                "fail_rate": test_data["fail_count"] / total_runs if total_runs > 0 else 0,
                "total_runs": total_runs,
                "flaky_since": test_data["flaky_since"],
                "recent_runs": test_data["runs"][-5:] if test_data["runs"] else []
            }
        
        # Optionally write the report to a file
        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Flaky test report written to {output_path}")
            except Exception as e:
                logger.error(f"Error writing flaky test report: {str(e)}")
        
        return report

def retry_flaky_test(max_retries: int = MAX_RETRIES, delay_seconds: int = 1):
    """
    Decorator that retries a flaky test multiple times before failing.
    
    Args:
        max_retries: Maximum number of times to retry the test
        delay_seconds: Delay between retries in seconds
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Determine test_id from the function
            module_name = func.__module__
            func_name = func.__name__
            
            # Try to get the class name if it's a method
            if args and hasattr(args[0], "__class__"):
                class_name = args[0].__class__.__name__
                test_id = f"{module_name}::{class_name}::{func_name}"
            else:
                test_id = f"{module_name}::{func_name}"
            
            manager = get_manager()
            is_flaky = manager.is_test_flaky(test_id)
            
            metadata = {
                "retried": False,
                "retry_count": 0,
                "environment": os.environ.get("TEST_ENV", "unknown")
            }
            
            start_time = time.time()
            
            # First try
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                manager.record_test_run(test_id, True, duration, metadata)
                return result
            except Exception as e:
                duration = time.time() - start_time
                manager.record_test_run(test_id, False, duration, metadata)
                
                # If the test is known to be flaky, retry it
                if is_flaky or max_retries > 0:
                    last_exception = e
                    
                    for retry in range(max_retries):
                        logger.info(f"Retrying flaky test {test_id} (attempt {retry + 1}/{max_retries})")
                        
                        # Add jitter to avoid timing issues
                        jitter = random.uniform(0, 0.5)
                        time.sleep(delay_seconds + jitter)
                        
                        metadata["retried"] = True
                        metadata["retry_count"] = retry + 1
                        
                        start_time = time.time()
                        
                        try:
                            result = func(*args, **kwargs)
                            duration = time.time() - start_time
                            manager.record_test_run(test_id, True, duration, metadata)
                            logger.info(f"Flaky test {test_id} passed on retry {retry + 1}")
                            return result
                        except Exception as e:
                            duration = time.time() - start_time
                            manager.record_test_run(test_id, False, duration, metadata)
                            last_exception = e
                    
                    # If we get here, all retries failed
                    logger.error(f"Flaky test {test_id} failed after {max_retries} retries")
                    
                    # Wrap the last exception to indicate it's a flaky test
                    if is_flaky:
                        raise FlakyTestException(f"Known flaky test failed: {str(last_exception)}") from last_exception
                    else:
                        raise last_exception
                else:
                    # Not considered flaky, so just re-raise the exception
                    raise
        
        return wrapper
    return decorator

def track_flaky_test(func):
    """
    Decorator that tracks test results for flaky test detection,
    without actually retrying the test.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine test_id from the function
        module_name = func.__module__
        func_name = func.__name__
        
        # Try to get the class name if it's a method
        if args and hasattr(args[0], "__class__"):
            class_name = args[0].__class__.__name__
            test_id = f"{module_name}::{class_name}::{func_name}"
        else:
            test_id = f"{module_name}::{func_name}"
        
        manager = get_manager()
        
        metadata = {
            "tracked": True,
            "environment": os.environ.get("TEST_ENV", "unknown")
        }
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            manager.record_test_run(test_id, True, duration, metadata)
            return result
        except Exception as e:
            duration = time.time() - start_time
            manager.record_test_run(test_id, False, duration, metadata)
            raise
    
    return wrapper 