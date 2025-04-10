#!/usr/bin/env python
import argparse
import logging
import os
import requests
import time
import json
import sys
import traceback
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path

# Import test configuration
from test_config import TEST_CONFIG, ENDPOINTS, PERFORMANCE_THRESHOLDS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test-logs/api_debug.log', mode='w')
    ]
)
logger = logging.getLogger('api_debug')

class APITestDebugger:
    """Tool for debugging and diagnosing API test performance issues"""
    
    def __init__(self, base_url: str, email: str, password: str, verbose: bool = False):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.verbose = verbose
        self.auth_token = None
        self.session = requests.Session()
        self.results = {}
        self.endpoint_timing = {}
        
        # Ensure the test-logs directory exists
        Path("./test-logs").mkdir(exist_ok=True)
        
        logger.info(f"API Test Debugger initialized with base URL: {base_url}")
        
    def timeout_decorator(self, timeout_seconds: int):
        """Decorator to add timeout to a function"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import threading
                result = {"value": None, "exception": None, "timed_out": False}
                
                def target():
                    try:
                        result["value"] = func(*args, **kwargs)
                    except Exception as e:
                        result["exception"] = e
                        logger.error(f"Exception in {func.__name__}: {str(e)}")
                        logger.error(traceback.format_exc())
                
                thread = threading.Thread(target=target)
                thread.daemon = True
                
                logger.debug(f"Starting {func.__name__} with {timeout_seconds}s timeout")
                start_time = time.time()
                thread.start()
                thread.join(timeout_seconds)
                elapsed = time.time() - start_time
                
                if thread.is_alive():
                    result["timed_out"] = True
                    logger.error(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                    # We don't kill the thread as it's daemon and will be terminated when the main thread exits
                
                logger.debug(f"Function {func.__name__} completed in {elapsed:.2f}s (timeout: {result['timed_out']})")
                
                if result["exception"]:
                    raise result["exception"]
                    
                if result["timed_out"]:
                    raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                    
                return result["value"]
            return wrapper
        return decorator
        
    def login(self) -> bool:
        """Attempt to login and get auth token"""
        try:
            logger.info("Attempting to login...")
            start_time = time.time()
            
            login_data = {
                "email": self.email,
                "password": self.password
            }
            
            response = self.session.post(
                f"{self.base_url}{ENDPOINTS['auth']['login']}", 
                json=login_data,
                timeout=10
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Login request completed in {elapsed:.2f}s with status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    self.auth_token = response.json().get("token")
                    if self.auth_token:
                        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                        logger.info("Login successful, token obtained")
                        return True
                    else:
                        logger.error("Token not found in response")
                except json.JSONDecodeError:
                    logger.error("Failed to parse login response as JSON")
            else:
                logger.error(f"Login failed with status code {response.status_code}")
                
            logger.debug(f"Response content: {response.text[:200]}...")
            return False
            
        except Exception as e:
            logger.error(f"Exception during login: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def test_endpoint(self, name: str, endpoint: str, method: str = "GET", data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and return timing information"""
        url = f"{self.base_url}{endpoint}"
        result = {
            "endpoint": endpoint,
            "method": method,
            "name": name,
            "url": url,
            "status_code": None,
            "success": False,
            "response_time": None,
            "error": None,
            "response_size": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            logger.info(f"Testing endpoint: {name} ({method} {endpoint})")
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            elapsed = time.time() - start_time
            
            result["status_code"] = response.status_code
            result["response_time"] = elapsed
            result["response_size"] = len(response.content)
            result["success"] = (response.status_code == expected_status)
            
            performance_rating = "fast"
            if elapsed > PERFORMANCE_THRESHOLDS["acceptable"]:
                performance_rating = "acceptable"
            if elapsed > PERFORMANCE_THRESHOLDS["slow"]:
                performance_rating = "slow"
            if elapsed > PERFORMANCE_THRESHOLDS["max_response_time"]:
                performance_rating = "too_slow"
                
            result["performance_rating"] = performance_rating
            
            logger.info(f"Endpoint {name} responded in {elapsed:.4f}s with status {response.status_code} [{performance_rating}]")
            
            if self.verbose and response.status_code == expected_status:
                try:
                    logger.debug(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
                except (json.JSONDecodeError, AttributeError):
                    logger.debug(f"Raw response: {response.text[:200]}...")
                    
            if response.status_code != expected_status:
                result["error"] = f"Expected status {expected_status}, got {response.status_code}"
                logger.error(result["error"])
                try:
                    logger.error(f"Error response: {response.text[:500]}")
                except:
                    pass
                    
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            result["error"] = f"Request timed out after {elapsed:.2f}s"
            result["response_time"] = elapsed
            logger.error(result["error"])
            
        except Exception as e:
            elapsed = time.time() - start_time if 'start_time' in locals() else None
            result["error"] = str(e)
            result["response_time"] = elapsed
            logger.error(f"Exception testing {name}: {str(e)}")
            logger.error(traceback.format_exc())
            
        self.endpoint_timing[name] = result
        return result
        
    def run_health_check(self) -> Dict[str, Any]:
        """Run a quick health check against the API"""
        return self.test_endpoint("health_check", ENDPOINTS["health"])
        
    def check_connection(self) -> bool:
        """Verify basic connectivity to API server"""
        try:
            logger.info("Checking basic API connectivity...")
            start = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            elapsed = time.time() - start
            
            logger.info(f"Health check completed in {elapsed:.4f}s with status {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False
            
    def run_endpoint_benchmark(self, count: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Run benchmark tests on key endpoints"""
        logger.info(f"Running endpoint benchmark with {count} iterations per endpoint")
        
        benchmark_results = {}
        endpoints_to_test = [
            ("health", ENDPOINTS["health"], "GET", None, 200),
            ("user_profile", ENDPOINTS["user"]["profile"], "GET", None, 200),
            ("training_sessions", ENDPOINTS["training"]["sessions"], "GET", None, 200)
        ]
        
        for name, endpoint, method, data, expected_status in endpoints_to_test:
            benchmark_results[name] = []
            
            for i in range(count):
                logger.info(f"Benchmark iteration {i+1}/{count} for {name}")
                result = self.test_endpoint(f"{name}_{i+1}", endpoint, method, data, expected_status)
                benchmark_results[name].append(result)
                time.sleep(0.5)  # Small delay between iterations
                
        self.analyze_benchmark_results(benchmark_results)
        return benchmark_results
    
    def analyze_benchmark_results(self, results: Dict[str, List[Dict[str, Any]]]) -> None:
        """Analyze benchmark results and identify potential issues"""
        analysis = {
            "summary": {},
            "problematic_endpoints": [],
            "recommendations": []
        }
        
        for endpoint, iterations in results.items():
            times = [r["response_time"] for r in iterations if r["response_time"] is not None]
            if not times:
                continue
                
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            variance = sum((t - avg_time) ** 2 for t in times) / len(times)
            
            analysis["summary"][endpoint] = {
                "average": avg_time,
                "min": min_time,
                "max": max_time,
                "variance": variance,
                "iterations": len(times)
            }
            
            # Check if endpoint is problematic
            if avg_time > PERFORMANCE_THRESHOLDS["slow"]:
                analysis["problematic_endpoints"].append({
                    "endpoint": endpoint,
                    "avg_time": avg_time,
                    "threshold": PERFORMANCE_THRESHOLDS["slow"]
                })
                
            if variance > 0.1 and max_time > 2 * min_time:
                analysis["recommendations"].append(
                    f"High variance in {endpoint} response times ({min_time:.2f}s to {max_time:.2f}s). Check for inconsistent processing."
                )
                
        # Generate overall recommendations
        if analysis["problematic_endpoints"]:
            analysis["recommendations"].append(
                f"Found {len(analysis['problematic_endpoints'])} slow endpoints. Consider optimizing server-side processing."
            )
            
        if any(s["variance"] > 0.25 for s in analysis["summary"].values()):
            analysis["recommendations"].append(
                "Response times show high variance. Check for resource contention or caching issues."
            )
            
        # Log the analysis
        logger.info("Benchmark Analysis:")
        for endpoint, stats in analysis["summary"].items():
            logger.info(f"{endpoint}: avg={stats['average']:.4f}s, min={stats['min']:.4f}s, max={stats['max']:.4f}s")
            
        for rec in analysis["recommendations"]:
            logger.info(f"Recommendation: {rec}")
            
        # Save analysis to file
        with open("test-logs/benchmark_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)
            
        logger.info("Benchmark analysis saved to test-logs/benchmark_analysis.json")
        
    def trace_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Perform detailed tracing of a single request"""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Tracing request: {method} {url}")
        
        trace_data = {
            "url": url,
            "method": method,
            "request_headers": {},
            "request_start": time.time(),
            "dns_lookup": None,
            "connection_time": None,
            "tls_handshake": None,
            "first_byte": None,
            "download_time": None,
            "total_time": None,
            "response_headers": {},
            "response_size": None,
            "status_code": None
        }
        
        try:
            # Use requests directly with timing hooks
            session = requests.Session()
            if self.auth_token:
                session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
            # Record request headers
            request_start = time.time()
            trace_data["request_start"] = request_start
            
            # Make the request
            if method.upper() == "GET":
                response = session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = session.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            request_end = time.time()
            
            # Record timing data
            trace_data["total_time"] = request_end - request_start
            trace_data["response_headers"] = dict(response.headers)
            trace_data["response_size"] = len(response.content)
            trace_data["status_code"] = response.status_code
            
            logger.info(f"Trace completed in {trace_data['total_time']:.4f}s with status {response.status_code}")
            
            if self.verbose:
                logger.debug(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
                try:
                    logger.debug(f"Response body: {json.dumps(response.json(), indent=2)[:500]}...")
                except (json.JSONDecodeError, AttributeError):
                    logger.debug(f"Raw response: {response.text[:500]}...")
                    
            # Save trace data
            with open(f"test-logs/trace_{int(time.time())}.json", "w") as f:
                json.dump(trace_data, f, indent=2)
                
            return trace_data
            
        except Exception as e:
            trace_data["error"] = str(e)
            logger.error(f"Trace failed: {str(e)}")
            logger.error(traceback.format_exc())
            return trace_data
            
    def run_isolated_test(self, name: str, endpoint: str, method: str = "GET", data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Run a test in isolation with no other activity"""
        logger.info(f"Running isolated test for {name} ({method} {endpoint})")
        
        # Clear session to start fresh
        self.session = requests.Session()
        if self.auth_token:
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            
        # Run the test with detailed monitoring
        result = self.test_endpoint(name, endpoint, method, data, expected_status)
        
        # If the test is slow, trace it
        if result["response_time"] and result["response_time"] > PERFORMANCE_THRESHOLDS["slow"]:
            logger.info(f"Test {name} was slow ({result['response_time']:.4f}s), running trace...")
            trace_data = self.trace_request(endpoint, method, data)
            result["trace_data"] = trace_data
            
        return result
        
    def export_results(self) -> None:
        """Export all test results and diagnostics"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "endpoint_timing": self.endpoint_timing,
            "performance_thresholds": PERFORMANCE_THRESHOLDS,
            "diagnostics": self.results
        }
        
        output_file = f"test-logs/debug_results_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
            
        logger.info(f"Debug results exported to {output_file}")
        
    @timeout_decorator(60)
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run full diagnostic suite"""
        self.results["start_time"] = datetime.now().isoformat()
        logger.info(f"Starting API diagnostics at {self.results['start_time']}")
        
        # 1. Basic connection check
        self.results["connection_check"] = self.check_connection()
        if not self.results["connection_check"]:
            logger.error("Basic connection check failed, aborting diagnostics")
            self.export_results()
            return self.results
            
        # 2. Login test 
        login_success = self.login()
        self.results["login_success"] = login_success
        if not login_success:
            logger.error("Login failed, proceeding with limited diagnostics")
            # Continue with tests that don't require auth
            
        # 3. Health check
        self.results["health_check"] = self.run_health_check()
        
        # 4. Run benchmark on key endpoints
        self.results["benchmark"] = self.run_endpoint_benchmark(count=3)
        
        # 5. Run isolated tests on problematic endpoints
        slow_endpoints = []
        for name, result in self.endpoint_timing.items():
            if result.get("performance_rating") in ["slow", "too_slow"]:
                slow_endpoints.append((name, result))
                
        if slow_endpoints:
            logger.info(f"Found {len(slow_endpoints)} slow endpoints, running isolated tests")
            self.results["isolated_tests"] = {}
            
            for name, result in slow_endpoints:
                isolated_result = self.run_isolated_test(
                    f"{name}_isolated", 
                    result["endpoint"], 
                    result["method"]
                )
                self.results["isolated_tests"][name] = isolated_result
                
        # 6. Export all results
        self.results["end_time"] = datetime.now().isoformat()
        self.export_results()
        
        logger.info(f"Diagnostics completed in {(datetime.now() - datetime.fromisoformat(self.results['start_time'])).total_seconds():.2f}s")
        return self.results


def main():
    parser = argparse.ArgumentParser(description="API Test Debugger")
    parser.add_argument("--url", type=str, default=TEST_CONFIG["API_BASE_URL"],
                        help=f"API base URL (default: {TEST_CONFIG['API_BASE_URL']})")
    parser.add_argument("--email", type=str, default=TEST_CONFIG["TEST_EMAIL"],
                        help=f"Test email (default: {TEST_CONFIG['TEST_EMAIL']})")
    parser.add_argument("--password", type=str, default=TEST_CONFIG["TEST_PASSWORD"],
                        help=f"Test password (default: {TEST_CONFIG['TEST_PASSWORD']})")
    parser.add_argument("--verbose", action="store_true", 
                        help="Enable verbose output")
    parser.add_argument("--benchmark", action="store_true",
                        help="Run benchmark tests only")
    parser.add_argument("--trace", type=str,
                        help="Trace a specific endpoint (e.g. /health)")
    
    args = parser.parse_args()
    
    debugger = APITestDebugger(
        base_url=args.url,
        email=args.email,
        password=args.password,
        verbose=args.verbose
    )
    
    try:
        # Basic connection check first
        if not debugger.check_connection():
            logger.error("Connection check failed. Please ensure the API server is running.")
            return 1
            
        if args.trace:
            # Run trace on specific endpoint
            endpoint = args.trace
            if not endpoint.startswith('/'):
                endpoint = '/' + endpoint
            logger.info(f"Running trace on endpoint: {endpoint}")
            trace_data = debugger.trace_request(endpoint)
            print(f"Trace completed in {trace_data.get('total_time', 'unknown')}s")
            return 0
            
        if args.benchmark:
            # Run benchmark only
            debugger.login()
            benchmark_results = debugger.run_endpoint_benchmark(count=5)
            debugger.export_results()
            return 0
            
        # Run full diagnostics
        results = debugger.run_diagnostics()
        
        # Summary
        print("\nAPI Test Diagnostic Summary:")
        print(f"Base URL: {args.url}")
        print(f"Connection Check: {'Passed' if results.get('connection_check') else 'Failed'}")
        print(f"Login Test: {'Passed' if results.get('login_success') else 'Failed'}")
        
        health_result = results.get('health_check', {})
        health_status = "Passed" if health_result.get('success') else "Failed"
        health_time = health_result.get('response_time', 'unknown')
        print(f"Health Check: {health_status} ({health_time}s)")
        
        # Performance summary
        benchmark = results.get('benchmark', {})
        if benchmark:
            print("\nEndpoint Performance:")
            for endpoint, tests in benchmark.items():
                times = [t.get('response_time', 0) for t in tests if t.get('response_time')]
                if times:
                    avg_time = sum(times) / len(times)
                    print(f"  {endpoint}: {avg_time:.4f}s average ({len(times)} tests)")
                    
        return 0
        
    except Exception as e:
        logger.error(f"Diagnostics failed: {str(e)}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main()) 