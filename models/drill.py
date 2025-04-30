from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DrillFocusArea(str, Enum):
    """Focus areas for training drills"""
    SHOOTING = "shooting"
    BALL_HANDLING = "ball_handling"
    PASSING = "passing"
    TRANSITION_OFFENSE = "transition_offense"
    TRANSITION_DEFENSE = "transition_defense"
    HALF_COURT_OFFENSE = "half_court_offense"
    HALF_COURT_DEFENSE = "half_court_defense"
    BALL_REVERSAL = "ball_reversal"
    PICK_AND_ROLL = "pick_and_roll"
    POST_PLAY = "post_play"
    REBOUNDING = "rebounding"
    CONDITIONING = "conditioning"
    RECOVERY = "recovery"
    TEAM_CHEMISTRY = "team_chemistry"


class DrillIntensityLevel(str, Enum):
    """Intensity levels for drills"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SuccessMetric(BaseModel):
    """Model for success metrics of a drill"""
    name: str
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    target_value: Optional[float] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class DrillConfiguration(BaseModel):
    """Drill configuration model"""
    drill_id: str
    name: str
    duration_minutes: int = Field(gt=0, le=60)
    focus_areas: List[DrillFocusArea]
    description: str
    equipment: List[str] = []
    intensity_level: DrillIntensityLevel = DrillIntensityLevel.MEDIUM
    participant_range: Dict[str, int] = Field(
        default_factory=lambda: {"min": 1, "max": 20}
    )
    success_metrics: List[SuccessMetric] = []
    instructions: str
    variations: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True

    def is_suitable_for_recovery(self) -> bool:
        """Check if drill is suitable for recovery sessions"""
        if DrillFocusArea.RECOVERY in self.focus_areas:
            return True
        return self.intensity_level in [DrillIntensityLevel.VERY_LOW, DrillIntensityLevel.LOW]
    
    def is_suitable_for_player_development(self, player_focus_areas: List[str]) -> bool:
        """Check if drill is suitable for specific player development areas"""
        return any(focus.value in player_focus_areas for focus in self.focus_areas)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum values as strings"""
        data = self.dict()
        data["focus_areas"] = [focus.value for focus in self.focus_areas]
        data["intensity_level"] = self.intensity_level.value
        return data


class DrillResult(BaseModel):
    """Results of a completed drill"""
    drill_id: str
    session_id: str
    duration_actual: int
    participant_ids: List[str]
    metrics_achieved: Dict[str, float] = {}
    coach_notes: str = ""
    player_feedback: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True 