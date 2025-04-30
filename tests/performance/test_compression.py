"""
Tests for the compression implementation in the 3&7 Training Platform API.
"""

import pytest
import requests
import gzip
import zlib
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

@pytest.mark.performance
class TestCompression:
    """Test suite for the compression functionality"""
    
    def setup_method(self):
        """Setup the test environment"""
        self.base_url = BASE_URL
        self.token = None
        
        # Authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with the API to get a token"""
        try:
            auth_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            else:
                print(f"Authentication failed: {response.status_code}")
                self.headers = {}
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            self.headers = {}
    
    def test_compression_gzip_supported(self):
        """Test that responses are compressed with gzip when supported"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
        
        # Request with gzip encoding support
        headers = {**self.headers, "Accept-Encoding": "gzip"}
        
        # Make a request that should return a large response
        response = requests.get(
            f"{self.base_url}/training/logs?limit=100",
            headers=headers
        )
        
        # Check that compression was applied
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert "content-encoding" in response.headers, "No content-encoding header found"
        assert response.headers["content-encoding"] == "gzip", "Expected gzip encoding"
        
        # Check compression rate header
        assert "x-compression-rate" in response.headers, "No compression rate header found"
        compression_rate = float(response.headers["x-compression-rate"].rstrip("%"))
        assert compression_rate > 0, "Compression rate should be greater than 0"
        
        # Verify the content was correctly decompressed by requests
        data = response.json()
        assert "logs" in data, "Expected logs field in response"
    
    def test_compression_deflate_supported(self):
        """Test that responses are compressed with deflate when supported"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
        
        # Request with deflate encoding support
        headers = {**self.headers, "Accept-Encoding": "deflate"}
        
        # Make a request that should return a large response
        response = requests.get(
            f"{self.base_url}/training/logs?limit=100",
            headers=headers
        )
        
        # Check that compression was applied
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert "content-encoding" in response.headers, "No content-encoding header found"
        assert response.headers["content-encoding"] == "deflate", "Expected deflate encoding"
        
        # Check compression rate header
        assert "x-compression-rate" in response.headers, "No compression rate header found"
        compression_rate = float(response.headers["x-compression-rate"].rstrip("%"))
        assert compression_rate > 0, "Compression rate should be greater than 0"
        
        # Verify the content was correctly decompressed by requests
        data = response.json()
        assert "logs" in data, "Expected logs field in response"
    
    def test_no_compression_when_not_supported(self):
        """Test that responses are not compressed when compression not supported"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
        
        # Request without compression support
        headers = {**self.headers, "Accept-Encoding": "identity"}
        
        # Make a request that should return a large response
        response = requests.get(
            f"{self.base_url}/training/logs?limit=100",
            headers=headers
        )
        
        # Check that compression was not applied
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert "content-encoding" not in response.headers, "Unexpected content-encoding header found"
        
        # Verify the content is valid JSON
        data = response.json()
        assert "logs" in data, "Expected logs field in response"
    
    def test_compression_size_threshold(self):
        """Test that small responses are not compressed"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
        
        # Request with gzip encoding support
        headers = {**self.headers, "Accept-Encoding": "gzip"}
        
        # Make a request that should return a small response
        response = requests.get(
            f"{self.base_url}/health",
            headers=headers
        )
        
        # Check that compression was not applied due to small size
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert "content-encoding" not in response.headers, "Unexpected content-encoding header found"
        
        # Verify the content is valid JSON
        data = response.json()
        assert "status" in data, "Expected status field in response"
    
    def test_compression_performance(self):
        """Test that compression improves performance for large responses"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
        
        # Make request with compression
        headers_with_compression = {**self.headers, "Accept-Encoding": "gzip"}
        response_compressed = requests.get(
            f"{self.base_url}/training/logs?limit=100",
            headers=headers_with_compression
        )
        
        # Make same request without compression
        headers_without_compression = {**self.headers, "Accept-Encoding": "identity"}
        response_uncompressed = requests.get(
            f"{self.base_url}/training/logs?limit=100",
            headers=headers_without_compression
        )
        
        # Get the compressed response size (from Content-Length header or actual content)
        compressed_size = int(response_compressed.headers.get("content-length", len(response_compressed.content)))
        
        # Get the uncompressed response size
        uncompressed_size = int(response_uncompressed.headers.get("content-length", len(response_uncompressed.content)))
        
        # Check that compressed size is smaller
        assert compressed_size < uncompressed_size, "Compressed response should be smaller than uncompressed response"
        
        # Calculate compression ratio
        compression_ratio = (uncompressed_size - compressed_size) / uncompressed_size * 100
        print(f"Compression ratio: {compression_ratio:.1f}%")
        
        # Compression should save significant bandwidth
        assert compression_ratio > 50, "Compression should save at least 50% bandwidth"