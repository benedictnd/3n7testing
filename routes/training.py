from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.notification import Notification, NotificationResponse
from models.training import FeedbackCreate, FeedbackResponse
from services.training_service import TrainingService
from services.notification_service import NotificationService
from repositories.notification_repository import NotificationRepository
from dependencies.database import get_db
from dependencies.auth import get_current_user

router = APIRouter(prefix="/training", tags=["training"])


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit feedback for a training session"""
    if current_user.role != "athlete":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only athletes can submit feedback"
        )
    
    # Initialize services
    training_service = TrainingService(db)
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo)
    
    # Submit feedback
    try:
        # Check if athlete attended the session
        if not await training_service.check_attendance(feedback.training_session_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must have attended the session to submit feedback"
            )
        
        # Check if athlete already submitted feedback
        if await training_service.has_submitted_feedback(feedback.training_session_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted feedback for this session"
            )
        
        # Create feedback
        feedback_db = await training_service.create_feedback(feedback, current_user.id)
        
        # Get session details
        session = await training_service.get_session(feedback.training_session_id)
        
        # Create notification for coach
        await notification_service.create_feedback_notification(
            feedback=feedback_db,
            session=session,
            athlete=current_user
        )
        
        return {
            "id": feedback_db.id,
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/notifications", response_model=NotificationResponse)
async def get_notifications(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get notifications for the current user"""
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo)
    
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    unread_count = await notification_service.get_unread_count(current_user.id)
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo)
    
    success = await notification_service.mark_as_read(notification_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo)
    
    count = await notification_service.mark_all_as_read(current_user.id)
    
    return {"message": f"{count} notifications marked as read"} 