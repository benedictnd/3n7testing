import os
import sys
import asyncio
import logging
from logging.config import fileConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect

from dependencies.database import DATABASE_URL


async def check_database_exists():
    """Check if the database exists and has tables"""
    try:
        # Create an async engine
        engine = create_async_engine(DATABASE_URL)
        
        # Create a connection
        async with engine.connect() as conn:
            # Get the inspector
            inspector = inspect(conn)
            
            # Get all table names
            tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
            
            # Check if any tables exist
            if tables:
                logger.info(f"Database exists with tables: {', '.join(tables)}")
                return True
            else:
                logger.info("Database exists but has no tables")
                return False
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return False


async def run_migrations():
    """Run Alembic migrations"""
    try:
        # Check if the database exists
        db_exists = await check_database_exists()
        
        # Get Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Check current revision
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Run migrations
        if db_exists:
            logger.info("Running migrations to head")
            command.upgrade(alembic_cfg, "head")
        else:
            logger.info("Running initial migration")
            command.upgrade(alembic_cfg, "head")
        
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise


if __name__ == "__main__":
    # Run the migrations
    try:
        asyncio.run(run_migrations())
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1) 