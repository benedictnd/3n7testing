#!/bin/bash
# Script to run both backend and frontend in development mode

# Enable error handling
set -e

# Function to handle termination
function cleanup {
  echo "Stopping services..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  exit
}

# Trap SIGINT and SIGTERM signals
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
else
  echo "Warning: Virtual environment not found. Please create it with 'python -m venv venv'"
fi

# Run database migrations
echo "Running database migrations..."
python run_migrations.py

# Start the backend
echo "Starting FastAPI backend..."
cd backend || cd . # If there's no backend directory, stay in the current directory
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start the frontend
echo "Starting Next.js frontend..."
cd ../frontend || cd frontend || (echo "Frontend directory not found" && exit 1)
npm run dev &
FRONTEND_PID=$!

# Keep script running
wait 