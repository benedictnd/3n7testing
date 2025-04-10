#!/usr/bin/env python3
"""
API Debug Utilities for 3&7 Training Platform

This module provides debugging tools for API testing, including:
- Request/response capture and analysis
- Connection troubleshooting
- Data validation helpers
- Performance profiling
- Visual request flow inspection
"""

import json
import time
import logging
import requests
import inspect
import traceback
import warnings
import socket
import sys
import os
import httpx
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs

# Configure logger
logger = logging.getLogger("api_debug")
log_level = os.environ.get("API_DEBUG_LEVEL", "INFO")
logger.setLevel(getattr(logging, log_level))

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(console_handler)


class APIDebugger:
    """Core class for API debugging capabilities"""

    def __init__(
        self,
        base_url: str = None,
        log_requests: bool = True,
        log_responses: bool = True,
        log_headers: bool = True,
        log_bodies: bool = True,
        max_body_length: int = 1000,
        performance_tracking: bool = True,
    ):
        """
        Initialize API debugger

        Args:
            base_url: Base URL for the API
            log_requests: Whether to log requests
            log_responses: Whether to log responses
            log_headers: Whether to log headers
            log_bodies: Whether to log request/response bodies
            max_body_length: Maximum length for logged bodies
            performance_tracking: Whether to track performance
        """
        self.base_url = base_url
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_headers = log_headers
        self.log_bodies = log_bodies
        self.max_body_length = max_body_length
        self.performance_tracking = performance_tracking
        
        # Request history
        self.history: List[Dict[str, Any]] = []
        self.slow_threshold_ms = 500  # Threshold for slow requests (ms)
        
        # Session for connection reuse
        self.session = requests.Session()
        
        logger.info(f"Initialized API debugger for {base_url}")
    
    def clear_history(self) -> None:
        """Clear request history"""
        self.history = []
        logger.debug("Request history cleared")
    
    @contextmanager
    def capture_request(self):
        """Context manager to capture request details"""
        start_time = time.time()
        request_info = {
            "timestamp": datetime.now().isoformat(),
            "caller": self._get_caller_info(),
        }
        
        try:
            yield request_info
            
        finally:
            # Calculate request duration
            request_info["duration_ms"] = round((time.time() - start_time) * 1000, 2)
            
            # Log performance warnings
            if self.performance_tracking and request_info.get("duration_ms", 0) > self.slow_threshold_ms:
                logger.warning(
                    f"Slow request detected: {request_info.get('method', 'UNKNOWN')} "
                    f"{request_info.get('url', 'unknown')} took {request_info['duration_ms']}ms"
                )
            
            # Add to history
            self.history.append(request_info)
            
            # Log request/response if enabled
            if self.log_requests and "method" in request_info and "url" in request_info:
                self._log_request(request_info)
            
            if self.log_responses and "status_code" in request_info:
                self._log_response(request_info)
    
    def _log_request(self, request_info: Dict[str, Any]) -> None:
        """Log request details"""
        method = request_info.get("method", "UNKNOWN")
        url = request_info.get("url", "unknown")
        
        log_message = f"➡️ {method} {url}"
        
        if self.log_headers and "request_headers" in request_info:
            headers_str = self._format_headers(request_info["request_headers"])
            log_message += f"\nRequest Headers: {headers_str}"
        
        if self.log_bodies and "request_body" in request_info and request_info["request_body"]:
            body = request_info["request_body"]
            body_str = self._format_body(body)
            log_message += f"\nRequest Body: {body_str}"
        
        logger.debug(log_message)
    
    def _log_response(self, request_info: Dict[str, Any]) -> None:
        """Log response details"""
        method = request_info.get("method", "UNKNOWN")
        url = request_info.get("url", "unknown")
        status_code = request_info.get("status_code", "???")
        duration_ms = request_info.get("duration_ms", 0)
        
        log_message = f"⬅️ {status_code} {method} {url} ({duration_ms}ms)"
        
        if self.log_headers and "response_headers" in request_info:
            headers_str = self._format_headers(request_info["response_headers"])
            log_message += f"\nResponse Headers: {headers_str}"
        
        if self.log_bodies and "response_body" in request_info and request_info["response_body"]:
            body = request_info["response_body"]
            body_str = self._format_body(body)
            log_message += f"\nResponse Body: {body_str}"
        
        log_func = logger.debug
        if 400 <= status_code < 500:
            log_func = logger.warning
        elif status_code >= 500:
            log_func = logger.error
        
        log_func(log_message)
    
    def _format_headers(self, headers: Dict[str, Any]) -> str:
        """Format headers for logging"""
        header_str = json.dumps(headers, indent=2)
        if len(header_str) > self.max_body_length:
            header_str = header_str[:self.max_body_length] + "... [truncated]"
        return header_str
    
    def _format_body(self, body: Union[Dict[str, Any], str, bytes]) -> str:
        """Format body content for logging"""
        if isinstance(body, bytes):
            try:
                body = body.decode('utf-8')
            except UnicodeDecodeError:
                return "[Binary data]"
        
        if isinstance(body, dict):
            body_str = json.dumps(body, indent=2)
        else:
            body_str = str(body)
        
        # Truncate if too long
        if len(body_str) > self.max_body_length:
            body_str = body_str[:self.max_body_length] + "... [truncated]"
            
        return body_str
    
    def _get_caller_info(self) -> Dict[str, Any]:
        """Get information about the caller from the stack"""
        caller_frame = None
        current_frame = inspect.currentframe()
        
        # Get the caller outside of this class
        if current_frame:
            try:
                frame = current_frame.f_back
                while frame:
                    module_name = frame.f_globals.get('__name__', '')
                    if module_name != __name__:
                        caller_frame = frame
                        break
                    frame = frame.f_back
            finally:
                del current_frame  # Avoid reference cycles
        
        if not caller_frame:
            return {"module": "unknown", "function": "unknown", "line": 0}
            
        return {
            "module": caller_frame.f_globals.get('__name__', 'unknown'),
            "function": caller_frame.f_code.co_name,
            "line": caller_frame.f_lineno
        }
    
    def send_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        data: Any = None,
        verify: bool = True,
        timeout: int = 30,
        **kwargs
    ) -> requests.Response:
        """
        Send HTTP request with debugging
        
        Args:
            method: HTTP method
            url: URL to request
            headers: Request headers
            params: URL parameters
            json_data: JSON body data
            data: Form data
            verify: Verify SSL certificates
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: Response object
        """
        # Prepend base_url if url is relative
        if self.base_url and not url.startswith(('http://', 'https://')):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        
        with self.capture_request() as request_info:
            request_info["method"] = method
            request_info["url"] = url
            request_info["request_headers"] = headers
            request_info["request_params"] = params
            
            if json_data:
                request_info["request_body"] = json_data
            elif data:
                request_info["request_body"] = data
            
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    data=data,
                    verify=verify,
                    timeout=timeout,
                    **kwargs
                )
                
                # Record response info
                request_info["status_code"] = response.status_code
                request_info["response_headers"] = dict(response.headers)
                
                # Try to parse response body
                try:
                    if response.text and response.headers.get('Content-Type', '').startswith('application/json'):
                        request_info["response_body"] = response.json()
                    else:
                        request_info["response_body"] = response.text
                except Exception:
                    request_info["response_body"] = "[Error parsing response body]"
                
                return response
                
            except Exception as e:
                request_info["error"] = str(e)
                request_info["traceback"] = traceback.format_exc()
                logger.error(f"Request error: {e}")
                raise
    
    def analyze_connection(self, url: str = None, timeout: int = 5) -> Dict[str, Any]:
        """
        Analyze connection to the specified URL
        
        Args:
            url: URL to analyze (defaults to base_url)
            timeout: Connection timeout in seconds
            
        Returns:
            Dict with connection analysis results
        """
        if not url and self.base_url:
            url = self.base_url
        
        if not url:
            raise ValueError("No URL provided for connection analysis")
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        results = {
            "url": url,
            "hostname": hostname,
            "port": port,
            "dns_resolution": None,
            "connection": None,
            "ssl_info": None,
            "http_response": None,
            "errors": []
        }
        
        # DNS resolution
        try:
            logger.info(f"Resolving DNS for {hostname}")
            start_time = time.time()
            ip_address = socket.gethostbyname(hostname)
            dns_time = (time.time() - start_time) * 1000
            
            results["dns_resolution"] = {
                "ip_address": ip_address,
                "time_ms": round(dns_time, 2)
            }
        except socket.gaierror as e:
            results["errors"].append(f"DNS resolution failed: {str(e)}")
            logger.error(f"DNS resolution failed for {hostname}: {e}")
            return results
        
        # Test TCP connection
        try:
            logger.info(f"Testing TCP connection to {hostname}:{port}")
            start_time = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip_address, port))
            connection_time = (time.time() - start_time) * 1000
            s.close()
            
            results["connection"] = {
                "successful": True,
                "time_ms": round(connection_time, 2)
            }
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            results["errors"].append(f"Connection failed: {str(e)}")
            logger.error(f"Connection failed to {hostname}:{port}: {e}")
            return results
        
        # HTTP request
        try:
            logger.info(f"Sending HTTP request to {url}")
            start_time = time.time()
            response = requests.get(url, timeout=timeout, verify=True)
            request_time = (time.time() - start_time) * 1000
            
            results["http_response"] = {
                "status_code": response.status_code,
                "time_ms": round(request_time, 2),
                "content_type": response.headers.get('Content-Type'),
                "server": response.headers.get('Server'),
                "headers": dict(response.headers)
            }
            
            if response.status_code >= 400:
                results["errors"].append(f"HTTP error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            results["errors"].append(f"HTTP request failed: {str(e)}")
            logger.error(f"HTTP request failed to {url}: {e}")
        
        return results

    def analyze_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Analyze HTTP response for common issues
        
        Args:
            response: Response object to analyze
            
        Returns:
            Dict with analysis results
        """
        analysis = {
            "status_code": response.status_code,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "content_type": response.headers.get('Content-Type'),
            "content_length": int(response.headers.get('Content-Length', 0)),
            "server": response.headers.get('Server'),
            "issues": [],
            "warnings": [],
            "security_headers": {}
        }
        
        # Check for error status
        if 400 <= response.status_code < 500:
            analysis["issues"].append(f"Client error: {response.status_code}")
        elif response.status_code >= 500:
            analysis["issues"].append(f"Server error: {response.status_code}")
        
        # Check performance
        if analysis["response_time_ms"] > 1000:
            analysis["warnings"].append(f"Slow response: {analysis['response_time_ms']}ms")
        
        # Check security headers
        security_headers = {
            "Strict-Transport-Security": "HSTS not enabled",
            "Content-Security-Policy": "CSP not enabled",
            "X-Content-Type-Options": "X-Content-Type-Options not set",
            "X-Frame-Options": "X-Frame-Options not set",
            "X-XSS-Protection": "X-XSS-Protection not set"
        }
        
        for header, warning in security_headers.items():
            value = response.headers.get(header)
            analysis["security_headers"][header] = value
            if not value:
                analysis["warnings"].append(warning)
        
        # JSON validation if applicable
        if response.headers.get('Content-Type', '').startswith('application/json'):
            try:
                json_data = response.json()
                analysis["json_valid"] = True
                analysis["json_keys"] = list(json_data.keys()) if isinstance(json_data, dict) else None
            except ValueError:
                analysis["json_valid"] = False
                analysis["issues"].append("Invalid JSON response")
        
        return analysis
    
    def export_history(self, filepath: str = None) -> str:
        """
        Export request history to JSON file
        
        Args:
            filepath: Path to export file (default: api_debug_history_{timestamp}.json)
            
        Returns:
            Path to the exported file
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"api_debug_history_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        logger.info(f"Exported {len(self.history)} requests to {filepath}")
        return filepath
    
    def print_statistics(self) -> Dict[str, Any]:
        """
        Print request statistics
        
        Returns:
            Dict with statistics
        """
        if not self.history:
            logger.info("No requests in history")
            return {}
        
        # Calculate statistics
        stats = {
            "total_requests": len(self.history),
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time_ms": 0,
            "slowest_request_ms": 0,
            "slowest_request_url": "",
            "status_codes": {},
            "methods": {},
        }
        
        total_time = 0
        
        for req in self.history:
            # Request method stats
            method = req.get("method", "UNKNOWN")
            stats["methods"][method] = stats["methods"].get(method, 0) + 1
            
            # Status code stats
            status_code = req.get("status_code")
            if status_code:
                status_str = str(status_code)
                stats["status_codes"][status_str] = stats["status_codes"].get(status_str, 0) + 1
                
                if 200 <= status_code < 400:
                    stats["successful_requests"] += 1
                else:
                    stats["failed_requests"] += 1
            
            # Timing stats
            if "duration_ms" in req:
                duration = req["duration_ms"]
                total_time += duration
                
                if duration > stats["slowest_request_ms"]:
                    stats["slowest_request_ms"] = duration
                    stats["slowest_request_url"] = req.get("url", "unknown")
        
        if stats["total_requests"] > 0:
            stats["avg_response_time_ms"] = round(total_time / stats["total_requests"], 2)
        
        # Log summary
        logger.info(f"API Request Statistics:")
        logger.info(f"  Total Requests: {stats['total_requests']}")
        logger.info(f"  Successful: {stats['successful_requests']}, Failed: {stats['failed_requests']}")
        logger.info(f"  Average Response Time: {stats['avg_response_time_ms']}ms")
        logger.info(f"  Slowest Request: {stats['slowest_request_ms']}ms ({stats['slowest_request_url']})")
        logger.info(f"  Status Codes: {stats['status_codes']}")
        logger.info(f"  Methods: {stats['methods']}")
        
        return stats


# Convenience functions for direct use
debugger = APIDebugger()

def configure(
    base_url: str = None,
    log_level: str = "INFO",
    log_requests: bool = True,
    log_responses: bool = True,
    log_headers: bool = True,
    log_bodies: bool = True,
) -> None:
    """Configure the global debugger instance"""
    global debugger
    debugger = APIDebugger(
        base_url=base_url,
        log_requests=log_requests,
        log_responses=log_responses,
        log_headers=log_headers,
        log_bodies=log_bodies,
    )
    logger.setLevel(getattr(logging, log_level))


def debug_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    params: Dict[str, Any] = None,
    json_data: Dict[str, Any] = None,
    data: Any = None,
    **kwargs
) -> requests.Response:
    """Send a request with debugging"""
    return debugger.send_request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json_data=json_data,
        data=data,
        **kwargs
    )


def test_connection(url: str = None) -> Dict[str, Any]:
    """Test connection to URL"""
    return debugger.analyze_connection(url)


def export_history(filepath: str = None) -> str:
    """Export request history to file"""
    return debugger.export_history(filepath)


def get_statistics() -> Dict[str, Any]:
    """Get request statistics"""
    return debugger.print_statistics()


def analyze_response(response: requests.Response) -> Dict[str, Any]:
    """Analyze HTTP response"""
    return debugger.analyze_response(response)


if __name__ == "__main__":
    # Enable more verbose logging for command-line usage
    logging.basicConfig(level=logging.DEBUG)
    
    import argparse
    
    parser = argparse.ArgumentParser(description="API Debug Utility")
    parser.add_argument("--url", help="URL to test connection", required=True)
    parser.add_argument("--method", help="HTTP method", default="GET")
    parser.add_argument("--headers", help="HTTP headers as JSON string")
    parser.add_argument("--body", help="Request body as JSON string")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    # Configure debugger
    configure(base_url=None, log_level="DEBUG")
    
    print(f"Testing connection to {args.url}...")
    conn_info = test_connection(args.url)
    
    print("\nConnection Analysis:")
    print(f"  DNS: {'Success' if conn_info.get('dns_resolution') else 'Failed'}")
    if conn_info.get('dns_resolution'):
        print(f"  IP: {conn_info['dns_resolution'].get('ip_address')}")
    
    print(f"  Connection: {'Success' if conn_info.get('connection', {}).get('successful') else 'Failed'}")
    
    if conn_info.get('http_response'):
        print(f"  HTTP Response: {conn_info['http_response'].get('status_code')}")
        print(f"  Response Time: {conn_info['http_response'].get('time_ms')}ms")
    
    if conn_info.get('errors'):
        print("\nErrors:")
        for error in conn_info['errors']:
            print(f"  - {error}")
    
    # Make a sample request if no errors
    if not conn_info.get('errors') and args.method:
        headers = json.loads(args.headers) if args.headers else {}
        body = json.loads(args.body) if args.body else None
        
        print(f"\nSending {args.method} request to {args.url}...")
        try:
            response = debug_request(
                method=args.method,
                url=args.url,
                headers=headers,
                json_data=body,
                timeout=10
            )
            
            analysis = analyze_response(response)
            
            print(f"\nResponse Analysis:")
            print(f"  Status: {analysis['status_code']}")
            print(f"  Time: {analysis['response_time_ms']}ms")
            print(f"  Content-Type: {analysis['content_type']}")
            
            if analysis.get('issues'):
                print("\nIssues:")
                for issue in analysis['issues']:
                    print(f"  - {issue}")
            
            if analysis.get('warnings'):
                print("\nWarnings:")
                for warning in analysis['warnings']:
                    print(f"  - {warning}")
            
        except Exception as e:
            print(f"Request failed: {e}")
    
    # Export results if output file specified
    if args.output and debugger.history:
        export_path = export_history(args.output)
        print(f"\nExported debug log to {export_path}") 