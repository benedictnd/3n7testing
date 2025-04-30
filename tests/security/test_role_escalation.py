import pytest
import requests
import json
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup test configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password123")

@pytest.mark.security
class TestRoleEscalation:
    """Tests for the role escalation vulnerability and fix"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.base_url = BASE_URL
        self.token = None
        self.headers = {}
        self.user = {}
        
        # Authenticate
        self._authenticate()
        
    def _authenticate(self) -> bool:
        """Authenticate with the API to get a token"""
        try:
            logger.info(f"Authenticating as {TEST_EMAIL}")
            
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user = data.get("user", {})
                self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                logger.info(f"Authenticated as user with role: {self.user.get('role')}")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
            
    def test_me_roles_endpoint_blocked(self):
        """Test if the /users/me/roles endpoint blocks role changes"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
        
        # Try to promote self to admin role
        role_update = {
            "roles": ["admin"]
        }
        
        logger.info("Attempting to update own role to admin via /users/me/roles")
        
        # Send request to update roles via /me/ endpoint
        response = requests.patch(
            f"{self.base_url}/users/me/roles",
            json=role_update,
            headers=self.headers
        )
        
        # Should be blocked completely
        assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
        logger.info("Self role update properly blocked at the /me/roles endpoint")
            
    def test_role_escalation_vulnerability(self):
        """Test if a user can escalate their own role by directly accessing their user ID endpoint"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
            
        # Get current user ID
        user_id = self.user.get("id")
        if not user_id:
            pytest.skip("Could not get user ID, skipping test")
            
        # Try to promote self to admin role
        role_update = {
            "roles": ["admin"]
        }
        
        logger.info(f"Attempting to update own role to admin via /users/{user_id}/roles")
        
        # Send request to update roles
        response = requests.patch(
            f"{self.base_url}/users/{user_id}/roles",
            json=role_update,
            headers=self.headers
        )
        
        # This should be blocked (403 Forbidden)
        assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
        logger.info("Self role promotion properly blocked")
        
        # Verify role hasn't changed
        me_response = requests.get(
            f"{self.base_url}/users/me",
            headers=self.headers
        )
        
        assert me_response.status_code == 200, "Failed to get current user profile"
        current_role = me_response.json().get("role")
        assert current_role != "admin", f"Role should not be admin, but got {current_role}"
        logger.info(f"Current role is still {current_role} - no escalation occurred")
            
    def test_admin_can_change_others_roles(self):
        """Test that admins can still change other users' roles"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
            
        # Skip if not admin
        if self.user.get("role") != "admin":
            pytest.skip("Test requires admin role, skipping")
            
        # Get a different user to update
        users_response = requests.get(
            f"{self.base_url}/users?limit=5",
            headers=self.headers
        )
        
        if users_response.status_code != 200:
            pytest.skip(f"Could not get users list: {users_response.status_code}, skipping test")
            
        users = users_response.json().get("users", [])
        other_user = None
        
        # Find a non-admin user that is not the current user
        for user in users:
            if user.get("id") != self.user.get("id") and user.get("role") != "admin":
                other_user = user
                break
                
        if not other_user:
            pytest.skip("No suitable user found to modify, skipping test")
            
        other_user_id = other_user.get("id")
        current_role = other_user.get("role")
        
        # Choose a role different from current but not higher than admin
        new_role = "athlete" if current_role != "athlete" else "coach"
        
        role_update = {
            "roles": [new_role]
        }
        
        logger.info(f"Admin attempting to change user {other_user_id} from {current_role} to {new_role}")
        
        # Send request to update roles
        response = requests.patch(
            f"{self.base_url}/users/{other_user_id}/roles",
            json=role_update,
            headers=self.headers
        )
        
        # Should succeed for admin changing another user
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code} with body: {response.text}"
        logger.info(f"Admin successfully changed other user's role")
        
        # Verify role was changed
        user_response = requests.get(
            f"{self.base_url}/users/{other_user_id}",
            headers=self.headers
        )
        
        assert user_response.status_code == 200, f"Failed to get user profile: {user_response.status_code}"
        updated_role = user_response.json().get("role")
        assert updated_role == new_role, f"Role should be {new_role}, but got {updated_role}"
        
        # Revert the change
        revert_update = {
            "roles": [current_role]
        }
        
        revert_response = requests.patch(
            f"{self.base_url}/users/{other_user_id}/roles",
            json=revert_update,
            headers=self.headers
        )
        
        if revert_response.status_code != 200:
            logger.warning(f"Failed to revert role change: {revert_response.status_code}")
            
    def test_higher_privilege_restriction(self):
        """Test that users cannot assign roles with higher privileges than their own"""
        if not self.token:
            pytest.skip("Authentication failed, skipping test")
            
        # This test requires a user with coach or athlete role
        if self.user.get("role") not in ["coach", "athlete"]:
            pytest.skip("Test requires non-admin role, skipping")
        
        # Get a different user to update
        users_response = requests.get(
            f"{self.base_url}/users?limit=5",
            headers=self.headers
        )
        
        if users_response.status_code != 200:
            pytest.skip(f"Could not get users list: {users_response.status_code}, skipping test")
            
        users = users_response.json().get("users", [])
        other_user = None
        
        # Find another user that is not the current user
        for user in users:
            if user.get("id") != self.user.get("id"):
                other_user = user
                break
                
        if not other_user:
            pytest.skip("No other user found, skipping test")
            
        other_user_id = other_user.get("id")
        
        # Try to promote the other user to admin (which should be denied)
        role_update = {
            "roles": ["admin"]
        }
        
        logger.info(f"Non-admin attempting to assign admin role to user {other_user_id}")
        
        # Send request to update roles
        response = requests.patch(
            f"{self.base_url}/users/{other_user_id}/roles",
            json=role_update,
            headers=self.headers
        )
        
        # Should be denied for non-admin trying to assign higher privileges
        assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
        logger.info("Higher privilege assignment properly blocked")

if __name__ == "__main__":
    pytest.main(["-v", __file__])