from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

from models.health_observation import HealthObservation
from utils.json_handler import JsonHandler

class JsonFeedbackService:
    """Service for feedback management using JSON storage"""
    
    def __init__(self, json_handler: Optional[JsonHandler] = None):
        """Initialize with a json_handler or create a new one"""
        self.json_handler = json_handler or JsonHandler()
        self.feedback_file = "feedback.json"
        
    def get_all_feedback(self, training_id: Optional[str] = None) -> List[Dict]:
        """
        Get all feedback, optionally filtered by training
        
        Args:
            training_id: Optional training ID to filter by
            
        Returns:
            List of feedback matching the criteria
        """
        feedbacks = self.json_handler.get_all_json_items(self.feedback_file, "feedback")
        
        if training_id:
            feedbacks = [f for f in feedbacks if f.get("training_id") == training_id]
            
        return feedbacks
    
    def get_feedback_by_id(self, feedback_id: str) -> Optional[Dict]:
        """
        Get feedback by ID
        
        Args:
            feedback_id: ID of the feedback to retrieve
            
        Returns:
            Feedback if found, None otherwise
        """
        return self.json_handler.get_json_item_by_id(self.feedback_file, "feedback", feedback_id)
    
    def create_feedback(self, feedback_data: Dict[str, Any]) -> Dict:
        """
        Create new feedback for a training session
        
        Args:
            feedback_data: Data for the new feedback
            
        Returns:
            Created feedback
        """
        # Validate required fields
        required_fields = ["training_id", "submitted_by", "quality_rating"]
        for field in required_fields:
            if field not in feedback_data:
                raise ValueError(f"Missing required field: {field}")
                
        # Generate ID if not provided
        if "id" not in feedback_data:
            feedback_data["id"] = f"feedback-{uuid.uuid4()}"
            
        # Add timestamp if not provided
        if "timestamp" not in feedback_data:
            feedback_data["timestamp"] = datetime.now().isoformat()
        
        # Validate health observation data
        if "health_observation" in feedback_data and feedback_data["health_observation"] is not None:
            # Ensure at least one fatigue or injury is reported
            health_obs = feedback_data["health_observation"]
            has_fatigue = "fatigue" in health_obs and health_obs["fatigue"]
            has_injuries = "injuries" in health_obs and health_obs["injuries"]
            
            if not has_fatigue and not has_injuries:
                raise ValueError("Health observation must contain at least one fatigue or injury report")
        
        # Check for injuries to trigger alerts
        self._check_injuries(feedback_data)
            
        # Save to JSON
        self.json_handler.append_to_json_array(self.feedback_file, "feedback", feedback_data)
        
        return feedback_data
    
    def update_feedback(self, feedback_id: str, feedback_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update existing feedback
        
        Args:
            feedback_id: ID of the feedback to update
            feedback_data: Updated data for the feedback
            
        Returns:
            Updated feedback or None if not found
        """
        # Get existing feedback
        existing_feedback = self.get_feedback_by_id(feedback_id)
        if not existing_feedback:
            return None
            
        # Update fields
        updated_feedback = {**existing_feedback, **feedback_data}
        
        # Validate health observation data if present
        if "health_observation" in updated_feedback and updated_feedback["health_observation"] is not None:
            # Ensure at least one fatigue or injury is reported
            health_obs = updated_feedback["health_observation"]
            has_fatigue = "fatigue" in health_obs and health_obs["fatigue"]
            has_injuries = "injuries" in health_obs and health_obs["injuries"]
            
            if not has_fatigue and not has_injuries:
                raise ValueError("Health observation must contain at least one fatigue or injury report")
        
        # Check for injuries to trigger alerts
        self._check_injuries(updated_feedback)
        
        # Save to JSON
        success = self.json_handler.update_json_item(
            self.feedback_file, "feedback", feedback_id, updated_feedback
        )
        
        return updated_feedback if success else None
    
    def set_health_observation(self, 
                            feedback_id: str, 
                            observation_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Set the health observation for existing feedback
        
        Args:
            feedback_id: ID of the feedback to update
            observation_data: Data for the health observation
            
        Returns:
            Updated feedback or None if not found
        """
        # Get existing feedback
        existing_feedback = self.get_feedback_by_id(feedback_id)
        if not existing_feedback:
            return None
            
        # Add timestamp to the observation if not present
        if "timestamp" not in observation_data:
            observation_data["timestamp"] = datetime.now().isoformat()
            
        # Ensure at least one fatigue or injury is reported
        has_fatigue = "fatigue" in observation_data and observation_data["fatigue"]
        has_injuries = "injuries" in observation_data and observation_data["injuries"]
        
        if not has_fatigue and not has_injuries:
            raise ValueError("Health observation must contain at least one fatigue or injury report")
            
        # Set the health observation
        existing_feedback["health_observation"] = observation_data
        
        # Check for injuries to trigger alerts
        self._check_injuries(existing_feedback)
        
        # Save to JSON
        success = self.json_handler.update_json_item(
            self.feedback_file, "feedback", feedback_id, existing_feedback
        )
        
        return existing_feedback if success else None
    
    def delete_feedback(self, feedback_id: str) -> bool:
        """
        Delete feedback
        
        Args:
            feedback_id: ID of the feedback to delete
            
        Returns:
            True if successfully deleted, False otherwise
        """
        return self.json_handler.delete_json_item(self.feedback_file, "feedback", feedback_id)
    
    def get_health_observations_by_athlete(self, athlete_id: str) -> List[Dict]:
        """
        Get all health observations for a specific athlete
        
        Args:
            athlete_id: ID of the athlete to retrieve observations for
            
        Returns:
            List of health observations for the athlete
        """
        feedbacks = self.get_all_feedback()
        
        observations = []
        for feedback in feedbacks:
            if "health_observation" in feedback and feedback["health_observation"] is not None:
                health_observation = feedback["health_observation"]
                
                # Check injuries
                if "injuries" in health_observation and health_observation["injuries"]:
                    for injury in health_observation["injuries"]:
                        if injury.get("athlete_id") == athlete_id:
                            # Include feedback context
                            injury_with_context = {
                                **injury,
                                "observation_type": "injury",
                                "feedback_id": feedback.get("id"),
                                "training_id": feedback.get("training_id"),
                                "feedback_date": feedback.get("date"),
                                "reported_by": feedback.get("submitted_by"),
                                "management": health_observation.get("management", [])
                            }
                            observations.append(injury_with_context)
                
                # For fatigue, add if any fatigue was reported for a session involving the athlete
                # This is a simplified approach since fatigue might be general and not tied to specific athletes
                if "fatigue" in health_observation and health_observation["fatigue"]:
                    # Get training session to check if athlete was involved
                    training_id = feedback.get("training_id")
                    # Here we'd ideally check if the athlete was part of this training
                    # For simplicity, we'll assume they were if there's fatigue reported
                    for fatigue in health_observation["fatigue"]:
                        fatigue_with_context = {
                            **fatigue,
                            "observation_type": "fatigue",
                            "athlete_id": athlete_id,  # Assumed to be relevant to this athlete
                            "feedback_id": feedback.get("id"),
                            "training_id": feedback.get("training_id"),
                            "feedback_date": feedback.get("date"),
                            "reported_by": feedback.get("submitted_by"),
                            "management": health_observation.get("management", [])
                        }
                        observations.append(fatigue_with_context)
                        
        return observations
    
    def _check_injuries(self, feedback_data: Dict[str, Any]) -> None:
        """
        Check for injuries in health observations and trigger alerts if needed
        
        Args:
            feedback_data: Feedback data containing health observations
        """
        if "health_observation" in feedback_data and feedback_data["health_observation"] is not None:
            health_observation = feedback_data["health_observation"]
            
            # Check for injuries
            if "injuries" in health_observation and health_observation["injuries"]:
                for injury in health_observation["injuries"]:
                    athlete_name = injury.get("athlete_name", "An athlete")
                    location = injury.get("location", "Unknown location")
                    injury_type = injury.get("type", "Unknown type")
                    severity = injury.get("severity", 0)
                    
                    # Major injuries (severity >= 4) trigger medical staff alerts
                    if severity >= 4:
                        print(f"MEDICAL ALERT: Severe injury ({severity}/5) reported")
                        print(f"Athlete: {athlete_name}")
                        print(f"Details: {injury_type} at {location}")
                        # In a real system, this would call a notification service or API
                    
                    # All injuries trigger coach alerts
                    print(f"COACH NOTIFICATION: {injury_type} at {location} (Severity: {severity}/5)")
                    print(f"Athlete: {athlete_name}")
                    
            # Check for severe fatigue
            if "fatigue" in health_observation and health_observation["fatigue"]:
                for fatigue in health_observation["fatigue"]:
                    if fatigue.get("severity", 0) >= 4:
                        fatigue_type = fatigue.get("type", "Unknown fatigue type")
                        notes = fatigue.get("notes", "No details provided")
                        print(f"COACH ALERT: Severe fatigue ({fatigue_type}) reported")
                        print(f"Severity: {fatigue.get('severity')}/5")
                        print(f"Notes: {notes}")
