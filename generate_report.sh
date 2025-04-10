#!/bin/bash

# Check if Python exists
if ! command -v python3 &> /dev/null; then
  echo "Python 3 not found"
  echo "Please install Python 3.10 or later"
  exit 1
fi

# Install required packages if needed
echo "Installing required packages..."
python3 -m pip install -r requirements.txt

# Create reports directory if it doesn't exist
mkdir -p reports

# Generate sample data and report
echo "Generating API test report..."
python3 generate_api_report.py --generate-data --output-file reports/api_report.html --force

if [ $? -eq 0 ]; then
  echo "Report generated successfully!"
  echo "Opening report..."
  # Try different commands to open the HTML file in a browser
  if command -v xdg-open &> /dev/null; then
    xdg-open reports/api_report.html
  elif command -v open &> /dev/null; then
    open reports/api_report.html
  else
    echo "Report available at: reports/api_report.html"
    echo "Open this file in a web browser to view the report."
  fi
else
  echo "Failed to generate report."
fi 