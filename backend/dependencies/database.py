import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

# Get database URL from environment variable or use default for development
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/appdb"
)

# Create sync engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# Create Redis client
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Dependency that provides a database session
def get_db() -> Generator:
    """
    Dependency function that yields a SQLAlchemy session.
    To be used in FastAPI dependency injection system.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis() -> Generator[redis.Redis, None, None]:
    """
    Get a Redis client for dependency injection
    """
    try:
        yield redis_client
    finally:
        pass  # Redis connections are managed by the client pool

# For backwards compatibility with any code using get_db_session
def get_db_session() -> Generator:
    """
    Alias for get_db() for backward compatibility
    """
    yield from get_db() 