from typing import List, Dict, Any, Optional, Union
from datetime import datetime, time

class CoachValidator:
    """
    Validator for coach assignments in training sessions
    """
    
    @staticmethod
    def validate_coach_assignment(coaches_assigned: List[Dict], training_date: str, 
                                start_time: str, end_time: str, 
                                available_coaches: List[Dict]) -> Dict[str, Any]:
        """
        Validate that the assigned coaches are available for the training session
        
        Args:
            coaches_assigned: List of coaches to assign
            training_date: Date of the training session
            start_time: Start time of the training session
            end_time: End time of the training session
            available_coaches: List of all available coaches with their schedules
            
        Returns:
            Dictionary with 'valid' flag and 'message' or 'conflicts'
        """
        if not coaches_assigned:
            return {
                "valid": False, 
                "message": "At least one coach must be assigned to a training session"
            }
            
        # Convert times to datetime.time objects for comparison
        try:
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            return {
                "valid": False,
                "message": "Invalid time format. Expected HH:MM."
            }
            
        if start >= end:
            return {
                "valid": False,
                "message": "End time must be after start time"
            }
            
        # Get day of week for the training date
        try:
            training_day = datetime.strptime(training_date, "%Y-%m-%d").strftime("%A")
        except ValueError:
            return {
                "valid": False,
                "message": "Invalid date format. Expected YYYY-MM-DD."
            }
            
        # Check coach availability
        conflicts = []
        coach_ids = [c["coach_id"] for c in coaches_assigned]
        for coach_id in coach_ids:
            # Find coach in available coaches
            coach = next((c for c in available_coaches if c["id"] == coach_id), None)
            if not coach:
                conflicts.append({
                    "coach_id": coach_id,
                    "reason": "Coach not found"
                })
                continue
                
            # Check if coach is available on the training day
            if training_day not in coach.get("availability", {}):
                conflicts.append({
                    "coach_id": coach_id,
                    "coach_name": coach["name"],
                    "reason": f"Coach not available on {training_day}"
                })
                continue
                
            # Check time slots
            available = False
            for time_slot in coach["availability"].get(training_day, []):
                slot_start, slot_end = time_slot.split("-")
                try:
                    slot_start_time = datetime.strptime(slot_start, "%H:%M").time()
                    slot_end_time = datetime.strptime(slot_end, "%H:%M").time()
                    
                    if start >= slot_start_time and end <= slot_end_time:
                        available = True
                        break
                except ValueError:
                    continue
                    
            if not available:
                conflicts.append({
                    "coach_id": coach_id,
                    "coach_name": coach["name"],
                    "reason": f"Coach not available at the requested time on {training_day}"
                })
        
        if conflicts:
            return {
                "valid": False,
                "conflicts": conflicts
            }
            
        # Add validation for lead coach (optional)
        lead_coaches = [c for c in coaches_assigned if c.get("role") == "Head Coach"]
        if len(lead_coaches) > 1:
            return {
                "valid": False,
                "message": "Only one coach can be assigned as 'Head Coach'"
            }
            
        return {"valid": True}
    
    @staticmethod
    def validate_multi_coach_selection(coaches_selected: List[str], all_coaches: List[Dict]) -> Dict[str, Any]:
        """
        Validate the multi-selection of coaches
        
        Args:
            coaches_selected: List of coach IDs selected
            all_coaches: List of all available coaches
            
        Returns:
            Dictionary with 'valid' flag and 'message' or 'valid_coaches'
        """
        if not coaches_selected:
            return {
                "valid": False, 
                "message": "At least one coach must be selected"
            }
            
        # Validate that all selected coaches exist
        valid_coaches = []
        invalid_coaches = []
        
        for coach_id in coaches_selected:
            coach = next((c for c in all_coaches if c["id"] == coach_id), None)
            if coach:
                valid_coaches.append({
                    "coach_id": coach_id,
                    "name": coach["name"]
                })
            else:
                invalid_coaches.append(coach_id)
                
        if invalid_coaches:
            return {
                "valid": False,
                "message": f"Invalid coach IDs: {', '.join(invalid_coaches)}"
            }
            
        return {
            "valid": True,
            "valid_coaches": valid_coaches
        }
