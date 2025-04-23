from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session

from dependencies.database import get_db
from dependencies.auth import get_current_user, get_optional_user
from models.training import (
    TrainingSessionCreate,
    TrainingSession,
    TrainingSessionDetail,
    TrainingSessionResponse
)
from models.db_models import User
from services.training_service import TrainingService

router = APIRouter(
    prefix="/training-sessions",
    tags=["Training Sessions"],
    responses={404: {"description": "Not found"}},
)

# Helper function to validate user role for endpoints
def validate_coach_permissions(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "coach" and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches and administrators can manage training sessions"
        )
    return current_user

@router.post("/", response_model=TrainingSession, status_code=status.HTTP_201_CREATED)
def create_training_session(
    session_data: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(validate_coach_permissions)
):
    """
    Create a new training session.
    
    Only coaches and admins can create training sessions.
    """
    try:
        training_service = TrainingService(db)
        session = training_service.create_session(session_data, current_user["id"])
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create training session: {str(e)}"
        )

@router.get("/", response_model=TrainingSessionResponse)
def list_training_sessions(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    type: Optional[str] = Query(None, description="Filter by session type"),
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(10, description="Page size", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List training sessions with optional filters and pagination."""
    try:
        training_service = TrainingService(db)
        offset = (page - 1) * size
        
        # Convert to dict for consistency
        filters = {}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if type:
            filters["type"] = type
            
        # Add role-based filtering
        if current_user["role"] == "athlete":
            # Athletes should only see sessions they are eligible for
            filters["athlete_id"] = current_user["id"]
        
        result = training_service.list_sessions(limit=size, offset=offset, filters=filters)
        return {
            "sessions": result["sessions"],
            "total": result["total"],
            "page": page,
            "size": size
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving training sessions: {str(e)}"
        )

@router.get("/{session_id}", response_model=TrainingSessionDetail)
def get_training_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific training session."""
    try:
        training_service = TrainingService(db)
        session = training_service.get_session_with_details(session_id)
        
        # Check if session exists
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
            
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving training session: {str(e)}"
        )

@router.put("/{session_id}", response_model=TrainingSession)
def update_training_session(
    session_id: str,
    session_data: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(validate_coach_permissions)
):
    """
    Update an existing training session.
    
    Only coaches who created the session and admins can update training sessions.
    """
    try:
        training_service = TrainingService(db)
        
        # Get existing session to check permissions
        existing_session = training_service.get_session(session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
            
        # Check if current user is the coach who created the session or an admin
        if current_user["role"] != "admin" and existing_session.coach_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this training session"
            )
            
        updated_session = training_service.update_session(session_id, session_data)
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update training session: {str(e)}"
        )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(validate_coach_permissions)
):
    """
    Delete a training session.
    
    Only coaches who created the session and admins can delete training sessions.
    """
    try:
        training_service = TrainingService(db)
        
        # Get existing session to check permissions
        existing_session = training_service.get_session(session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
            
        # Check if current user is the coach who created the session or an admin
        if current_user["role"] != "admin" and existing_session.coach_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this training session"
            )
            
        training_service.delete_session(session_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete training session: {str(e)}"
        )

@router.post("/{session_id}/attendance", status_code=status.HTTP_201_CREATED)
def mark_attendance(
    session_id: str,
    athlete_ids: List[str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(validate_coach_permissions)
):
    """
    Mark attendance for multiple athletes.
    
    Only coaches and admins can mark attendance for other athletes.
    """
    try:
        training_service = TrainingService(db)
        training_service.mark_attendance(session_id, athlete_ids)
        return {"detail": "Attendance marked successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not mark attendance: {str(e)}"
        )

@router.get("/{session_id}/attendance", status_code=status.HTTP_200_OK)
def get_session_attendance(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get attendance records for a specific training session."""
    try:
        training_service = TrainingService(db)
        
        # Get existing session to check permissions
        existing_session = training_service.get_session(session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
        
        # For athletes, only allow them to see their own attendance
        if current_user["role"] == "athlete":
            # Check if athlete has marked attendance
            has_attended = training_service.check_attendance(session_id, current_user["id"])
            return {
                "session_id": session_id,
                "has_attended": has_attended,
                "attendance": []  # Don't return other athletes' data
            }
        
        # For coaches and admins, return all attendance records
        attendance = training_service.get_session_attendance(session_id)
        return {
            "session_id": session_id,
            "attendance": attendance
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving attendance: {str(e)}"
        )

@router.post("/{session_id}/self-attendance", status_code=status.HTTP_201_CREATED)
def mark_self_attendance(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark attendance for the currently logged-in athlete.
    
    Athletes can only mark their own attendance.
    """
    # Only athletes can mark their own attendance
    if current_user["role"] != "athlete":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only athletes can mark their own attendance"
        )
    
    try:
        training_service = TrainingService(db)
        
        # Check if session exists
        existing_session = training_service.get_session(session_id)
        if not existing_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found"
            )
        
        # Check if attendance already marked
        already_attended = training_service.check_attendance(session_id, current_user["id"])
        if already_attended:
            return {"detail": "Attendance already marked"}
        
        # Mark attendance for athlete
        training_service.mark_attendance(session_id, [current_user["id"]])
        return {"detail": "Attendance marked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not mark attendance: {str(e)}"
        )

@router.get("/")
def get_training_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
    skip: int = 0,
    limit: int = 10
):
    """
    Get all training sessions
    """
    sessions = db.query(TrainingSession).offset(skip).limit(limit).all()
    return sessions

@router.get("/{session_id}")
def get_training_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Get a specific training session by ID
    """
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    return session 