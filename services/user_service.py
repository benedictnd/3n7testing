from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import and_
from fastapi import HTTPException, status
from sqlalchemy.future import select
from pydantic import BaseModel

from models.user import UserUpdate, UserResponse, UserDetail, User
from models.database import User


class UserService:
    """Service for user-related operations with security controls"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
        # Define role hierarchy for permission checks
        self.role_hierarchy = {
            "superadmin": 1000,
            "admin": 100,
            "coach": 50,
            "athlete": 10,
            "guest": 1
        }
    
    async def get_users(self, role: Optional[str] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get list of users with optional role filtering"""
        query = select(User)
        
        # Apply role filter if provided
        if role:
            query = query.where(User.role == role)
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Get total count for pagination
        count_query = select(User)
        if role:
            count_query = count_query.where(User.role == role)
        
        # Execute queries
        result = await self.db_session.execute(query)
        count_result = await self.db_session.execute(count_query)
        
        users = result.scalars().all()
        total = len(count_result.scalars().all())
        
        return {
            "users": users,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        result = await self.db_session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """Update a user's profile information"""
        # Get user from database
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Update user fields
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        
        # Save changes
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        
        return user
    
    async def update_user_roles(self, user_id: str, roles: List[str], current_user_role: str) -> User:
        """
        Update a user's roles with security validation
        
        Args:
            user_id: ID of user to update
            roles: New roles to assign
            current_user_role: Role of the user making the change
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If role change is invalid or user not found
        """
        # Get user from database
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Security check: validate role change
        if not self._validate_role_change(user.role, roles, current_user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges for requested role change"
            )
        
        # Update user roles (support both single and multiple roles)
        if hasattr(user, 'roles'):
            # If model supports multiple roles
            user.roles = roles
        else:
            # If model supports only one role
            if roles and len(roles) > 0:
                user.role = roles[0]
        
        # Save changes
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: str) -> Dict[str, str]:
        """Delete a user"""
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        await self.db_session.delete(user)
        await self.db_session.commit()
        
        return {"message": f"User {user_id} deleted successfully"}
    
    def _validate_role_change(self, current_role: str, new_roles: List[str], admin_role: str) -> bool:
        """
        Validate if a role change is permitted based on role hierarchy
        
        Args:
            current_role: Current role of the user being modified
            new_roles: New roles to be assigned
            admin_role: Role of the admin making the change
            
        Returns:
            True if the change is valid, False otherwise
        """
        # Get privilege levels
        admin_level = self.role_hierarchy.get(admin_role, 0)
        
        # Admins can only assign roles at or below their own level
        for role in new_roles:
            role_level = self.role_hierarchy.get(role, 0)
            if role_level > admin_level:
                return False
        
        return True
    
    # Helper methods for role-specific profile data
    
    async def _get_user_profile_data(self, user: User) -> Dict[str, Any]:
        """
        Get role-specific profile data for a user
        """
        profile_data = {}
        
        # Get data based on role
        if user.role == "athlete":
            # Get athlete profile data
            # In real implementation, this would query the AthleteProfile table
            profile_data = {
                "sports": ["Running", "Swimming"],  # Example data
                "experience_level": "Advanced",
                "achievements": ["Regional Championship 2023"]
            }
        elif user.role == "coach":
            # Get coach profile data
            profile_data = {
                "specializations": ["Strength Training", "Recovery"],
                "certifications": ["NASM CPT", "ISSA SNC"],
                "years_experience": 8
            }
        elif user.role == "stakeholder":
            # Get stakeholder profile data
            profile_data = {
                "organization": "Sports Academy",
                "position": "Director",
                "interests": ["Athletics", "Youth Development"]
            }
        elif user.role == "support":
            # Get support staff profile data
            profile_data = {
                "profession": "Physical Therapist",
                "qualifications": ["DPT", "CSCS"],
                "services": ["Injury Assessment", "Rehabilitation"]
            }
        
        return profile_data
    
    async def _update_user_profile_data(self, user: User, profile_data: Dict[str, Any]) -> None:
        """
        Update role-specific profile data for a user
        """
        # In a real implementation, this would update the appropriate profile table
        # based on the user's role
        
        # Example implementation:
        if user.role == "athlete":
            # Update athlete profile
            pass
        elif user.role == "coach":
            # Update coach profile
            pass
        elif user.role == "stakeholder":
            # Update stakeholder profile
            pass
        elif user.role == "support":
            # Update support staff profile
            pass
    
    async def _delete_user_profile_data(self, user: User) -> None:
        """
        Delete role-specific profile data for a user
        """
        # In a real implementation, this would delete the appropriate profile data
        # based on the user's role
        
        # Example implementation:
        if user.role == "athlete":
            # Delete athlete profile
            pass
        elif user.role == "coach":
            # Delete coach profile
            pass
        elif user.role == "stakeholder":
            # Delete stakeholder profile
            pass
        elif user.role == "support":
            # Delete support staff profile
            pass 