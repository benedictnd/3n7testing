from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr

from dependencies.auth import get_current_user, get_user_role, has_role, is_admin, validate_role_change
from dependencies.database import get_db_session
from models.user import UserResponse, UserDetail, UserUpdate, UserList, User as UserModel
from services.user_service import UserService
from sqlalchemy.future import select

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

class UserBase(BaseModel):
    email: EmailStr
    name: str
    
class UserCreate(UserBase):
    password: str
    role: str = "athlete"
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
class RoleUpdate(BaseModel):
    roles: List[str]
    
class User(UserBase):
    id: str
    role: str
    
    class Config:
        orm_mode = True


@router.get("/", response_model=UserList)
async def list_users(
    role: Optional[str] = Query(None, description="Filter users by role"),
    limit: int = Query(10, description="Number of users to return per page", ge=1, le=100),
    offset: int = Query(0, description="Number of users to skip", ge=0),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    List users with optional role filtering.
    Only coaches and administrators can list all users.
    """
    # Check if user has permission to list users
    if user_role not in ["coach", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view user list"
        )
    
    user_service = UserService(db_session)
    users = await user_service.get_users(role, limit, offset)
    
    return users


@router.get("/me", response_model=UserDetail)
async def get_current_user_profile(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Get the profile of the currently logged in user.
    """
    user_service = UserService(db_session)
    user = await user_service.get_user(current_user["id"])
    
    return user


@router.get("/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: str,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Get detailed information about a specific user.
    Users can view their own profile.
    Coaches can view their athletes' profiles.
    Administrators can view any profile.
    """
    # Check if user has permission to view this profile
    is_self = current_user["id"] == user_id
    is_coach = user_role == "coach"
    is_admin = user_role == "admin"
    
    if not (is_self or is_admin):
        if is_coach:
            # Check if this user is one of the coach's athletes
            # In real implementation, this would check coach-athlete relationships
            # For now, we'll allow coaches to view any athlete profile
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this user profile"
            )
    
    user_service = UserService(db_session)
    user = await user_service.get_user(user_id)
    
    return user


@router.put("/{user_id}", response_model=UserDetail)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    user_role: str = Depends(get_user_role),
):
    """
    Update a user's profile.
    Users can update their own profile.
    Administrators can update any profile.
    """
    # Check if user has permission to update this profile
    is_self = current_user["id"] == user_id
    is_admin = user_role == "admin"
    
    if not (is_self or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user profile"
        )
    
    user_service = UserService(db_session)
    updated_user = await user_service.update_user(user_id, user_data)
    
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    has_admin_role: bool = Depends(has_role("admin")),
):
    """
    Delete a user.
    Only administrators can delete users.
    """
    # Prevent admins from deleting themselves
    if current_user["id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete own account"
        )
    
    user_service = UserService(db_session)
    result = await user_service.delete_user(user_id)
    
    return result


@router.patch("/{user_id}/roles")
async def update_user_roles(
    user_id: str,
    role_data: RoleUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    has_admin_role: bool = Depends(has_role("admin")),
):
    """
    Update a user's roles
    
    This endpoint is protected against privilege escalation:
    1. Only admins can change roles
    2. Users cannot assign roles with higher privilege than their own
    3. Users cannot elevate their own privileges
    
    Args:
        user_id: ID of the user to update
        role_data: New roles data
        db_session: Database session
        current_user: Current authenticated user
        has_admin_role: Verified admin role check
        
    Returns:
        Updated user with new roles
    """
    user_service = UserService(db_session)
    
    # Get user to update
    user_to_update = await user_service.get_user(user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent self-promotion - block any attempt to modify own roles
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users cannot modify their own roles"
        )
    
    # Validate role elevation
    current_role_value = get_role_value(user_to_update.role)
    requested_role_value = max(get_role_value(role) for role in role_data.roles)
    admin_role_value = get_role_value(current_user["role"])
    
    # Admins can only assign roles with equal or lower privileges than their own
    if requested_role_value > admin_role_value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign a role with higher privileges than your own"
        )
    
    # Update the user's roles
    updated_user = await user_service.update_user_roles(user_id, role_data.roles, current_user["role"])
    
    return updated_user

def get_role_value(role: str) -> int:
    """Get numeric value for role hierarchy"""
    role_values = {
        "superadmin": 1000,
        "admin": 100,
        "coach": 50,
        "athlete": 10,
        "guest": 1
    }
    return role_values.get(role, 0)

@router.patch("/me/roles")
async def update_self_roles(
    role_data: RoleUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Update the current user's roles
    
    This endpoint prevents privilege escalation by:
    1. Blocking all self-role updates (users cannot change their own roles)
    
    Args:
        role_data: New roles data
        db_session: Database session
        current_user: Current authenticated user
        
    Returns:
        Error response - self role updates are not allowed
    """
    # Block all self-role updates to prevent privilege escalation
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Users cannot change their own roles"
    ) 