#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from test_config import TEST_CONFIG, ENDPOINTS, RESPONSE_CODES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test-run.log")
    ]
)
logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self, base_url: str, email: str, password: str, verbose: bool = False):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.verbose = verbose
        self.test_results: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        # Ensure test logs directory exists
        TEST_CONFIG["TEST_LOGS_DIR"].mkdir(parents=True, exist_ok=True)
        
        # Set environment variables for tests
        os.environ["API_BASE_URL"] = base_url
        os.environ["TEST_EMAIL"] = email
        os.environ["TEST_PASSWORD"] = password

    def run_security_scan(self) -> bool:
        """Run security scan using bandit"""
        try:
            logger.info("Running security scan...")
            result = subprocess.run(
                ["bandit", "-r"] + TEST_CONFIG["SECURITY_SCAN_PATHS"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("Security scan failed:")
                logger.error(result.stderr)
                return False
                
            logger.info("Security scan completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error running security scan: {str(e)}")
            return False

    def run_tests(self) -> bool:
        """Run the API tests"""
        try:
            # Run security scan first (if not skipped)
            if not TEST_CONFIG.get("SKIP_SECURITY_SCAN", False):
                if not self.run_security_scan():
                    logger.error("Security scan failed, aborting tests")
                    return False
            else:
                logger.info("Security scan skipped as per configuration")

            # Run the main test script
            logger.info("Running API tests...")
            python_path = os.getenv("PYTHON_PATH", "python")
            cmd = [python_path, "api_test.py", 
                   "--url", self.base_url,
                   "--email", self.email,
                   "--password", self.password]
            if self.verbose:
                cmd.append("--verbose")
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error("Tests failed:")
                logger.error(result.stderr)
                return False
                
            logger.info("Tests completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            return False

    def generate_report(self) -> None:
        """Generate a test report"""
        report_file = TEST_CONFIG["TEST_LOGS_DIR"] / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["duration"] = (
            datetime.fromisoformat(self.test_results["end_time"]) - 
            datetime.fromisoformat(self.test_results["start_time"])
        ).total_seconds()
        
        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
            
        logger.info(f"Test report generated: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Run API tests for the 3&7 Training Platform")
    parser.add_argument("--url", default=TEST_CONFIG["API_BASE_URL"], help="API Base URL")
    parser.add_argument("--email", default=TEST_CONFIG["TEST_EMAIL"], help="Test email")
    parser.add_argument("--password", default=TEST_CONFIG["TEST_PASSWORD"], help="Test password")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    runner = TestRunner(args.url, args.email, args.password, args.verbose)
    
    if runner.run_tests():
        runner.generate_report()
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 