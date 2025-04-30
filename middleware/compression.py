"""
Compression middleware for the 3&7 Training Platform API.

This middleware automatically applies compression to API responses
when appropriate based on response size and client capabilities.
"""

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any, Optional
import gzip
import zlib
import json
import logging

from utils.compression import (
    CompressionFormat,
    CompressionLevel,
    get_client_supported_compression,
    should_compress
)

logger = logging.getLogger(__name__)

class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware that compresses API responses based on client capabilities and response size."""
    
    def __init__(
        self, 
        app: FastAPI, 
        compression_threshold: int = 1024,  # 1KB default threshold
        minimum_size: int = 256,  # Don't compress very small responses
        default_level: int = CompressionLevel.DEFAULT,
        excluded_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.compression_threshold = compression_threshold
        self.minimum_size = minimum_size
        self.compression_level = default_level
        self.excluded_paths = excluded_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        logger.info(f"Compression middleware initialized with threshold: {compression_threshold} bytes")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and apply compression to the response if appropriate."""
        
        # Skip compression for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Get the accept-encoding header
        accept_encoding = request.headers.get("accept-encoding", "")
        compression_format = get_client_supported_compression(accept_encoding)
        
        # If client doesn't support compression, skip compression
        if compression_format == CompressionFormat.NONE:
            return await call_next(request)
        
        # Process the request
        response = await call_next(request)
        
        # Skip compression for responses with content-encoding already set
        if "content-encoding" in response.headers:
            return response
            
        # Skip compression for non-JSON responses
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response
            
        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Check if response should be compressed
        if not should_compress(len(response_body), self.compression_threshold) or len(response_body) < self.minimum_size:
            # Return uncompressed response with original body
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
        # Apply compression
        try:
            if compression_format == CompressionFormat.GZIP:
                compressed_body = gzip.compress(response_body, self.compression_level)
                encoding = "gzip"
            elif compression_format == CompressionFormat.DEFLATE:
                compressed_body = zlib.compress(response_body, self.compression_level)
                encoding = "deflate"
            else:
                # This shouldn't happen, but just in case
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                
            # Calculate compression rate for logging
            original_size = len(response_body)
            compressed_size = len(compressed_body)
            reduction = (original_size - compressed_size) / original_size * 100
            
            logger.debug(
                f"Compressed response: {request.method} {request.url.path} - "
                f"{original_size} → {compressed_size} bytes "
                f"({reduction:.1f}% reduction)"
            )
            
            # Create new response with compressed body
            headers = dict(response.headers)
            headers["content-encoding"] = encoding
            headers["X-Compression-Rate"] = f"{reduction:.1f}%"
            
            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type
            )
            
        except Exception as e:
            # Log error and fall back to uncompressed response
            logger.error(f"Compression error: {str(e)}")
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
# Function to add compression middleware to FastAPI app
def add_compression_middleware(
    app: FastAPI,
    compression_threshold: int = 1024,
    default_level: int = CompressionLevel.DEFAULT
) -> None:
    """Add compression middleware to the FastAPI application"""
    app.add_middleware(
        CompressionMiddleware,
        compression_threshold=compression_threshold,
        default_level=default_level
    )
    logger.info("Compression middleware added to application") 