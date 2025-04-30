from typing import List, Dict, Any, Optional, Union

class HealthValidator:
    """
    Validator for health observations and injury flags
    """
    
    @staticmethod
    def validate_health_observation(observation_data: Dict[str, Any], athletes: List[Dict]) -> Dict[str, Any]:
        """
        Validate health observation data and trigger appropriate responses
        
        Args:
            observation_data: Health observation data
            athletes: List of athletes to validate against
            
        Returns:
            Dictionary with 'valid' flag, 'message', and 'alert_required' flags
        """
        # Required fields
        required_fields = ["athlete_id", "observation_type", "details"]
        for field in required_fields:
            if field not in observation_data:
                return {
                    "valid": False,
                    "message": f"Missing required field: {field}"
                }
                
        # Validate athlete exists
        athlete_id = observation_data["athlete_id"]
        athlete = next((a for a in athletes if a.get("id") == athlete_id), None)
        if not athlete:
            return {
                "valid": False,
                "message": f"Athlete with ID {athlete_id} not found"
            }
            
        # Add athlete name if not provided
        if "athlete_name" not in observation_data and athlete:
            observation_data["athlete_name"] = athlete.get("name", "Unknown")
            
        # Validate observation type
        valid_types = ["Fatigue observed", "Minor injury", "Major injury"]
        if observation_data["observation_type"] not in valid_types:
            return {
                "valid": False,
                "message": f"Invalid observation type. Must be one of: {', '.join(valid_types)}"
            }
            
        # Set alert flags based on observation type
        alert_medical = observation_data["observation_type"] == "Major injury"
        alert_coach = observation_data["observation_type"] in ["Minor injury", "Major injury"]
        
        return {
            "valid": True,
            "alert_medical": alert_medical,
            "alert_coach": alert_coach,
            "data": observation_data
        }
    
    @staticmethod
    def process_alerts(validation_result: Dict[str, Any]) -> None:
        """
        Process alerts based on validation result
        
        Args:
            validation_result: Result from validate_health_observation
        """
        if not validation_result.get("valid", False):
            return
            
        data = validation_result.get("data", {})
        athlete_name = data.get("athlete_name", "An athlete")
        observation_type = data.get("observation_type", "")
        details = data.get("details", "No details provided")
        
        # Medical staff alert for major injuries
        if validation_result.get("alert_medical", False):
            # In a real system, this would send an email, SMS, or push notification
            # to medical staff. For now, just print a message.
            print(f"MEDICAL ALERT: Major injury reported for {athlete_name}.")
            print(f"Details: {details}")
            
        # Coach alert for any injury
        if validation_result.get("alert_coach", False):
            # In a real system, this would notify coaches. For now, just print a message.
            print(f"COACH NOTIFICATION: {observation_type} reported for {athlete_name}.")
            print(f"Details: {details}")
