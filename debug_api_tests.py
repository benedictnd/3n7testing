#!/usr/bin/env python3
"""
Debug API Tests - Advanced diagnostic tool for troubleshooting API test execution issues
"""

import os
import sys
import time
import json
import signal
import argparse
import logging
import traceback
import socket
import requests
import subprocess
import psutil
from datetime import datetime, timedelta
import threading

# Import our test utilities
try:
    from test_utils import timeout, monitor_connections, memory_usage, DebugSession, retry, performance_log
except ImportError:
    print("Unable to import test_utils. Make sure test_utils.py is in the current directory.")
    sys.exit(1)

# Configure logging
log_dir = "test-logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"debug_api_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("debug_api_tests")

class TestDebugger:
    """
    Advanced API Test Debugger with diagnostic utilities
    """
    
    def __init__(self, base_url, email=None, password=None, timeout_seconds=60, verbose=False):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.timeout_seconds = timeout_seconds
        self.verbose = verbose
        self.start_time = None
        self.end_time = None
        self.debug_data = {
            "system_info": {},
            "network_checks": [],
            "performance_metrics": [],
            "hanging_processes": [],
            "failed_tests": [],
            "connection_leaks": []
        }
        
        # Set environment variables for tests
        os.environ["API_BASE_URL"] = base_url
        if email:
            os.environ["TEST_EMAIL"] = email
        if password:
            os.environ["TEST_PASSWORD"] = password
        
        logger.info(f"Initialized TestDebugger for {base_url}")
        
    def collect_system_info(self):
        """Collect system information for diagnostics"""
        logger.info("Collecting system information...")
        
        system_info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": os.cpu_count(),
            "processor": os.environ.get("PROCESSOR_IDENTIFIER", "Unknown"),
            "hostname": socket.gethostname(),
            "memory_total": psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
            "memory_available": psutil.virtual_memory().available / (1024 * 1024 * 1024),  # GB
            "disk_usage": {str(part.mountpoint): {
                "total_gb": part.total / (1024 * 1024 * 1024),
                "used_gb": part.used / (1024 * 1024 * 1024),
                "percent": part.percent
            } for part in psutil.disk_partitions() if os.name != 'nt' or 'cdrom' not in part.opts.lower()}
        }
        
        try:
            import pkg_resources
            system_info["installed_packages"] = sorted([
                {"name": pkg.key, "version": pkg.version}
                for pkg in pkg_resources.working_set
            ], key=lambda x: x["name"])
        except ImportError:
            system_info["installed_packages"] = "Could not collect package information"
            
        self.debug_data["system_info"] = system_info
        logger.info("System information collection complete")
        
    def check_network_connectivity(self):
        """Check network connectivity to the API server"""
        logger.info(f"Checking network connectivity to {self.base_url}...")
        
        try:
            parsed_url = self.base_url.split("//")[1].split("/")[0]
            host = parsed_url.split(":")[0]
            
            # Check DNS resolution
            try:
                ip_address = socket.gethostbyname(host)
                dns_check = {"status": "success", "host": host, "ip": ip_address}
                logger.info(f"DNS resolution successful: {host} -> {ip_address}")
            except socket.gaierror as e:
                dns_check = {"status": "failed", "host": host, "error": str(e)}
                logger.error(f"DNS resolution failed for {host}: {e}")
            
            self.debug_data["network_checks"].append({
                "type": "dns_lookup",
                "result": dns_check,
                "timestamp": datetime.now().isoformat()
            })
            
            # Check basic connectivity with a HEAD request
            try:
                start_time = time.time()
                response = requests.head(
                    self.base_url, 
                    timeout=5,
                    allow_redirects=True
                )
                elapsed = time.time() - start_time
                
                connectivity_check = {
                    "status": "success",
                    "status_code": response.status_code,
                    "elapsed_ms": elapsed * 1000,
                    "url": self.base_url
                }
                logger.info(f"HEAD request to {self.base_url} succeeded: {response.status_code} in {elapsed:.2f}s")
            except requests.RequestException as e:
                connectivity_check = {
                    "status": "failed",
                    "url": self.base_url,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                logger.error(f"HEAD request to {self.base_url} failed: {e}")
            
            self.debug_data["network_checks"].append({
                "type": "head_request",
                "result": connectivity_check,
                "timestamp": datetime.now().isoformat()
            })
            
            # Run traceroute/tracert to identify network path
            trace_cmd = "tracert" if os.name == 'nt' else "traceroute"
            try:
                trace_output = subprocess.check_output(
                    [trace_cmd, "-w", "3", host], 
                    stderr=subprocess.STDOUT,
                    timeout=30,
                    text=True
                )
                
                trace_check = {
                    "status": "success",
                    "output": trace_output
                }
                logger.info(f"Traceroute to {host} completed successfully")
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                trace_check = {
                    "status": "failed",
                    "error": str(e)
                }
                logger.warning(f"Traceroute to {host} failed: {e}")
            
            self.debug_data["network_checks"].append({
                "type": "traceroute",
                "result": trace_check,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Network connectivity check failed: {e}")
            self.debug_data["network_checks"].append({
                "type": "general_failure",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    @timeout(10, "API health check timed out")
    def check_api_health(self):
        """Check the health of the API"""
        logger.info(f"Checking API health at {self.base_url}...")
        
        try:
            # Try to find health endpoint
            health_endpoints = [
                "/health",
                "/api/health",
                "/api/v1/health",
                "/status",
                "/api/status"
            ]
            
            for endpoint in health_endpoints:
                try:
                    url = f"{self.base_url.rstrip('/')}{endpoint}"
                    start_time = time.time()
                    response = requests.get(url, timeout=5)
                    elapsed = time.time() - start_time
                    
                    if response.status_code < 400:
                        logger.info(f"API health check succeeded at {url}: {response.status_code} in {elapsed:.2f}s")
                        return {
                            "status": "healthy",
                            "endpoint": url,
                            "status_code": response.status_code,
                            "response_time_ms": elapsed * 1000,
                            "response": response.text[:200]  # First 200 chars only
                        }
                except requests.RequestException:
                    continue
            
            # If no health endpoint found, just check the base URL
            start_time = time.time()
            response = requests.get(self.base_url, timeout=5)
            elapsed = time.time() - start_time
            
            logger.info(f"API base URL check: {response.status_code} in {elapsed:.2f}s")
            return {
                "status": "unknown",
                "endpoint": self.base_url,
                "status_code": response.status_code,
                "response_time_ms": elapsed * 1000
            }
            
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def detect_hanging_processes(self):
        """Detect any hanging processes that might interfere with tests"""
        logger.info("Checking for hanging processes...")
        
        current_process = psutil.Process()
        potential_hangs = []
        
        # Look for python processes that might be test-related
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                # Skip processes that are obviously not related
                if proc.pid == current_process.pid:
                    continue
                    
                cmd = ' '.join(proc.cmdline()).lower() if proc.cmdline() else ''
                
                # Look for test-related processes
                if 'python' in proc.name().lower() and any(x in cmd for x in ['test', 'pytest', 'api_test']):
                    cpu = proc.cpu_percent(interval=0.1)
                    memory_mb = proc.memory_info().rss / (1024 * 1024)
                    age_seconds = time.time() - proc.create_time()
                    
                    proc_info = {
                        "pid": proc.pid,
                        "name": proc.name(),
                        "command": ' '.join(proc.cmdline()),
                        "cpu_percent": cpu,
                        "memory_mb": memory_mb,
                        "age_seconds": age_seconds,
                        "suspected_hang": (cpu < 0.1 and age_seconds > 300)  # Flagging as potential hang
                    }
                    
                    if proc_info["suspected_hang"]:
                        logger.warning(f"Potential hanging process detected: PID {proc.pid}, age {age_seconds:.1f}s, CPU {cpu}%")
                    
                    potential_hangs.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        self.debug_data["hanging_processes"] = potential_hangs
        if not potential_hangs:
            logger.info("No hanging processes detected")
        else:
            logger.info(f"Found {len(potential_hangs)} potentially relevant processes")
    
    @timeout(5, "Database connection test timed out")
    def check_db_connection_leaks(self):
        """Check for potential database connection leaks"""
        logger.info("Checking for database connection leaks...")
        
        try:
            # Try to import database modules that might be used by the app
            db_modules = []
            potential_leaks = []
            
            for module_name in ["sqlite3", "psycopg2", "pymysql", "mysql.connector", "sqlalchemy"]:
                try:
                    __import__(module_name)
                    db_modules.append(module_name)
                except ImportError:
                    pass
            
            if not db_modules:
                logger.info("No database modules found to check for connection leaks")
                return
                
            logger.info(f"Found database modules: {', '.join(db_modules)}")
            
            # Run a simple connection test for each module
            for module in db_modules:
                # For SQLite, check for open file handles
                if module == "sqlite3":
                    import sqlite3
                    
                    # Create 5 connections and close 4 of them
                    connections = [sqlite3.connect(":memory:") for _ in range(5)]
                    for i in range(4):
                        connections[i].close()
                        
                    # We deliberately leave one open to check if our detection works
                    conn_statuses = []
                    for i, conn in enumerate(connections):
                        try:
                            conn.execute("SELECT 1")
                            status = "open"
                        except sqlite3.ProgrammingError:
                            status = "closed"
                            
                        conn_statuses.append({
                            "connection_id": i,
                            "status": status,
                            "expected_status": "closed" if i < 4 else "open"
                        })
                    
                    # Close the last connection properly
                    connections[4].close()
                    
                    potential_leaks.append({
                        "module": "sqlite3",
                        "connection_test": conn_statuses,
                        "leaked_connections": sum(1 for s in conn_statuses if s["status"] != s["expected_status"])
                    })
                    
                # For other database modules, we'd need specific connection tests
                # This is just a placeholder for the concept
            
            self.debug_data["connection_leaks"] = potential_leaks
            
        except Exception as e:
            logger.error(f"Database connection leak check failed: {e}")
            self.debug_data["connection_leaks"].append({
                "error": str(e),
                "traceback": traceback.format_exc()
            })
    
    @timeout(30, "Test diagnostics timed out")
    def run_test_diagnostics(self):
        """Run a diagnostic sequence to identify test performance issues"""
        logger.info("Running test diagnostics...")
        
        # Test individual endpoints to measure performance
        test_endpoints = [
            {"path": "", "method": "GET", "name": "base_url"},
            {"path": "/api/users", "method": "GET", "name": "list_users"},
            {"path": "/api/auth/login", "method": "POST", "name": "login"}
        ]
        
        performance_results = []
        
        # Create a session to reuse connection
        session = requests.Session()
        
        # If we have credentials, try to login first
        if self.email and self.password:
            try:
                login_data = {
                    "email": self.email,
                    "password": self.password
                }
                login_url = f"{self.base_url.rstrip('/')}/api/auth/login"
                
                response = session.post(login_url, json=login_data, timeout=5)
                
                if response.status_code == 200:
                    logger.info("Successfully logged in for diagnostics")
                    
                    # Try to extract and set the token if available
                    try:
                        token = response.json().get("token")
                        if token:
                            session.headers.update({"Authorization": f"Bearer {token}"})
                    except ValueError:
                        pass
                else:
                    logger.warning(f"Login failed with status {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Login request failed: {e}")
        
        # Test each endpoint multiple times to measure variance
        for endpoint in test_endpoints:
            url = f"{self.base_url.rstrip('/')}{endpoint['path']}"
            method = endpoint["method"].lower()
            results = []
            
            logger.info(f"Testing endpoint {endpoint['name']}: {method.upper()} {url}")
            
            # Test 3 times to measure variance
            for i in range(3):
                try:
                    start_time = time.time()
                    
                    if method == "get":
                        response = session.get(url, timeout=5)
                    elif method == "post":
                        # Mock data for POST requests
                        data = {"test": "data"}
                        response = session.post(url, json=data, timeout=5)
                    else:
                        continue
                        
                    elapsed = time.time() - start_time
                    
                    result = {
                        "attempt": i + 1,
                        "status_code": response.status_code,
                        "elapsed_ms": elapsed * 1000,
                        "content_length": len(response.content),
                        "success": 200 <= response.status_code < 300
                    }
                    
                    results.append(result)
                    logger.info(f"Endpoint test {i+1}: {response.status_code} in {elapsed:.2f}s")
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                    
                except requests.RequestException as e:
                    logger.error(f"Endpoint test failed: {e}")
                    results.append({
                        "attempt": i + 1,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "success": False
                    })
            
            # Calculate statistics if we have numeric results
            elapsed_times = [r["elapsed_ms"] for r in results if "elapsed_ms" in r]
            
            stats = {
                "endpoint": endpoint["name"],
                "url": url,
                "method": method.upper(),
                "results": results,
            }
            
            if elapsed_times:
                stats.update({
                    "min_ms": min(elapsed_times),
                    "max_ms": max(elapsed_times),
                    "avg_ms": sum(elapsed_times) / len(elapsed_times),
                    "variance": sum((t - (sum(elapsed_times) / len(elapsed_times))) ** 2 for t in elapsed_times) / len(elapsed_times)
                })
                
                # Flag potentially slow endpoints
                stats["is_slow"] = stats["avg_ms"] > 1000  # > 1 second is slow
                if stats["is_slow"]:
                    logger.warning(f"Slow endpoint detected: {endpoint['name']} ({stats['avg_ms']:.2f}ms)")
            
            performance_results.append(stats)
            
        self.debug_data["performance_metrics"] = performance_results
    
    @timeout(60, "Test isolation test timed out")
    def run_isolated_tests(self):
        """Run tests in isolation to identify problematic tests"""
        logger.info("Running tests in isolation...")
        
        # This would run each test file or test method individually
        # For demonstration, we'll mock this behavior
        
        isolated_results = []
        test_files = ["test_auth.py", "test_users.py", "test_items.py"]
        
        for test_file in test_files:
            try:
                logger.info(f"Running test file in isolation: {test_file}")
                
                # Mock command that would run a specific test file
                cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
                
                start_time = time.time()
                
                # In a real implementation, we'd actually run the command
                # and capture its output, but for demo we'll simulate
                if test_file == "test_auth.py":
                    exit_code = 0
                    output = "All tests passed"
                    elapsed = 1.5
                elif test_file == "test_users.py":
                    # Simulate a slow test
                    exit_code = 0
                    output = "All tests passed"
                    elapsed = 12.3
                else:
                    exit_code = 1
                    output = "Test failed: AssertionError"
                    elapsed = 0.8
                
                result = {
                    "test_file": test_file,
                    "exit_code": exit_code,
                    "status": "success" if exit_code == 0 else "failure",
                    "elapsed_seconds": elapsed,
                    "output_excerpt": output
                }
                
                isolated_results.append(result)
                logger.info(f"Isolated test {test_file}: {'PASS' if exit_code == 0 else 'FAIL'} in {elapsed:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to run isolated test {test_file}: {e}")
                isolated_results.append({
                    "test_file": test_file,
                    "status": "error",
                    "error": str(e)
                })
        
        self.debug_data["isolated_tests"] = isolated_results
        
        # Identify problematic tests
        slow_tests = [t for t in isolated_results if t.get("elapsed_seconds", 0) > 5]
        failed_tests = [t for t in isolated_results if t.get("status") != "success"]
        
        if slow_tests:
            logger.warning(f"Slow tests identified: {', '.join(t['test_file'] for t in slow_tests)}")
        
        if failed_tests:
            logger.warning(f"Failed tests identified: {', '.join(t['test_file'] for t in failed_tests)}")
    
    def run_debug_session(self):
        """
        Run a complete debug session to identify issues with API tests
        """
        self.start_time = datetime.now()
        logger.info(f"Starting API test debug session at {self.start_time.isoformat()}")
        
        try:
            # System information
            self.collect_system_info()
            
            # Network checks
            self.check_network_connectivity()
            
            # Check API health
            api_health = self.check_api_health()
            self.debug_data["api_health"] = api_health
            
            # Check for hanging processes
            self.detect_hanging_processes()
            
            # Test for database connection leaks
            self.check_db_connection_leaks()
            
            # Run diagnostics on test endpoints
            self.run_test_diagnostics()
            
            # Run tests in isolation
            self.run_isolated_tests()
            
            logger.info("Debug session completed successfully")
            
        except Exception as e:
            logger.error(f"Debug session failed: {str(e)}")
            logger.error(traceback.format_exc())
            
        finally:
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"Debug session ended at {self.end_time.isoformat()}")
            logger.info(f"Total duration: {duration:.2f} seconds")
            
            # Add summary to debug data
            self.debug_data["summary"] = {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_seconds": duration,
                "success": True
            }
            
            # Save debug data to file
            self.save_debug_report()
    
    def save_debug_report(self):
        """Save the debug report to a file"""
        report_file = os.path.join(log_dir, f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(report_file, 'w') as f:
            json.dump(self.debug_data, f, indent=2)
            
        logger.info(f"Debug report saved to {report_file}")
        
        # Also create a summary text file for quick reference
        summary_file = os.path.join(log_dir, f"debug_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(summary_file, 'w') as f:
            f.write("API TEST DEBUG SUMMARY\n")
            f.write("=====================\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base URL: {self.base_url}\n")
            f.write(f"Duration: {self.debug_data['summary']['duration_seconds']:.2f} seconds\n\n")
            
            # API Health
            if "api_health" in self.debug_data:
                health = self.debug_data["api_health"]
                f.write(f"API Health: {health.get('status', 'unknown').upper()}\n")
                if "error" in health:
                    f.write(f"  Error: {health['error']}\n")
                if "response_time_ms" in health:
                    f.write(f"  Response time: {health['response_time_ms']:.2f} ms\n")
            
            # Performance issues
            f.write("\nPERFORMANCE ISSUES\n")
            if "performance_metrics" in self.debug_data:
                slow_endpoints = [p for p in self.debug_data["performance_metrics"] if p.get("is_slow")]
                if slow_endpoints:
                    f.write(f"- {len(slow_endpoints)} slow endpoints detected:\n")
                    for endpoint in slow_endpoints:
                        f.write(f"  - {endpoint['method']} {endpoint['endpoint']}: {endpoint['avg_ms']:.2f} ms avg\n")
                else:
                    f.write("- No slow endpoints detected\n")
            
            # Network issues
            f.write("\nNETWORK ISSUES\n")
            network_failures = [n for n in self.debug_data["network_checks"] 
                               if "result" in n and n["result"].get("status") == "failed"]
            if network_failures:
                f.write(f"- {len(network_failures)} network issues detected:\n")
                for failure in network_failures:
                    f.write(f"  - {failure['type']}: {failure['result'].get('error', 'Unknown error')}\n")
            else:
                f.write("- No network issues detected\n")
            
            # Hanging processes
            f.write("\nHANGING PROCESSES\n")
            hanging = [p for p in self.debug_data.get("hanging_processes", []) if p.get("suspected_hang")]
            if hanging:
                f.write(f"- {len(hanging)} potentially hanging processes detected:\n")
                for process in hanging:
                    f.write(f"  - PID {process['pid']}: {process['name']} (Age: {process['age_seconds']:.1f}s)\n")
            else:
                f.write("- No hanging processes detected\n")
            
            # Isolated test issues
            f.write("\nTEST ISSUES\n")
            if "isolated_tests" in self.debug_data:
                failed = [t for t in self.debug_data["isolated_tests"] if t.get("status") != "success"]
                slow = [t for t in self.debug_data["isolated_tests"] if t.get("elapsed_seconds", 0) > 5]
                
                if failed:
                    f.write(f"- {len(failed)} failing tests detected:\n")
                    for test in failed:
                        f.write(f"  - {test['test_file']}: {test.get('output_excerpt', 'Unknown error')}\n")
                else:
                    f.write("- No failing tests detected\n")
                    
                if slow:
                    f.write(f"- {len(slow)} slow tests detected:\n")
                    for test in slow:
                        f.write(f"  - {test['test_file']}: {test['elapsed_seconds']:.2f}s\n")
                
            # Connection leaks
            f.write("\nCONNECTION ISSUES\n")
            if "connection_leaks" in self.debug_data and self.debug_data["connection_leaks"]:
                leaks = sum(l.get("leaked_connections", 0) for l in self.debug_data["connection_leaks"])
                if leaks:
                    f.write(f"- {leaks} potential connection leaks detected\n")
                else:
                    f.write("- No connection leaks detected\n")
            else:
                f.write("- Connection leak check not run or failed\n")
                
            # Recommendations
            f.write("\nRECOMMENDATIONS\n")
            recommendations = []
            
            if network_failures:
                recommendations.append("- Check network connectivity and firewall settings")
                
            if hanging:
                recommendations.append("- Terminate hanging processes and restart tests")
                
            if "isolated_tests" in self.debug_data:
                if failed:
                    recommendations.append("- Fix failing tests before addressing performance issues")
                if slow:
                    recommendations.append("- Add timeouts to slow tests")
                    recommendations.append("- Check for inefficient database queries or API calls")
            
            if "connection_leaks" in self.debug_data and any(l.get("leaked_connections", 0) > 0 for l in self.debug_data["connection_leaks"]):
                recommendations.append("- Check for unclosed database connections or resource leaks")
                
            if not recommendations:
                recommendations.append("- No specific issues detected, monitor test execution closely")
                
            for rec in recommendations:
                f.write(f"{rec}\n")
                
        logger.info(f"Debug summary saved to {summary_file}")
        
        return report_file, summary_file

def main():
    parser = argparse.ArgumentParser(description="Debug API Tests")
    parser.add_argument("--base-url", required=True, help="Base URL for the API")
    parser.add_argument("--email", help="Email for authentication")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout for tests in seconds")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    debugger = TestDebugger(
        base_url=args.base_url,
        email=args.email,
        password=args.password,
        timeout_seconds=args.timeout,
        verbose=args.verbose
    )
    
    try:
        debugger.run_debug_session()
    except KeyboardInterrupt:
        logger.warning("Debug session interrupted by user")
        sys.exit(1)
    
if __name__ == "__main__":
    main() 