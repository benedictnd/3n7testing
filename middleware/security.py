from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Set, List
import time
import os
from redis import Redis
import json

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.secure_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",  # Changed from ALLOW-FROM to DENY
            "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none';",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(self)",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache"
        }

    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)

        # Add security headers
        for header_name, header_value in self.secure_headers.items():
            response.headers[header_name] = header_value

        return response

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for implementing rate limiting."""

    def __init__(self, app: FastAPI, rate_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        
        # Path-specific rate limits for sensitive endpoints
        self.path_rate_limits = {
            "/email/send": 10,           # Limit email sending to 10 per minute
            "/email/send-test": 5,       # Limit test emails to 5 per minute
            "/email/send-with-attachments": 5,  # Limit attachment emails to 5 per minute
            "/auth/login": 10,           # Limit login attempts to 10 per minute
            "/users/*/roles": 3,         # Limit role changes to 3 per minute (for security)
        }
        
        # Higher limits for public endpoints
        self.public_rate_limit = 180     # 3 requests per second
        
        # Redis connection for distributed rate limiting
        redis_url = os.getenv("REDIS_URL")
        self.redis = Redis.from_url(redis_url) if redis_url else None
        
        # Whitelisted IPs that bypass rate limiting
        self.whitelisted_ips = set(os.getenv("RATE_LIMIT_WHITELIST", "").split(","))

    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address for simplicity)
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for whitelisted IPs
        if client_ip in self.whitelisted_ips:
            return await call_next(request)
        
        # Determine the rate limit based on the path
        path = request.url.path
        
        # Find matching path pattern
        rate_limit = self.rate_limit
        for pattern, limit in self.path_rate_limits.items():
            if self._path_matches(path, pattern):
                rate_limit = limit
                break
                
        # Use Redis for rate limiting if available, otherwise use in-memory
        if self.redis:
            # Generate a key based on IP and path
            key = f"rate_limit:{client_ip}:{path}"
            current_time = int(time.time())
            window_start = current_time - self.window_seconds
            
            # Count requests in the current window
            pipeline = self.redis.pipeline()
            pipeline.zremrangebyscore(key, 0, window_start)
            pipeline.zadd(key, {str(current_time): current_time})
            pipeline.zcard(key)
            pipeline.expire(key, self.window_seconds * 2)  # Set TTL for the key
            _, _, request_count, _ = pipeline.execute()
            
            # Check if rate limit is exceeded
            if request_count > rate_limit:
                return self._rate_limit_response(rate_limit)
        else:
            # In-memory rate limiting (not suitable for distributed setups)
            # Implementation omitted for brevity - in production, Redis should be used
            pass
        
        # Process the request normally
        response = await call_next(request)
        return response
    
    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern with wildcards."""
        if '*' not in pattern:
            return path == pattern
            
        parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(parts) != len(path_parts):
            return False
            
        for i, part in enumerate(parts):
            if part == '*':
                continue
            if part != path_parts[i]:
                return False
                
        return True
    
    def _rate_limit_response(self, rate_limit: int) -> Response:
        """Create rate limit exceeded response."""
        from fastapi.responses import JSONResponse
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Too many requests. Maximum {rate_limit} requests per {self.window_seconds} seconds."
            },
            headers={
                "Retry-After": str(self.window_seconds)
            }
        )

class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Middleware for auditing security-sensitive operations."""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.sensitive_operations = {
            ("PATCH", "/users/.*/roles"): "ROLE_CHANGE",
            ("POST", "/email/send"): "EMAIL_SEND",
            ("DELETE", "/users/.*"): "USER_DELETE",
        }
        
    async def dispatch(self, request: Request, call_next):
        # Track original path and method for auditing
        path = request.url.path
        method = request.method
        
        # Process the request
        response = await call_next(request)
        
        # Check if this is a sensitive operation that needs auditing
        operation_type = None
        for (op_method, op_path), op_type in self.sensitive_operations.items():
            if method == op_method and self._path_matches(path, op_path):
                operation_type = op_type
                break
                
        if operation_type:
            # In a real implementation, log the operation to a secure audit log
            # This would include user info, timestamps, IP, etc.
            # For simplicity in this example, we'll just add an audit header
            response.headers["X-Audit-ID"] = f"{int(time.time())}-{operation_type}"
            
        return response
        
    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches a regex pattern."""
        import re
        return bool(re.match(f"^{pattern}$", path))

def add_security_middleware(app: FastAPI) -> None:
    """Add all security middleware to the application."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(SecurityAuditMiddleware) 