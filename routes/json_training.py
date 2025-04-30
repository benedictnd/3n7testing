from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from datetime import date

from services.json_training_service import JsonTrainingService
from utils.json_handler import JsonHandler

router = APIRouter(
    prefix="/api/json/trainings",
    tags=["trainings"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get the training service
def get_training_service():
    json_handler = JsonHandler()
    return JsonTrainingService(json_handler)

@router.get("/")
async def get_training_sessions(
    team_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Get training sessions with optional filtering by team"""
    return training_service.get_training_sessions(team_id, limit, offset)

@router.get("/{training_id}")
async def get_training_session(
    training_id: str,
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Get a specific training session by ID"""
    training = training_service.get_training_session(training_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    return training

@router.post("/")
async def create_training_session(
    training_data: Dict[str, Any],
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Create a new training session"""
    try:
        return training_service.create_training_session(training_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{training_id}")
async def update_training_session(
    training_id: str,
    training_data: Dict[str, Any],
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Update an existing training session"""
    try:
        updated = training_service.update_training_session(training_id, training_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{training_id}")
async def delete_training_session(
    training_id: str,
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Delete a training session"""
    deleted = training_service.delete_training_session(training_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    return {"success": True, "message": "Training session deleted successfully"}

@router.get("/coaches/available")
async def get_available_coaches(
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Get all available coaches"""
    return training_service.get_available_coaches()

@router.get("/coaches/{coach_id}")
async def get_coach(
    coach_id: str,
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Get a specific coach by ID"""
    coach = training_service.get_coach_by_id(coach_id)
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found"
        )
    return coach

@router.post("/{training_id}/coaches")
async def assign_coaches(
    training_id: str,
    coach_assignments: List[Dict[str, Any]],
    training_service: JsonTrainingService = Depends(get_training_service)
):
    """Assign coaches to a training session"""
    try:
        updated = training_service.assign_coaches_to_session(training_id, coach_assignments)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
