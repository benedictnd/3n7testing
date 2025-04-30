from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import random
from datetime import timedelta

from models.drill import DrillConfiguration, DrillFocusArea, DrillIntensityLevel
from models.team import Athlete
from models.training import TrainingSession, TrainingActivity
from services.drill_configuration import (
    DrillLibrary, 
    TrainingFocus,
    DifficultyLevel
)
from models.drill_configuration import DrillCategory, DrillFocus, SkillLevel, AgeGroup, DrillIntensity
from services.drill_service import DrillService


class SessionBuilder(ABC):
    """Abstract base class for session builders"""
    
    def __init__(self, db_session: AsyncSession, focus_players: List[str] = None):
        self.db_session = db_session
        self.focus_players = focus_players or []
        self.drills: List[DrillConfiguration] = []
        self.athletes: List[Athlete] = []
        
    async def initialize(self, team_id: str):
        """Initialize the builder with data"""
        # In a real implementation, these would be fetched from the database
        await self._load_drills()
        await self._load_athletes(team_id)
        
    async def _load_drills(self):
        """Load available drills from the database"""
        # Mock implementation - would be replaced with actual DB queries
        # In a real implementation, we would fetch from DB:
        # self.drills = await self.db_session.execute(select(DrillConfiguration))
        pass
        
    async def _load_athletes(self, team_id: str):
        """Load athletes from the database"""
        # Mock implementation - would be replaced with actual DB queries
        # In a real implementation:
        # query = select(Athlete).where(Athlete.team_id == team_id)
        # result = await self.db_session.execute(query)
        # self.athletes = result.scalars().all()
        pass
    
    def _get_athlete_focus_areas(self, athlete_id: str) -> List[str]:
        """Get focus areas for a specific athlete"""
        # Mock implementation - in real app, this would come from athlete profiles or feedback
        return ["shooting", "conditioning", "ball_handling"]
    
    def _get_suitable_drills(self, criteria: Dict[str, Any]) -> List[DrillConfiguration]:
        """Get drills matching specific criteria"""
        # This would filter the available drills based on provided criteria
        # Mock implementation
        return []
    
    @abstractmethod
    async def build(self, team_id: str, date: datetime.date, coach_id: str) -> TrainingSession:
        """Build a session based on the builder's strategy"""
        pass


class RecoverySessionBuilder(SessionBuilder):
    """Builder for recovery-focused sessions"""
    
    async def build(self, team_id: str, date: datetime.date, coach_id: str) -> TrainingSession:
        """Build a recovery-focused session"""
        await self.initialize(team_id)
        
        # Create basic session structure
        session = {
            "id": f"session_{date.isoformat()}_{team_id}",
            "team_id": team_id,
            "date": date,
            "start_time": datetime.time(9, 0),  # 9:00 AM
            "end_time": datetime.time(10, 30),  # 10:30 AM
            "time_slot": "Morning",
            "location": "Main Training Facility",
            "coach_ids": [coach_id],
            "session_type": "Recovery",
            "focus_areas": ["recovery", "mobility", "light_skills"],
        }
        
        # Add recovery-focused activities
        activities = self._generate_recovery_activities()
        session["activities"] = activities
        
        # In a real implementation, we would persist to database
        return TrainingSession(**session)
    
    def _generate_recovery_activities(self) -> List[Dict[str, Any]]:
        """Generate recovery-focused activities"""
        return [
            {
                "name": "Light Shooting Drills",
                "duration_minutes": 15,
                "description": "Low-intensity shooting drills with focus on form",
                "intensity_level": 2,
                "equipment_needed": ["basketballs", "shooting_targets"]
            },
            {
                "name": "Mobility Circuit",
                "duration_minutes": 20,
                "description": "Dynamic stretching and mobility exercises",
                "intensity_level": 1,
                "equipment_needed": ["yoga_mats", "resistance_bands"]
            },
            {
                "name": "Recovery Swimming",
                "duration_minutes": 25,
                "description": "Light swimming session for active recovery",
                "intensity_level": 2,
                "equipment_needed": []
            },
            {
                "name": "Team Film Review",
                "duration_minutes": 30,
                "description": "Review recent games with minimal physical activity",
                "intensity_level": 1,
                "equipment_needed": ["projector", "whiteboards"]
            }
        ]


class IntensiveSessionBuilder(SessionBuilder):
    """Builder for high-intensity sessions"""
    
    async def build(self, team_id: str, date: datetime.date, coach_id: str) -> TrainingSession:
        """Build an intensive training session"""
        await self.initialize(team_id)
        
        # Create basic session structure
        session = {
            "id": f"session_{date.isoformat()}_{team_id}",
            "team_id": team_id,
            "date": date,
            "start_time": datetime.time(15, 0),  # 3:00 PM
            "end_time": datetime.time(17, 0),  # 5:00 PM
            "time_slot": "Afternoon",
            "location": "Main Training Facility",
            "coach_ids": [coach_id],
            "session_type": "Intensive",
            "focus_areas": ["conditioning", "team_defense", "transition"],
        }
        
        # Add high-intensity activities
        activities = self._generate_intensive_activities()
        session["activities"] = activities
        
        # In a real implementation, we would persist to database
        return TrainingSession(**session)
    
    def _generate_intensive_activities(self) -> List[Dict[str, Any]]:
        """Generate high-intensity activities"""
        return [
            {
                "name": "Full-Court Transition Drill",
                "duration_minutes": 20,
                "description": "High-intensity 3v2 and 2v1 transition situations",
                "intensity_level": 5,
                "equipment_needed": ["basketballs", "pinnies", "shot_clock"]
            },
            {
                "name": "Defensive Shell Drill",
                "duration_minutes": 25,
                "description": "Intense defensive rotations and communication work",
                "intensity_level": 4,
                "equipment_needed": ["basketballs", "cones"]
            },
            {
                "name": "Conditioning Circuit",
                "duration_minutes": 15,
                "description": "High-intensity interval training specific to basketball",
                "intensity_level": 5,
                "equipment_needed": ["agility_ladders", "cones", "resistance_bands"]
            },
            {
                "name": "5v5 Scrimmage",
                "duration_minutes": 30,
                "description": "Full-court scrimmage with specific situational focus",
                "intensity_level": 5,
                "equipment_needed": ["basketballs", "pinnies", "shot_clock"]
            },
            {
                "name": "Shooting Under Fatigue",
                "duration_minutes": 15,
                "description": "High-volume shooting drills under fatigue conditions",
                "intensity_level": 4,
                "equipment_needed": ["basketballs", "rebounding_machine"]
            }
        ]


class SkillDevelopmentSessionBuilder(SessionBuilder):
    """Builder for skill development sessions"""
    
    async def build(self, team_id: str, date: datetime.date, coach_id: str) -> TrainingSession:
        """Build a skill development session"""
        await self.initialize(team_id)
        
        # In real implementation, we would analyze athlete needs
        focus_areas = self._determine_focus_areas()
        
        # Create basic session structure
        session = {
            "id": f"session_{date.isoformat()}_{team_id}",
            "team_id": team_id,
            "date": date,
            "start_time": datetime.time(10, 0),  # 10:00 AM
            "end_time": datetime.time(12, 0),  # 12:00 PM
            "time_slot": "Morning",
            "location": "Development Center",
            "coach_ids": [coach_id],
            "session_type": "Skill Development",
            "focus_areas": focus_areas,
        }
        
        # Add skill development activities
        activities = self._generate_skill_activities(focus_areas)
        session["activities"] = activities
        
        # In a real implementation, we would persist to database
        return TrainingSession(**session)
    
    def _determine_focus_areas(self) -> List[str]:
        """Determine the focus areas based on athlete needs"""
        # This would analyze athlete data, recent performance, etc.
        if self.focus_players:
            # If we have focus players, get their development needs
            areas = []
            for player_id in self.focus_players:
                areas.extend(self._get_athlete_focus_areas(player_id))
            # Return unique areas
            return list(set(areas))
        
        # Default focus areas if no specific players
        return ["shooting", "ball_handling", "decision_making"]
    
    def _generate_skill_activities(self, focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Generate skill development activities based on focus areas"""
        activities = []
        
        if "shooting" in focus_areas:
            activities.append({
                "name": "Form Shooting Progression",
                "duration_minutes": 20,
                "description": "Progressive shooting drills focusing on mechanics",
                "intensity_level": 3,
                "equipment_needed": ["basketballs", "shooting_targets"]
            })
            
        if "ball_handling" in focus_areas:
            activities.append({
                "name": "Advanced Dribbling Circuit",
                "duration_minutes": 15,
                "description": "Complex ball handling drills with pressure",
                "intensity_level": 3,
                "equipment_needed": ["basketballs", "cones", "tennis_balls"]
            })
            
        if "decision_making" in focus_areas:
            activities.append({
                "name": "Read and React Situations",
                "duration_minutes": 25,
                "description": "Small-sided games requiring quick decisions",
                "intensity_level": 4,
                "equipment_needed": ["basketballs", "cones", "whiteboards"]
            })
        
        # Add some standard activities
        activities.extend([
            {
                "name": "Position-Specific Skill Work",
                "duration_minutes": 30,
                "description": "Breakout groups by position for targeted skill development",
                "intensity_level": 3,
                "equipment_needed": ["basketballs", "training_aids"]
            },
            {
                "name": "Application Scrimmage",
                "duration_minutes": 20,
                "description": "Controlled scrimmage to apply skills in game situations",
                "intensity_level": 4,
                "equipment_needed": ["basketballs", "pinnies", "whistle"]
            }
        ])
        
        return activities


class SessionTemplate:
    """
    Template for creating training sessions with predefined structure
    """
    
    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        default_duration_minutes: int,
        sections: List[Dict[str, Any]],
        suitable_for: List[str],
        difficulty: DifficultyLevel,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a session template
        
        Args:
            template_id: Unique identifier
            name: Template name
            description: Template description
            default_duration_minutes: Default total duration
            sections: List of session sections with timing and purpose
            suitable_for: List of team types this template is suitable for
            difficulty: Overall difficulty level
            metadata: Additional metadata
        """
        self.template_id = template_id
        self.name = name
        self.description = description
        self.default_duration_minutes = default_duration_minutes
        self.sections = sections
        self.suitable_for = suitable_for
        self.difficulty = difficulty
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "default_duration_minutes": self.default_duration_minutes,
            "sections": self.sections,
            "suitable_for": self.suitable_for,
            "difficulty": self.difficulty,
            "metadata": self.metadata
        }


class SessionGoal:
    """
    Represents a specific goal for a training session
    """
    
    def __init__(
        self,
        primary_focus: TrainingFocus,
        secondary_focus: Optional[TrainingFocus] = None,
        skill_emphasis: Optional[str] = None,
        description: str = ""
    ):
        """
        Initialize a session goal
        
        Args:
            primary_focus: Primary training focus
            secondary_focus: Secondary training focus
            skill_emphasis: Specific skill to emphasize
            description: Detailed goal description
        """
        self.primary_focus = primary_focus
        self.secondary_focus = secondary_focus
        self.skill_emphasis = skill_emphasis
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "primary_focus": self.primary_focus,
            "secondary_focus": self.secondary_focus,
            "skill_emphasis": self.skill_emphasis,
            "description": self.description
        }


class SessionParameters:
    """Parameters for session generation"""
    def __init__(
        self,
        team_id: str,
        duration_minutes: int = 90,
        skill_level: SkillLevel = SkillLevel.INTERMEDIATE,
        age_group: AgeGroup = AgeGroup.SENIOR,
        focus_areas: Optional[List[DrillFocus]] = None,
        intensity: DrillIntensity = DrillIntensity.MEDIUM,
        player_count: int = 20,
        include_warmup: bool = True,
        include_cooldown: bool = True,
        date: Optional[datetime] = None,
        coach_id: str = None,
        custom_parameters: Optional[Dict[str, Any]] = None
    ):
        self.team_id = team_id
        self.duration_minutes = duration_minutes
        self.skill_level = skill_level
        self.age_group = age_group
        self.focus_areas = focus_areas or []
        self.intensity = intensity
        self.player_count = player_count
        self.include_warmup = include_warmup
        self.include_cooldown = include_cooldown
        self.date = date or datetime.utcnow() + timedelta(days=1)
        self.coach_id = coach_id
        self.custom_parameters = custom_parameters or {}


class SessionBuilder:
    """Service for building automated training sessions"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.drill_service = DrillService(db_session)
    
    async def generate_session(self, params: SessionParameters) -> Dict[str, Any]:
        """Generate a new training session based on provided parameters"""
        session_id = str(uuid.uuid4())
        
        # Initialize session structure
        session = {
            "session_id": session_id,
            "team_id": params.team_id,
            "coach_id": params.coach_id,
            "title": f"Training Session - {params.date.strftime('%Y-%m-%d')}",
            "date": params.date.isoformat(),
            "duration_minutes": params.duration_minutes,
            "skill_level": params.skill_level.value,
            "age_group": params.age_group.value,
            "intensity": params.intensity.value,
            "player_count": params.player_count,
            "focus_areas": [area.value for area in params.focus_areas],
            "segments": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "draft",
            "custom_parameters": params.custom_parameters
        }
        
        # Calculate time allocation for session segments
        time_allocations = self._calculate_time_allocations(params)
        
        # Build warmup segment if requested
        if params.include_warmup:
            warmup = await self._build_warmup_segment(params)
            session["segments"].append(warmup)
        
        # Build main segments based on focus areas
        main_segments = await self._build_main_segments(params, time_allocations)
        session["segments"].extend(main_segments)
        
        # Build cooldown segment if requested
        if params.include_cooldown:
            cooldown = await self._build_cooldown_segment(params)
            session["segments"].append(cooldown)
        
        # Store the session in the database
        # In a real implementation, you would save this to a session table
        
        return session
    
    def _calculate_time_allocations(self, params: SessionParameters) -> Dict[str, int]:
        """Calculate time allocation for each session segment"""
        total_minutes = params.duration_minutes
        allocations = {}
        
        # Basic allocation:
        # - Warmup: 15% of total time
        # - Cooldown: 10% of total time
        # - Main segments: Remaining time split among focus areas
        
        if params.include_warmup:
            allocations["warmup"] = int(total_minutes * 0.15)
            total_minutes -= allocations["warmup"]
        
        if params.include_cooldown:
            allocations["cooldown"] = int(total_minutes * 0.1)
            total_minutes -= allocations["cooldown"]
        
        # Split remaining time among focus areas
        focus_count = max(1, len(params.focus_areas))
        minutes_per_focus = total_minutes // focus_count
        
        for i, focus in enumerate(params.focus_areas):
            # Last focus area gets any remaining minutes
            if i == focus_count - 1:
                allocations[focus.value] = total_minutes
            else:
                allocations[focus.value] = minutes_per_focus
                total_minutes -= minutes_per_focus
        
        # If no focus areas specified, allocate all to "general"
        if not params.focus_areas:
            allocations["general"] = total_minutes
        
        return allocations
    
    async def _build_warmup_segment(self, params: SessionParameters) -> Dict[str, Any]:
        """Build the warmup segment of the session"""
        # In a real implementation, you would query the database for suitable warmup drills
        search_params = {
            "categories": [DrillCategory.WARMUP],
            "intensity": DrillIntensity.LOW,
            "skill_level": params.skill_level,
            "age_group": params.age_group,
            "player_count": params.player_count,
            "page": 1,
            "page_size": 5
        }
        
        # This is a simplified implementation
        # In a real-world scenario, you would use a more sophisticated selection algorithm
        
        return {
            "segment_id": str(uuid.uuid4()),
            "type": "warmup",
            "title": "Warm-up",
            "duration_minutes": self._calculate_time_allocations(params).get("warmup", 15),
            "drills": [],  # In a real implementation, this would contain actual drill data
            "notes": "Start with light cardio and dynamic stretching"
        }
    
    async def _build_main_segments(self, params: SessionParameters, time_allocations: Dict[str, int]) -> List[Dict[str, Any]]:
        """Build the main segments of the session based on focus areas"""
        segments = []
        
        # If no focus areas specified, create a general segment
        if not params.focus_areas:
            general_segment = {
                "segment_id": str(uuid.uuid4()),
                "type": "main",
                "title": "Main Training",
                "duration_minutes": time_allocations.get("general", 60),
                "drills": [],  # In a real implementation, this would contain actual drill data
                "notes": "General training activities"
            }
            segments.append(general_segment)
            return segments
        
        # Create a segment for each focus area
        for focus_area in params.focus_areas:
            segment = {
                "segment_id": str(uuid.uuid4()),
                "type": "main",
                "title": f"{focus_area.value.capitalize()} Training",
                "duration_minutes": time_allocations.get(focus_area.value, 20),
                "focus": focus_area.value,
                "drills": [],  # In a real implementation, this would contain actual drill data
                "notes": f"Drills focused on {focus_area.value}"
            }
            segments.append(segment)
        
        return segments
    
    async def _build_cooldown_segment(self, params: SessionParameters) -> Dict[str, Any]:
        """Build the cooldown segment of the session"""
        # Similar to warmup, this would query for suitable cooldown drills
        
        return {
            "segment_id": str(uuid.uuid4()),
            "type": "cooldown",
            "title": "Cool-down",
            "duration_minutes": self._calculate_time_allocations(params).get("cooldown", 10),
            "drills": [],  # In a real implementation, this would contain actual drill data
            "notes": "Finish with static stretching and light recovery activities"
        }
    
    async def populate_segment_drills(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Populate drills for each segment based on segment parameters"""
        updated_segments = []
        
        for segment in session["segments"]:
            segment_type = segment["type"]
            duration = segment["duration_minutes"]
            
            # Search parameters will vary based on segment type
            search_params = {
                "page": 1,
                "page_size": 10
            }
            
            if segment_type == "warmup":
                search_params["categories"] = [DrillCategory.WARMUP]
                search_params["intensity"] = DrillIntensity.LOW
            elif segment_type == "cooldown":
                search_params["categories"] = [DrillCategory.RECOVERY]
                search_params["intensity"] = DrillIntensity.LOW
            else:  # Main segment
                if "focus" in segment:
                    # Convert string focus to enum
                    focus_enum = DrillFocus(segment["focus"])
                    search_params["focus_areas"] = [focus_enum]
                
                search_params["intensity"] = DrillIntensity(session["intensity"])
            
            # Additional common parameters
            search_params["skill_level"] = SkillLevel(session["skill_level"])
            search_params["age_group"] = AgeGroup(session["age_group"])
            search_params["player_count"] = session["player_count"]
            
            # In a real implementation, you would query the database for matching drills
            # and select an appropriate subset based on total duration and other factors
            
            # This is a placeholder - in a real implementation, this would contain actual drill data
            segment["drills"] = []
            
            updated_segments.append(segment)
        
        session["segments"] = updated_segments
        return session
    
    async def save_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Save the generated session to the database"""
        # In a real implementation, you would save the session to a database table
        
        # This is a simplified implementation
        # Normally you would create a SessionModel and save it to the database
        
        session["status"] = "saved"
        session["updated_at"] = datetime.utcnow().isoformat()
        
        return session
    
    async def publish_session(self, session_id: str) -> Dict[str, Any]:
        """Publish a session, making it visible to team members"""
        # In a real implementation, you would retrieve the session from the database,
        # update its status, and save it back
        
        # This is a simplified placeholder
        return {
            "session_id": session_id,
            "status": "published",
            "updated_at": datetime.utcnow().isoformat()
        }


async def generate_session_plan(
    db_session: AsyncSession,
    session_type: str,
    team_id: str,
    date: datetime.date,
    coach_id: str,
    focus_players: List[str] = None
) -> TrainingSession:
    """
    Auto-generates session based on team needs
    
    Args:
        db_session: Database session
        session_type: Type of session to create (recovery, intensive, skills)
        team_id: Team ID
        date: Session date
        coach_id: Coach ID
        focus_players: List of athlete IDs to focus on (optional)
        
    Returns:
        A TrainingSession object
    """
    if session_type.lower() == "recovery":
        builder = RecoverySessionBuilder(db_session, focus_players)
        return await builder.build(team_id, date, coach_id)
    
    elif session_type.lower() == "intensive":
        builder = IntensiveSessionBuilder(db_session, focus_players)
        return await builder.build(team_id, date, coach_id)
    
    elif session_type.lower() in ["skills", "skill_development"]:
        builder = SkillDevelopmentSessionBuilder(db_session, focus_players)
        return await builder.build(team_id, date, coach_id)
    
    else:
        raise ValueError(f"Unsupported session type: {session_type}") 