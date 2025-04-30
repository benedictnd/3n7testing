from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import os
import json
import time
from datetime import datetime

# Current date for use in date comparisons
today = datetime.now()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load dummy data from JSON file
try:
    with open("dummy_data.json", "r") as f:
        dummy_data = json.load(f)
    logger.info("Successfully loaded dummy data")
except Exception as e:
    logger.error(f"Error loading dummy data: {str(e)}")
    dummy_data = {"error": "Failed to load data"}

# Define Pydantic models for API documentation
class TeamSummary(BaseModel):
    id: str
    name: str

class CoachSummary(BaseModel):
    id: str
    name: str
    role: str
    team_id: str

class AthleteSummary(BaseModel):
    id: str
    name: str
    team_id: str

class TeamResponse(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    sport: Optional[str] = None
    division: Optional[str] = None
    established: Optional[int] = None
    home_venue: Optional[str] = None
    team_colors: Optional[List[str]] = None
    coaches: List[CoachSummary] = []
    athletes: List[AthleteSummary] = []

class TeamList(BaseModel):
    teams: List[TeamSummary]

class TrainingSegmentTime(BaseModel):
    warm_up_minutes: int = 0
    main_minutes: int = 0
    cool_down_minutes: int = 0

class TrainingFeedback(BaseModel):
    quality_rating: Optional[int] = None  # 1-10
    condition_rating: Optional[int] = None  # 1-10
    expectation_rating: Optional[int] = None  # 1-10
    coach_notes: Optional[str] = None

class TrainingSessionResponse(BaseModel):
    id: str
    team_id: str
    title: str
    date: str
    start_time: str
    end_time: str
    location: str
    description: Optional[str] = None
    objectives: Optional[List[str]] = None
    team_name: Optional[str] = None
    training_type: Optional[str] = None  # "core" or "speed_endurance"
    session_time: Optional[str] = None  # "morning", "afternoon", "night"
    total_minutes: Optional[int] = None
    segment_times: Optional[TrainingSegmentTime] = None
    feedback: Optional[TrainingFeedback] = None

class DateSessionCount(BaseModel):
    date: str
    session_count: int

class SessionTimeCount(BaseModel):
    morning_count: int = 0
    afternoon_count: int = 0
    night_count: int = 0

class TrainingTypeCount(BaseModel):
    core_count: int = 0
    speed_endurance_count: int = 0

class TrainingDuration(BaseModel):
    shortest_minutes: Optional[int] = None
    longest_minutes: Optional[int] = None
    average_minutes: Optional[float] = None

class SegmentTimeStats(BaseModel):
    avg_warm_up_minutes: float = 0
    avg_main_minutes: float = 0
    avg_cool_down_minutes: float = 0

class FeedbackStats(BaseModel):
    avg_quality_rating: Optional[float] = None
    avg_condition_rating: Optional[float] = None
    avg_expectation_rating: Optional[float] = None

class TrainingSessionList(BaseModel):
    training_sessions: List[TrainingSessionResponse]
    total_count: int = 0
    sessions_by_date: List[DateSessionCount] = []
    session_time_counts: Optional[SessionTimeCount] = None
    training_type_counts: Optional[TrainingTypeCount] = None
    duration_stats: Optional[TrainingDuration] = None
    segment_time_stats: Optional[SegmentTimeStats] = None
    feedback_stats: Optional[FeedbackStats] = None

# Custom exception class
class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

# Create app with OpenAPI enabled
app = FastAPI(
    title="3&7 Training Platform API",
    description="API for the 3&7 Training and Recovery Platform",
    version="1.0.0",
    # Explicitly enable OpenAPI schema generation
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Frontend dev server
    "https://training.3and7.com",  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error during request: {str(e)} - Time: {process_time:.4f}s")
        raise

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."}
    )

# Root endpoint
@app.get("/")
def root():
    return {"message": "3&7 Backend API"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

# The following will be uncommented one by one to identify which causes recursion issues:
# app.include_router(training_sessions.router)
# app.include_router(users.router)
# app.include_router(reports.router)
# app.include_router(email.router)

# Dummy data API endpoints

# Get all dummy data
@app.get("/api/dummy-data")
def get_all_dummy_data():
    return JSONResponse(content=dummy_data)

# Get teams
@app.get("/api/teams", 
    response_model=TeamList,
    summary="Get all teams",
    description="Retrieve a list of all registered teams with basic information.",
    tags=["Teams"])
def get_teams():
    """Get a list of all teams with summary information.
    
    Returns:
        TeamList: A list of teams with their basic details
    """
    return {"teams": [TeamSummary(**team) for team in dummy_data.get("teams", [])]}

# Get single team by ID
@app.get("/api/teams/{team_id}", 
    response_model=TeamResponse,
    summary="Get team details",
    description="Retrieve detailed information about a specific team, including coaches and athletes.",
    tags=["Teams"])
def get_team(team_id: str):
    """Get detailed information about a specific team.
    
    Args:
        team_id (str): The unique identifier of the team
        
    Returns:
        TeamResponse: Detailed team information including coaches and athletes
        
    Raises:
        HTTPException: 404 error if team is not found
    """
    teams = dummy_data.get("teams", [])
    for team in teams:
        if team.get("id") == team_id:
            # Construct proper response with model validation
            return TeamResponse(**team)
    raise HTTPException(status_code=404, detail="Team not found")

# Get coaches for a team
@app.get("/api/teams/{team_id}/coaches")
def get_team_coaches(team_id: str):
    teams = dummy_data.get("teams", [])
    for team in teams:
        if team.get("id") == team_id:
            return JSONResponse(content={"coaches": team.get("coaches", [])})
    raise HTTPException(status_code=404, detail="Team not found")

# Get athletes for a team
@app.get("/api/teams/{team_id}/athletes")
def get_team_athletes(team_id: str):
    teams = dummy_data.get("teams", [])
    for team in teams:
        if team.get("id") == team_id:
            return JSONResponse(content={"athletes": team.get("athletes", [])})
    raise HTTPException(status_code=404, detail="Team not found")

# Get training sessions
@app.get("/api/training-sessions", 
    summary="Get comprehensive training statistics",
    description="Retrieve detailed training statistics including counts by type, preferred days/times, duration metrics, and coach feedback.",
    tags=["Training"])
def get_training_sessions():
    """Get comprehensive training statistics.
    
    This endpoint provides detailed statistics for all training sessions:
    - Total count of training plans executed
    - Count of core training sessions executed
    - Count of speed & endurance training sessions executed
    - Preferred training days analysis
    - Preferred session times (morning, afternoon, night)
    - Length of training segments (warming up, main, cooling down)
    - Post-training feedback summary from coaches
    
    Returns:
        dict: Comprehensive training statistics
    """
    sessions = dummy_data.get("training_sessions", [])
    
    # Enhanced statistics calculations
    # 1. Counts by training type
    core_count = 0
    speed_endurance_count = 0
    
    # 2. Session time preferences
    session_times = {"morning": 0, "afternoon": 0, "night": 0}
    
    # 3. Training day preferences
    training_days = {}
    
    # 4. Training segment durations
    segment_durations = {
        "warm_up_total": 0,
        "main_total": 0,
        "cool_down_total": 0
    }
    
    # 5. Feedback metrics
    feedback_metrics = {
        "quality_ratings": [],
        "condition_ratings": [],
        "expectation_ratings": [],
        "coach_feedback": []
    }
    
    # Enhanced sessions with calculated fields
    enhanced_sessions = []
    
    for session in sessions:
        # Create enhanced session
        enhanced_session = session.copy()
        
        # Add team name
        team_id = session.get("team_id")
        for team in dummy_data.get("teams", []):
            if team.get("id") == team_id:
                enhanced_session["team_name"] = team.get("name")
                break
        
        # Process time data safely
        start_time = session.get("start_time", "00:00")
        end_time = session.get("end_time", "00:00")
        
        # Extract hours safely
        try:
            start_hour = int(start_time.split(":")[0])
        except (ValueError, IndexError):
            start_hour = 0
        
        # Determine session time (morning, afternoon, night)
        if start_hour < 12:
            session_time = "morning"
            session_times["morning"] += 1
        elif start_hour < 17:
            session_time = "afternoon"
            session_times["afternoon"] += 1
        else:
            session_time = "night"
            session_times["night"] += 1
        
        enhanced_session["session_time"] = session_time
        
        # Process training type
        # Using ID to deterministically assign training types (for demo purposes)
        session_id = session.get("id", "")
        is_core = len(session_id) % 2 == 0  # Simple rule for demo
        
        if is_core:
            training_type = "core"
            core_count += 1
        else:
            training_type = "speed_endurance"
            speed_endurance_count += 1
        
        enhanced_session["training_type"] = training_type
        
        # Process training day preferences
        date = session.get("date", "")
        if date:
            try:
                # Try to extract day of week
                from datetime import datetime
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")  # Full day name
                
                if day_name in training_days:
                    training_days[day_name] += 1
                else:
                    training_days[day_name] = 1
            except ValueError:
                # Handle invalid dates gracefully
                pass
        
        # Generate segment durations (for demo)
        import random
        # Use consistent seed for reproducibility
        random.seed(session_id if session_id else "default")
        
        # Calculate total duration first
        try:
            start_parts = start_time.split(":")
            end_parts = end_time.split(":")
            
            start_hours = int(start_parts[0]) if len(start_parts) > 0 else 0
            start_minutes = int(start_parts[1]) if len(start_parts) > 1 else 0
            end_hours = int(end_parts[0]) if len(end_parts) > 0 else 0
            end_minutes = int(end_parts[1]) if len(end_parts) > 1 else 0
            
            start_total_minutes = start_hours * 60 + start_minutes
            end_total_minutes = end_hours * 60 + end_minutes
            
            # Handle overnight sessions
            if end_total_minutes < start_total_minutes:
                end_total_minutes += 24 * 60
            
            total_duration = end_total_minutes - start_total_minutes
        except (ValueError, IndexError):
            total_duration = 120  # Default to 2 hours if calculation fails
        
        # Allocate segment durations
        warm_up_minutes = max(10, int(total_duration * 0.15))  # 15% of total time
        cool_down_minutes = max(10, int(total_duration * 0.1))  # 10% of total time
        main_minutes = total_duration - warm_up_minutes - cool_down_minutes
        
        segment_durations["warm_up_total"] += warm_up_minutes
        segment_durations["main_total"] += main_minutes
        segment_durations["cool_down_total"] += cool_down_minutes
        
        enhanced_session["segment_times"] = {
            "warm_up_minutes": warm_up_minutes,
            "main_minutes": main_minutes,
            "cool_down_minutes": cool_down_minutes,
            "total_minutes": total_duration
        }
        
        # Generate feedback for past sessions
        if date <= today.strftime("%Y-%m-%d"):
            # Ensure consistent random values
            random.seed(f"{session_id}-feedback" if session_id else "feedback-default")
            
            quality = random.randint(1, 10)
            condition = random.randint(1, 10)
            expectation = random.randint(1, 10)
            
            feedback_metrics["quality_ratings"].append(quality)
            feedback_metrics["condition_ratings"].append(condition)
            feedback_metrics["expectation_ratings"].append(expectation)
            
            feedback_notes = f"Session quality: {quality}/10. " + \
                           f"Athlete condition: {condition}/10. " + \
                           f"Met expectations: {expectation}/10."
            
            issues = []
            if quality < 5:
                issues.append("Quality issues in training execution")
            if condition < 5:
                issues.append("Athletes showing signs of fatigue")
            if expectation < 5:
                issues.append("Training not meeting planned objectives")
            
            if issues:
                feedback_notes += " Issues: " + ", ".join(issues)
                
            feedback_metrics["coach_feedback"].append({
                "session_id": session_id,
                "notes": feedback_notes,
                "issues_identified": len(issues) > 0
            })
            
            enhanced_session["feedback"] = {
                "quality_rating": quality,
                "condition_rating": condition,
                "expectation_rating": expectation,
                "notes": feedback_notes
            }
        
        enhanced_sessions.append(enhanced_session)
    
    # Calculate averages for feedback metrics
    avg_quality = sum(feedback_metrics["quality_ratings"]) / len(feedback_metrics["quality_ratings"]) if feedback_metrics["quality_ratings"] else 0
    avg_condition = sum(feedback_metrics["condition_ratings"]) / len(feedback_metrics["condition_ratings"]) if feedback_metrics["condition_ratings"] else 0
    avg_expectation = sum(feedback_metrics["expectation_ratings"]) / len(feedback_metrics["expectation_ratings"]) if feedback_metrics["expectation_ratings"] else 0
    
    # Find preferred day (most frequent)
    preferred_day = max(training_days.items(), key=lambda x: x[1])[0] if training_days else "N/A"
    
    # Find preferred session time
    preferred_time = max(session_times.items(), key=lambda x: x[1])[0] if any(session_times.values()) else "N/A"
    
    # Prepare segment duration averages
    session_count = len(sessions)
    avg_segment_durations = {}
    if session_count > 0:
        avg_segment_durations = {
            "avg_warm_up_minutes": segment_durations["warm_up_total"] / session_count,
            "avg_main_minutes": segment_durations["main_total"] / session_count,
            "avg_cool_down_minutes": segment_durations["cool_down_total"] / session_count,
            "avg_total_minutes": (segment_durations["warm_up_total"] + segment_durations["main_total"] + segment_durations["cool_down_total"]) / session_count
        }
    
    # Prepare final summary statistics
    summary_stats = {
        "total_training_plans": len(sessions),
        "training_type_counts": {
            "core_training": core_count,
            "speed_endurance_training": speed_endurance_count
        },
        "training_day_preferences": {
            "day_distribution": training_days,
            "preferred_day": preferred_day
        },
        "session_time_preferences": {
            "time_distribution": session_times,
            "preferred_time": preferred_time
        },
        "segment_durations": {
            "total_durations": segment_durations,
            "average_durations": avg_segment_durations
        },
        "feedback_summary": {
            "average_ratings": {
                "quality": avg_quality,
                "athlete_condition": avg_condition,
                "met_expectations": avg_expectation
            },
            "issue_count": sum(1 for feedback in feedback_metrics["coach_feedback"] if feedback.get("issues_identified", False)),
            "total_feedback_count": len(feedback_metrics["coach_feedback"])
        }
    }
    
    return JSONResponse(content={
        "training_sessions": enhanced_sessions,
        "summary_statistics": summary_stats
    })

# Get a single training session
@app.get("/api/training-sessions/{session_id}", 
    response_model=TrainingSessionResponse,
    summary="Get training session details",
    description="Retrieve detailed information about a specific training session, including segment times and feedback metrics.",
    tags=["Training"])
def get_training_session(session_id: str):
    """Get detailed information about a specific training session.
    
    This endpoint provides comprehensive details about a single training session, including:
    - Basic session information (title, date, time)
    - Training type (core or speed & endurance)
    - Session time (morning, afternoon, night)
    - Total duration in minutes
    - Breakdown of time spent in each segment (warm-up, main, cool-down)
    - Coach feedback ratings and notes
    
    Args:
        session_id (str): The unique identifier of the training session
        
    Returns:
        TrainingSessionResponse: Detailed training session information with segment times and feedback
        
    Raises:
        HTTPException: 404 error if session is not found
    """
    sessions = dummy_data.get("training_sessions", [])
    for session in sessions:
        if session.get("id") == session_id:
            # Create enhanced session object with additional calculated fields
            enhanced_session = session.copy()
            
            # Find team information
            team_id = session.get("team_id")
            team_name = ""
            for team in dummy_data.get("teams", []):
                if team.get("id") == team_id:
                    team_name = team.get("name")
                    break
            enhanced_session["team_name"] = team_name
            
            # Calculate training duration in minutes
            start_time = session.get("start_time", "00:00")
            end_time = session.get("end_time", "00:00")
            
            # Safely handle time formats
            start_parts = start_time.split(":")
            end_parts = end_time.split(":")
            
            # Ensure we only get hours and minutes
            start_hours = int(start_parts[0]) if len(start_parts) > 0 else 0
            start_minutes = int(start_parts[1]) if len(start_parts) > 1 else 0
            end_hours = int(end_parts[0]) if len(end_parts) > 0 else 0
            end_minutes = int(end_parts[1]) if len(end_parts) > 1 else 0
            
            start_total_minutes = start_hours * 60 + start_minutes
            end_total_minutes = end_hours * 60 + end_minutes
            
            # Handle overnight sessions
            if end_total_minutes < start_total_minutes:
                end_total_minutes += 24 * 60
            
            total_minutes = end_total_minutes - start_total_minutes
            enhanced_session["total_minutes"] = total_minutes
            
            # Set training type (based on session ID for consistency)
            training_type = "core" if session.get("id", "")[-1].isdigit() and int(session.get("id", "")[-1]) % 2 == 0 else "speed_endurance"
            enhanced_session["training_type"] = training_type
            
            # Set session time based on start time
            if start_hours < 12:
                session_time = "morning"
            elif start_hours < 17:
                session_time = "afternoon"
            else:
                session_time = "night"
            enhanced_session["session_time"] = session_time
            
            # Generate segment times (consistent for specific session)
            import random
            # Use session_id to seed random generator for consistency
            random.seed(session_id)
            warm_up_minutes = random.randint(10, 30)
            cool_down_minutes = random.randint(10, 20)
            main_minutes = total_minutes - warm_up_minutes - cool_down_minutes
            
            if main_minutes < 0:
                main_minutes = max(total_minutes - 15, 0)
                warm_up_minutes = 10 if total_minutes > 10 else total_minutes // 2
                cool_down_minutes = max(total_minutes - warm_up_minutes - main_minutes, 0)
            
            enhanced_session["segment_times"] = {
                "warm_up_minutes": warm_up_minutes,
                "main_minutes": main_minutes,
                "cool_down_minutes": cool_down_minutes
            }
            
            # Generate feedback for past sessions
            if session.get("date") <= today.strftime("%Y-%m-%d"):
                # Reset seed to ensure consistent values
                random.seed(session_id + "feedback")
                quality = random.randint(1, 10)
                condition = random.randint(1, 10)
                expectation = random.randint(1, 10)
                
                enhanced_session["feedback"] = {
                    "quality_rating": quality,
                    "condition_rating": condition,
                    "expectation_rating": expectation,
                    "coach_notes": f"Session was rated {quality}/10 for quality, {condition}/10 for athlete condition, and {expectation}/10 for meeting expectations."
                }
            
            return TrainingSessionResponse(**enhanced_session)
    raise HTTPException(status_code=404, detail="Training session not found")

# Get performance assessments
@app.get("/api/performance-assessments")
def get_performance_assessments():
    return JSONResponse(content={"performance_assessments": dummy_data.get("performance_assessments", [])})

# Get injury reports
@app.get("/api/injury-reports")
def get_injury_reports():
    return JSONResponse(content={"injury_reports": dummy_data.get("injury_reports", [])})

# Get recovery data
@app.get("/api/recovery-data")
def get_recovery_data():
    return JSONResponse(content={"recovery_data": dummy_data.get("recovery_data", [])})