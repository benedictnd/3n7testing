from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ReportFormat(str, Enum):
    """Enum for report formats"""
    JSON = "json"
    PDF = "pdf"
    PPT = "ppt"


class TrainingSessionSummary(BaseModel):
    """Model for training session summary in reports"""
    id: str
    date: str
    type: str
    coach_name: str
    duration_minutes: int
    attendees_count: int
    feedback: Dict[str, float] = Field(
        default_factory=lambda: {
            "training_quality_avg": 0,
            "expectations_avg": 0,
            "body_condition_avg": 0,
            "intensity_avg": 0
        }
    )


class AttendanceSummary(BaseModel):
    """Model for attendance summary in reports"""
    athlete_id: str
    athlete_name: str
    sessions_attended: int
    sessions_missed: int
    attendance_rate: float


class FeedbackSummary(BaseModel):
    """Model for feedback summary in reports"""
    session_id: str
    date: str
    type: str
    coach_name: str
    training_quality_avg: float
    expectations_avg: float
    body_condition_avg: float
    intensity_avg: float
    feedback_count: int


class SessionAttendance(BaseModel):
    """Model for session attendance in reports"""
    id: str
    date: str
    type: str
    coach_name: str
    attended: bool
    check_in_time: Optional[str] = None


class AthleteAttendanceReport(BaseModel):
    """Model for athlete attendance report"""
    athlete_id: str
    athlete_name: str
    attended_count: int
    total_count: int
    attendance_rate: float
    sessions: List[SessionAttendance]


class TeamAttendanceReport(BaseModel):
    """Model for team attendance report"""
    total_athletes: int
    avg_attendance_rate: float
    athletes: List[AttendanceSummary]


class FeedbackDetail(BaseModel):
    """Model for detailed feedback in reports"""
    id: str
    athlete_id: str
    athlete_name: str
    training_quality: int
    expectations: int
    body_condition: int
    intensity: int
    notes: Optional[str] = None
    created_at: str


class SessionFeedbackReport(BaseModel):
    """Model for session feedback report"""
    session_id: str
    date: str
    type: str
    coach_name: str
    feedback_count: int
    training_quality_avg: float
    expectations_avg: float
    body_condition_avg: float
    intensity_avg: float
    feedbacks: List[FeedbackDetail]


class TrainingReportResponse(BaseModel):
    """Response model for training report"""
    title: str
    generated_at: datetime
    date_range: str
    summary: Dict[str, Any]
    data: List[TrainingSessionSummary]


class AttendanceReportResponse(BaseModel):
    """Response model for attendance report"""
    title: str
    generated_at: datetime
    date_range: str
    summary: Dict[str, Any]
    data: List[Any]  # Can be either AthleteAttendanceReport or TeamAttendanceReport


class FeedbackReportResponse(BaseModel):
    """Response model for feedback report"""
    title: str
    generated_at: datetime
    date_range: str
    summary: Dict[str, Any]
    data: List[Any]  # Can be FeedbackDetail or FeedbackSummary


class ReportExportRequest(BaseModel):
    """Request model for exporting a custom report"""
    title: str
    data: Dict[str, Any]
    format: ReportFormat = ReportFormat.PDF


class IndependentTrainingSummary(BaseModel):
    """Model for independent training summary in reports"""
    id: str
    date: str
    type: str
    start_time: str
    end_time: str
    location: str
    intensity: int
    body_condition: int


class MonthlyReportResponse(BaseModel):
    """Response model for monthly report"""
    title: str
    generated_at: datetime
    date_range: str
    summary: Dict[str, Any]
    data: List[TrainingSessionSummary]
    independent_training: List[IndependentTrainingSummary] 