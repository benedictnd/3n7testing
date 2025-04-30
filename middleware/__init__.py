"""
Security and performance middlewares for the 3&7 Training Platform API
"""

from middleware.security import SecurityHeadersMiddleware, RateLimitingMiddleware, add_security_middleware
from middleware.compression import CompressionMiddleware, add_compression_middleware

__all__ = [
    'SecurityHeadersMiddleware',
    'RateLimitingMiddleware',
    'CompressionMiddleware',
    'add_security_middleware',
    'add_compression_middleware',
] 