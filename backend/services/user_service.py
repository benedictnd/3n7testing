from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import and_
from fastapi import HTTPException, status

from models.user import UserUpdate, UserResponse, UserDetail
from models.database import User


class UserService:
    """Service for managing users"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_users(
        self,
        role: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get a list of users with optional role filtering and pagination
        """
        # Build base query
        query = select(User)
        
        # Apply role filter if specified
        if role:
            query = query.where(User.role == role)
        
        # Get total count for pagination
        count_query = select(User)
        if role:
            count_query = count_query.where(User.role == role)
        
        count_result = await self.db_session.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await self.db_session.execute(query)
        users = result.scalars().all()
        
        # Format response
        user_list = []
        for user in users:
            user_list.append(
                UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    role=user.role
                )
            )
        
        # Calculate page number
        page = offset // limit + 1 if offset > 0 else 1
        
        return {
            "users": user_list,
            "total": total,
            "page": page,
            "size": limit
        }
    
    async def get_user(self, user_id: str) -> UserDetail:
        """
        Get detailed information about a specific user
        """
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Get user profile data based on role
        profile_data = await self._get_user_profile_data(user)
        
        # Combine base user data with profile data
        user_detail = UserDetail(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            **profile_data
        )
        
        return user_detail
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserDetail:
        """
        Update a user's information
        """
        # Check if user exists
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Convert user data to dict and remove None values
        update_data = user_data.dict(exclude_unset=True)
        
        if not update_data:
            # No fields to update
            return await self.get_user(user_id)
        
        # Extract base user fields
        base_fields = {k: v for k, v in update_data.items() 
                      if k in ['name', 'email']}
        
        # Extract profile-specific fields
        profile_fields = {k: v for k, v in update_data.items() 
                         if k not in ['name', 'email']}
        
        # Update basic user information
        if base_fields:
            update_query = (
                update(User)
                .where(User.id == user_id)
                .values(**base_fields)
            )
            await self.db_session.execute(update_query)
        
        # Update profile information based on role
        if profile_fields:
            await self._update_user_profile_data(user, profile_fields)
        
        # Commit changes
        await self.db_session.commit()
        
        # Return updated user
        return await self.get_user(user_id)
    
    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Delete a user
        """
        # Check if user exists
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Delete profile data based on role
        await self._delete_user_profile_data(user)
        
        # Delete user
        delete_query = delete(User).where(User.id == user_id)
        await self.db_session.execute(delete_query)
        
        # Commit changes
        await self.db_session.commit()
        
        return {"message": f"User with ID {user_id} successfully deleted"}
    
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