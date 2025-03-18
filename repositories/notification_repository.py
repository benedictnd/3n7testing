from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from sqlalchemy.orm import selectinload

from models.db_models import Notification
from models.notification import NotificationCreate


class NotificationRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create a new notification in the database"""
        db_notification = Notification(
            title=notification.title,
            message=notification.message,
            notification_type=notification.notification_type,
            recipient_id=notification.recipient_id,
            sender_id=notification.sender_id,
            related_id=notification.related_id,
            link=notification.link,
            is_read=False
        )
        
        self.db_session.add(db_notification)
        await self.db_session.commit()
        await self.db_session.refresh(db_notification)
        return db_notification
    
    async def get_notifications_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Notification]:
        """Get notifications for a specific user"""
        query = select(Notification).where(Notification.recipient_id == user_id)\
            .order_by(desc(Notification.created_at))\
            .limit(limit).offset(offset)
        
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        query = select(func.count()).where(
            (Notification.recipient_id == user_id) & 
            (Notification.is_read == False)
        )
        result = await self.db_session.execute(query)
        return result.scalar()
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        query = update(Notification).where(Notification.id == notification_id)\
            .values(is_read=True)
        result = await self.db_session.execute(query)
        await self.db_session.commit()
        return result.rowcount > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        query = update(Notification).where(
            (Notification.recipient_id == user_id) & 
            (Notification.is_read == False)
        ).values(is_read=True)
        result = await self.db_session.execute(query)
        await self.db_session.commit()
        return result.rowcount
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        notification = await self.db_session.get(Notification, notification_id)
        if notification:
            await self.db_session.delete(notification)
            await self.db_session.commit()
            return True
        return False 