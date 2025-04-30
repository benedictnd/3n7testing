import os
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, List, Callable

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from functools import wraps

from dependencies.database import get_db
from models.db_models import User

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development_secret_key")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set for secure operation")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Set up OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class TokenData(BaseModel):
    """Token data model"""
    sub: str
    exp: int
    role: str
    id: str


class UserInDB(BaseModel):
    """User in database model"""
    id: str
    email: str
    name: str
    role: str

    class Config:
        orm_mode = True


# Role hierarchy definition
ROLE_HIERARCHY = {
    "admin": 100,
    "superadmin": 1000,
    "coach": 50,
    "athlete": 10,
    "guest": 1
}

# Function to create access token
def create_access_token(data: Dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token for a user
    
    Args:
        data: Dictionary containing user information
        expires_delta: Optional expiration time delta
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Get the current authenticated user from the JWT token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User object if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(
            sub=user_id,
            exp=payload.get("exp"),
            role=payload.get("role", "guest"),
            id=payload.get("id")
        )
        
        # Check token expiration
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    return UserInDB.from_orm(user)


def validate_role_change(current_roles: List[str], requested_roles: List[str], user: UserInDB) -> bool:
    """
    Validate if the user has permission to assign the requested roles.
    
    This prevents privilege escalation by enforcing that:
    1. Users can only assign roles with lower or equal privilege level to their own
    2. Users cannot elevate their own privileges
    
    Args:
        current_roles: Current roles before change
        requested_roles: Requested roles after change
        user: User making the change
        
    Returns:
        True if the role change is valid, False otherwise
    """
    # Get the user's role level
    user_role_level = ROLE_HIERARCHY.get(user.role, 0)
    
    # Check each requested role
    for role in requested_roles:
        # Get the requested role level
        requested_role_level = ROLE_HIERARCHY.get(role, 0)
        
        # Prevent assigning roles with higher privileges than the user's own role
        if requested_role_level > user_role_level:
            return False
            
    # Special case: prevent self-promotion
    if user.id in [role.split(':')[1] for role in requested_roles if ':' in role]:
        # Check if user is trying to elevate their own privileges
        current_max_level = max([ROLE_HIERARCHY.get(role.split(':')[0], 0) 
                               for role in current_roles if ':' in role] or [0])
        requested_max_level = max([ROLE_HIERARCHY.get(role.split(':')[0], 0) 
                                 for role in requested_roles if ':' in role] or [0])
        
        if requested_max_level > current_max_level:
            return False
            
    return True


def role_required(allowed_roles: List[str]):
    """
    Dependency for role-based access control.
    
    Args:
        allowed_roles: List of roles that are allowed to access the endpoint
        
    Returns:
        Dependency function that validates the user's role
    """
    async def validate_role(user: UserInDB = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action"
            )
        return user
    return validate_role


def is_admin(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Check if user is an admin"""
    if user.role != "admin" and user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user 