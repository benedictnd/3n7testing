#!/bin/bash

# Run load tests for the 3&7 Training Platform

# Set default values
HOST="http://localhost:8000"
USERS=10
SPAWN_RATE=1
RUN_TIME="1m"
USER_CLASS="TrainingPlatformUser"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host)
      HOST="$2"
      shift 2
      ;;
    --users)
      USERS="$2"
      shift 2
      ;;
    --spawn-rate)
      SPAWN_RATE="$2"
      shift 2
      ;;
    --run-time)
      RUN_TIME="$2"
      shift 2
      ;;
    --user-class)
      USER_CLASS="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --host HOST         Host to test (default: http://localhost:8000)"
      echo "  --users USERS       Number of users to simulate (default: 10)"
      echo "  --spawn-rate RATE   Spawn rate in users per second (default: 1)"
      echo "  --run-time TIME     Run time in minutes (default: 1m)"
      echo "  --user-class CLASS  User class to use (default: TrainingPlatformUser)"
      echo "  --help              Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if locust is installed
if ! command -v locust &> /dev/null; then
  echo "Locust is not installed. Installing..."
  pip install locust
fi

# Run the load test
echo "Running load test with the following parameters:"
echo "  Host: $HOST"
echo "  Users: $USERS"
echo "  Spawn rate: $SPAWN_RATE"
echo "  Run time: $RUN_TIME"
echo "  User class: $USER_CLASS"
echo ""

locust -f locustfile.py --headless -u $USERS -r $SPAWN_RATE --run-time $RUN_TIME --host $HOST -c $USER_CLASS

# Check if the load test was successful
if [ $? -eq 0 ]; then
  echo "Load test completed successfully."
else
  echo "Load test failed."
  exit 1
fi 