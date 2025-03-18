from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class NotificationType(str, Enum):
    FEEDBACK_SUBMITTED = "feedback_submitted"
    SESSION_CREATED = "session_created"
    ATTENDANCE_MARKED = "attendance_marked"
    GENERAL = "general"


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationType
    related_id: Optional[str] = None
    link: Optional[str] = None


class NotificationCreate(NotificationBase):
    recipient_id: str
    sender_id: Optional[str] = None


class Notification(NotificationBase):
    id: str
    recipient_id: str
    sender_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


class NotificationResponse(BaseModel):
    notifications: List[Notification]
    unread_count: int 