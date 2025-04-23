import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Integer, Date, ARRAY, Float, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from models.notification import NotificationType

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    training_sessions = relationship("TrainingSession", back_populates="coach")
    attendances = relationship("Attendance", back_populates="athlete")
    feedbacks = relationship("Feedback", back_populates="athlete")
    received_notifications = relationship("Notification", foreign_keys="Notification.recipient_id", back_populates="recipient")
    sent_notifications = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender")
    independent_training_sessions = relationship("IndependentTrainingSession", back_populates="athlete")


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    date = Column(Date)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    coach_id = Column(Integer, ForeignKey("users.id"))
    training_quality = Column(Integer)
    expectations = Column(Integer)
    team_condition = Column(Integer)
    notes = Column(Text)
    documentation = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    coach = relationship("User", foreign_keys=[coach_id])
    warming_ups = relationship("WarmingUp", back_populates="training_session")
    main_trainings = relationship("MainTraining", back_populates="training_session")
    cooling_downs = relationship("CoolingDown", back_populates="training_session")
    attendances = relationship("Attendance", back_populates="training_session")
    feedbacks = relationship("Feedback", back_populates="training_session")


class WarmingUp(Base):
    __tablename__ = "warming_ups"
    
    id = Column(Integer, primary_key=True, index=True)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"))
    notes = Column(Text)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    training_session = relationship("TrainingSession", back_populates="warming_ups")


class MainTraining(Base):
    __tablename__ = "main_trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"))
    notes = Column(Text)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    training_session = relationship("TrainingSession", back_populates="main_trainings")
    performance_records = relationship("PerformanceRecord", back_populates="main_training")


class CoolingDown(Base):
    __tablename__ = "cooling_downs"
    
    id = Column(Integer, primary_key=True, index=True)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"))
    notes = Column(Text)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    training_session = relationship("TrainingSession", back_populates="cooling_downs")


class PerformanceRecord(Base):
    __tablename__ = "performance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    main_training_id = Column(Integer, ForeignKey("main_trainings.id"))
    athlete_id = Column(Integer, ForeignKey("users.id"))
    time = Column(Time, nullable=True)
    repetitions = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    main_training = relationship("MainTraining", back_populates="performance_records")
    athlete = relationship("User", foreign_keys=[athlete_id])


class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"))
    athlete_id = Column(Integer, ForeignKey("users.id"))
    check_in_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    training_session = relationship("TrainingSession", back_populates="attendances")
    athlete = relationship("User", foreign_keys=[athlete_id])


class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"))
    athlete_id = Column(Integer, ForeignKey("users.id"))
    training_quality = Column(Integer)
    expectations = Column(Integer)
    body_condition = Column(Integer)
    intensity = Column(Integer)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    training_session = relationship("TrainingSession", back_populates="feedbacks")
    athlete = relationship("User", foreign_keys=[athlete_id])


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_id = Column(Integer, nullable=True)
    link = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    recipient = relationship("User", foreign_keys=[recipient_id])
    sender = relationship("User", foreign_keys=[sender_id])


class IndependentTrainingSession(Base):
    """Database model for independent training sessions"""
    __tablename__ = "independent_training_sessions"

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    intensity = Column(Integer, nullable=True)  # Scale from 1-10
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    athlete = relationship("User", back_populates="independent_training_sessions")
    
    def __repr__(self):
        return f"<IndependentTrainingSession {self.id} - {self.title}>" 