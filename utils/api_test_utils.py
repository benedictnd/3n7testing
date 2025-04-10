"""
API Testing Utilities

This module provides utility functions for API testing, including:
- Request helpers with retry and timeout management
- Response validation functions
- Data generation for testing
- Common assertions for API testing
"""

import json
import logging
import random
import string
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, List, Optional, Callable, Union, Tuple

import requests
from requests.exceptions import RequestException, Timeout

# Setup logging
logger = logging.getLogger("api_test_utils")

# Constants
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRIES = 3
RETRY_BACKOFF_FACTOR = 1.5
MAX_RETRY_DELAY = 10  # seconds

class APITestException(Exception):
    """Custom exception for API testing errors."""
    pass

class APITimeoutException(APITestException):
    """Exception raised when an API request times out."""
    pass

class APIResponseException(APITestException):
    """Exception raised when an API response is invalid."""
    pass

def retry_request(
    max_retries: int = DEFAULT_RETRIES,
    retry_on_exceptions: Tuple = (RequestException,),
    retry_on_status_codes: List[int] = [429, 500, 502, 503, 504],
    backoff_factor: float = RETRY_BACKOFF_FACTOR
) -> Callable:
    """
    Decorator for retrying API requests on failure.
    
    Args:
        max_retries: Maximum number of retries
        retry_on_exceptions: Exceptions that trigger a retry
        retry_on_status_codes: HTTP status codes that trigger a retry
        backoff_factor: Exponential backoff factor for retries
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries <= max_retries:
                try:
                    response = func(*args, **kwargs)
                    
                    # Check if status code should trigger retry
                    if response.status_code in retry_on_status_codes:
                        logger.warning(
                            f"Received status code {response.status_code}, "
                            f"retrying ({retries}/{max_retries})"
                        )
                        retries += 1
                        if retries > max_retries:
                            break
                            
                        # Calculate exponential backoff
                        delay = min(backoff_factor * (2 ** (retries - 1)), MAX_RETRY_DELAY)
                        time.sleep(delay)
                        continue
                        
                    return response
                    
                except retry_on_exceptions as e:
                    last_exception = e
                    retries += 1
                    if retries > max_retries:
                        break
                        
                    # Calculate exponential backoff
                    delay = min(backoff_factor * (2 ** (retries - 1)), MAX_RETRY_DELAY)
                    logger.warning(
                        f"Request failed with error: {str(e)}, "
                        f"retrying ({retries}/{max_retries}) after {delay:.2f}s"
                    )
                    time.sleep(delay)
            
            # All retries failed
            if last_exception:
                logger.error(f"Request failed after {max_retries} retries: {str(last_exception)}")
                raise last_exception
            else:
                logger.error(f"Request failed with status code {response.status_code} after {max_retries} retries")
                return response
                
        return wrapper
    return decorator

def with_timeout(timeout: float = DEFAULT_TIMEOUT) -> Callable:
    """
    Decorator to add timeout to functions.
    
    Args:
        timeout: Timeout in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add timeout to kwargs if it's a request function
            if "timeout" not in kwargs:
                kwargs["timeout"] = timeout
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry_request()
@with_timeout()
def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    auth: Optional[Tuple[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    verify: bool = True,
    allow_redirects: bool = True,
    **kwargs
) -> requests.Response:
    """
    Make an HTTP request with retry logic and timeout.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: URL to request
        headers: Request headers
        params: Query parameters
        data: Form data
        json_data: JSON data
        files: Files to upload
        auth: Basic auth credentials
        timeout: Request timeout in seconds
        verify: Verify SSL certificates
        allow_redirects: Follow redirects
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Response object
    """
    # Start timer
    start_time = time.time()
    
    # Log request
    logger.info(f"Making {method} request to {url}")
    if params:
        logger.debug(f"Request params: {params}")
    if json_data:
        logger.debug(f"Request JSON data: {json_data}")
    
    # Make request
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            files=files,
            auth=auth,
            timeout=timeout,
            verify=verify,
            allow_redirects=allow_redirects,
            **kwargs
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Add response time to response object
        response.elapsed_seconds = response_time
        
        # Log response
        logger.info(f"Received response from {url}: {response.status_code} in {response_time:.2f}s")
        
        return response
        
    except Timeout:
        elapsed = time.time() - start_time
        logger.error(f"Request to {url} timed out after {elapsed:.2f}s")
        raise APITimeoutException(f"Request to {url} timed out after {elapsed:.2f}s")
        
    except RequestException as e:
        elapsed = time.time() - start_time
        logger.error(f"Request to {url} failed after {elapsed:.2f}s: {str(e)}")
        raise

def assert_status_code(
    response: requests.Response,
    expected_status: Union[int, List[int]]
) -> None:
    """
    Assert that a response has the expected status code.
    
    Args:
        response: Response object
        expected_status: Expected status code or list of expected status codes
        
    Raises:
        AssertionError: If the status code doesn't match the expected status
    """
    if isinstance(expected_status, int):
        expected_status = [expected_status]
        
    assert response.status_code in expected_status, (
        f"Expected status code {expected_status}, got {response.status_code}. "
        f"Response: {response.text[:500]}"
    )

def assert_json_response(response: requests.Response) -> Dict[str, Any]:
    """
    Assert that a response contains valid JSON and return the parsed data.
    
    Args:
        response: Response object
        
    Returns:
        Parsed JSON data
        
    Raises:
        AssertionError: If the response doesn't contain valid JSON
    """
    try:
        return response.json()
    except ValueError:
        raise AssertionError(
            f"Response doesn't contain valid JSON. Status: {response.status_code}, "
            f"Content-Type: {response.headers.get('Content-Type')}, "
            f"Text: {response.text[:500]}"
        )

def assert_response_time(response: requests.Response, max_time: float) -> None:
    """
    Assert that a response was received within the maximum time.
    
    Args:
        response: Response object
        max_time: Maximum allowed time in seconds
        
    Raises:
        AssertionError: If the response time exceeds the maximum time
    """
    assert response.elapsed_seconds <= max_time, (
        f"Response time {response.elapsed_seconds:.2f}s exceeds maximum allowed time {max_time:.2f}s"
    )

def assert_header_present(response: requests.Response, header_name: str) -> None:
    """
    Assert that a response contains a specific header.
    
    Args:
        response: Response object
        header_name: Name of the header to check
        
    Raises:
        AssertionError: If the header is not present
    """
    assert header_name.lower() in [h.lower() for h in response.headers], (
        f"Header '{header_name}' not found in response headers: {response.headers}"
    )

def assert_header_value(
    response: requests.Response,
    header_name: str,
    expected_value: str
) -> None:
    """
    Assert that a response header has the expected value.
    
    Args:
        response: Response object
        header_name: Name of the header to check
        expected_value: Expected value of the header
        
    Raises:
        AssertionError: If the header value doesn't match the expected value
    """
    # Case-insensitive header name lookup
    header_found = False
    actual_value = None
    
    for header, value in response.headers.items():
        if header.lower() == header_name.lower():
            header_found = True
            actual_value = value
            break
            
    assert header_found, f"Header '{header_name}' not found in response headers"
    assert actual_value == expected_value, (
        f"Expected header '{header_name}' to have value '{expected_value}', "
        f"got '{actual_value}'"
    )

def assert_json_schema(json_data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Assert that JSON data conforms to a schema.
    
    This is a simple schema validation that checks for required fields and types.
    For more complex schema validation, use a library like jsonschema.
    
    Args:
        json_data: JSON data to validate
        schema: Schema to validate against
        
    Raises:
        AssertionError: If the JSON data doesn't conform to the schema
    """
    try:
        # Check for required fields
        for field, field_schema in schema.items():
            if field_schema.get("required", False):
                assert field in json_data, f"Required field '{field}' not found in JSON data"
                
            # Check type if field exists and has a type specified
            if field in json_data and "type" in field_schema:
                expected_type = field_schema["type"]
                
                if expected_type == "string":
                    assert isinstance(json_data[field], str), (
                        f"Field '{field}' should be a string, got {type(json_data[field]).__name__}"
                    )
                elif expected_type == "number":
                    assert isinstance(json_data[field], (int, float)), (
                        f"Field '{field}' should be a number, got {type(json_data[field]).__name__}"
                    )
                elif expected_type == "integer":
                    assert isinstance(json_data[field], int), (
                        f"Field '{field}' should be an integer, got {type(json_data[field]).__name__}"
                    )
                elif expected_type == "boolean":
                    assert isinstance(json_data[field], bool), (
                        f"Field '{field}' should be a boolean, got {type(json_data[field]).__name__}"
                    )
                elif expected_type == "array":
                    assert isinstance(json_data[field], list), (
                        f"Field '{field}' should be an array, got {type(json_data[field]).__name__}"
                    )
                elif expected_type == "object":
                    assert isinstance(json_data[field], dict), (
                        f"Field '{field}' should be an object, got {type(json_data[field]).__name__}"
                    )
    except AssertionError as e:
        # Add additional context to the assertion error
        raise AssertionError(f"JSON schema validation failed: {str(e)}")

def generate_random_string(length: int = 10) -> str:
    """
    Generate a random alphanumeric string.
    
    Args:
        length: Length of the string
        
    Returns:
        Random string
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_email() -> str:
    """
    Generate a random email address.
    
    Returns:
        Random email address
    """
    username = generate_random_string(8)
    domain = generate_random_string(5)
    return f"{username}@{domain}.com"

def generate_random_date(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Generate a random date between start_date and end_date.
    
    Args:
        start_date: Start date (default: 1 year ago)
        end_date: End date (default: today)
        
    Returns:
        Random date in ISO format
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
        
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    random_date = start_date + timedelta(days=random_days)
    
    return random_date.isoformat()

def generate_test_data(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test data based on a schema.
    
    Args:
        schema: Schema describing the data structure
        
    Returns:
        Generated test data
    """
    data = {}
    
    for field, field_schema in schema.items():
        field_type = field_schema.get("type", "string")
        
        if field_type == "string":
            if field.lower().endswith("email"):
                data[field] = generate_random_email()
            elif field.lower().endswith("date"):
                data[field] = generate_random_date()
            else:
                data[field] = generate_random_string()
        elif field_type in ["number", "integer"]:
            min_val = field_schema.get("minimum", 0)
            max_val = field_schema.get("maximum", 1000)
            data[field] = random.randint(min_val, max_val)
        elif field_type == "boolean":
            data[field] = random.choice([True, False])
        elif field_type == "array":
            items_schema = field_schema.get("items", {"type": "string"})
            min_items = field_schema.get("minItems", 1)
            max_items = field_schema.get("maxItems", 5)
            count = random.randint(min_items, max_items)
            
            if items_schema.get("type") == "object":
                data[field] = [generate_test_data(items_schema.get("properties", {})) for _ in range(count)]
            else:
                data[field] = [generate_random_string() for _ in range(count)]
        elif field_type == "object":
            properties = field_schema.get("properties", {})
            data[field] = generate_test_data(properties)
    
    return data

def time_request(func: Callable) -> Callable:
    """
    Decorator to time a function and log its execution time.
    
    Args:
        func: Function to time
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
        return result
    return wrapper 