#!/bin/bash

# Run API tests for the 3&7 Training Platform

# Set default values
API_BASE_URL="http://localhost:8000"
EMAIL="test@example.com"
PASSWORD="password123"
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --url)
      API_BASE_URL="$2"
      shift 2
      ;;
    --email)
      EMAIL="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --url URL           API Base URL (default: http://localhost:8000)"
      echo "  --email EMAIL       Email for authentication (default: test@example.com)"
      echo "  --password PASS     Password for authentication (default: password123)"
      echo "  --verbose           Show verbose output"
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

# Function to check if command exists
command_exists() {
  command -v "$1" &> /dev/null
}

# Ensure required tools are installed
if ! command_exists python3; then
  echo "Error: python3 is required but not installed"
  exit 1
fi

# Check if test-requirements.txt exists and install dependencies if needed
if [ -f "test-requirements.txt" ]; then
  if ! command_exists pip; then
    echo "Error: pip is required but not installed"
    exit 1
  fi
  
  echo "Installing test dependencies..."
  pip install -r test-requirements.txt
fi

# Run security scan
if command_exists bandit; then
  echo "Running security scan with bandit..."
  bandit -r routes/ middleware/ dependencies/ || { echo "Security scan failed"; exit 1; }
fi

# Run API tests
echo "Running API tests against $API_BASE_URL"
export API_BASE_URL="$API_BASE_URL"

if [ "$VERBOSE" = true ]; then
  python3 api_test.py --url "$API_BASE_URL" --email "$EMAIL" --password "$PASSWORD" -v
else
  python3 api_test.py --url "$API_BASE_URL" --email "$EMAIL" --password "$PASSWORD"
fi

# Check if the tests were successful
if [ $? -eq 0 ]; then
  echo "API tests completed successfully"
else
  echo "API tests failed"
  exit 1
fi

# Displaying test results
if [ -d "./test-logs" ]; then
  # Find the most recent report file
  LATEST_REPORT=$(ls -t ./test-logs/report_*.md | head -1)
  
  if [ -n "$LATEST_REPORT" ]; then
    echo "Latest test report: $LATEST_REPORT"
    
    # If we have the rich tool installed, use it to display the report
    if command_exists rich; then
      rich "$LATEST_REPORT"
    else
      cat "$LATEST_REPORT"
    fi
  else
    echo "No test reports found"
  fi
else
  echo "No test logs directory found"
fi 