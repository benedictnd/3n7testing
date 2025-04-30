from typing import Dict, List, Optional, Union, Set, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid
from datetime import datetime


class SkillLevel(str, Enum):
    """Skill levels for drills"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"
    ALL = "all"
    ALL_LEVELS = "all_levels"


class DrillCategory(str, Enum):
    """Categories of training drills"""
    TECHNICAL = "technical"
    TACTICAL = "tactical"
    PHYSICAL = "physical"
    MENTAL = "mental"
    GAME_SPECIFIC = "game_specific"
    WARMUP = "warmup"
    COOLDOWN = "cooldown"
    TEAM_BUILDING = "team_building"
    WARM_UP = "warm_up"
    CONDITIONING = "conditioning"
    GAME_SITUATION = "game_situation"
    RECOVERY = "recovery"
    STRENGTH = "strength"
    COORDINATION = "coordination"
    AGILITY = "agility"
    SPEED = "speed"
    ENDURANCE = "endurance"
    OTHER = "other"


class DrillFocus(str, Enum):
    """Specific focus areas of drills"""
    PASSING = "passing"
    SHOOTING = "shooting"
    DRIBBLING = "dribbling"
    DEFENDING = "defending"
    ATTACKING = "attacking"
    GOALKEEPING = "goalkeeping"
    COORDINATION = "coordination"
    SPEED = "speed"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    AGILITY = "agility"
    BALANCE = "balance"
    REACTION = "reaction"
    DECISION_MAKING = "decision_making"
    COMMUNICATION = "communication"
    TEAMWORK = "teamwork"
    POSITIONING = "positioning"
    GAME_AWARENESS = "game_awareness"
    MENTAL_TOUGHNESS = "mental_toughness"
    RECOVERY = "recovery"
    FOOTWORK = "footwork"
    REBOUNDING = "rebounding"
    BALL_HANDLING = "ball_handling"
    SCREEN_SETTING = "screen_setting"
    CUTTING = "cutting"
    SPACING = "spacing"
    TRANSITION = "transition"
    TEAM_DEFENSE = "team_defense"
    POST_PLAY = "post_play"
    PERIMETER_PLAY = "perimeter_play"
    OTHER = "other"


class DrillIntensity(str, Enum):
    """Intensity levels for drills"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    MAXIMAL = "maximal"
    VARIABLE = "variable"


class AgeGroup(str, Enum):
    """Age groups for drill suitability"""
    U6 = "under_6"
    U8 = "under_8"
    U10 = "under_10"
    U12 = "under_12"
    U14 = "under_14"
    U16 = "under_16"
    U18 = "under_18"
    ADULT = "adult"
    SENIOR = "senior"
    UNDER_10 = "under_10"
    UNDER_12 = "under_12"
    UNDER_14 = "under_14"
    UNDER_16 = "under_16"
    UNDER_18 = "under_18"
    ALL_AGES = "all_ages"


class FieldZone(str, Enum):
    """Zones of the field/court"""
    DEFENSIVE_THIRD = "defensive_third"
    MIDDLE_THIRD = "middle_third"
    ATTACKING_THIRD = "attacking_third"
    DEFENSIVE_HALF = "defensive_half"
    ATTACKING_HALF = "attacking_half"
    WINGS = "wings"
    CENTER = "center"
    PENALTY_AREA = "penalty_area"
    GOAL_AREA = "goal_area"
    FULL_FIELD = "full_field"
    CUSTOM = "custom"


class Equipment(BaseModel):
    """Equipment that may be required for drills"""
    BALL = "ball"
    CONE = "cone"
    MARKER = "marker"
    BIBS = "bibs"
    GOAL = "goal"
    MINI_GOAL = "mini_goal"
    HURDLE = "hurdle"
    LADDER = "ladder"
    POLE = "pole"
    MANNEQUIN = "mannequin"
    HOOP = "hoop"
    WHISTLE = "whistle"
    STOPWATCH = "stopwatch"
    RESISTANCE_BAND = "resistance_band"
    MEDICINE_BALL = "medicine_ball"
    SLALOM_POLE = "slalom_pole"
    REBOUND_BOARD = "rebound_board"
    NONE = "none"
    name: str
    quantity: int = 1
    description: Optional[str] = None


class ScoringMethod(str, Enum):
    """Methods for scoring/evaluating drills"""
    TIME_BASED = "time_based"
    POINTS_BASED = "points_based"
    COMPLETION_BASED = "completion_based"
    QUALITY_BASED = "quality_based"
    REPETITION_BASED = "repetition_based"
    DISTANCE_BASED = "distance_based"
    CUSTOM = "custom"
    NONE = "none"


class ProgressionType(str, Enum):
    """Types of drill progressions"""
    TECHNICAL = "technical"
    TACTICAL = "tactical"
    PHYSICAL = "physical"
    COGNITIVE = "cognitive"
    COMPETITIVE = "competitive"
    CONSTRAINT = "constraint"


class TeamType(str, Enum):
    """Types of teams a drill is suitable for"""
    INDIVIDUAL = "individual"
    SMALL_GROUP = "small_group"
    PARTIAL_TEAM = "partial_team"
    FULL_TEAM = "full_team"
    MULTIPLE_TEAMS = "multiple_teams"


class FieldDimension(BaseModel):
    """Represents field/court dimensions for a drill"""
    length: Optional[int] = None
    width: Optional[int] = None
    shape: str = "rectangle"
    custom_layout: Optional[str] = None
    
    @validator('shape')
    def validate_shape(cls, v):
        allowed_shapes = ["rectangle", "square", "circle", "diamond", "custom"]
        if v not in allowed_shapes:
            raise ValueError(f"Shape must be one of {allowed_shapes}")
        return v


class PlayerRole(BaseModel):
    """Defines a player role within a drill"""
    role_name: str
    description: str
    max_players: int
    min_players: int = 1
    responsibilities: List[str] = []
    starting_positions: Optional[List[Dict[str, Any]]] = None
    bibs_color: Optional[str] = None


class DrillProgression(BaseModel):
    """A progression or variation of the drill"""
    progression_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: ProgressionType
    difficulty_modifier: int = 0  # -2 to +2 relative to base drill
    changes: Dict[str, Any] = {}
    coaching_points: List[str] = []


class PerformanceBenchmark(BaseModel):
    """Performance benchmarks for different skill levels"""
    skill_level: SkillLevel
    expected_values: Dict[str, Any]
    scoring_criteria: Optional[Dict[str, Any]] = None


class DrillConfiguration(BaseModel):
    """
    Comprehensive configuration for a training drill
    """
    # Core information
    drill_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    objective: str
    estimated_duration_minutes: int
    
    # Categorization
    category: DrillCategory
    focus_areas: List[DrillFocus]
    intensity: DrillIntensity
    skill_level: List[SkillLevel]
    suitable_age_groups: List[AgeGroup]
    team_type: List[TeamType]
    
    # Setup details
    field_zones: List[FieldZone]
    field_dimensions: Optional[FieldDimension] = None
    required_equipment: List[Equipment] = []
    setup_time_minutes: int = 5
    
    # Participants
    min_players: int
    max_players: int
    player_roles: List[PlayerRole] = []
    coach_involvement: bool = False
    coach_role_description: Optional[str] = None
    
    # Instructions
    setup_instructions: List[str]
    execution_instructions: List[str]
    rules: List[str] = []
    variations: List[DrillProgression] = []
    coaching_points: List[str] = []
    
    # Evaluation
    scoring_method: ScoringMethod = ScoringMethod.NONE
    scoring_details: Optional[Dict[str, Any]] = None
    performance_benchmarks: List[PerformanceBenchmark] = []
    success_criteria: List[str] = []
    
    # Media and resources
    diagram_urls: List[str] = []
    video_urls: List[str] = []
    
    # Metadata
    tags: List[str] = []
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Extended configuration
    related_drills: List[str] = []  # IDs of related drills
    progression_path: List[str] = []  # IDs of drills in progression
    is_featured: bool = False
    difficulty_rating: int = Field(1, ge=1, le=5)  # 1-5 rating

    @validator('min_players')
    def validate_min_players(cls, v, values):
        if v < 1:
            raise ValueError("Minimum players must be at least 1")
        return v
    
    @validator('max_players')
    def validate_max_players(cls, v, values):
        if 'min_players' in values and v < values['min_players']:
            raise ValueError("Maximum players must be greater than or equal to minimum players")
        return v
    
    @validator('estimated_duration_minutes')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v
    
    @validator('setup_time_minutes')
    def validate_setup_time(cls, v):
        if v < 0:
            raise ValueError("Setup time cannot be negative")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum values as strings"""
        result = self.dict()
        
        # Convert enum lists to string lists
        for field in ["focus_areas", "skill_level", "suitable_age_groups", "field_zones", 
                     "required_equipment", "team_type"]:
            if field in result and result[field]:
                result[field] = [item.value if hasattr(item, 'value') else item for item in result[field]]
        
        # Convert individual enums to strings
        if "intensity" in result and result["intensity"]:
            result["intensity"] = result["intensity"].value
        
        if "category" in result and result["category"]:
            result["category"] = result["category"].value
        
        if "scoring_method" in result and result["scoring_method"]:
            result["scoring_method"] = result["scoring_method"].value
        
        return result
    
    def get_total_space_required(self) -> Dict[str, Any]:
        """Calculate the total space required for this drill"""
        if not self.field_dimensions:
            return {"units": "not_specified"}
        
        dims = self.field_dimensions
        
        if dims.shape == "rectangle" or dims.shape == "square":
            if dims.length and dims.width:
                area = dims.length * dims.width
                return {
                    "length": dims.length,
                    "width": dims.width,
                    "area": area,
                    "units": "square_meters"
                }
        
        return {"shape": dims.shape, "custom": dims.custom_layout, "units": "not_specified"}
    
    def get_equipment_count(self) -> Dict[str, int]:
        """
        Calculate the estimated equipment count needed based on the drill configuration
        
        Returns:
            Dictionary mapping equipment types to counts
        """
        result = {}
        
        # Basic estimates based on players
        mid_players = (self.min_players + self.max_players) // 2
        
        for equipment in self.required_equipment:
            if equipment == Equipment.BALL:
                # Estimate balls - typically 1 per player or fewer
                result[equipment.value] = mid_players
            elif equipment == Equipment.CONE or equipment == Equipment.MARKER:
                # Cones/markers - often used to mark areas
                result[equipment.value] = mid_players * 2
            elif equipment == Equipment.BIBS:
                # Bibs - typically for half the players or based on roles
                result[equipment.value] = mid_players // 2
            elif equipment == Equipment.GOAL:
                # Goals - usually 2 for a standard drill
                result[equipment.value] = 2
            elif equipment == Equipment.MINI_GOAL:
                # Mini goals - often 2-4
                result[equipment.value] = 2
            else:
                # Default to 1 for other equipment
                result[equipment.value] = 1
                
        # Adjust based on field dimensions if available
        if self.field_dimensions and self.field_dimensions.length and self.field_dimensions.width:
            perimeter = 2 * (self.field_dimensions.length + self.field_dimensions.width)
            if Equipment.CONE.value in result:
                # For larger areas, more cones might be needed for marking
                result[Equipment.CONE.value] = max(result[Equipment.CONE.value], perimeter // 5)
        
        return result


class DrillSearchParams(BaseModel):
    """Parameters for searching drills"""
    categories: Optional[List[DrillCategory]] = None
    focus_areas: Optional[List[DrillFocus]] = None
    intensity: Optional[List[DrillIntensity]] = None
    skill_levels: Optional[List[SkillLevel]] = None
    age_groups: Optional[List[AgeGroup]] = None
    team_types: Optional[List[TeamType]] = None
    player_count: Optional[int] = None
    duration_min: Optional[int] = None
    duration_max: Optional[int] = None
    equipment: Optional[List[Equipment]] = None
    exclude_equipment: Optional[List[Equipment]] = None
    tags: Optional[List[str]] = None
    query: Optional[str] = None
    limit: int = 20
    offset: int = 0


class DrillDB(BaseModel):
    """Database model for drill configurations"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    configuration: Dict[str, Any]
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True 