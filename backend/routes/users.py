from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import get_optional_user
from models.db_models import User

# Create router
router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
    skip: int = 0,
    limit: int = 10
):
    """
    Get all users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Get a specific user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 