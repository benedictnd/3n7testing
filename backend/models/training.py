from datetime import datetime, date, time
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class SessionType(str, Enum):
    """Types of training sessions"""
    STRENGTH = "strength"
    CONDITIONING = "conditioning"
    RECOVERY = "recovery"
    SKILLS = "skills"
    TEAM_PRACTICE = "team_practice"
    OTHER = "other"


class TrainingPhase(BaseModel):
    """Model for a training phase (warm-up, main, cool-down)"""
    name: str
    description: str
    duration_minutes: int
    exercises: List[str]
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v


class TrainingSessionBase(BaseModel):
    """Base model for training session without ID"""
    title: str
    type: SessionType
    date: date
    start_time: datetime
    end_time: datetime
    location: str
    description: Optional[str] = None
    max_participants: Optional[int] = None
    phases: List[TrainingPhase]
    equipment_needed: Optional[List[str]] = None
    notes: Optional[str] = None
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v


class TrainingSessionCreate(TrainingSessionBase):
    """Model for creating a training session"""
    athlete_group_ids: Optional[List[str]] = None
    individual_athlete_ids: Optional[List[str]] = None


class TrainingSession(TrainingSessionBase):
    """Model for a training session with ID"""
    id: str
    coach_id: str
    coach_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class AttendanceRecord(BaseModel):
    """Model for an attendance record"""
    id: str
    session_id: str
    athlete_id: str
    athlete_name: str
    check_in_time: datetime
    
    class Config:
        orm_mode = True


class FeedbackSummary(BaseModel):
    """Summary of feedback for a training session"""
    feedback_count: int
    average_rating: float
    sentiment: Optional[str] = None


class TrainingSessionDetail(TrainingSession):
    """Detailed model for a training session with attendance and feedback"""
    attendees: List[AttendanceRecord]
    feedback: Optional[FeedbackSummary] = None
    
    class Config:
        orm_mode = True


class TrainingSessionResponse(BaseModel):
    """Response model for listing training sessions with pagination"""
    sessions: List[TrainingSession]
    total: int
    page: int
    size: int


class IndependentTrainingType(str, Enum):
    """Types of independent training sessions"""
    STRENGTH = "strength"
    CONDITIONING = "conditioning"
    RECOVERY = "recovery"
    SKILLS = "skills"
    CARDIO = "cardio"
    OTHER = "other"


class IndependentTrainingBase(BaseModel):
    """Base model for independent training session"""
    title: str
    type: IndependentTrainingType
    date: date
    start_time: datetime
    end_time: datetime
    location: str
    description: Optional[str] = None
    phases: List[TrainingPhase]
    equipment_needed: Optional[List[str]] = None
    notes: Optional[str] = None
    intensity: int = Field(..., ge=1, le=10, description="Training intensity from 1-10")
    body_condition: int = Field(..., ge=1, le=10, description="Body condition from 1-10")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v


class IndependentTrainingCreate(IndependentTrainingBase):
    """Model for creating an independent training session"""
    pass


class IndependentTraining(IndependentTrainingBase):
    """Model for an independent training session with ID"""
    id: str
    athlete_id: str
    athlete_name: str
    created_at: datetime
    updated_at: datetime
    coach_notified: bool = False
    
    class Config:
        orm_mode = True


class IndependentTrainingResponse(BaseModel):
    """Response model for listing independent training sessions"""
    sessions: List[IndependentTraining]
    total: int
    page: int
    size: int 