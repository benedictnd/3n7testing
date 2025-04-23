from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete, and_, or_, func
from datetime import datetime, date
from models.db_models import TrainingSession, Attendance, Feedback
import logging

logger = logging.getLogger(__name__)

class TrainingService:
    """Service for managing training sessions"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_session(self, session_data, coach_id: str):
        """Create a new training session"""
        try:
            new_session = TrainingSession(
                coach_id=coach_id,
                type=session_data.type,
                date=session_data.date,
                start_time=session_data.start_time,
                end_time=session_data.end_time,
                training_quality=session_data.training_quality,
                expectations=session_data.expectations,
                team_condition=session_data.team_condition,
                notes=session_data.notes,
                documentation=session_data.documentation
            )
            
            self.db_session.add(new_session)
            self.db_session.commit()
            self.db_session.refresh(new_session)
            
            return new_session
        except Exception as e:
            logger.error(f"Error creating training session: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create training session: {str(e)}"
            )
    
    def get_session(self, session_id: str):
        """Get a training session by ID (returns DB model)"""
        session = self.db_session.query(TrainingSession).filter(
            TrainingSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training session with ID {session_id} not found"
            )
        
        return session
    
    def get_session_with_details(self, session_id: str):
        """Get a training session with attendance and feedback details"""
        session = self.get_session(session_id)
        
        # Get attendance data
        attendance = self.db_session.query(Attendance).filter(
            Attendance.training_session_id == session_id
        ).all()
        
        # Get feedback data
        feedback = self.db_session.query(Feedback).filter(
            Feedback.training_session_id == session_id
        ).all()
        
        return {
            "session": session,
            "attendance": attendance,
            "feedback": feedback
        }
    
    def list_sessions(self, limit: int = 10, offset: int = 0, filters: Dict[str, Any] = None):
        """List training sessions with filters and pagination"""
        query = self.db_session.query(TrainingSession)
        
        if filters:
            # Apply filters
            if filters.get("date_from"):
                query = query.filter(TrainingSession.date >= filters["date_from"])
            
            if filters.get("date_to"):
                query = query.filter(TrainingSession.date <= filters["date_to"])
                
            if filters.get("type"):
                query = query.filter(TrainingSession.type == filters["type"])
                
            if filters.get("coach_id"):
                query = query.filter(TrainingSession.coach_id == filters["coach_id"])
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Get results
        sessions = query.all()
        
        return {
            "sessions": sessions,
            "total": total
        }
    
    def update_session(self, session_id: str, session_data):
        """Update an existing training session"""
        session = self.get_session(session_id)
        
        try:
            # Update fields
            for key, value in session_data.dict(exclude_unset=True).items():
                setattr(session, key, value)
            
            self.db_session.commit()
            self.db_session.refresh(session)
            
            return session
        except Exception as e:
            logger.error(f"Error updating training session: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update training session: {str(e)}"
            )
    
    def delete_session(self, session_id: str):
        """Delete a training session"""
        session = self.get_session(session_id)
        
        try:
            self.db_session.delete(session)
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Error deleting training session: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete training session: {str(e)}"
            )
    
    def mark_attendance(self, session_id: str, athlete_ids: List[str]):
        """Mark attendance for multiple athletes"""
        session = self.get_session(session_id)
        attendances = []
        
        try:
            for athlete_id in athlete_ids:
                # Check if attendance already exists
                existing = self.db_session.query(Attendance).filter(
                    Attendance.training_session_id == session_id,
                    Attendance.athlete_id == athlete_id
                ).first()
                
                if not existing:
                    attendance = Attendance(
                        training_session_id=session_id,
                        athlete_id=athlete_id,
                        check_in_time=datetime.now()
                    )
                    self.db_session.add(attendance)
                    attendances.append(attendance)
            
            self.db_session.commit()
            return attendances
        except Exception as e:
            logger.error(f"Error marking attendance: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark attendance: {str(e)}"
            )
    
    def get_session_attendance(self, session_id: str):
        """Get all attendance records for a session"""
        session = self.get_session(session_id)
        
        attendance = self.db_session.query(Attendance).filter(
            Attendance.training_session_id == session_id
        ).all()
        
        return attendance
    
    def check_attendance(self, session_id: str, athlete_id: str):
        """Check if an athlete has marked attendance for a session"""
        attendance = self.db_session.query(Attendance).filter(
            Attendance.training_session_id == session_id,
            Attendance.athlete_id == athlete_id
        ).first()
        
        return bool(attendance) 