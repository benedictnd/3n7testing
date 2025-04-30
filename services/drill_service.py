from typing import Dict, List, Optional, Any, Union
from fastapi import HTTPException, status
from sqlalchemy import select, or_, and_, count, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from pydantic import ValidationError
from datetime import datetime
import uuid
import logging
import json

from models.drill_configuration import (
    DrillConfiguration, 
    DrillSearchParams,
    DrillCategory,
    DrillFocus,
    SkillLevel,
    AgeGroup,
    DrillIntensity,
    TeamType,
    Equipment,
    DrillDB
)

# Assuming there's a database model for DrillConfiguration
from database.models import DrillConfig as DrillConfigDB
from database.models import DrillTag as DrillTagDB


logger = logging.getLogger(__name__)


class DrillService:
    """Service for managing drill configurations"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create_drill(self, drill_config: DrillConfiguration, user_id: str) -> Dict[str, Any]:
        """Create a new drill configuration"""
        # Set the created_by field to the user_id
        drill_config.created_by = user_id
        
        # Create a new DB entry
        drill_db = DrillDB(
            id=drill_config.drill_id,
            configuration=drill_config.dict(),
            created_by=user_id
        )
        
        self.db_session.add(drill_db)
        await self.db_session.commit()
        await self.db_session.refresh(drill_db)
        
        return drill_config.dict()
    
    async def get_drill(self, drill_id: str) -> Dict[str, Any]:
        """Get a drill configuration by ID"""
        result = await self.db_session.execute(
            select(DrillDB).where(DrillDB.id == drill_id)
        )
        
        drill_db = result.scalars().first()
        
        if not drill_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drill with ID {drill_id} not found"
            )
            
        return DrillConfiguration(**drill_db.configuration).dict()
    
    async def update_drill(self, drill_id: str, drill_config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update an existing drill configuration"""
        result = await self.db_session.execute(
            select(DrillDB).where(DrillDB.id == drill_id)
        )
        
        drill_db = result.scalars().first()
        
        if not drill_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drill with ID {drill_id} not found"
            )
            
        # Check if user is the creator or has admin/coach role (implement role check in route handler)
        if drill_db.created_by != user_id:
            # The permission check for admin/coach will be done at the route level
            pass
            
        # Update configuration
        current_config = drill_db.configuration
        current_config.update(drill_config)
        current_config["updated_at"] = datetime.utcnow().isoformat()
        
        drill_db.configuration = current_config
        drill_db.updated_at = datetime.utcnow()
        
        await self.db_session.commit()
        await self.db_session.refresh(drill_db)
        
        return DrillConfiguration(**drill_db.configuration).dict()
    
    async def delete_drill(self, drill_id: str, user_id: str) -> bool:
        """Delete a drill configuration"""
        result = await self.db_session.execute(
            select(DrillDB).where(DrillDB.id == drill_id)
        )
        
        drill_db = result.scalars().first()
        
        if not drill_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drill with ID {drill_id} not found"
            )
            
        # Check if user is the creator or has admin role (implement role check in route handler)
        if drill_db.created_by != user_id:
            # The permission check for admin will be done at the route level
            pass
            
        await self.db_session.delete(drill_db)
        await self.db_session.commit()
        
        return True
    
    async def search_drills(self, search_params: DrillSearchParams, user_id: str) -> Dict[str, Any]:
        """Search for drill configurations based on criteria"""
        # Start with a base query
        query = select(DrillDB)
        
        # Apply filters based on search parameters
        if search_params.categories:
            # We need to filter by checking the JSON configuration field
            category_conditions = []
            for category in search_params.categories:
                category_conditions.append(f"configuration->>'category' = '{category.value}'")
            
            if category_conditions:
                query = query.where(text(" OR ".join(category_conditions)))
        
        # Similar filters would be applied for other search parameters
        # This is a simplified implementation - in a real-world scenario,
        # we would need to add more sophisticated JSON filtering based on your database
        
        # Apply pagination
        query = query.limit(search_params.page_size).offset((search_params.page - 1) * search_params.page_size)
        
        # Execute query
        result = await self.db_session.execute(query)
        drills = result.scalars().all()
        
        # Count total matches for pagination info
        count_query = select(func.count()).select_from(DrillDB)
        # Apply the same filters as the main query
        count_result = await self.db_session.execute(count_query)
        total_count = count_result.scalar()
        
        # Format the results
        drill_list = [DrillConfiguration(**drill.configuration).dict() for drill in drills]
        
        return {
            "items": drill_list,
            "total": total_count,
            "page": search_params.page,
            "page_size": search_params.page_size,
            "pages": (total_count + search_params.page_size - 1) // search_params.page_size
        }
    
    async def get_categories(self) -> List[str]:
        """Get list of available drill categories"""
        return [category.value for category in DrillCategory]
    
    async def get_focus_areas(self) -> List[str]:
        """Get list of available focus areas"""
        return [focus.value for focus in DrillFocus]
    
    async def get_skill_levels(self) -> List[str]:
        """Get list of available skill levels"""
        return [level.value for level in SkillLevel]
    
    async def get_age_groups(self) -> List[str]:
        """Get list of available age groups"""
        return [group.value for group in AgeGroup]
    
    async def get_intensity_levels(self) -> List[str]:
        """Get list of available intensity levels"""
        return [level.value for level in DrillIntensity]
    
    def _apply_complex_filters(
        self, 
        drill_list: List[Dict[str, Any]], 
        search_params: DrillSearchParams
    ) -> List[Dict[str, Any]]:
        """Apply filters that require examining the JSON configuration"""
        result = []
        
        for drill in drill_list:
            # Skip this drill if it doesn't pass all filters
            include_drill = True
            
            # Focus areas filter
            if search_params.focus_areas and include_drill:
                # Convert string values to enum values for comparison
                drill_focus_areas = drill.get("focus_areas", [])
                param_focus_areas = [area.value for area in search_params.focus_areas]
                
                # Check if any focus area matches
                if not any(area in param_focus_areas for area in drill_focus_areas):
                    include_drill = False
            
            # Skill level filter
            if search_params.skill_levels and include_drill:
                drill_skill_levels = drill.get("skill_level", [])
                param_skill_levels = [level.value for level in search_params.skill_levels]
                
                if not any(level in param_skill_levels for level in drill_skill_levels):
                    include_drill = False
            
            # Age groups filter
            if search_params.age_groups and include_drill:
                drill_age_groups = drill.get("suitable_age_groups", [])
                param_age_groups = [group.value for group in search_params.age_groups]
                
                if not any(group in param_age_groups for group in drill_age_groups):
                    include_drill = False
            
            # Team types filter
            if search_params.team_types and include_drill:
                drill_team_types = drill.get("team_type", [])
                param_team_types = [team_type.value for team_type in search_params.team_types]
                
                if not any(team_type in param_team_types for team_type in drill_team_types):
                    include_drill = False
            
            # Equipment requirements filter
            if search_params.equipment and include_drill:
                drill_equipment = drill.get("required_equipment", [])
                param_equipment = [equip.value for equip in search_params.equipment]
                
                # Check if all required equipment is present
                if not all(equip in drill_equipment for equip in param_equipment):
                    include_drill = False
            
            # Equipment exclusion filter
            if search_params.exclude_equipment and include_drill:
                drill_equipment = drill.get("required_equipment", [])
                exclude_equipment = [equip.value for equip in search_params.exclude_equipment]
                
                # Check if any excluded equipment is present
                if any(equip in drill_equipment for equip in exclude_equipment):
                    include_drill = False
            
            # Intensity filter
            if search_params.intensity and include_drill:
                drill_intensity = drill.get("intensity")
                param_intensities = [intensity.value for intensity in search_params.intensity]
                
                if drill_intensity not in param_intensities:
                    include_drill = False
            
            # If the drill passed all filters, include it
            if include_drill:
                result.append(drill)
        
        return result 