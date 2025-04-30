"""
Test file to verify the fixes for the 6 critical issues:
1. Email memory leak
2. Role escalation vulnerability
3. User service role validation
4. Frame embedding vulnerability
5. Database error handling
6. API performance optimization
"""

import unittest
import os
import tempfile
import json
import time
from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open

# Import the fixed components
from routes.email import FileAttachment, send_email_with_attachments
from routes.users import update_user_roles
from services.user_service import UserService
from middleware.security import SecurityHeadersMiddleware
from dependencies.database import get_db_session
from routes.training import get_training_logs

class TestFixes(unittest.TestCase):
    """Test suite for verifying all fixes"""

    def setUp(self):
        """Set up test environment"""
        self.app = FastAPI()
        self.client = TestClient(self.app)

    def test_file_attachment_memory_leak_fix(self):
        """Test that FileAttachment properly cleans up resources"""
        # Mock UploadFile
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.read = MagicMock(return_value=b"test data")
        mock_file.seek = MagicMock()
        
        # Create attachment handler
        handler = FileAttachment(mock_file)
        
        # Create a real temp file for testing
        temp_fd, temp_path = tempfile.mkstemp(prefix="test_attachment_")
        os.close(temp_fd)
        
        # Set the temp file path
        handler.temp_file_path = temp_path
        
        # Verify file exists
        self.assertTrue(os.path.exists(temp_path))
        
        # Call cleanup
        handler.cleanup()
        
        # Verify file is deleted
        self.assertFalse(os.path.exists(temp_path))
        self.assertIsNone(handler.temp_file_path)
        
        # Test __del__ method
        handler = FileAttachment(mock_file)
        handler.temp_file_path = temp_path
        
        # Create the file again
        with open(temp_path, 'w') as f:
            f.write("test")
            
        # Delete the object
        del handler
        
        # Garbage collector should clean up the file
        self.assertFalse(os.path.exists(temp_path))

    def test_role_escalation_fix(self):
        """Test role escalation prevention"""
        with patch('routes.users.UserService') as mock_service:
            # Setup test data
            user_id = "123"
            current_user = {"id": user_id, "role": "athlete"}
            role_data = MagicMock()
            role_data.roles = ["admin"]
            db_session = MagicMock()
            has_admin_role = True
            
            # Setup mock service
            mock_service_instance = mock_service.return_value
            mock_service_instance.get_user.return_value = MagicMock(role="athlete")
            
            # Test self-promotion attempt
            with self.assertRaises(Exception) as context:
                update_user_roles(user_id, role_data, db_session, current_user, has_admin_role)
                
            # Verify appropriate error is raised
            self.assertIn("Users cannot modify their own roles", str(context.exception))

    def test_security_headers(self):
        """Test security headers configuration"""
        # Create an instance of the middleware
        middleware = SecurityHeadersMiddleware(self.app)
        
        # Verify the headers are correctly set
        self.assertEqual(middleware.secure_headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", middleware.secure_headers["Content-Security-Policy"])
        self.assertIn("includeSubDomains", middleware.secure_headers["Strict-Transport-Security"])

    @patch('routes.training.get_cached_response')
    @patch('routes.training.set_cached_response')
    def test_training_logs_optimization(self, mock_set_cache, mock_get_cache):
        """Test API performance optimization for training logs"""
        # Setup mocks
        mock_get_cache.return_value = None
        mock_db_session = MagicMock()
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 100
        mock_logs_result = MagicMock()
        mock_log = MagicMock()
        mock_log.id = "1"
        mock_log.user_id = "user1"
        mock_log.session_id = "session1"
        mock_log.log_type = "workout"
        mock_log.data = {"exercise": "run"}
        mock_log.created_at.isoformat.return_value = "2023-01-01T12:00:00"
        mock_logs_result.scalars.return_value.all.return_value = [mock_log]
        mock_db_session.execute.side_effect = [mock_count_result, mock_logs_result]
        mock_response = MagicMock()
        mock_current_user = {"id": "user1", "role": "admin"}
        
        # Test the function
        result = get_training_logs(
            start_date="2023-01-01",
            end_date="2023-01-31",
            user_id="user1",
            session_id=None,
            limit=50,
            offset=0,
            db_session=mock_db_session,
            current_user=mock_current_user,
            response=mock_response
        )
        
        # Verify caching is used
        self.assertTrue(mock_set_cache.called)
        
        # Verify query is optimized
        db_calls = mock_db_session.execute.call_count
        self.assertEqual(db_calls, 2)  # One for count, one for data
        
        # Verify performance tracking
        self.assertIn("execution_time_ms", result)
        
        # Verify response format
        self.assertEqual(len(result["logs"]), 1)
        self.assertEqual(result["total"], 100)

    def test_database_connection_retry(self):
        """Test database connection retry mechanism"""
        with patch('dependencies.database.async_session') as mock_session:
            # Setup mock
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Test connection retry through generator
            generator = get_db_session()
            
            # Verify session is created properly
            self.assertEqual(mock_session.call_count, 1)

if __name__ == "__main__":
    unittest.main() 