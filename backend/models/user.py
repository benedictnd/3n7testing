from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserBase(BaseModel):
    """Base class for user models"""
    email: EmailStr
    name: str
    role: str


class UserResponse(UserBase):
    """User response model with ID"""
    id: str


class UserDetail(UserResponse):
    """Detailed user information"""
    # Role-specific fields
    # For athletes
    sports: Optional[List[str]] = None
    experience_level: Optional[str] = None
    achievements: Optional[List[str]] = None
    
    # For coaches
    specializations: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    years_experience: Optional[int] = None
    
    # For stakeholders
    organization: Optional[str] = None
    position: Optional[str] = None
    interests: Optional[List[str]] = None
    
    # For support staff
    profession: Optional[str] = None
    qualifications: Optional[List[str]] = None
    services: Optional[List[str]] = None


class UserUpdate(BaseModel):
    """Model for updating user information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    # Role-specific fields that can be updated
    # For athletes
    sports: Optional[List[str]] = None
    experience_level: Optional[str] = None
    achievements: Optional[List[str]] = None
    
    # For coaches
    specializations: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    years_experience: Optional[int] = None
    
    # For stakeholders
    organization: Optional[str] = None
    position: Optional[str] = None
    interests: Optional[List[str]] = None
    
    # For support staff
    profession: Optional[str] = None
    qualifications: Optional[List[str]] = None
    services: Optional[List[str]] = None


class UserList(BaseModel):
    """Model for listing users with pagination"""
    users: List[UserResponse]
    total: int
    page: int
    size: int 