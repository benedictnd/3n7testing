from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional

from services.json_feedback_service import JsonFeedbackService
from utils.json_handler import JsonHandler

router = APIRouter(
    prefix="/api/json/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get the feedback service
def get_feedback_service():
    json_handler = JsonHandler()
    return JsonFeedbackService(json_handler)

@router.get("/")
async def get_all_feedback(
    training_id: Optional[str] = None,
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Get all feedback, optionally filtered by training"""
    return feedback_service.get_all_feedback(training_id)

@router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: str,
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Get a specific feedback by ID"""
    feedback = feedback_service.get_feedback_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback

@router.post("/")
async def create_feedback(
    feedback_data: Dict[str, Any],
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Create new feedback for a training session"""
    try:
        return feedback_service.create_feedback(feedback_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{feedback_id}")
async def update_feedback(
    feedback_id: str,
    feedback_data: Dict[str, Any],
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Update existing feedback"""
    try:
        updated = feedback_service.update_feedback(feedback_id, feedback_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Delete feedback"""
    deleted = feedback_service.delete_feedback(feedback_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return {"success": True, "message": "Feedback deleted successfully"}

@router.post("/{feedback_id}/health-observation")
async def set_health_observation(
    feedback_id: str,
    observation_data: Dict[str, Any],
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Set the health observation for existing feedback"""
    try:
        updated = feedback_service.set_health_observation(feedback_id, observation_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/athletes/{athlete_id}/health-observations")
async def get_athlete_health_observations(
    athlete_id: str,
    observation_type: Optional[str] = Query(None, description="Filter by observation type: 'fatigue' or 'injury'"),
    severity_min: Optional[int] = Query(None, ge=1, le=5, description="Minimum severity level (1-5)"),
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Get all health observations for a specific athlete with optional filters"""
    observations = feedback_service.get_health_observations_by_athlete(athlete_id)
    
    # Apply filters if provided
    if observation_type:
        observations = [o for o in observations if o.get("observation_type") == observation_type]
        
    if severity_min is not None:
        observations = [o for o in observations if o.get("severity", 0) >= severity_min]
        
    return observations

@router.post("/retroactive")
async def create_retroactive_feedback(
    feedback_data: Dict[str, Any],
    feedback_service: JsonFeedbackService = Depends(get_feedback_service)
):
    """Create feedback for a past training session"""
    try:
        # Mark as retroactive
        feedback_data["is_retroactive"] = True
        
        return feedback_service.create_feedback(feedback_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
