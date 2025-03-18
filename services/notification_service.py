from typing import List, Optional
from repositories.notification_repository import NotificationRepository
from models.notification import NotificationCreate, Notification, NotificationType
from models.db_models import Feedback, TrainingSession, User


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo
    
    async def create_feedback_notification(self, feedback: Feedback, session: TrainingSession, athlete: User) -> Notification:
        """Create notification for coach when athlete submits feedback"""
        notification = NotificationCreate(
            title="New Training Feedback",
            message=f"{athlete.name} has submitted feedback for the training session on {session.date.strftime('%Y-%m-%d')}",
            notification_type=NotificationType.FEEDBACK_SUBMITTED,
            recipient_id=session.coach_id,
            sender_id=athlete.id,
            related_id=feedback.id,
            link=f"/feedback/{feedback.id}"
        )
        
        return await self.notification_repo.create_notification(notification)
    
    async def get_user_notifications(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Notification]:
        """Get notifications for a user"""
        return await self.notification_repo.get_notifications_by_user(user_id, limit, offset)
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        return await self.notification_repo.get_unread_count(user_id)
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        return await self.notification_repo.mark_as_read(notification_id)
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        return await self.notification_repo.mark_all_as_read(user_id)
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        return await self.notification_repo.delete_notification(notification_id) 