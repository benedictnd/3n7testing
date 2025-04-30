from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
import uuid
import os

from models.training import TrainingSession, TrainingSessionCreate, TrainingSessionBase
from models.coach_assignment import CoachAssignment
from utils.json_handler import JsonHandler

class JsonTrainingService:
    """Service for training management using JSON storage"""
    
    def __init__(self, json_handler: Optional[JsonHandler] = None):
        """Initialize with a json_handler or create a new one"""
        self.json_handler = json_handler or JsonHandler()
        self.trainings_file = "trainings.json"
        self.coaches_file = "coaches.json"
        
    def get_training_sessions(self, 
                             team_id: Optional[str] = None, 
                             limit: int = 100,
                             offset: int = 0) -> List[Dict]:
        """
        Get training sessions, optionally filtered by team
        
        Args:
            team_id: Optional team ID to filter by
            limit: Maximum number of sessions to return
            offset: Offset for pagination
            
        Returns:
            List of training sessions matching the criteria
        """
        trainings = self.json_handler.get_all_json_items(self.trainings_file, "trainings")
        
        if team_id:
            trainings = [t for t in trainings if t.get("team_id") == team_id]
            
        # Apply pagination
        paginated = trainings[offset:offset + limit]
        
        return paginated
    
    def get_training_session(self, session_id: str) -> Optional[Dict]:
        """
        Get a training session by ID
        
        Args:
            session_id: ID of the training session to retrieve
            
        Returns:
            Training session if found, None otherwise
        """
        trainings = self.json_handler.get_all_json_items(self.trainings_file, "trainings")
        
        for training in trainings:
            if training.get("id") == session_id:
                return training
                
        return None
    
    def create_training_session(self, session_data: Dict[str, Any]) -> Dict:
        """
        Create a new training session
        
        Args:
            session_data: Data for the new training session
            
        Returns:
            Created training session
        """
        # Validate required fields
        required_fields = ["date", "session_type", "drills", "team_id"]
        for field in required_fields:
            if field not in session_data:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate coaches assignment - at least one coach required
        if "coaches_assigned" not in session_data or not session_data["coaches_assigned"]:
            raise ValueError("At least one coach must be assigned to the session")
            
        # Generate ID if not provided
        if "id" not in session_data:
            session_data["id"] = f"training-{uuid.uuid4()}"
            
        # Add timestamp
        current_time = datetime.now().isoformat()
        session_data["created_at"] = current_time
        session_data["updated_at"] = current_time
        
        # Save to JSON
        self.json_handler.append_to_json_array(self.trainings_file, "trainings", session_data)
        
        return session_data
    
    def update_training_session(self, 
                              session_id: str, 
                              session_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update a training session
        
        Args:
            session_id: ID of the session to update
            session_data: Updated data for the session
            
        Returns:
            Updated training session or None if not found
        """
        # Get existing session
        existing_session = self.get_training_session(session_id)
        if not existing_session:
            return None
            
        # Update fields
        updated_session = {**existing_session, **session_data}
        
        # Validate coaches assignment - at least one coach required
        if "coaches_assigned" in updated_session and not updated_session["coaches_assigned"]:
            raise ValueError("At least one coach must be assigned to the session")
            
        # Update timestamp
        updated_session["updated_at"] = datetime.now().isoformat()
        
        # Save to JSON
        success = self.json_handler.update_json_item(
            self.trainings_file, "trainings", session_id, updated_session
        )
        
        return updated_session if success else None
    
    def delete_training_session(self, session_id: str) -> bool:
        """
        Delete a training session
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if successfully deleted, False otherwise
        """
        return self.json_handler.delete_json_item(self.trainings_file, "trainings", session_id)
    
    def get_available_coaches(self) -> List[Dict]:
        """
        Get all available coaches
        
        Returns:
            List of coaches
        """
        return self.json_handler.get_all_json_items(self.coaches_file, "coaches")
    
    def get_coach_by_id(self, coach_id: str) -> Optional[Dict]:
        """
        Get a coach by ID
        
        Args:
            coach_id: ID of the coach to retrieve
            
        Returns:
            Coach if found, None otherwise
        """
        return self.json_handler.get_json_item_by_id(self.coaches_file, "coaches", coach_id)
    
    def assign_coaches_to_session(self, 
                                session_id: str, 
                                coach_assignments: List[Dict]) -> Optional[Dict]:
        """
        Assign coaches to a training session
        
        Args:
            session_id: ID of the session to update
            coach_assignments: List of coach assignments with coach_id, name, and role
            
        Returns:
            Updated training session or None if not found
        """
        # Validate coaches
        if not coach_assignments:
            raise ValueError("At least one coach must be assigned to the session")
            
        # Get existing session
        existing_session = self.get_training_session(session_id)
        if not existing_session:
            return None
            
        # Update coaches assigned
        existing_session["coaches_assigned"] = coach_assignments
        existing_session["updated_at"] = datetime.now().isoformat()
        
        # Save to JSON
        success = self.json_handler.update_json_item(
            self.trainings_file, "trainings", session_id, existing_session
        )
        
        return existing_session if success else None
