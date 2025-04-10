from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to every response"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)
        
        # Add security headers to the response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Only add HSTS header for HTTPS requests
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add a basic Content Security Policy
        # This can be customized based on your application's needs
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'"
        
        # Add an explicit content type if not already set
        if "Content-Type" not in response.headers and request.url.path.startswith("/api"):
            response.headers["Content-Type"] = "application/json"
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware (in-memory implementation)"""
    
    def __init__(self, app: FastAPI, rate_limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit  # Requests per window
        self.window_seconds = window_seconds  # Window size in seconds
        self.clients = {}  # In-memory storage of client requests
        
        # For production, use a distributed cache like Redis instead of in-memory dictionary
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address for simplicity)
        client_ip = request.client.host
        
        # Skip rate limiting for certain paths
        if request.url.path == "/health" or request.url.path == "/":
            return await call_next(request)
        
        # Get current timestamp
        import time
        current_time = int(time.time())
        
        # Initialize or clean up old requests
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Remove requests outside the current window
        window_start = current_time - self.window_seconds
        self.clients[client_ip] = [timestamp for timestamp in self.clients[client_ip] if timestamp > window_start]
        
        # Check if client exceeded rate limit
        if len(self.clients[client_ip]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(window_start + self.window_seconds)
                }
            )
        
        # Add current request timestamp
        self.clients[client_ip].append(current_time)
        
        # Add rate limit headers to the response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(self.rate_limit - len(self.clients[client_ip]))
        response.headers["X-RateLimit-Reset"] = str(window_start + self.window_seconds)
        
        return response


def add_security_middleware(app: FastAPI) -> None:
    """Add security middlewares to the FastAPI application"""
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add rate limiting with a limit of 120 requests per minute by default
    app.add_middleware(RateLimitingMiddleware, rate_limit=120, window_seconds=60)
    
    logger.info("Security middlewares added to the application") 