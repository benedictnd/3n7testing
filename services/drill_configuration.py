from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
import json
import uuid


class DifficultyLevel(str, Enum):
    """Difficulty levels for drills"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"
    CUSTOM = "custom"


class TrainingFocus(str, Enum):
    """Training focus areas"""
    SHOOTING = "shooting"
    DRIBBLING = "dribbling"
    PASSING = "passing"
    DEFENSE = "defense"
    CONDITIONING = "conditioning"
    TEAMWORK = "teamwork"
    TACTICS = "tactics"
    MENTAL = "mental"
    RECOVERY = "recovery"


class ProgressionType(str, Enum):
    """Types of progressions for drills"""
    LINEAR = "linear"  # Fixed progression through stages
    ADAPTIVE = "adaptive"  # Adjusts based on performance
    BRANCHING = "branching"  # Multiple paths based on outcomes
    CUSTOM = "custom"  # Custom progression logic


class DrillParameter:
    """
    Parameter for configuring drills with validation
    """
    
    def __init__(
        self,
        name: str,
        data_type: type,
        description: str,
        default_value: Any,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        choices: Optional[List[Any]] = None,
        required: bool = False,
        validator: Optional[Callable[[Any], bool]] = None
    ):
        """
        Initialize a drill parameter
        
        Args:
            name: Parameter name
            data_type: Python type of the parameter
            description: Description of what the parameter controls
            default_value: Default value if not specified
            min_value: Minimum allowed value (for numeric types)
            max_value: Maximum allowed value (for numeric types)
            choices: List of allowed values (for enum-like parameters)
            required: Whether this parameter must be specified
            validator: Optional custom validation function
        """
        self.name = name
        self.data_type = data_type
        self.description = description
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.choices = choices
        self.required = required
        self.validator = validator
    
    def validate(self, value: Any) -> bool:
        """
        Validate a value for this parameter
        
        Args:
            value: The value to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Check type
        if not isinstance(value, self.data_type):
            raise ValueError(f"Parameter '{self.name}' must be of type {self.data_type.__name__}")
        
        # Check numeric bounds
        if (self.min_value is not None and 
            isinstance(value, (int, float)) and 
            value < self.min_value):
            raise ValueError(f"Parameter '{self.name}' must be at least {self.min_value}")
            
        if (self.max_value is not None and 
            isinstance(value, (int, float)) and 
            value > self.max_value):
            raise ValueError(f"Parameter '{self.name}' must be at most {self.max_value}")
        
        # Check choices
        if self.choices is not None and value not in self.choices:
            raise ValueError(f"Parameter '{self.name}' must be one of {self.choices}")
        
        # Apply custom validator if provided
        if self.validator is not None and not self.validator(value):
            raise ValueError(f"Parameter '{self.name}' failed custom validation")
        
        return True


class DrillVariant:
    """
    A variant of a drill with specific parameters
    """
    
    def __init__(
        self,
        variant_id: str,
        name: str,
        description: str,
        difficulty: DifficultyLevel,
        parameters: Dict[str, Any],
        focus_areas: List[TrainingFocus]
    ):
        """
        Initialize a drill variant
        
        Args:
            variant_id: Unique identifier for this variant
            name: Name of the variant
            description: Description of what makes this variant unique
            difficulty: Difficulty level of this variant
            parameters: Parameters specific to this variant
            focus_areas: Training focus areas addressed by this variant
        """
        self.variant_id = variant_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.parameters = parameters
        self.focus_areas = focus_areas
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation of this variant
        """
        return {
            "variant_id": self.variant_id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "parameters": self.parameters,
            "focus_areas": self.focus_areas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DrillVariant':
        """
        Create from dictionary representation
        
        Args:
            data: Dictionary representation
            
        Returns:
            New DrillVariant instance
        """
        return cls(
            variant_id=data["variant_id"],
            name=data["name"],
            description=data["description"],
            difficulty=data["difficulty"],
            parameters=data["parameters"],
            focus_areas=data["focus_areas"]
        )


class DrillProgression:
    """
    Defines how a drill progresses through different stages
    """
    
    def __init__(
        self,
        progression_id: str,
        name: str,
        description: str,
        progression_type: ProgressionType,
        stages: List[Dict[str, Any]],
        advancement_criteria: Dict[str, Any] = None
    ):
        """
        Initialize a drill progression
        
        Args:
            progression_id: Unique identifier for this progression
            name: Name of the progression
            description: Description of the progression
            progression_type: Type of progression
            stages: List of stages in this progression
            advancement_criteria: Criteria for advancing between stages
        """
        self.progression_id = progression_id
        self.name = name
        self.description = description
        self.progression_type = progression_type
        self.stages = stages
        self.advancement_criteria = advancement_criteria or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation of this progression
        """
        return {
            "progression_id": self.progression_id,
            "name": self.name,
            "description": self.description,
            "progression_type": self.progression_type,
            "stages": self.stages,
            "advancement_criteria": self.advancement_criteria
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DrillProgression':
        """
        Create from dictionary representation
        
        Args:
            data: Dictionary representation
            
        Returns:
            New DrillProgression instance
        """
        return cls(
            progression_id=data["progression_id"],
            name=data["name"],
            description=data["description"],
            progression_type=data["progression_type"],
            stages=data["stages"],
            advancement_criteria=data.get("advancement_criteria", {})
        )


class DrillConfiguration:
    """
    Configuration for a training drill with variants and progressions
    """
    
    def __init__(
        self,
        drill_id: str,
        name: str,
        description: str,
        category: str,
        default_duration_minutes: int,
        min_players: int,
        max_players: int,
        equipment: List[str],
        space_requirements: str,
        parameters: Dict[str, DrillParameter],
        variants: List[DrillVariant] = None,
        progressions: List[DrillProgression] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a drill configuration
        
        Args:
            drill_id: Unique identifier for this drill
            name: Name of the drill
            description: Description of the drill
            category: Category of the drill
            default_duration_minutes: Default duration in minutes
            min_players: Minimum number of players required
            max_players: Maximum number of players supported
            equipment: List of required equipment
            space_requirements: Description of space needed
            parameters: Configurable parameters for this drill
            variants: Predefined variants of this drill
            progressions: Progression options for this drill
            metadata: Additional metadata
        """
        self.drill_id = drill_id
        self.name = name
        self.description = description
        self.category = category
        self.default_duration_minutes = default_duration_minutes
        self.min_players = min_players
        self.max_players = max_players
        self.equipment = equipment
        self.space_requirements = space_requirements
        self.parameters = parameters
        self.variants = variants or []
        self.progressions = progressions or []
        self.metadata = metadata or {}
    
    def add_variant(self, variant: DrillVariant) -> None:
        """
        Add a variant to this drill
        
        Args:
            variant: The variant to add
        """
        # Check for duplicate variant ID
        if any(v.variant_id == variant.variant_id for v in self.variants):
            raise ValueError(f"Variant with ID {variant.variant_id} already exists")
        
        # Validate variant parameters against drill parameters
        for param_name, param_value in variant.parameters.items():
            if param_name in self.parameters:
                self.parameters[param_name].validate(param_value)
            # Note: variants can include additional parameters not defined at the drill level
        
        self.variants.append(variant)
    
    def add_progression(self, progression: DrillProgression) -> None:
        """
        Add a progression to this drill
        
        Args:
            progression: The progression to add
        """
        # Check for duplicate progression ID
        if any(p.progression_id == progression.progression_id for p in self.progressions):
            raise ValueError(f"Progression with ID {progression.progression_id} already exists")
        
        self.progressions.append(progression)
    
    def create_instance(
        self,
        variant_id: Optional[str] = None,
        progression_id: Optional[str] = None,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a specific instance of this drill with selected variant and progression
        
        Args:
            variant_id: ID of variant to use (None for default)
            progression_id: ID of progression to use (None for default)
            custom_parameters: Custom parameter values
            
        Returns:
            Drill instance configuration
        """
        # Start with base parameters (default values)
        parameters = {name: param.default_value for name, param in self.parameters.items()}
        
        # Apply variant parameters if specified
        variant = None
        if variant_id:
            variant = next((v for v in self.variants if v.variant_id == variant_id), None)
            if not variant:
                raise ValueError(f"Variant with ID {variant_id} not found")
            
            # Update parameters with variant-specific values
            parameters.update(variant.parameters)
        
        # Apply progression if specified
        progression = None
        if progression_id:
            progression = next((p for p in self.progressions if p.progression_id == progression_id), None)
            if not progression:
                raise ValueError(f"Progression with ID {progression_id} not found")
        
        # Apply custom parameters, validating each one
        if custom_parameters:
            for name, value in custom_parameters.items():
                if name in self.parameters:
                    self.parameters[name].validate(value)
                    parameters[name] = value
                else:
                    raise ValueError(f"Unknown parameter: {name}")
        
        # Create the instance
        instance = {
            "instance_id": str(uuid.uuid4()),
            "drill_id": self.drill_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "duration_minutes": self.default_duration_minutes,
            "parameters": parameters,
            "equipment": self.equipment,
            "space_requirements": self.space_requirements,
            "created_at": None  # This would be set by the caller
        }
        
        # Add variant information if used
        if variant:
            instance["variant"] = {
                "variant_id": variant.variant_id,
                "name": variant.name,
                "difficulty": variant.difficulty,
                "focus_areas": variant.focus_areas
            }
        
        # Add progression information if used
        if progression:
            instance["progression"] = {
                "progression_id": progression.progression_id,
                "name": progression.name,
                "progression_type": progression.progression_type,
                "current_stage": 0,
                "stages": progression.stages,
                "advancement_criteria": progression.advancement_criteria
            }
        
        return instance
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary representation
        """
        # Convert parameters to a serializable format
        serialized_params = {}
        for name, param in self.parameters.items():
            serialized_params[name] = {
                "name": param.name,
                "data_type": param.data_type.__name__,
                "description": param.description,
                "default_value": param.default_value,
                "min_value": param.min_value,
                "max_value": param.max_value,
                "choices": param.choices,
                "required": param.required
                # Note: validator functions can't be serialized
            }
        
        return {
            "drill_id": self.drill_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "default_duration_minutes": self.default_duration_minutes,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "equipment": self.equipment,
            "space_requirements": self.space_requirements,
            "parameters": serialized_params,
            "variants": [v.to_dict() for v in self.variants],
            "progressions": [p.to_dict() for p in self.progressions],
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """
        Convert to JSON string
        
        Returns:
            JSON representation
        """
        return json.dumps(self.to_dict(), indent=2)


class DrillLibrary:
    """
    Manages a collection of drill configurations
    """
    
    def __init__(self):
        """
        Initialize an empty drill library
        """
        self.drills: Dict[str, DrillConfiguration] = {}
    
    def add_drill(self, drill: DrillConfiguration) -> None:
        """
        Add a drill to the library
        
        Args:
            drill: The drill configuration to add
        """
        if drill.drill_id in self.drills:
            raise ValueError(f"Drill with ID {drill.drill_id} already exists")
        
        self.drills[drill.drill_id] = drill
    
    def get_drill(self, drill_id: str) -> DrillConfiguration:
        """
        Get a drill by ID
        
        Args:
            drill_id: Drill ID
            
        Returns:
            Drill configuration
        """
        if drill_id not in self.drills:
            raise ValueError(f"Drill with ID {drill_id} not found")
            
        return self.drills[drill_id]
    
    def list_drills(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all drills with basic information
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of drill summaries
        """
        result = []
        for drill in self.drills.values():
            if category is None or drill.category == category:
                result.append({
                    "drill_id": drill.drill_id,
                    "name": drill.name,
                    "category": drill.category,
                    "description": drill.description,
                    "default_duration_minutes": drill.default_duration_minutes,
                    "min_players": drill.min_players,
                    "max_players": drill.max_players,
                    "variant_count": len(drill.variants),
                    "progression_count": len(drill.progressions)
                })
        
        return result
    
    def search_drills(
        self,
        text: Optional[str] = None,
        categories: Optional[List[str]] = None,
        focus_areas: Optional[List[TrainingFocus]] = None,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        difficulty: Optional[DifficultyLevel] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for drills matching criteria
        
        Args:
            text: Text to search for in name and description
            categories: Categories to include
            focus_areas: Focus areas to include
            min_players: Minimum number of players
            max_players: Maximum number of players
            difficulty: Difficulty level
            
        Returns:
            List of matching drill summaries
        """
        result = []
        
        for drill in self.drills.values():
            # Apply text search
            if text and text.lower() not in drill.name.lower() and text.lower() not in drill.description.lower():
                continue
            
            # Filter by category
            if categories and drill.category not in categories:
                continue
            
            # Filter by player count
            if min_players is not None and drill.max_players < min_players:
                continue
                
            if max_players is not None and drill.min_players > max_players:
                continue
            
            # Check for focus areas and difficulty via variants
            if focus_areas or difficulty:
                matching_variant = False
                
                for variant in drill.variants:
                    # Check focus areas
                    if focus_areas and not any(focus in variant.focus_areas for focus in focus_areas):
                        continue
                    
                    # Check difficulty
                    if difficulty and variant.difficulty != difficulty:
                        continue
                    
                    matching_variant = True
                    break
                
                if not matching_variant and (focus_areas or difficulty):
                    continue
            
            # Drill passed all filters, add to results
            result.append({
                "drill_id": drill.drill_id,
                "name": drill.name,
                "category": drill.category,
                "description": drill.description,
                "default_duration_minutes": drill.default_duration_minutes,
                "min_players": drill.min_players,
                "max_players": drill.max_players,
                "variant_count": len(drill.variants),
                "progression_count": len(drill.progressions)
            })
        
        return result
    
    def export_to_json(self, file_path: str) -> None:
        """
        Export the entire library to a JSON file
        
        Args:
            file_path: Path to save the JSON file
        """
        data = {
            "drills": {drill_id: drill.to_dict() for drill_id, drill in self.drills.items()}
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def import_from_json(cls, file_path: str) -> 'DrillLibrary':
        """
        Import a library from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            New DrillLibrary instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        library = cls()
        
        # This is a simplified version - a full implementation would need to
        # properly reconstruct the DrillParameter objects with their data types and validators
        
        # In a real implementation, you would need to handle converting serialized
        # parameter data types back to actual Python types
        
        # For now, we'll just issue a warning
        print("Warning: Imported drill library has limited functionality")
        print("Parameter validators and custom data types are not preserved")
        
        return library 