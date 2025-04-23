#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  echo "PostgreSQL unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up - continuing"

# Wait for Redis to be ready
echo "Waiting for Redis..."
until redis-cli -h $REDIS_HOST -p $REDIS_PORT ping | grep -q "PONG"; do
  echo "Redis unavailable - sleeping"
  sleep 2
done
echo "Redis is up - continuing"

# Run database migrations
echo "Running database migrations..."
if [ -d "alembic" ]; then
  alembic upgrade head
fi

# Start the application
echo "Starting the application..."
uvicorn main:app --host 0.0.0.0 --port $PORT --reload 