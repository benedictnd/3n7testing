# API Test Report Generator

A powerful visual reporting tool for API test results. This tool generates interactive HTML reports that showcase the results of API tests, including success rates, performance metrics, security findings, and flaky test analysis.

## Features

- **Interactive Visualizations**: Charts and graphs powered by Chart.js
- **Comprehensive Metrics**: Test success rates, response times, error distributions, and more
- **Security Analysis**: Display of security scan results and header implementations
- **Flaky Test Tracking**: Identification and monitoring of unstable tests
- **Sample Data Generation**: Built-in capability to generate realistic test data
- **Flexible Input Sources**: Support for various JSON data input formats

## Installation

The report generator requires Python 3.10 or later, and the following dependencies:

```bash
pip install -r requirements.txt
```

The main dependencies include:
- Jinja2 (for HTML template rendering)
- Various testing tools for data generation

## Quick Start

### Option 1: Using the Convenience Scripts

#### Windows
```
generate_report.bat
```

#### Unix/Linux/Mac
```
./generate_report.sh
```

### Option 2: Using the Command Line Interface

```bash
# Generate a report with sample data
python generate_api_report.py --generate-data --output-file reports/api_report.html

# Generate a report using existing test data
python generate_api_report.py --input-dir test-data --output-file reports/api_report.html
```

## Command Line Options

```
usage: generate_api_report.py [-h] [--input-dir INPUT_DIR] [--output-file OUTPUT_FILE]
                             [--generate-data] [--data-dir DATA_DIR] [--force]

Generate visual reports for API test results

options:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR, -i INPUT_DIR
                        Directory containing JSON test data files
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Output HTML report file path
  --generate-data, -g   Generate sample data instead of using existing files
  --data-dir DATA_DIR, -d DATA_DIR
                        Directory for generated sample data (when using --generate-data)
  --force, -f           Overwrite existing report file if it exists
```

## Input Data Format

The generator expects the following JSON files in the input directory:

1. **test_results.json**: Contains overall test results data
   ```json
   {
     "total_tests": 100,
     "passed": 90,
     "failed": 10,
     "success_rate": 90.0,
     "environment": "development",
     "api_version": "1.2.3",
     "duration": 60,
     "covered_endpoints": 30,
     "total_endpoints": 35,
     "validation_errors": 5,
     "server_errors": 3,
     "network_errors": 2
   }
   ```

2. **performance_metrics.json**: Contains API performance data
   ```json
   {
     "response_times": [120, 130, 125, 150, 110, 140],
     "avg_response_time": 129,
     "requests_per_second": 25.5,
     "p50": 125,
     "p90": 145,
     "p95": 148,
     "p99": 150
   }
   ```

3. **security_scan.json**: Contains security findings
   ```json
   {
     "vulnerabilities": [
       {
         "type": "XSS",
         "severity": "Medium",
         "location": "/api/users"
       }
     ],
     "csp_implemented": true,
     "hsts_implemented": true,
     "x_content_type_implemented": true,
     "owasp_coverage": 85
   }
   ```

4. **flaky_tests.json**: Contains flaky test information
   ```json
   {
     "flaky_tests": ["test_auth_login", "test_file_upload"],
     "test_details": {
       "test_auth_login": {
         "name": "test_auth_login",
         "flakiness_score": 0.3,
         "failures": 3,
         "total_runs": 10
       }
     },
     "retry_stats": {
       "total_retries": 5,
       "successful_retries": 3,
       "avg_retries_per_test": 1.5
     }
   }
   ```

## Integration with Testing Framework

### Using with pytest

You can integrate the report generator with pytest using a custom hook:

```python
# conftest.py
import pytest
import json
from pathlib import Path
from utils.api_report_generator import APIReportGenerator

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Generate HTML report after test session finishes"""
    if session.config.getoption("--generate-report", False):
        # Collect test results
        test_results = {
            "total_tests": session.testscollected,
            "passed": session.testscollected - session.testsfailed,
            "failed": session.testsfailed,
            "success_rate": round(((session.testscollected - session.testsfailed) / session.testscollected) * 100, 1)
            # Add more test results as needed
        }
        
        # Save results to JSON files
        output_dir = Path("test-data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        # Generate the report
        # (Assumes other data files exist or are generated separately)
        report = APIReportGenerator.from_json_files(
            test_results_path=str(output_dir / "test_results.json"),
            performance_path=str(output_dir / "performance_metrics.json"),
            security_path=str(output_dir / "security_scan.json"),
            flaky_path=str(output_dir / "flaky_tests.json")
        )
        
        report_path = report.generate_report("reports/api_test_report.html")
        print(f"\nGenerated API test report: {report_path}")

def pytest_addoption(parser):
    """Add report-related options to pytest"""
    parser.addoption("--generate-report", action="store_true", 
                    help="Generate HTML report after tests complete")
```

Then run your tests with:

```bash
pytest --generate-report
```

## Customization

### Modifying the HTML Template

The HTML template is located at `utils/templates/api_report_template.html`. You can customize this template to change the report's appearance and content.

### Adding New Visualizations

To add new visualizations:

1. Update the `_prepare_chart_data` method in `APIReportGenerator` to include data for your new chart
2. Add the chart container and JavaScript code to the HTML template

### Extending Data Processing

To process additional data types:

1. Add new methods to the `APIReportGenerator` class to process your data
2. Update the `_structure_report_data` method to include the new data
3. Add visualizations or sections to the HTML template to display the data

## License

This project is open source and available under the MIT License.

## Credits

- Chart.js for the interactive visualizations
- Jinja2 for HTML template rendering 