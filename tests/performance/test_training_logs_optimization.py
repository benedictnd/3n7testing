import pytest
import time
import json
import gzip
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from typing import Dict, List, Any
import asyncio

# Import the FastAPI app and relevant functions
from main import app
from routes.training import get_training_logs, get_cached_response, set_cached_response
from utils.compression import CompressionFormat, CompressionLevel, compress_json

# Create test client
client = TestClient(app)

@pytest.mark.performance
class TestTrainingLogsOptimization:
    """Test suite for verifying performance optimizations in the training logs endpoint"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock auth token
        self.auth_token = "mock_token"
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Sample test user
        self.test_user = {
            "id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete"
        }
        
        # Mock database session
        self.mock_db_session = MagicMock()
    
    @patch("routes.training.get_current_user")
    @patch("routes.training.get_db_session")
    def test_cache_hit_performance(self, mock_get_db, mock_get_user):
        """Test that cached responses are returned quickly without database queries"""
        # Setup mocks
        mock_get_user.return_value = self.test_user
        mock_get_db.return_value = self.mock_db_session
        
        # Mock the cache functions
        with patch("routes.training.get_cached_response") as mock_get_cache:
            # Prepare mock cache data
            mock_cache_data = {
                "logs": [{"id": f"log{i}", "user_id": "user123"} for i in range(10)],
                "total": 10,
                "limit": 50,
                "offset": 0
            }
            mock_get_cache.return_value = mock_cache_data
            
            # Make the request and measure time
            start_time = time.time()
            response = client.get(
                "/training/logs?limit=50", 
                headers=self.headers
            )
            execution_time = time.time() - start_time
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            assert "X-Cache" in response.headers
            assert response.headers["X-Cache"] == "HIT"
            assert mock_get_db.call_count == 1  # Called for dependency but not used
            assert self.mock_db_session.execute.call_count == 0  # No DB queries executed
            assert execution_time < 0.1  # Cache hit should be very fast (less than 100ms)
    
    @patch("routes.training.get_current_user")
    @patch("routes.training.get_db_session")
    def test_cache_miss_with_parallel_queries(self, mock_get_db, mock_get_user):
        """Test that database queries run in parallel on cache miss"""
        # Setup mocks
        mock_get_user.return_value = self.test_user
        mock_get_db.return_value = self.mock_db_session
        
        # Create a mock for the database execution with controlled timing
        async def mock_execute_slow(*args, **kwargs):
            # Simulate slow queries
            await asyncio.sleep(0.1)
            mock_result = MagicMock()
            # Different behavior based on the query
            if "COUNT" in str(args[0]):
                mock_result.scalar_one.return_value = 100
                return mock_result
            else:
                mock_result.fetchall.return_value = [MagicMock() for _ in range(10)]
                return mock_result
        
        self.mock_db_session.execute.side_effect = mock_execute_slow
        
        # Mock empty cache to force DB query
        with patch("routes.training.get_cached_response") as mock_get_cache, \
             patch("routes.training.set_cached_response") as mock_set_cache:
            mock_get_cache.return_value = None
            
            # Make the request and measure time
            start_time = time.time()
            response = client.get(
                "/training/logs?limit=50", 
                headers=self.headers
            )
            execution_time = time.time() - start_time
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            assert "X-Cache" in response.headers
            assert response.headers["X-Cache"] == "MISS"
            assert self.mock_db_session.execute.call_count == 2  # Two DB queries
            assert mock_set_cache.call_count == 1  # Cache was updated
            
            # The key optimization: parallel queries should take ~0.1s, not ~0.2s
            # Allow some overhead for processing
            assert execution_time < 0.2
    
    @patch("routes.training.get_current_user")
    @patch("routes.training.get_db_session")
    def test_compression_applied(self, mock_get_db, mock_get_user):
        """Test that large responses are compressed when clients support it"""
        # Setup mocks
        mock_get_user.return_value = self.test_user
        mock_get_db.return_value = self.mock_db_session
        
        # Create mock for large dataset
        async def mock_execute_large_dataset(*args, **kwargs):
            mock_result = MagicMock()
            if "COUNT" in str(args[0]):
                mock_result.scalar_one.return_value = 1000
                return mock_result
            else:
                # Create many mock logs to ensure large response size
                logs = []
                for i in range(50):
                    log = MagicMock()
                    log.id = f"log{i}"
                    log.user_id = "user123"
                    log.session_id = f"session{i % 5}"
                    log.log_type = "activity"
                    log.data = {"details": "a" * 100}  # Add large data
                    log.created_at.isoformat.return_value = f"2024-05-{i % 30 + 1}T10:00:00"
                    logs.append(log)
                mock_result.fetchall.return_value = logs
                return mock_result
        
        self.mock_db_session.execute.side_effect = mock_execute_large_dataset
        
        # Mock empty cache
        with patch("routes.training.get_cached_response") as mock_get_cache, \
             patch("routes.training.set_cached_response") as mock_set_cache:
            mock_get_cache.return_value = None
            
            # Make request with gzip support
            response = client.get(
                "/training/logs?limit=50", 
                headers={**self.headers, "Accept-Encoding": "gzip"}
            )
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            assert "Content-Encoding" in response.headers
            assert response.headers["Content-Encoding"] == "gzip"
            
            # Decompress to verify content is correct
            decompressed_data = json.loads(gzip.decompress(response.content))
            assert "logs" in decompressed_data
            assert len(decompressed_data["logs"]) == 50
            assert "compression_applied" in decompressed_data
            assert decompressed_data["compression_applied"] is True
            
            # Verify compression ratio
            original_size = len(json.dumps(decompressed_data).encode('utf-8'))
            compressed_size = len(response.content)
            compression_ratio = compressed_size / original_size
            assert compression_ratio < 0.5  # At least 50% reduction
    
    @patch("routes.training.get_current_user")
    def test_index_used_with_session_filter(self, mock_get_user):
        """Test that the composite index is used when filtering by session_id"""
        # This test is more of an integration test that requires DB access
        # Just verify that the query is formed correctly with the right hints
        mock_get_user.return_value = {"id": "user123", "role": "athlete"}
        
        # Extract the SQL query without executing it
        with patch("routes.training.AsyncSession.execute") as mock_execute:
            # Make the request
            client.get(
                "/training/logs?session_id=session123",
                headers=self.headers
            )
            
            # Get the SQL for the data query (second call)
            calls = mock_execute.call_args_list
            assert len(calls) >= 2
            sql_query = str(calls[1][0][0])
            
            # Verify index hint is included for session_id filter
            assert "/*+ INDEX" in sql_query or "INDEX(tl training_logs_user_session_idx)" in sql_query
            assert "session_id = :session_id" in sql_query
            assert "ORDER BY tl.created_at DESC" in sql_query
    
    def test_load_simulation(self):
        """Simulate load to measure actual throughput improvement"""
        # Skip this test in CI environment
        pytest.skip("This test should be run manually in a local environment")
        
        # Setup authentication 
        response = client.post(
            "/auth/login", 
            json={"email": "test@example.com", "password": "password123"}
        )
        auth_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Run 100 requests and measure throughput
        start_time = time.time()
        success_count = 0
        
        for _ in range(100):
            try:
                response = client.get("/training/logs?limit=50", headers=headers)
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass
        
        total_time = time.time() - start_time
        requests_per_second = success_count / total_time
        
        # Log results
        print(f"Throughput: {requests_per_second:.2f} requests per second")
        print(f"Success rate: {success_count}%")
        
        # Check minimum throughput meets requirements
        assert requests_per_second > 30  # Should exceed 30 req/sec
        assert success_count >= 95       # 95% success rate minimum 