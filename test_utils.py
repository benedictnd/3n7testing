#!/usr/bin/env python3
"""
Test Utilities - Helper functions and decorators for test monitoring and debugging
"""

import os
import sys
import time
import json
import signal
import logging
import functools
import threading
import traceback
from datetime import datetime
import psutil
import requests

# Configure logging
log_dir = "test-logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"test_utils_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_utils")

class TimeoutError(Exception):
    """Exception raised when a function call times out."""
    pass

def timeout(seconds=30):
    """
    Decorator that applies a timeout to a function.
    If the function takes longer than `seconds` to complete, it will be terminated.
    
    Usage:
        @timeout(10)  # 10 second timeout
        def slow_function():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            is_timeout = [False]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
                    logger.error(f"Exception in {func.__name__}: {e}")
                    logger.error(traceback.format_exc())
            
            def handle_timeout():
                is_timeout[0] = True
                thread_id = thread.ident
                
                # Log thread stack trace if possible
                for th in threading.enumerate():
                    if th.ident == thread_id:
                        stack = traceback.format_stack()
                        logger.warning(f"Thread stack trace at timeout:\n{''.join(stack)}")
                
                # Find all Python processes created by this process
                try:
                    current_process = psutil.Process(os.getpid())
                    children = current_process.children(recursive=True)
                    
                    if children:
                        logger.warning(f"Found {len(children)} child processes that may need cleanup:")
                        for child in children:
                            try:
                                logger.warning(f"  PID: {child.pid}, Name: {child.name()}, Status: {child.status()}")
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                            
                            try:
                                child.kill()
                                logger.warning(f"  Killed child process PID: {child.pid}")
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                except Exception as e:
                    logger.error(f"Error during child process cleanup: {e}")
                
                # Force thread to stop by raising an exception into it
                if sys.version_info >= (3, 8):
                    try:
                        import _thread
                        _thread.interrupt_main()
                    except (ImportError, RuntimeError) as e:
                        logger.error(f"Failed to interrupt main thread: {e}")
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            
            timer = threading.Timer(seconds, handle_timeout)
            timer.daemon = True
            timer.start()
            
            try:
                thread.join(seconds + 0.1)  # Give slightly more time than the timeout
                timer.cancel()  # Cancel the timer if the function completes in time
                
                if is_timeout[0]:
                    logger.warning(f"Function {func.__name__} timed out after {seconds} seconds")
                    raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
                    
                if exception[0]:
                    raise exception[0]
                    
                return result[0]
                
            except (KeyboardInterrupt, TimeoutError) as e:
                timer.cancel()
                if isinstance(e, KeyboardInterrupt):
                    logger.warning(f"Function {func.__name__} was interrupted by user")
                raise
                
        return wrapper
    return decorator

def monitor_connections(func):
    """
    Decorator that monitors network connections before and after a function call
    to detect potential connection leaks.
    
    Usage:
        @monitor_connections
        def function_that_makes_network_calls():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get current network connections
        before_connections = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                before_connections.add(f"{conn.laddr.ip}:{conn.laddr.port}->{conn.raddr.ip}:{conn.raddr.port}")
        
        logger.info(f"Function {func.__name__} started with {len(before_connections)} active connections")
        
        # Call the original function
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Check for connection leaks
        after_connections = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                after_connections.add(f"{conn.laddr.ip}:{conn.laddr.port}->{conn.raddr.ip}:{conn.raddr.port}")
        
        # Analyze connection differences
        new_connections = after_connections - before_connections
        closed_connections = before_connections - after_connections
        
        logger.info(f"Function {func.__name__} completed in {duration:.2f} seconds")
        logger.info(f"Network connections - Before: {len(before_connections)}, After: {len(after_connections)}, "
                   f"New: {len(new_connections)}, Closed: {len(closed_connections)}")
        
        if new_connections:
            logger.warning(f"Potential connection leaks detected in {func.__name__}: "
                          f"{len(new_connections)} connections were opened but not closed")
            
            # Log details of potentially leaked connections
            for conn in new_connections:
                logger.warning(f"  Unclosed connection: {conn}")
        
        return result
    
    return wrapper

def trace_http_calls(func):
    """
    Decorator that traces HTTP calls made by the requests library.
    This helps identify slow or hanging requests.
    
    Usage:
        @trace_http_calls
        def function_that_makes_http_requests():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Store original methods
        original_request = requests.Session.request
        
        # Define a hook to trace HTTP requests
        all_requests = []
        
        def trace_request(self, method, url, **kwargs):
            start_time = time.time()
            request_id = len(all_requests) + 1
            
            logger.info(f"HTTP Request #{request_id} started: {method} {url}")
            
            try:
                response = original_request(self, method, url, **kwargs)
                
                duration = time.time() - start_time
                logger.info(f"HTTP Request #{request_id} completed: {method} {url} - "
                           f"Status: {response.status_code}, Duration: {duration:.2f}s")
                
                # Record request details
                all_requests.append({
                    'id': request_id,
                    'method': method,
                    'url': url,
                    'start_time': start_time,
                    'duration': duration,
                    'status_code': response.status_code,
                    'headers': dict(response.headers)
                })
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"HTTP Request #{request_id} failed: {method} {url} - "
                            f"Error: {str(e)}, Duration: {duration:.2f}s")
                
                # Record failed request
                all_requests.append({
                    'id': request_id,
                    'method': method,
                    'url': url,
                    'start_time': start_time,
                    'duration': duration,
                    'error': str(e)
                })
                
                raise
        
        # Patch requests.Session.request
        requests.Session.request = trace_request
        
        try:
            return func(*args, **kwargs)
            
        finally:
            # Restore original method
            requests.Session.request = original_request
            
            # Create a summary of HTTP requests
            if all_requests:
                total_time = sum(req.get('duration', 0) for req in all_requests)
                success_count = sum(1 for req in all_requests if 'status_code' in req)
                failed_count = sum(1 for req in all_requests if 'error' in req)
                
                logger.info(f"HTTP Requests Summary for {func.__name__}:")
                logger.info(f"  Total Requests: {len(all_requests)}")
                logger.info(f"  Successful: {success_count}")
                logger.info(f"  Failed: {failed_count}")
                logger.info(f"  Total Time: {total_time:.2f}s")
                
                # Save detailed report to file
                report_file = os.path.join(log_dir, f"http_trace_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(report_file, 'w') as f:
                    json.dump(all_requests, f, indent=2)
                
                logger.info(f"HTTP trace report saved to {report_file}")
    
    return wrapper

def detect_db_connection_leaks():
    """
    Check for common database connection libraries and detect potential connection leaks.
    
    Returns:
        dict: Dictionary with leak detection results for each supported database library.
    """
    results = {}
    
    # Check for psycopg2 (PostgreSQL)
    try:
        import psycopg2
        from psycopg2 import pool
        
        # Check if there's a connection pool with connections
        pool_status = {
            "installed": True,
            "connection_pools": []
        }
        
        # Try to access psycopg2's internal connection pool if available
        # This is implementation-specific and may change in different versions
        if hasattr(pool, "_pools"):
            for p in pool._pools:
                if hasattr(p, "_used") and hasattr(p, "_unused"):
                    pool_status["connection_pools"].append({
                        "used_connections": len(p._used),
                        "unused_connections": len(p._unused)
                    })
        
        results["psycopg2"] = pool_status
        
    except ImportError:
        results["psycopg2"] = {"installed": False}
    except Exception as e:
        results["psycopg2"] = {"installed": True, "error": str(e)}
    
    # Check for mysql-connector-python (MySQL)
    try:
        import mysql.connector
        from mysql.connector import pooling
        
        # Try to check pooling status
        pool_status = {
            "installed": True,
            "pooling_enabled": hasattr(pooling, "MySQLConnectionPool")
        }
        
        results["mysql_connector"] = pool_status
        
    except ImportError:
        results["mysql_connector"] = {"installed": False}
    except Exception as e:
        results["mysql_connector"] = {"installed": True, "error": str(e)}
    
    # Check for pymongo (MongoDB)
    try:
        import pymongo
        
        # Get MongoDB client pools if any exist
        mongo_status = {
            "installed": True,
            "client_pools": []
        }
        
        if hasattr(pymongo, "MongoClient"):
            # Try to access internal connection pools
            if hasattr(pymongo.MongoClient, "_topology"):
                for client in pymongo.MongoClient.__instances__:
                    if hasattr(client, "_topology") and hasattr(client._topology, "_servers"):
                        mongo_status["client_pools"].append({
                            "servers": len(client._topology._servers),
                            "options": str(client._options)
                        })
        
        results["pymongo"] = mongo_status
        
    except ImportError:
        results["pymongo"] = {"installed": False}
    except Exception as e:
        results["pymongo"] = {"installed": True, "error": str(e)}
    
    # Check for SQLAlchemy
    try:
        import sqlalchemy
        from sqlalchemy import create_engine
        
        sqlalchemy_status = {
            "installed": True,
            "version": sqlalchemy.__version__
        }
        
        # Check for engine instances
        if hasattr(create_engine, "_engines"):
            sqlalchemy_status["active_engines"] = len(create_engine._engines)
        
        results["sqlalchemy"] = sqlalchemy_status
        
    except ImportError:
        results["sqlalchemy"] = {"installed": False}
    except Exception as e:
        results["sqlalchemy"] = {"installed": True, "error": str(e)}
    
    return results

def check_api_timeout(url, method="GET", timeout=5, headers=None, data=None, retries=2):
    """
    Check if an API endpoint is responding within the expected timeout.
    
    Args:
        url (str): The URL to check
        method (str): HTTP method to use (GET, POST, etc.)
        timeout (int): Timeout in seconds
        headers (dict): Optional headers to include
        data (dict): Optional data to send (for POST, PUT, etc.)
        retries (int): Number of retry attempts
    
    Returns:
        dict: Response information including status, time taken, and any errors
    """
    result = {
        "url": url,
        "method": method,
        "timeout_set": timeout,
        "success": False,
        "retries_attempted": 0,
        "time_taken": None,
        "status_code": None,
        "error": None
    }
    
    headers = headers or {}
    
    # Add a custom user agent for tracking these checks
    headers["User-Agent"] = "API-Timeout-Check/1.0"
    
    for attempt in range(retries + 1):
        start_time = time.time()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                timeout=timeout
            )
            
            time_taken = time.time() - start_time
            result["time_taken"] = time_taken
            result["status_code"] = response.status_code
            result["success"] = response.status_code < 400
            result["retries_attempted"] = attempt
            
            # Record headers but filter out sensitive information
            safe_headers = {k: v for k, v in response.headers.items() 
                          if k.lower() not in ("authorization", "cookie", "set-cookie")}
            result["response_headers"] = safe_headers
            
            # If successful, break out of retry loop
            if result["success"]:
                break
                
        except requests.exceptions.Timeout:
            time_taken = time.time() - start_time
            result["time_taken"] = time_taken
            result["error"] = f"Request timed out after {time_taken:.2f}s (timeout was set to {timeout}s)"
            result["retries_attempted"] = attempt
            
        except requests.exceptions.ConnectionError as e:
            time_taken = time.time() - start_time
            result["time_taken"] = time_taken
            result["error"] = f"Connection error: {str(e)}"
            result["retries_attempted"] = attempt
            
        except Exception as e:
            time_taken = time.time() - start_time
            result["time_taken"] = time_taken
            result["error"] = f"Error: {str(e)}"
            result["retries_attempted"] = attempt
    
    return result

if __name__ == "__main__":
    # If run directly, show basic usage examples
    logger.info("Test Utilities Module - Usage Examples:")
    logger.info("1. Timeout Decorator: @timeout(seconds)")
    logger.info("2. Monitor Connections: @monitor_connections")
    logger.info("3. Trace HTTP Calls: @trace_http_calls")
    logger.info("4. DB Connection Leak Detection: detect_db_connection_leaks()")
    logger.info("5. API Timeout Check: check_api_timeout(url, method, timeout)") 