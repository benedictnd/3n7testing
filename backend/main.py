from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker, Session
import logging
import time
import os
from typing import Dict, Any, List

# Add Redis imports
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis

from models.db_models import Base, User, TrainingSession, WarmingUp, MainTraining, CoolingDown, Attendance, Feedback, PerformanceRecord, Notification
from routes import training_sessions, users, reports
from routes.auth import router as auth_router
from dependencies.database import get_db, DATABASE_URL, REDIS_URL, engine, redis_client

# Import routes
from routes.users import router as users_router
from routes.training_sessions import router as training_sessions_router
from routes.reports import router as reports_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Custom exception class for application errors
class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application
    """
    # Startup: Create tables if they don't exist
    logger.info("Starting up application...")
    try:
        # Create tables
        logger.info("Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready.")
        
        # Set up Redis caching
        redis_connection = redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis_connection), prefix="fastapi-cache")
        logger.info("Redis cache initialized.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

    # Application runs here
    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down application...")
    logger.info("Database connections closed.")


# Create FastAPI app with rich configuration
app = FastAPI(
    title="3&7 Training Platform API",
    description="API for the 3&7 Training and Recovery Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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


# Custom middleware for request timing and logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log request information and timing
    """
    start_time = time.time()
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request: {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.4f}s"
        )
        raise


# Custom exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handle application-specific exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Generic exception handler for unexpected errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle any unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."}
    )


# Custom SwaggerUI with better styling
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Serve custom Swagger UI
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/image/favicon.ico",
    )


# Custom OpenAPI schema with more details
def custom_openapi():
    """
    Generate customized OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token with 'Bearer ' prefix",
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Include routers
app.include_router(auth_router)
app.include_router(training_sessions_router)
app.include_router(users_router)
app.include_router(reports_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint to verify the API is running
    """
    return {
        "status": "healthy",
        "version": app.version,
        "environment": os.environ.get("ENVIRONMENT", "development")
    }


@app.get("/")
async def root():
    return {"message": "Welcome to 3&7 Training Platform API"}


# User endpoints
@app.get("/api/users", tags=["Users"], response_model=List[Dict[str, Any]])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        for user in users
    ]


# Training session endpoints
@app.get("/api/training-sessions", tags=["Training Sessions"], response_model=List[Dict[str, Any]])
def get_training_sessions(db: Session = Depends(get_db)):
    sessions = db.query(TrainingSession).all()
    return [
        {
            "id": session.id,
            "type": session.type,
            "date": session.date.isoformat() if session.date else None,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "coach": session.coach.name if session.coach else None,
            "training_quality": session.training_quality,
            "expectations": session.expectations,
            "team_condition": session.team_condition,
            "notes": session.notes,
        }
        for session in sessions
    ]


# Get training session with details
@app.get("/api/training-sessions/{session_id}", tags=["Training Sessions"], response_model=Dict[str, Any])
def get_training_session_details(session_id: int, db: Session = Depends(get_db)):
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    # Get warming up data
    warming_ups = db.query(WarmingUp).filter(WarmingUp.training_session_id == session_id).all()
    warming_up_data = [
        {
            "id": wu.id,
            "notes": wu.notes,
            "duration": wu.duration
        }
        for wu in warming_ups
    ]
    
    # Get main training data
    main_trainings = db.query(MainTraining).filter(MainTraining.training_session_id == session_id).all()
    main_training_data = []
    
    for mt in main_trainings:
        # Get performance records for this main training
        performance_records = db.query(PerformanceRecord).filter(PerformanceRecord.main_training_id == mt.id).all()
        performance_data = [
            {
                "id": pr.id,
                "athlete": pr.athlete.name if pr.athlete else None,
                "time": str(pr.time) if pr.time else None,
                "repetitions": pr.repetitions,
                "sets": pr.sets,
                "weight": pr.weight,
                "notes": pr.notes
            }
            for pr in performance_records
        ]
        
        main_training_data.append({
            "id": mt.id,
            "notes": mt.notes,
            "duration": mt.duration,
            "performance_records": performance_data
        })
    
    # Get cooling down data
    cooling_downs = db.query(CoolingDown).filter(CoolingDown.training_session_id == session_id).all()
    cooling_down_data = [
        {
            "id": cd.id,
            "notes": cd.notes,
            "duration": cd.duration
        }
        for cd in cooling_downs
    ]
    
    # Get attendance data
    attendances = db.query(Attendance).filter(Attendance.training_session_id == session_id).all()
    attendance_data = [
        {
            "id": a.id,
            "athlete": a.athlete.name if a.athlete else None,
            "check_in_time": a.check_in_time.isoformat() if a.check_in_time else None
        }
        for a in attendances
    ]
    
    # Get feedback data
    feedbacks = db.query(Feedback).filter(Feedback.training_session_id == session_id).all()
    feedback_data = [
        {
            "id": f.id,
            "athlete": f.athlete.name if f.athlete else None,
            "training_quality": f.training_quality,
            "expectations": f.expectations,
            "body_condition": f.body_condition,
            "intensity": f.intensity,
            "notes": f.notes
        }
        for f in feedbacks
    ]
    
    # Compile complete training session data
    return {
        "id": session.id,
        "type": session.type,
        "date": session.date.isoformat() if session.date else None,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "coach": {
            "id": session.coach.id if session.coach else None,
            "name": session.coach.name if session.coach else None,
        },
        "training_quality": session.training_quality,
        "expectations": session.expectations,
        "team_condition": session.team_condition,
        "notes": session.notes,
        "documentation": session.documentation,
        "warming_ups": warming_up_data,
        "main_trainings": main_training_data,
        "cooling_downs": cooling_down_data,
        "attendances": attendance_data,
        "feedbacks": feedback_data
    }


@app.get("/api/all-data", tags=["Data Export"], response_model=Dict[str, Any])
def get_all_data(db: Session = Depends(get_db)):
    """
    Get all database data for export
    """
    users = db.query(User).all()
    users_data = [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]
    
    sessions = db.query(TrainingSession).all()
    sessions_data = []
    
    for session in sessions:
        # Get warming up data
        warming_ups = db.query(WarmingUp).filter(WarmingUp.training_session_id == session.id).all()
        warming_up_data = [
            {
                "id": wu.id,
                "notes": wu.notes,
                "duration": wu.duration
            }
            for wu in warming_ups
        ]
        
        # Get main training data
        main_trainings = db.query(MainTraining).filter(MainTraining.training_session_id == session.id).all()
        main_training_data = []
        
        for mt in main_trainings:
            # Get performance records for this main training
            performance_records = db.query(PerformanceRecord).filter(PerformanceRecord.main_training_id == mt.id).all()
            performance_data = [
                {
                    "id": pr.id,
                    "athlete": {
                        "id": pr.athlete.id,
                        "name": pr.athlete.name
                    } if pr.athlete else None,
                    "time": str(pr.time) if pr.time else None,
                    "repetitions": pr.repetitions,
                    "sets": pr.sets,
                    "weight": pr.weight,
                    "notes": pr.notes
                }
                for pr in performance_records
            ]
            
            main_training_data.append({
                "id": mt.id,
                "notes": mt.notes,
                "duration": mt.duration,
                "performance_records": performance_data
            })
        
        # Get cooling down data
        cooling_downs = db.query(CoolingDown).filter(CoolingDown.training_session_id == session.id).all()
        cooling_down_data = [
            {
                "id": cd.id,
                "notes": cd.notes,
                "duration": cd.duration
            }
            for cd in cooling_downs
        ]
        
        # Get attendance data
        attendances = db.query(Attendance).filter(Attendance.training_session_id == session.id).all()
        attendance_data = [
            {
                "id": a.id,
                "athlete": {
                    "id": a.athlete.id,
                    "name": a.athlete.name
                } if a.athlete else None,
                "check_in_time": a.check_in_time.isoformat() if a.check_in_time else None
            }
            for a in attendances
        ]
        
        # Get feedback data
        feedbacks = db.query(Feedback).filter(Feedback.training_session_id == session.id).all()
        feedback_data = [
            {
                "id": f.id,
                "athlete": {
                    "id": f.athlete.id,
                    "name": f.athlete.name
                } if f.athlete else None,
                "training_quality": f.training_quality,
                "expectations": f.expectations,
                "body_condition": f.body_condition,
                "intensity": f.intensity,
                "notes": f.notes
            }
            for f in feedbacks
        ]
        
        sessions_data.append({
            "id": session.id,
            "type": session.type,
            "date": session.date.isoformat() if session.date else None,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "coach": {
                "id": session.coach.id,
                "name": session.coach.name
            } if session.coach else None,
            "training_quality": session.training_quality,
            "expectations": session.expectations,
            "team_condition": session.team_condition,
            "notes": session.notes,
            "documentation": session.documentation,
            "warming_ups": warming_up_data,
            "main_trainings": main_training_data,
            "cooling_downs": cooling_down_data,
            "attendances": attendance_data,
            "feedbacks": feedback_data
        })
    
    # Get notifications data
    notifications = db.query(Notification).all()
    notifications_data = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "recipient": {
                "id": n.recipient.id,
                "name": n.recipient.name
            } if n.recipient else None,
            "sender": {
                "id": n.sender.id,
                "name": n.sender.name
            } if n.sender else None,
            "related_id": n.related_id,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }
        for n in notifications
    ]
    
    return {
        "users": users_data,
        "training_sessions": sessions_data,
        "notifications": notifications_data
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 