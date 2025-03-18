from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class AttendanceBase(BaseModel):
    """Base model for attendance records"""
    session_id: str
    athlete_id: str


class AttendanceCreate(AttendanceBase):
    """Model for creating an attendance record"""
    pass


class AttendanceUpdate(BaseModel):
    """Model for updating an attendance record"""
    check_in_time: Optional[datetime] = None


class AttendanceResponse(AttendanceBase):
    """Model for attendance response"""
    id: str
    check_in_time: datetime
    athlete_name: Optional[str] = None
    
    class Config:
        orm_mode = True


class BulkAttendanceCreate(BaseModel):
    """Model for creating multiple attendance records at once"""
    athlete_ids: List[str]
    
    @validator('athlete_ids')
    def validate_athlete_ids(cls, v):
        if not v:
            raise ValueError("At least one athlete ID is required")
        return v


class AttendanceStats(BaseModel):
    """Statistics about attendance for an athlete or session"""
    total_sessions: int
    attended_sessions: int
    attendance_rate: float
    last_attended: Optional[datetime] = None


class SessionAttendanceResponse(BaseModel):
    """Model for session attendance response"""
    session_id: str
    session_date: datetime
    total_attendees: int
    attendees: List[AttendanceResponse]
    
    class Config:
        orm_mode = True


class AthleteAttendanceResponse(BaseModel):
    """Model for athlete attendance response"""
    athlete_id: str
    athlete_name: str
    stats: AttendanceStats
    recent_sessions: List[AttendanceResponse]
    
    class Config:
        orm_mode = True 