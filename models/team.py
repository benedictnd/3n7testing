from __future__ import annotations
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, ForwardRef
from pydantic import BaseModel, Field

class Position(str, Enum):
    """Basketball positions"""
    POINT_GUARD = "PG"
    SHOOTING_GUARD = "SG"  
    SMALL_FORWARD = "SF"
    POWER_FORWARD = "PF"
    CENTER = "C"


# Use these models for API responses to avoid circular references
class CoachSummary(BaseModel):
    """Summary model for coach to avoid circular references"""
    id: str
    name: str
    role: str
    team_id: str
    
    class Config:
        from_attributes = True


class AthleteSummary(BaseModel):
    """Summary model for athlete to avoid circular references"""
    id: str
    name: str
    team_id: str
    
    class Config:
        from_attributes = True


class TeamSummary(BaseModel):
    """Summary model for team to avoid circular references"""
    id: str
    name: str
    
    class Config:
        from_attributes = True


# Full models with proper forward references
class Coach(BaseModel):
    """Coach model representing coaching staff"""
    id: str
    name: str
    role: str  # Head Coach, Associate Coach, Assistant Coach
    team_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    # Use TeamSummary instead of Team to avoid circular references
    team: Optional[TeamSummary] = None
    
    class Config:
        from_attributes = True


class Athlete(BaseModel):
    """Athlete model representing basketball players"""
    id: str
    name: str
    positions: List[Position]
    team_id: str
    jersey_number: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    # Use TeamSummary instead of Team to avoid circular references
    team: Optional[TeamSummary] = None
    
    class Config:
        from_attributes = True


class Team(BaseModel):
    """Team model representing a basketball team"""
    id: str
    name: str
    coaches: List[CoachSummary] = []
    athletes: List[AthleteSummary] = []
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None
    home_venue: Optional[str] = None
    
    class Config:
        from_attributes = True