#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta, date, time
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Add the parent directory to the path so we can import the models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db_models import (
    User, TrainingSession, WarmingUp, MainTraining, CoolingDown,
    PerformanceRecord, Attendance, Feedback, Notification,
    IndependentTrainingSession, Base
)

# Connect to the database
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@postgres:5432/training_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a session
db = SessionLocal()

# Sample data
user_data = [
    {"email": "admin@example.com", "password": "hashed_password", "name": "Admin User", "role": "admin"},
    {"email": "coach1@example.com", "password": "hashed_password", "name": "Coach One", "role": "coach"},
    {"email": "coach2@example.com", "password": "hashed_password", "name": "Coach Two", "role": "coach"},
    {"email": "athlete1@example.com", "password": "hashed_password", "name": "Athlete One", "role": "athlete"},
    {"email": "athlete2@example.com", "password": "hashed_password", "name": "Athlete Two", "role": "athlete"},
    {"email": "athlete3@example.com", "password": "hashed_password", "name": "Athlete Three", "role": "athlete"},
    {"email": "athlete4@example.com", "password": "hashed_password", "name": "Athlete Four", "role": "athlete"},
    {"email": "athlete5@example.com", "password": "hashed_password", "name": "Athlete Five", "role": "athlete"},
]

training_types = ["Sprint", "Endurance", "Strength", "Flexibility", "Team Practice", "Individual", "Recovery"]
locations = ["Main Field", "Track", "Gym", "Pool", "Studio", "Indoor Court", "Outdoor Court"]
equipment = ["Balls", "Cones", "Weights", "Resistance Bands", "Mats", "Jumpropes", "Hurdles"]

def create_users():
    """Create users if they don't exist"""
    existing_users = db.query(User).all()
    if existing_users:
        print(f"Users already exist. Skipping user creation.")
        return existing_users
    
    users = []
    for data in user_data:
        user = User(**data)
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"Created {len(users)} users")
    return users

def create_training_sessions(coaches, start_date=None, num_sessions=20):
    """Create training sessions for coaches"""
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    
    sessions = []
    for i in range(num_sessions):
        coach = random.choice([u for u in coaches if u.role == "coach"])
        session_date = start_date + timedelta(days=random.randint(0, 60))
        start_hour = random.randint(7, 18)
        duration = random.randint(1, 3)
        
        session = TrainingSession(
            coach_id=coach.id,
            type=random.choice(training_types),
            date=session_date,
            start_time=datetime.combine(session_date, time(start_hour, 0)),
            end_time=datetime.combine(session_date, time(start_hour + duration, 0)),
            training_quality=random.randint(1, 10),
            expectations=random.randint(1, 10),
            team_condition=random.randint(1, 10),
            notes=f"Training session {i+1} notes",
            documentation=f"Documentation for session {i+1}"
        )
        db.add(session)
        sessions.append(session)
    
    db.commit()
    print(f"Created {len(sessions)} training sessions")
    return sessions

def create_warming_ups(training_sessions):
    """Create warming up activities for training sessions"""
    warming_ups = []
    for session in training_sessions:
        warming_up = WarmingUp(
            training_session_id=session.id,
            notes=f"Warming up for session {session.id}",
            duration=random.randint(10, 20)
        )
        db.add(warming_up)
        warming_ups.append(warming_up)
    
    db.commit()
    print(f"Created {len(warming_ups)} warming up activities")
    return warming_ups

def create_main_trainings(training_sessions):
    """Create main training activities for training sessions"""
    main_trainings = []
    for session in training_sessions:
        main_training = MainTraining(
            training_session_id=session.id,
            notes=f"Main training for session {session.id}",
            duration=random.randint(30, 90)
        )
        db.add(main_training)
        main_trainings.append(main_training)
    
    db.commit()
    print(f"Created {len(main_trainings)} main training activities")
    return main_trainings

def create_cooling_downs(training_sessions):
    """Create cooling down activities for training sessions"""
    cooling_downs = []
    for session in training_sessions:
        cooling_down = CoolingDown(
            training_session_id=session.id,
            notes=f"Cooling down for session {session.id}",
            duration=random.randint(10, 15)
        )
        db.add(cooling_down)
        cooling_downs.append(cooling_down)
    
    db.commit()
    print(f"Created {len(cooling_downs)} cooling down activities")
    return cooling_downs

def create_performance_records(main_trainings, athletes):
    """Create performance records for athletes during main training"""
    records = []
    for main_training in main_trainings:
        # Select a subset of athletes for each main training
        selected_athletes = random.sample(
            [u for u in athletes if u.role == "athlete"],
            random.randint(1, len([u for u in athletes if u.role == "athlete"]))
        )
        
        for athlete in selected_athletes:
            record = PerformanceRecord(
                main_training_id=main_training.id,
                athlete_id=athlete.id,
                time=time(minute=random.randint(0, 59), second=random.randint(0, 59)),
                repetitions=random.randint(5, 20),
                sets=random.randint(1, 5),
                weight=random.uniform(0.0, 100.0),
                notes=f"Performance record for {athlete.name} in training {main_training.id}"
            )
            db.add(record)
            records.append(record)
    
    db.commit()
    print(f"Created {len(records)} performance records")
    return records

def create_attendance(training_sessions, athletes):
    """Create attendance records for athletes in training sessions"""
    attendances = []
    for session in training_sessions:
        # Select a subset of athletes for each session
        selected_athletes = random.sample(
            [u for u in athletes if u.role == "athlete"],
            random.randint(1, len([u for u in athletes if u.role == "athlete"]))
        )
        
        for athlete in selected_athletes:
            attendance = Attendance(
                training_session_id=session.id,
                athlete_id=athlete.id,
                check_in_time=session.start_time + timedelta(minutes=random.randint(-15, 5))
            )
            db.add(attendance)
            attendances.append(attendance)
    
    db.commit()
    print(f"Created {len(attendances)} attendance records")
    return attendances

def create_feedback(training_sessions, athletes):
    """Create feedback from athletes about training sessions"""
    feedbacks = []
    for session in training_sessions:
        # Only create feedback for sessions in the past
        if session.date > date.today():
            continue
            
        # Select a subset of athletes for each session
        selected_athletes = random.sample(
            [u for u in athletes if u.role == "athlete"],
            random.randint(0, len([u for u in athletes if u.role == "athlete"]))
        )
        
        for athlete in selected_athletes:
            feedback = Feedback(
                training_session_id=session.id,
                athlete_id=athlete.id,
                training_quality=random.randint(1, 10),
                expectations=random.randint(1, 10),
                body_condition=random.randint(1, 10),
                intensity=random.randint(1, 10),
                notes=f"Feedback from {athlete.name} for session {session.id}"
            )
            db.add(feedback)
            feedbacks.append(feedback)
    
    db.commit()
    print(f"Created {len(feedbacks)} feedback records")
    return feedbacks

def create_notifications(users):
    """Create notifications for users"""
    notifications = []
    notification_types = ["training_reminder", "feedback_request", "announcement", "personal_message"]
    
    for i in range(50):
        recipient = random.choice(users)
        sender = random.choice([u for u in users if u.role in ("admin", "coach")])
        notif_type = random.choice(notification_types)
        
        notification = Notification(
            title=f"Notification {i+1}",
            message=f"This is a notification message {i+1}",
            notification_type=notif_type,
            recipient_id=recipient.id,
            sender_id=sender.id,
            related_id=random.randint(1, 100) if random.random() < 0.5 else None,
            link=f"/some/link/{i}" if random.random() < 0.5 else None,
            is_read=random.choice([True, False])
        )
        db.add(notification)
        notifications.append(notification)
    
    db.commit()
    print(f"Created {len(notifications)} notifications")
    return notifications

def create_independent_training_sessions(athletes):
    """Create independent training sessions for athletes"""
    sessions = []
    start_date = date.today() - timedelta(days=30)
    
    for athlete in [u for u in athletes if u.role == "athlete"]:
        num_sessions = random.randint(3, 10)
        
        for i in range(num_sessions):
            session_date = start_date + timedelta(days=random.randint(0, 60))
            duration = random.randint(30, 120)
            
            session = IndependentTrainingSession(
                athlete_id=athlete.id,
                title=f"Independent training {i+1}",
                description=f"Description for independent training {i+1}",
                date=session_date,
                duration=duration,
                intensity=random.randint(1, 10),
                notes=f"Notes for independent training {i+1}"
            )
            db.add(session)
            sessions.append(session)
    
    db.commit()
    print(f"Created {len(sessions)} independent training sessions")
    return sessions

def main():
    print("Generating dummy data...")
    
    # Create users
    users = create_users()
    coaches = [u for u in users if u.role == "coach"]
    athletes = [u for u in users if u.role == "athlete"]
    
    # Create training sessions and related data
    training_sessions = create_training_sessions(coaches)
    
    warming_ups = create_warming_ups(training_sessions)
    main_trainings = create_main_trainings(training_sessions)
    cooling_downs = create_cooling_downs(training_sessions)
    
    performance_records = create_performance_records(main_trainings, athletes)
    attendances = create_attendance(training_sessions, athletes)
    feedbacks = create_feedback(training_sessions, athletes)
    
    # Create notifications
    notifications = create_notifications(users)
    
    # Create independent training sessions
    independent_sessions = create_independent_training_sessions(athletes)
    
    print("Dummy data generation complete!")

if __name__ == "__main__":
    main() 