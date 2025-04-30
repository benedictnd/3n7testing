from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
import uuid

from models.drill_configuration import (
    DrillConfiguration, 
    DrillSearchParams,
    DrillCategory,
    DrillFocus,
    SkillLevel,
    AgeGroup,
    DrillIntensity
)
from dependencies.auth import get_current_user
from dependencies.database import get_db_session
from services.drill_service import DrillService

router = APIRouter(
    prefix="/drills",
    tags=["drills"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_drill(
    drill_data: dict,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new drill configuration.
    
    Only coaches and administrators can create drills.
    """
    # Check user role permissions
    if not any(role in ["coach", "admin", "superadmin"] for role in current_user.get("roles", [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches and administrators can create drills"
        )
        
    # If no ID provided, generate one
    if "drill_id" not in drill_data:
        drill_data["drill_id"] = str(uuid.uuid4())
        
    drill_service = DrillService(db_session)
    result = await drill_service.create_drill(drill_data, current_user["id"])
    return result

@router.get("/{drill_id}")
async def get_drill(
    drill_id: str,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a drill configuration by ID"""
    drill_service = DrillService(db_session)
    result = await drill_service.get_drill(drill_id)
    return result

@router.put("/{drill_id}")
async def update_drill(
    drill_id: str,
    drill_data: dict,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update an existing drill configuration.
    
    Users can only update drills they created unless they are administrators.
    """
    drill_service = DrillService(db_session)
    result = await drill_service.update_drill(drill_id, drill_data, current_user["id"])
    return result

@router.delete("/{drill_id}")
async def delete_drill(
    drill_id: str,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a drill configuration.
    
    Users can only delete drills they created unless they are administrators.
    """
    drill_service = DrillService(db_session)
    result = await drill_service.delete_drill(drill_id, current_user["id"])
    return result

@router.post("/search")
async def search_drills(
    search_params: DrillSearchParams,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search for drills based on various criteria"""
    drill_service = DrillService(db_session)
    result = await drill_service.search_drills(search_params)
    return result

@router.get("/categories")
async def list_categories() -> Dict[str, List[str]]:
    """Get all available drill categories"""
    return {
        "categories": [category.value for category in DrillCategory]
    }

@router.get("/focus-areas")
async def list_focus_areas() -> Dict[str, List[str]]:
    """Get all available drill focus areas"""
    return {
        "focus_areas": [focus.value for focus in DrillFocus]
    }

@router.get("/skill-levels")
async def list_skill_levels() -> Dict[str, List[str]]:
    """Get all available skill levels"""
    return {
        "skill_levels": [level.value for level in SkillLevel]
    }

@router.get("/age-groups")
async def list_age_groups() -> Dict[str, List[str]]:
    """Get all available age groups"""
    return {
        "age_groups": [group.value for group in AgeGroup]
    }

@router.get("/intensity-levels")
async def list_intensity_levels() -> Dict[str, List[str]]:
    """Get all available intensity levels"""
    return {
        "intensity_levels": [intensity.value for intensity in DrillIntensity]
    } 