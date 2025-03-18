from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from dependencies.auth import get_current_user, get_user_role, has_role
from dependencies.database import get_db_session
from models.user import UserResponse, UserDetail, UserUpdate, UserList
from services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


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