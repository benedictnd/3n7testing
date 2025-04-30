import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logging
import time
from fastapi import HTTPException, status
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment variable or use default for development
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/training_platform"
)

# Maximum retries for database connections
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Check connection validity before using from pool
    pool_recycle=300,  # Recycle connections after 5 minutes
    pool_size=10,      # Maximum number of connections in pool
    max_overflow=20    # Maximum overflow connections
)

# Create session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@asynccontextmanager
async def get_db():
    """Get database session with error handling and connection retries."""
    session = None
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            session = async_session()
            await session.connection()  # Test connection
            yield session
            break
        except Exception as e:
            retries += 1
            if session:
                await session.close()
                session = None
            
            logger.error(f"Database connection error (attempt {retries}/{MAX_RETRIES}): {str(e)}")
            
            if retries >= MAX_RETRIES:
                logger.critical(f"Failed to connect to database after {MAX_RETRIES} attempts")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection failed. Please try again later."
                )
            
            # Wait before retrying
            time.sleep(RETRY_DELAY * retries)  # Exponential backoff
    
    # Cleanup
    if session:
        try:
            await session.close()
        except Exception as e:
            logger.error(f"Error closing database session: {str(e)}")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session with proper error handling."""
    session = None
    try:
        session = async_session()
        yield session
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        if session:
            await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later."
        )
    finally:
        if session:
            await session.close() 