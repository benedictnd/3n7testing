import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Integer, Date, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from models.notification import NotificationType

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # athlete, coach, stakeholder, support
    
    # Relationships
    training_sessions = relationship("TrainingSession", back_populates="coach")
    attendances = relationship("Attendance", back_populates="athlete")
    feedbacks = relationship("Feedback", back_populates="athlete")
    received_notifications = relationship("Notification", foreign_keys="Notification.recipient_id", back_populates="recipient")
    sent_notifications = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender")
    independent_training_sessions = relationship("IndependentTrainingSession", back_populates="athlete")


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    coach_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    coach = relationship("User", back_populates="training_sessions")
    attendances = relationship("Attendance", back_populates="training_session")
    feedbacks = relationship("Feedback", back_populates="training_session")


class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    training_session_id = Column(String, ForeignKey("training_sessions.id"), nullable=False)
    athlete_id = Column(String, ForeignKey("users.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)
    
    # Relationships
    training_session = relationship("TrainingSession", back_populates="attendances")
    athlete = relationship("User", back_populates="attendances")


class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    training_session_id = Column(String, ForeignKey("training_sessions.id"), nullable=False)
    athlete_id = Column(String, ForeignKey("users.id"), nullable=False)
    training_quality = Column(Integer, nullable=False)  # 1-5 rating
    expectations = Column(Integer, nullable=False)  # 1-5 rating
    body_condition = Column(Integer, nullable=False)  # 1-10 rating
    intensity = Column(Integer, nullable=False)  # 1-10 rating
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    training_session = relationship("TrainingSession", back_populates="feedbacks")
    athlete = relationship("User", back_populates="feedbacks")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=True)
    related_id = Column(String, nullable=True)  # ID of related entity (e.g., feedback_id)
    link = Column(String, nullable=True)  # URL to redirect when clicked
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_notifications")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_notifications")


class IndependentTrainingSession(Base):
    """Database model for independent training sessions"""
    __tablename__ = "independent_training_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Maps to IndependentTrainingType
    date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    equipment_needed = Column(ARRAY(String), nullable=True)
    notes = Column(String, nullable=True)
    intensity = Column(Integer, nullable=False)
    body_condition = Column(Integer, nullable=False)
    coach_notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    athlete = relationship("User", back_populates="independent_training_sessions")
    phases = relationship("TrainingPhase", back_populates="independent_training_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<IndependentTrainingSession {self.title}>" 