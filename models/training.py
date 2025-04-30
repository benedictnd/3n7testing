from datetime import datetime, date, time
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

from models.coach_assignment import CoachAssignment
from models.health_observation import HealthObservation


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
    coaches_assigned: Optional[List[CoachAssignment]] = None
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v


class TrainingSessionCreate(TrainingSessionBase):
    """Model for creating a training session"""
    athlete_group_ids: Optional[List[str]] = None
    individual_athlete_ids: Optional[List[str]] = None
    coaches_assigned: List[CoachAssignment]


class TrainingSession(TrainingSessionBase):
    """Model for a training session with ID"""
    id: str
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


class TrainingActivity(BaseModel):
    """Specific activity during a training session"""
    name: str
    duration_minutes: int
    description: str
    intensity_level: Optional[int] = None  # 1-5 scale
    equipment_needed: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class Feedback(BaseModel):
    """Feedback and notes for a training session"""
    id: Optional[str] = None
    training_id: str
    date: date
    submitted_by: str
    reporter_name: str
    overall_rating: int = Field(..., ge=1, le=10)  # 1-10 scale
    intensity_rating: int = Field(..., ge=1, le=10)  # 1-10 scale
    quality_rating: int = Field(..., ge=1, le=10)  # 1-10 scale
    notes: str = ""
    post_training_summary: str = ""
    health_observation: Optional[HealthObservation] = None
    athlete_feedbacks: Optional[Dict[str, Dict[str, Any]]] = None
    timestamp: Optional[datetime] = None
    is_retroactive: bool = False  # True for feedback added to past sessions
    
    class Config:
        from_attributes = True


class Attendance(BaseModel):
    """Attendance record for an athlete at a training session"""
    session_id: str
    athlete_id: str
    status: str  # "present", "absent", "late", "excused"
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    notes: str = ""
    
    class Config:
        from_attributes = True


class TrainingSession(BaseModel):
    """Training session model"""
    id: str
    team_id: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    time_slot: str  # "Morning", "Afternoon", "Night"
    location: str
    coach_ids: List[str]
    activities: Optional[List[TrainingActivity]] = None
    feedback: Optional[Feedback] = None
    session_type: Optional[str] = "Regular"  # "Regular", "Recovery", "Game Preparation", "Skills Focus"
    focus_areas: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class TrainingPlan(BaseModel):
    """Training plan for a specific period"""
    id: str
    team_id: str
    title: str
    start_date: datetime.date
    end_date: datetime.date
    description: str = ""
    created_by: str  # coach_id
    sessions: List[TrainingSession] = []
    goals: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class InjuryReport(BaseModel):
    """Injury report for an athlete"""
    id: str
    athlete_id: str
    date_reported: datetime.date
    injury_type: str
    severity: int = Field(..., ge=1, le=5)  # 1-5 scale
    body_part: str
    description: str
    reported_by: str  # coach_id
    estimated_recovery_days: Optional[int] = None
    status: str = "Active"  # "Active", "Recovering", "Resolved"
    
    class Config:
        from_attributes = True


class PerformanceMetric(BaseModel):
    """Performance metrics for an athlete"""
    id: str
    athlete_id: str
    session_id: str
    metric_name: str  # e.g., "Shooting Accuracy", "Sprint Speed"
    value: float
    date_recorded: datetime.date
    recorded_by: str  # coach_id
    
    class Config:
        from_attributes = True 