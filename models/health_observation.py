from datetime import datetime
from typing import Optional, List, Literal, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class FatigueType(str, Enum):
    """Detailed types of fatigue observations"""
    OVERTRAINING = "Overtraining"
    LACK_OF_RECOVERY = "Lack of Recovery"
    POOR_NUTRITION = "Poor Nutrition"
    IMPROPER_TECHNIQUE = "Improper Technique"
    EXTERNAL_PRESSURES = "External Pressures"
    ENVIRONMENTAL_CONDITIONS = "Environmental Conditions"
    MONOTONY = "Monotony in Training"

class BodyPart(str, Enum):
    """Body parts for injury reporting"""
    ACHILLES = "Achilles Tendon"
    ANKLE = "Ankle"
    ELBOW = "Elbow"
    HEAD = "Head"
    KNEE = "Knee"
    LEG_MUSCLES = "Leg Muscles"
    SHOULDER = "Shoulder"
    BONE = "Bone Injuries"
    SOFT_TISSUE = "Soft Tissue"
    JOINT = "Joint Dislocation"
    LIGAMENT_MUSCLE = "Ligament/Muscle"
    TENDON = "Tendon"

class InjuryType(BaseModel):
    """Injury types based on body part"""
    location: str  # Body part where injury occurred
    type: str      # Specific injury type
    athlete_id: str
    athlete_name: str
    severity: int = Field(1, ge=1, le=5)  # 1-5 scale
    notes: Optional[str] = None

class FatigueObservation(BaseModel):
    """Detailed fatigue observation with type, severity and notes"""
    type: FatigueType
    severity: int = Field(1, ge=1, le=5)  # 1-5 scale
    notes: Optional[str] = None
    contributors: Optional[List[str]] = None

class ManagementStrategy(str, Enum):
    """Management strategies for fatigue and injuries"""
    ACTIVE_RECOVERY = "Active Recovery"
    ADEQUATE_SLEEP = "Adequate Sleep"
    NUTRITION_HYDRATION = "Nutrition/Hydration Plan"
    MENTAL_TRAINING = "Mental Training"
    PERIODIZATION = "Periodization"
    PSYCHOLOGICAL_SUPPORT = "Psychological Support"

class HealthObservation(BaseModel):
    """Comprehensive health observation report"""
    session_date: datetime
    reported_by: str  # ID of coach or athlete who reported
    reporter_name: str
    timestamp: datetime
    fatigue: Optional[List[FatigueObservation]] = None
    injuries: Optional[List[InjuryType]] = None
    management: Optional[List[ManagementStrategy]] = None
    additional_notes: Optional[str] = None
    
    class Config:
        from_attributes = True
