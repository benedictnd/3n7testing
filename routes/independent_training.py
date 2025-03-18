from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.training import (
    IndependentTraining,
    IndependentTrainingCreate,
    IndependentTrainingResponse,
    IndependentTrainingType
)
from models.db_models import IndependentTrainingSession, User
from services.notification import create_notification

router = APIRouter(prefix="/independent-training", tags=["independent-training"])


@router.post("/", response_model=IndependentTraining)
async def create_independent_training(
    training: IndependentTrainingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new independent training session"""
    if current_user.role != "athlete":
        raise HTTPException(status_code=403, detail="Only athletes can create independent training sessions")
    
    # Create training session
    db_training = IndependentTrainingSession(
        athlete_id=current_user.id,
        athlete_name=current_user.name,
        **training.dict()
    )
    
    db.add(db_training)
    await db.commit()
    await db.refresh(db_training)
    
    # Notify coach
    await notify_coach(db, db_training)
    
    return IndependentTraining.from_orm(db_training)


@router.get("/", response_model=IndependentTrainingResponse)
async def get_independent_training_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get independent training sessions"""
    query = select(IndependentTrainingSession)
    
    # Filter by date range if provided
    if start_date:
        query = query.where(IndependentTrainingSession.date >= start_date.date())
    if end_date:
        query = query.where(IndependentTrainingSession.date <= end_date.date())
    
    # Filter by user role
    if current_user.role == "athlete":
        query = query.where(IndependentTrainingSession.athlete_id == current_user.id)
    elif current_user.role == "coach":
        # Get sessions for athletes managed by the coach
        query = query.join(User).where(User.coach_id == current_user.id)
    
    # Get total count
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return IndependentTrainingResponse(
        sessions=[IndependentTraining.from_orm(s) for s in sessions],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{training_id}", response_model=IndependentTraining)
async def get_independent_training(
    training_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific independent training session"""
    query = select(IndependentTrainingSession).where(IndependentTrainingSession.id == training_id)
    
    # Filter by user role
    if current_user.role == "athlete":
        query = query.where(IndependentTrainingSession.athlete_id == current_user.id)
    elif current_user.role == "coach":
        # Get session if athlete is managed by the coach
        query = query.join(User).where(User.coach_id == current_user.id)
    
    result = await db.execute(query)
    training = result.scalar_one_or_none()
    
    if not training:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    return IndependentTraining.from_orm(training)


@router.put("/{training_id}", response_model=IndependentTraining)
async def update_independent_training(
    training_id: str,
    training_update: IndependentTrainingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an independent training session"""
    query = select(IndependentTrainingSession).where(IndependentTrainingSession.id == training_id)
    
    # Only allow athletes to update their own sessions
    if current_user.role != "athlete":
        raise HTTPException(status_code=403, detail="Only athletes can update their training sessions")
    
    query = query.where(IndependentTrainingSession.athlete_id == current_user.id)
    result = await db.execute(query)
    db_training = result.scalar_one_or_none()
    
    if not db_training:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    # Update fields
    for field, value in training_update.dict().items():
        setattr(db_training, field, value)
    
    await db.commit()
    await db.refresh(db_training)
    
    return IndependentTraining.from_orm(db_training)


@router.delete("/{training_id}")
async def delete_independent_training(
    training_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an independent training session"""
    query = select(IndependentTrainingSession).where(IndependentTrainingSession.id == training_id)
    
    # Only allow athletes to delete their own sessions
    if current_user.role != "athlete":
        raise HTTPException(status_code=403, detail="Only athletes can delete their training sessions")
    
    query = query.where(IndependentTrainingSession.athlete_id == current_user.id)
    result = await db.execute(query)
    db_training = result.scalar_one_or_none()
    
    if not db_training:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    await db.delete(db_training)
    await db.commit()
    
    return {"message": "Training session deleted successfully"}


async def notify_coach(db: AsyncSession, training: IndependentTrainingSession):
    """Create a notification for the coach about a new independent training session"""
    # Get the athlete's coach
    query = select(User).where(User.id == training.athlete_id)
    result = await db.execute(query)
    athlete = result.scalar_one_or_none()
    
    if not athlete or not athlete.coach_id:
        return
    
    # Create notification
    await create_notification(
        db,
        recipient_id=athlete.coach_id,
        sender_id=athlete.id,
        title="New Independent Training Session",
        message=f"{athlete.name} has completed an independent {training.type} training session.",
        notification_type="independent_training",
        related_id=training.id
    ) 