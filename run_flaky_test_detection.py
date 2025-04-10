#!/usr/bin/env python3
"""
Flaky Test Detection Tool

This tool runs tests multiple times to detect flaky tests. It generates a report
of flaky tests with their flakiness scores, pass rates, and other metrics.

Usage:
    python run_flaky_test_detection.py --iterations 20 --test-file tests/stability/test_flaky_api.py
"""

import argparse
import logging
import os
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_ITERATIONS = 10
DEFAULT_TEST_DIR = "tests/stability"
DEFAULT_REPORT_DIR = "test-reports/flaky-tests"


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests to detect flaky behavior")
    
    parser.add_argument(
        "--iterations", "-i", 
        type=int, 
        default=DEFAULT_ITERATIONS,
        help=f"Number of test iterations to run (default: {DEFAULT_ITERATIONS})"
    )
    
    parser.add_argument(
        "--test-file", "-f", 
        type=str, 
        help="Specific test file to run (e.g., tests/stability/test_flaky_api.py)"
    )
    
    parser.add_argument(
        "--test-dir", "-d", 
        type=str, 
        default=DEFAULT_TEST_DIR,
        help=f"Directory containing test files (default: {DEFAULT_TEST_DIR})"
    )
    
    parser.add_argument(
        "--report-dir", "-r", 
        type=str, 
        default=DEFAULT_REPORT_DIR,
        help=f"Directory to save reports (default: {DEFAULT_REPORT_DIR})"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--html", 
        action="store_true", 
        help="Generate HTML report in addition to JSON"
    )
    
    parser.add_argument(
        "--threshold", "-t", 
        type=float, 
        default=0.1,
        help="Flakiness threshold to consider a test flaky (default: 0.1)"
    )
    
    return parser.parse_args()


def setup_environment(args):
    """Set up the environment for running the tests."""
    # Create report directory if it doesn't exist
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = os.path.abspath(os.getcwd())
    os.environ["FLAKY_TEST_THRESHOLD"] = str(args.threshold)
    
    if args.verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    return report_dir


def run_tests(args, report_dir):
    """Run the specified tests multiple times to detect flaky behavior."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine which tests to run
    if args.test_file:
        test_files = [args.test_file]
    else:
        test_dir = Path(args.test_dir)
        test_files = list(test_dir.glob("test_*.py"))
        if not test_files:
            logger.error(f"No test files found in directory: {args.test_dir}")
            return False
    
    logger.info(f"Running flaky test detection on {len(test_files)} test file(s) for {args.iterations} iterations")
    
    test_results = {}
    start_time = time.time()
    
    for test_file in test_files:
        test_file_path = str(test_file)
        test_name = os.path.basename(test_file_path)
        
        logger.info(f"Running tests from {test_name}")
        
        # Run the test with Python directly
        try:
            cmd = [
                sys.executable,
                test_file_path
            ]
            
            env = os.environ.copy()
            env["FLAKY_TEST_ITERATIONS"] = str(args.iterations)
            
            process = subprocess.run(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            test_results[test_name] = {
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr
            }
            
            if process.returncode != 0:
                logger.warning(f"Test {test_name} exited with code {process.returncode}")
                if args.verbose:
                    logger.error(process.stderr)
            
        except Exception as e:
            logger.error(f"Error running test {test_name}: {e}")
            test_results[test_name] = {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Generate detailed report
    report_data = {
        "timestamp": timestamp,
        "duration": duration,
        "iterations": args.iterations,
        "test_files": [str(file) for file in test_files],
        "test_results": test_results,
        "flakiness_threshold": args.threshold
    }
    
    # Save report
    report_file = report_dir / f"flaky_tests_report_{timestamp}.json"
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)
    
    logger.info(f"Flaky test report saved to {report_file}")
    
    # Generate HTML report if requested
    if args.html:
        generate_html_report(report_data, report_dir, timestamp)
    
    # Process the results to extract flaky tests
    process_results(test_results, args.threshold)
    
    return True


def process_results(test_results, threshold):
    """Process test results to identify flaky tests."""
    logger.info("Processing test results to identify flaky tests:")
    
    flaky_tests_found = False
    
    for test_name, result in test_results.items():
        # Extract flaky test information from the output
        flaky_tests = extract_flaky_tests(result["stdout"])
        
        if flaky_tests:
            flaky_tests_found = True
            logger.info(f"\nFlaky tests detected in {test_name}:")
            
            for test_id, details in flaky_tests.items():
                flakiness = details.get("flakiness_score", 0)
                pass_rate = details.get("pass_rate", 1.0)
                runs = details.get("total_runs", 0)
                
                if flakiness >= threshold:
                    logger.warning(
                        f"  - {test_id}: "
                        f"Score: {flakiness:.2f}, "
                        f"Pass rate: {pass_rate:.2f}, "
                        f"Runs: {runs}"
                    )
                else:
                    logger.info(
                        f"  - {test_id}: "
                        f"Score: {flakiness:.2f}, "
                        f"Pass rate: {pass_rate:.2f}, "
                        f"Runs: {runs}"
                    )
    
    if not flaky_tests_found:
        logger.info("No flaky tests detected.")


def extract_flaky_tests(output):
    """Extract flaky test information from test output."""
    flaky_tests = {}
    
    try:
        # Look for a JSON report in the output
        start_marker = "FLAKY_TEST_REPORT_BEGIN"
        end_marker = "FLAKY_TEST_REPORT_END"
        
        if start_marker in output and end_marker in output:
            start_index = output.find(start_marker) + len(start_marker)
            end_index = output.find(end_marker)
            json_data = output[start_index:end_index].strip()
            report = json.loads(json_data)
            
            # Extract flaky tests from the report
            if "test_details" in report:
                return report["test_details"]
        
        # If no JSON report found, parse the output manually
        lines = output.splitlines()
        current_test = None
        
        for line in lines:
            if "- test_" in line and "Score:" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    test_id = parts[0].strip().strip("- ")
                    
                    # Extract metrics
                    metrics_part = ":".join(parts[1:])
                    score_match = re.search(r"Score: ([0-9.]+)", metrics_part)
                    pass_match = re.search(r"Pass rate: ([0-9.]+)", metrics_part)
                    runs_match = re.search(r"Runs: ([0-9]+)", metrics_part)
                    
                    flaky_tests[test_id] = {
                        "flakiness_score": float(score_match.group(1)) if score_match else 0,
                        "pass_rate": float(pass_match.group(1)) if pass_match else 1.0,
                        "total_runs": int(runs_match.group(1)) if runs_match else 0
                    }
    except Exception as e:
        logger.error(f"Error parsing test output: {e}")
    
    return flaky_tests


def generate_html_report(report_data, report_dir, timestamp):
    """Generate an HTML report from the test results."""
    try:
        html_file = report_dir / f"flaky_tests_report_{timestamp}.html"
        
        # Simple HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flaky Test Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .test {{ margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .test-name {{ font-weight: bold; }}
                .flaky {{ background-color: #fff0f0; }}
                .passed {{ background-color: #f0fff0; }}
                .failed {{ background-color: #fff0f0; }}
                pre {{ background-color: #f9f9f9; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Flaky Test Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Timestamp: {report_data['timestamp']}</p>
                <p>Duration: {report_data['duration']:.2f} seconds</p>
                <p>Iterations: {report_data['iterations']}</p>
                <p>Files tested: {len(report_data['test_files'])}</p>
                <p>Flakiness threshold: {report_data['flakiness_threshold']}</p>
            </div>
            
            <h2>Test Files</h2>
            <ul>
        """
        
        for test_file in report_data['test_files']:
            html_content += f"<li>{test_file}</li>\n"
        
        html_content += """
            </ul>
            
            <h2>Test Results</h2>
        """
        
        for test_name, result in report_data['test_results'].items():
            status_class = "passed" if result['returncode'] == 0 else "failed"
            html_content += f"""
            <div class="test {status_class}">
                <div class="test-name">{test_name}</div>
                <p>Exit code: {result['returncode']}</p>
                <h3>Standard Output</h3>
                <pre>{result['stdout']}</pre>
                <h3>Standard Error</h3>
                <pre>{result['stderr']}</pre>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(html_file, "w") as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to {html_file}")
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")


def main():
    """Main entry point for the flaky test detection tool."""
    args = parse_arguments()
    report_dir = setup_environment(args)
    
    logger.info("=== Flaky Test Detection Tool ===")
    logger.info(f"Running with {args.iterations} iterations")
    
    try:
        success = run_tests(args, report_dir)
        if success:
            logger.info("Flaky test detection completed successfully")
        else:
            logger.error("Flaky test detection failed")
            return 1
    except KeyboardInterrupt:
        logger.info("Flaky test detection interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Flaky test detection failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import re  # Import needed for regex in extract_flaky_tests
    sys.exit(main()) 