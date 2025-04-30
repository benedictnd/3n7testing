"""
Response compression utility for the 3&7 Training Platform API.

This module provides compression utilities to reduce response payload size
for large responses, improving network performance and reducing bandwidth usage.
"""

import gzip
import json
import zlib
from typing import Dict, Any, Union, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CompressionFormat(str, Enum):
    """Supported compression formats"""
    GZIP = "gzip"
    DEFLATE = "deflate"
    NONE = "none"

class CompressionLevel(int, Enum):
    """Compression levels from 0 (no compression) to 9 (max compression)"""
    NONE = 0
    FAST = 1
    DEFAULT = 6
    BEST = 9

def compress_json(data: Union[Dict[str, Any], List[Any]], 
                  format: CompressionFormat = CompressionFormat.GZIP,
                  level: CompressionLevel = CompressionLevel.DEFAULT) -> bytes:
    """
    Compress JSON data using the specified format and compression level
    
    Args:
        data: The JSON data to compress
        format: Compression format (gzip or deflate)
        level: Compression level from 0-9
        
    Returns:
        Compressed bytes
    """
    # Convert data to JSON string
    json_str = json.dumps(data).encode('utf-8')
    original_size = len(json_str)
    
    # No compression requested
    if format == CompressionFormat.NONE or level == CompressionLevel.NONE:
        return json_str
    
    try:
        # Apply compression
        if format == CompressionFormat.GZIP:
            compressed = gzip.compress(json_str, level)
        elif format == CompressionFormat.DEFLATE:
            compressed = zlib.compress(json_str, level)
        else:
            return json_str
            
        compressed_size = len(compressed)
        compression_ratio = (original_size - compressed_size) / original_size * 100
        
        logger.debug(
            f"Compressed data: {original_size} → {compressed_size} bytes "
            f"({compression_ratio:.1f}% reduction)"
        )
        
        return compressed
    except Exception as e:
        logger.error(f"Compression error: {str(e)}")
        return json_str

def should_compress(data_size: int, threshold: int = 1024) -> bool:
    """
    Determine if data should be compressed based on size
    
    Args:
        data_size: Size of data in bytes
        threshold: Minimum size threshold for compression (default: 1KB)
        
    Returns:
        True if data should be compressed, False otherwise
    """
    return data_size >= threshold

def get_client_supported_compression(accept_encoding: Optional[str]) -> CompressionFormat:
    """
    Determine the best compression format supported by the client
    
    Args:
        accept_encoding: Accept-Encoding header from the client
        
    Returns:
        The best supported compression format
    """
    if not accept_encoding:
        return CompressionFormat.NONE
        
    accept_encoding = accept_encoding.lower()
    
    if "gzip" in accept_encoding:
        return CompressionFormat.GZIP
    elif "deflate" in accept_encoding:
        return CompressionFormat.DEFLATE
    else:
        return CompressionFormat.NONE 