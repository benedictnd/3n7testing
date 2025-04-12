from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc, text
from datetime import datetime, timedelta
import os
import json
import hashlib
import time
import asyncio
from redis import Redis

from models.notification import Notification, NotificationResponse
from models.training import FeedbackCreate, FeedbackResponse, TrainingLog, TrainingSession
from services.training_service import TrainingService
from services.notification_service import NotificationService
from repositories.notification_repository import NotificationRepository
from dependencies.database import get_db_session
from dependencies.auth import get_current_user
from utils.compression import (
    CompressionFormat, 
    CompressionLevel, 
    compress_json, 
    should_compress,
    get_client_supported_compression
)

router = APIRouter(
    prefix="/training",
    tags=["training"],
    responses={404: {"description": "Not found"}},
)

# Initialize Redis connection for caching
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
redis_client = Redis.from_url(redis_url) if redis_enabled else None
CACHE_TTL = 600  # Cache TTL in seconds (10 minutes)
COMPRESSION_THRESHOLD = 4096  # 4KB threshold for compression

def get_cache_key(user_id: str, endpoint: str, params: Dict[str, Any]) -> str:
    """Generate a unique cache key based on user and request parameters"""
    # Sort params to ensure consistent key generation
    sorted_params = sorted((k, str(v)) for k, v in params.items() if v is not None)
    param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
    key_data = f"{user_id}:{endpoint}:{param_str}"
    return f"training_api:{hashlib.md5(key_data.encode()).hexdigest()}"

async def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response if available"""
    if not redis_enabled or not redis_client:
        return None
        
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        # Log error but continue with DB query
        print(f"Cache error: {str(e)}")
    return None

async def set_cached_response(cache_key: str, response_data: Dict[str, Any], ttl: int = CACHE_TTL) -> None:
    """Cache response data"""
    if not redis_enabled or not redis_client:
        return
        
    try:
        redis_client.setex(
            cache_key,
            ttl,
            json.dumps(response_data)
        )
    except Exception as e:
        # Log error but continue
        print(f"Cache error: {str(e)}")

@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db_session),
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
    db: AsyncSession = Depends(get_db_session),
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
    db: AsyncSession = Depends(get_db_session),
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
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo)
    
    count = await notification_service.mark_all_as_read(current_user.id)
    
    return {"message": f"{count} notifications marked as read"}

@router.get("/logs")
async def get_training_logs(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(50, description="Number of logs to return", ge=1, le=100),
    offset: int = Query(0, description="Number of logs to skip", ge=0),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    response: Response = None,
    accept_encoding: Optional[str] = Header(None),
):
    """
    Get training logs with filters and pagination
    
    Optimized with:
    - Efficient SQL queries with composite indexes
    - Response compression for large payloads
    - Redis caching with key-based invalidation
    - Parallel query execution
    - Optimized data serialization
    """
    # Check if user has permission
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Prepare cache params and key
    cache_params = {
        "start_date": start_date,
        "end_date": end_date,
        "user_id": user_id,
        "session_id": session_id,
        "limit": limit,
        "offset": offset,
    }
    cache_key = get_cache_key(current_user["id"], "training_logs", cache_params)
    
    # Check cache first (fast path)
    cached_response = await get_cached_response(cache_key)
    if cached_response:
        if response:
            response.headers["X-Cache"] = "HIT"
        
        # If client supports compression, apply it directly to the cached response
        result_json = json.dumps(cached_response).encode('utf-8')
        if should_compress(len(result_json), COMPRESSION_THRESHOLD):
            compression_format = get_client_supported_compression(accept_encoding)
            if compression_format != CompressionFormat.NONE:
                compressed_data = compress_json(
                    cached_response, 
                    format=compression_format,
                    level=CompressionLevel.DEFAULT
                )
                if response:
                    response.headers["Content-Encoding"] = compression_format.value
                    response.headers["Content-Length"] = str(len(compressed_data))
                return Response(
                    content=compressed_data,
                    media_type="application/json",
                    headers=response.headers if response else None
                )
        
        return cached_response
    
    # Cache miss - need to query database
    if response:
        response.headers["X-Cache"] = "MISS"
    
    # Start timer for performance tracking
    start_time = time.time()
    
    # Build query components - optimized for the new indexes
    where_clauses = []
    params = {}
    
    if start_date:
        where_clauses.append("tl.created_at >= :start_date")
        params["start_date"] = datetime.fromisoformat(start_date)
    
    if end_date:
        # Add one day to include the end date completely
        end_date_obj = datetime.fromisoformat(end_date) + timedelta(days=1)
        where_clauses.append("tl.created_at < :end_date")
        params["end_date"] = end_date_obj
    
    if user_id:
        where_clauses.append("tl.user_id = :user_id")
        params["user_id"] = user_id
    
    if session_id:
        where_clauses.append("tl.session_id = :session_id")
        params["session_id"] = session_id
    
    # Apply permissions - users can only see their own logs unless they are coaches or admins
    if current_user["role"] not in ["coach", "admin"]:
        where_clauses.append("tl.user_id = :current_user_id")
        params["current_user_id"] = current_user["id"]
    
    # Combine WHERE clauses
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Define optimized SQL queries with explicit index hints for PostgreSQL
    count_sql = f"""
    SELECT COUNT(*) 
    FROM training_logs tl
    {where_sql}
    """
    
    # Add index hint for PostgreSQL (will be ignored by other DB engines)
    index_hint = ""
    if user_id or (current_user["role"] not in ["coach", "admin"]):
        index_hint = "/*+ INDEX(tl training_logs_user_session_idx) */"
    
    query_sql = f"""
    SELECT {index_hint} tl.* 
    FROM training_logs tl
    {where_sql}
    ORDER BY tl.created_at DESC
    LIMIT :limit OFFSET :offset
    """
    
    params["limit"] = limit
    params["offset"] = offset
    
    # Execute queries in parallel using asyncio.gather for better performance
    async def execute_count_query():
        result = await db_session.execute(text(count_sql), params)
        return result.scalar_one()
    
    async def execute_data_query():
        result = await db_session.execute(text(query_sql), params)
        return result.fetchall()
    
    # Run queries in parallel
    try:
        total, logs = await asyncio.gather(
            execute_count_query(),
            execute_data_query()
        )
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Database query error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query error occurred"
        )
    
    # Format response data efficiently
    logs_data = []
    for log in logs:
        # Use direct attribute access instead of dict lookups for better performance
        log_data = {
            "id": log.id,
            "user_id": log.user_id,
            "session_id": log.session_id,
            "log_type": log.log_type,
            "data": log.data,
            "created_at": log.created_at.isoformat(),
        }
        logs_data.append(log_data)
    
    # Create response with execution time and cache status
    response_data = {
        "logs": logs_data,
        "total": total,
        "limit": limit,
        "offset": offset,
        "execution_time_ms": int((time.time() - start_time) * 1000),
        "cache": "MISS",
        "compression_applied": False
    }
    
    # Cache the response for future requests
    await set_cached_response(cache_key, response_data, CACHE_TTL)
    
    # Apply compression if needed
    result_json = json.dumps(response_data).encode('utf-8')
    if should_compress(len(result_json), COMPRESSION_THRESHOLD):
        compression_format = get_client_supported_compression(accept_encoding)
        if compression_format != CompressionFormat.NONE:
            response_data["compression_applied"] = True
            compressed_data = compress_json(
                response_data, 
                format=compression_format,
                level=CompressionLevel.DEFAULT
            )
            
            if response:
                response.headers["Content-Encoding"] = compression_format.value
                response.headers["Content-Length"] = str(len(compressed_data))
            
            return Response(
                content=compressed_data,
                media_type="application/json",
                headers=response.headers if response else None
            )
    
    return response_data 