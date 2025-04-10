#!/usr/bin/env python
"""
API Test Report Generator CLI

Command-line tool for generating visual API test reports.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from utils.api_report_generator import APIReportGenerator
from utils.generate_test_data import generate_all_data

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Generate visual reports for API test results")
    
    parser.add_argument("--input-dir", "-i", 
                        help="Directory containing JSON test data files")
    
    parser.add_argument("--output-file", "-o", default="api_test_report.html",
                       help="Output HTML report file path")
    
    parser.add_argument("--generate-data", "-g", action="store_true",
                       help="Generate sample data instead of using existing files")
    
    parser.add_argument("--data-dir", "-d", default="test-data",
                       help="Directory for generated sample data (when using --generate-data)")
    
    parser.add_argument("--force", "-f", action="store_true",
                      help="Overwrite existing report file if it exists")
    
    return parser.parse_args()

def main():
    """Main entry point for the CLI"""
    args = parse_args()
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine output file path
    output_path = Path(args.output_file)
    if not args.force and output_path.exists():
        print(f"Error: Output file '{output_path}' already exists. Use --force to overwrite.")
        return 1
    
    # Generate or use existing data
    if args.generate_data:
        print(f"Generating sample test data in '{args.data_dir}'...")
        data = generate_all_data(args.data_dir)
        
        # Use the generated data directly
        report_generator = APIReportGenerator(
            test_results=data["test_results"],
            performance_data=data["performance_data"],
            security_findings=data["security_findings"],
            flaky_tests=data["flaky_tests"]
        )
    else:
        if not args.input_dir:
            print("Error: Please specify --input-dir or use --generate-data")
            return 1
        
        input_dir = Path(args.input_dir)
        if not input_dir.exists() or not input_dir.is_dir():
            print(f"Error: Input directory '{input_dir}' does not exist or is not a directory")
            return 1
        
        # Check if required files exist
        required_files = [
            "test_results.json", 
            "performance_metrics.json", 
            "security_scan.json", 
            "flaky_tests.json"
        ]
        
        missing_files = [f for f in required_files if not (input_dir / f).exists()]
        if missing_files:
            print(f"Error: Missing required data files in '{input_dir}':")
            for file in missing_files:
                print(f"  - {file}")
            return 1
        
        print(f"Loading test data from '{input_dir}'...")
        # Create the report generator from JSON files
        report_generator = APIReportGenerator.from_json_files(
            test_results_path=str(input_dir / "test_results.json"),
            performance_path=str(input_dir / "performance_metrics.json"),
            security_path=str(input_dir / "security_scan.json"),
            flaky_path=str(input_dir / "flaky_tests.json")
        )
    
    # Generate the report
    print(f"Generating API test report...")
    report_path = report_generator.generate_report(str(output_path))
    
    print(f"Report generated successfully: {report_path}")
    
    # Print additional instructions
    print("\nTo view the report:")
    if os.name == 'nt':  # Windows
        print(f"  > start {report_path}")
    else:  # Unix-like
        print(f"  $ open {report_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 