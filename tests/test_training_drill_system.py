"""
Unit tests for the BasketballTrainingSystem class
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from datetime import datetime

from services.training_drill_system import BasketballTrainingSystem


class TestBasketballTrainingSystem(unittest.TestCase):
    """Test cases for the BasketballTrainingSystem class."""
    
    def setUp(self):
        """Set up the test fixtures."""
        # Mock the file operations
        self.patcher = patch('os.path.exists')
        self.mock_exists = self.patcher.start()
        self.mock_exists.return_value = False
        
        self.system = BasketballTrainingSystem()
        
        # Sample drill for testing
        self.sample_drill = {
            "id": "D-001",
            "name": "3v2 Fast Break",
            "duration": 15,
            "category": ["Transition", "Offense"],
            "equipment": ["Cones", "Basketballs"],
            "description": "Offensive fast break drill with 3 attackers vs 2 defenders",
            "created_date": "2024-03-01",
            "usage_count": 5,
            "last_used": "2024-03-15"
        }
        
        # Add sample drill to the system
        self.system.saved_drills.append(self.sample_drill)

    def tearDown(self):
        """Tear down the test fixtures."""
        self.patcher.stop()

    def test_initialization(self):
        """Test that the system initializes correctly."""
        self.assertEqual(len(self.system.current_session), 0)
        self.assertEqual(len(self.system.unsaved_drills), 0)
        self.assertIsInstance(self.system.session_metadata, dict)
        self.assertIn("date", self.system.session_metadata)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_saved_drills(self, mock_json_load, mock_file_open):
        """Test loading drills from storage."""
        # Setup the mock
        self.mock_exists.return_value = True
        mock_drills = [
            {"id": "D-001", "name": "Test Drill", "duration": 30}
        ]
        mock_json_load.return_value = mock_drills
        
        # Create a new system which will trigger the load
        system = BasketballTrainingSystem()
        
        # Check that the mock was called correctly
        mock_file_open.assert_called_once_with("data/drills.json", "r")
        self.assertEqual(system.saved_drills, mock_drills)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('os.makedirs')
    def test_save_drills_to_storage(self, mock_makedirs, mock_json_dump, mock_file_open):
        """Test saving drills to storage."""
        self.system._save_drills_to_storage()
        
        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file_open.assert_called_once_with("data/drills.json", "w")
        mock_json_dump.assert_called_once()
        # Check that the first arg to json.dump was the saved_drills list
        self.assertEqual(mock_json_dump.call_args[0][0], self.system.saved_drills)

    def test_calculate_duration(self):
        """Test calculating the total session duration."""
        # Empty session
        self.assertEqual(self.system._calculate_duration(), 0)
        
        # Add some drills
        self.system.current_session = [
            {"name": "Drill 1", "duration": 15},
            {"name": "Drill 2", "duration": 20},
            {"name": "Drill 3", "duration": 10}
        ]
        
        self.assertEqual(self.system._calculate_duration(), 45)

    def test_get_category_counts(self):
        """Test counting drills by category."""
        # Setup test data
        self.system.saved_drills = [
            {"id": "D-001", "name": "Drill 1", "category": ["Shooting"]},
            {"id": "D-002", "name": "Drill 2", "category": ["Defense"]},
            {"id": "D-003", "name": "Drill 3", "category": ["Transition"]},
            {"id": "D-004", "name": "Drill 4", "category": ["Shooting", "Defense"]},
            {"id": "D-005", "name": "Drill 5", "category": ["Transition", "Defense"]}
        ]
        
        # Test counts
        shooting, defense, transition = self.system._get_category_counts()
        self.assertEqual(shooting, 2)
        self.assertEqual(defense, 3)
        self.assertEqual(transition, 2)

    @patch('builtins.input', side_effect=["Y"])
    def test_confirm_exit_with_session(self, mock_input):
        """Test confirming exit with active session."""
        self.system.current_session = [{"name": "Test Drill"}]
        result = self.system._confirm_exit()
        self.assertTrue(result)
        mock_input.assert_called_once()

    def test_confirm_exit_empty_session(self):
        """Test confirming exit with empty session."""
        self.system.current_session = []
        result = self.system._confirm_exit()
        self.assertTrue(result)

    def test_reset_session(self):
        """Test resetting the session state."""
        # Setup some data
        self.system.current_session = [{"name": "Test Drill"}]
        self.system.unsaved_drills = [{"name": "Unsaved Drill"}]
        self.system.session_metadata["coach"] = "Test Coach"
        
        # Reset
        self.system._reset_session()
        
        # Check results
        self.assertEqual(len(self.system.current_session), 0)
        self.assertEqual(len(self.system.unsaved_drills), 0)
        self.assertEqual(self.system.session_metadata["coach"], "")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('os.makedirs')
    def test_finalize_session(self, mock_makedirs, mock_json_dump, mock_file_open):
        """Test finalizing a session."""
        # Setup test data
        self.system.current_session = [
            {"id": "D-001", "name": "Test Drill", "duration": 30}
        ]
        self.system.session_metadata = {
            "date": "2024-03-20",
            "coach": "Test Coach",
            "team": "Test Team",
            "location": "Test Location"
        }
        
        # Finalize the session
        self.system._finalize_session()
        
        # Check that directories were created
        mock_makedirs.assert_called_with("data/sessions", exist_ok=True)
        
        # Check that the file was opened for writing
        self.assertTrue(mock_file_open.call_args[0][0].startswith("data/sessions/S-"))
        
        # Check that json.dump was called
        mock_json_dump.assert_called()
        
        # Check that the session data was correctly structured
        session_data = mock_json_dump.call_args[0][0]
        self.assertEqual(session_data["metadata"], self.system.session_metadata)
        self.assertEqual(session_data["drills"], self.system.current_session)
        self.assertEqual(session_data["total_duration"], 30)

    @patch('builtins.input', side_effect=["Key Player 1, Key Player 2", "Completion Time, Accuracy"])
    def test_save_drill_prompt(self, mock_input):
        """Test the drill saving prompt."""
        drill = self.sample_drill.copy()
        drill["id"] = "D-002"  # New ID
        
        # Add to unsaved drills
        self.system.unsaved_drills.append(drill)
        
        # Initial length of saved drills
        initial_count = len(self.system.saved_drills)
        
        # Call the method
        with patch.object(self.system, '_save_drills_to_storage') as mock_save:
            self.system._save_drill_prompt(drill)
            
            # Check that the drill was added to saved drills
            self.assertEqual(len(self.system.saved_drills), initial_count + 1)
            
            # Check that it was removed from unsaved drills
            self.assertNotIn(drill, self.system.unsaved_drills)
            
            # Check that the storage was updated
            mock_save.assert_called_once()
            
            # Check that the drill was properly updated
            saved_drill = self.system.saved_drills[-1]
            self.assertEqual(saved_drill["key_players"], ["Key Player 1", " Key Player 2"])
            self.assertEqual(saved_drill["success_metrics"], ["Completion Time", " Accuracy"])

    def test_save_all_drills(self):
        """Test saving all unsaved drills."""
        # Setup test data
        unsaved1 = {"id": "D-101", "name": "Unsaved 1", "duration": 15}
        unsaved2 = {"id": "D-102", "name": "Unsaved 2", "duration": 20}
        self.system.unsaved_drills = [unsaved1, unsaved2]
        
        # Initial saved count
        initial_count = len(self.system.saved_drills)
        
        # Call the method
        with patch.object(self.system, '_save_drills_to_storage') as mock_save:
            self.system._save_all_drills()
            
            # Check that all drills were saved
            self.assertEqual(len(self.system.saved_drills), initial_count + 2)
            
            # Check that unsaved list is empty
            self.assertEqual(len(self.system.unsaved_drills), 0)
            
            # Check that the storage was updated
            mock_save.assert_called_once()
            
            # Check that usage stats were updated
            for drill in self.system.saved_drills[-2:]:
                self.assertEqual(drill["usage_count"], 1)
                self.assertTrue("last_used" in drill)


if __name__ == '__main__':
    unittest.main() 