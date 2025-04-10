#!/usr/bin/env python3
"""
Sample script to demonstrate the API report generator.
This script generates a report from sample test results and opens it in the browser.
"""

import os
import logging
from utils.api_report_generator import APIReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ensure the reports directory exists
os.makedirs('reports', exist_ok=True)

def main():
    """Generate a sample report and open it in the browser"""
    try:
        # Create the report generator with the sample data
        generator = APIReportGenerator(input_file='sample_test_results.json')
        
        # Generate the report
        report_file = generator.generate_report()
        
        # Open the report in the browser
        generator.open_in_browser(report_file)
        
        print(f"Report generated successfully: {report_file}")
        print("The report has been opened in your browser.")
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        raise

if __name__ == "__main__":
    main() 