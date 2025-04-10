#!/usr/bin/env python3
"""
Generate a comprehensive HTML report for API test results.

This script processes test results from security scans, unit tests, API tests,
and performance benchmarks to create a consolidated HTML report.
"""

import argparse
import json
import os
import glob
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    HAS_PLOTTING = True
except ImportError:
    print("Warning: matplotlib, numpy, or jinja2 not available. Some report features will be disabled.")
    HAS_PLOTTING = False

class ReportGenerator:
    """Generate HTML reports from test results."""
    
    def __init__(self, input_dir: str, output_file: str):
        """
        Initialize the report generator.
        
        Args:
            input_dir: Directory containing test results
            output_file: Path to output HTML report
        """
        self.input_dir = input_dir
        self.output_file = output_file
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "security": {},
            "tests": {},
            "api": {},
            "performance": {}
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create templates directory if it doesn't exist for Jinja2
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create default template if it doesn't exist
        self._create_default_template(templates_dir)
        
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _create_default_template(self, templates_dir: str):
        """Create default HTML template if it doesn't exist."""
        template_file = os.path.join(templates_dir, "report_template.html")
        
        if not os.path.exists(template_file):
            with open(template_file, 'w') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>API Test Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background-color: #f8f8f8;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 5px solid #4CAF50;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .summary {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .summary-card {
            background-color: #fff;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            width: 22%;
            min-width: 250px;
            margin-bottom: 20px;
        }
        .success { border-left: 5px solid #4CAF50; }
        .warning { border-left: 5px solid #FF9800; }
        .danger { border-left: 5px solid #F44336; }
        .info { border-left: 5px solid #2196F3; }
        
        .card-title {
            font-size: 1.2em;
            font-weight: bold;
            margin: 0 0 15px 0;
        }
        .card-value {
            font-size: 2em;
            font-weight: bold;
        }
        .card-footer {
            font-size: 0.9em;
            color: #777;
            margin-top: 15px;
        }
        
        section {
            background-color: #fff;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            text-align: left;
            padding: 12px;
        }
        td {
            padding: 12px;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        .chart {
            margin: 30px 0;
            text-align: center;
        }
        .chart img {
            max-width: 100%;
            height: auto;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #777;
        }
        
        @media (max-width: 768px) {
            .summary-card {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>API Test Report</h1>
            <p>Generated on {{ timestamp }}</p>
        </header>
        
        <div class="summary">
            <div class="summary-card {{ 'success' if security.pass_rate > 90 else 'warning' if security.pass_rate > 70 else 'danger' }}">
                <div class="card-title">Security</div>
                <div class="card-value">{{ security.pass_rate }}%</div>
                <div class="card-footer">{{ security.issues }} issues found</div>
            </div>
            
            <div class="summary-card {{ 'success' if tests.pass_rate > 90 else 'warning' if tests.pass_rate > 70 else 'danger' }}">
                <div class="card-title">Unit Tests</div>
                <div class="card-value">{{ tests.pass_rate }}%</div>
                <div class="card-footer">{{ tests.passed }}/{{ tests.total }} tests passed</div>
            </div>
            
            <div class="summary-card {{ 'success' if api.pass_rate > 90 else 'warning' if api.pass_rate > 70 else 'danger' }}">
                <div class="card-title">API Tests</div>
                <div class="card-value">{{ api.pass_rate }}%</div>
                <div class="card-footer">{{ api.passed }}/{{ api.total }} tests passed</div>
            </div>
            
            <div class="summary-card {{ 'success' if performance.rating == 'excellent' else 'warning' if performance.rating == 'acceptable' else 'danger' }}">
                <div class="card-title">Performance</div>
                <div class="card-value">{{ performance.rating|capitalize }}</div>
                <div class="card-footer">Avg response: {{ "%.2f"|format(performance.avg_response) }}ms</div>
            </div>
        </div>
        
        <section>
            <h2>Security Scan Results</h2>
            {% if security.vulnerabilities %}
                <h3>Vulnerabilities Found</h3>
                <table>
                    <tr>
                        <th>Severity</th>
                        <th>File</th>
                        <th>Issue</th>
                        <th>Line</th>
                    </tr>
                    {% for vuln in security.vulnerabilities %}
                    <tr>
                        <td>{{ vuln.severity }}</td>
                        <td>{{ vuln.file }}</td>
                        <td>{{ vuln.issue }}</td>
                        <td>{{ vuln.line }}</td>
                    </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>No security vulnerabilities found.</p>
            {% endif %}
        </section>
        
        <section>
            <h2>Test Results</h2>
            
            <h3>Unit Tests</h3>
            {% if tests.failures %}
                <table>
                    <tr>
                        <th>Test</th>
                        <th>Message</th>
                    </tr>
                    {% for failure in tests.failures %}
                    <tr>
                        <td>{{ failure.name }}</td>
                        <td>{{ failure.message }}</td>
                    </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>All unit tests passed!</p>
            {% endif %}
            
            <h3>API Tests</h3>
            {% if api.failures %}
                <table>
                    <tr>
                        <th>Test</th>
                        <th>Message</th>
                    </tr>
                    {% for failure in api.failures %}
                    <tr>
                        <td>{{ failure.name }}</td>
                        <td>{{ failure.message }}</td>
                    </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>All API tests passed!</p>
            {% endif %}
        </section>
        
        <section>
            <h2>Performance Results</h2>
            
            <div class="chart">
                <h3>Response Times</h3>
                {% if performance.charts.response_times %}
                    <img src="{{ performance.charts.response_times }}" alt="Response Times Chart">
                {% else %}
                    <p>No response time chart available</p>
                {% endif %}
            </div>
            
            <div class="chart">
                <h3>Success Rates</h3>
                {% if performance.charts.success_rates %}
                    <img src="{{ performance.charts.success_rates }}" alt="Success Rates Chart">
                {% else %}
                    <p>No success rate chart available</p>
                {% endif %}
            </div>
            
            <h3>Endpoint Performance</h3>
            {% if performance.endpoints %}
                <table>
                    <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Mean (ms)</th>
                        <th>P95 (ms)</th>
                        <th>Success Rate</th>
                    </tr>
                    {% for endpoint in performance.endpoints %}
                    <tr>
                        <td>{{ endpoint.path }}</td>
                        <td>{{ endpoint.method }}</td>
                        <td>{{ "%.2f"|format(endpoint.mean_ms) }}</td>
                        <td>{{ "%.2f"|format(endpoint.p95_ms) }}</td>
                        <td>{{ "%.1f"|format(endpoint.success_rate * 100) }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>No endpoint performance data available</p>
            {% endif %}
        </section>
        
        <footer>
            <p>Generated by API Test Framework | {{ timestamp }}</p>
        </footer>
    </div>
</body>
</html>""")
    
    def parse_junit_xml(self, xml_path: str) -> Dict:
    """Parse JUnit XML test results."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
            # Get testsuite element (could be root or child)
            if root.tag == 'testsuite':
                testsuite = root
            else:
                testsuite = root.find('.//testsuite')
            
            if testsuite is None:
                return {"total": 0, "failures": 0, "errors": 0, "skipped": 0, "tests": []}
            
            total = int(testsuite.get('tests', 0))
            failures = int(testsuite.get('failures', 0))
            errors = int(testsuite.get('errors', 0))
            skipped = int(testsuite.get('skipped', 0))
            
            # Process individual test cases
            tests = []
            failed_tests = []
            
            for testcase in testsuite.findall('.//testcase'):
                test_name = f"{testcase.get('classname', '')}.{testcase.get('name', '')}"
                
                # Check for failures or errors
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped_test = testcase.find('skipped')
                
                if failure is not None:
                    tests.append({
                        "name": test_name,
                        "status": "failed",
                        "message": failure.get('message', '')
                    })
                    failed_tests.append({
                        "name": test_name,
                        "message": failure.get('message', '')
                    })
                elif error is not None:
                    tests.append({
                        "name": test_name,
                        "status": "error",
                        "message": error.get('message', '')
                    })
                    failed_tests.append({
                        "name": test_name,
                        "message": error.get('message', '')
                    })
                elif skipped_test is not None:
                    tests.append({
                        "name": test_name,
                        "status": "skipped",
                        "message": skipped_test.get('message', '')
                    })
                else:
                    tests.append({
                        "name": test_name,
                        "status": "passed",
                        "message": ""
                    })
            
            return {
                "total": total,
                "failures": failures,
                "errors": errors,
                "skipped": skipped,
                "passed": total - failures - errors - skipped,
                "tests": tests,
                "failed_tests": failed_tests
            }
            
        except Exception as e:
            print(f"Error parsing JUnit XML {xml_path}: {str(e)}")
            return {"total": 0, "failures": 0, "errors": 0, "skipped": 0, "tests": []}
    
    def parse_json_results(self, json_path: str) -> Dict:
        """Parse JSON test or benchmark results."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error parsing JSON file {json_path}: {str(e)}")
            return {}
    
    def parse_security_scan(self, json_path: str) -> Dict:
        """Parse security scan results (e.g., bandit, safety)."""
        data = self.parse_json_results(json_path)
        
        # Different format for different tools
        if 'results' in data:
            # Likely a bandit report
            vulnerabilities = []
            total_issues = len(data.get('results', []))
            
            for issue in data.get('results', []):
                vulnerabilities.append({
                    "severity": issue.get('issue_severity', 'unknown'),
                    "file": issue.get('filename', 'unknown'),
                    "line": issue.get('line_number', 0),
                    "issue": issue.get('issue_text', 'unknown'),
                    "confidence": issue.get('issue_confidence', 'unknown')
                })
            
            return {
                "tool": "bandit",
                "issues": total_issues,
                "vulnerabilities": vulnerabilities,
                "pass_rate": 100 - (total_issues * 10) if total_issues < 10 else 0  # Simple pass rate calc
            }
            
        elif 'vulnerabilities' in data:
            # Likely a safety report
            vulnerabilities = []
            total_issues = len(data.get('vulnerabilities', []))
            
            for issue in data.get('vulnerabilities', []):
                vulnerabilities.append({
                    "severity": issue.get('severity', 'unknown'),
                    "file": issue.get('package_name', 'unknown'),
                    "line": 0,
                    "issue": issue.get('vulnerability', 'unknown'),
                    "confidence": "high"
                })
            
            return {
                "tool": "safety",
                "issues": total_issues,
                "vulnerabilities": vulnerabilities,
                "pass_rate": 100 - (total_issues * 5) if total_issues < 20 else 0  # Simple pass rate calc
            }
            
        return {
            "tool": "unknown",
            "issues": 0,
            "vulnerabilities": [],
            "pass_rate": 100
        }
    
    def find_test_results(self) -> None:
        """Find and parse all test results."""
        # Find and parse security scan results
        security_files = glob.glob(os.path.join(self.input_dir, "**", "*security*.json"), recursive=True)
        for file_path in security_files:
            result = self.parse_security_scan(file_path)
            self.results["security"][os.path.basename(file_path)] = result
        
        # Find and parse JUnit XML results
        junit_files = glob.glob(os.path.join(self.input_dir, "**", "*.xml"), recursive=True)
        
        for file_path in junit_files:
            # Use filename to determine test type (unit or API)
            filename = os.path.basename(file_path)
            result = self.parse_junit_xml(file_path)
            
            if "api" in filename.lower():
                self.results["api"][filename] = result
            else:
                self.results["tests"][filename] = result
        
        # Find and parse performance benchmark results
        perf_files = glob.glob(os.path.join(self.input_dir, "**", "*benchmark*.json"), recursive=True)
        perf_files.extend(glob.glob(os.path.join(self.input_dir, "**", "*performance*.json"), recursive=True))
        
        for file_path in perf_files:
            result = self.parse_json_results(file_path)
            self.results["performance"][os.path.basename(file_path)] = result
    
    def generate_performance_charts(self) -> Dict[str, str]:
        """Generate performance charts from benchmark data."""
        if not HAS_PLOTTING:
            return {}
        
        charts = {}
        
        # Skip if no performance data
        if not self.results["performance"]:
            return charts
        
        # Get the first performance result
        perf_data = next(iter(self.results["performance"].values()), {})
        
        # Skip if no endpoints data
        if not perf_data.get("endpoints"):
            return charts
        
        # Create directory for charts
        charts_dir = os.path.join(os.path.dirname(self.output_file), "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # Generate response times chart
        plt.figure(figsize=(12, 6))
        
        endpoints = []
        mean_times = []
        p95_times = []
        
        for endpoint_key, endpoint_data in perf_data.get("endpoints", {}).items():
            if not isinstance(endpoint_data, dict) or "metrics" not in endpoint_data:
                continue
                
            endpoints.append(f"{endpoint_data.get('method', 'GET')} {endpoint_data.get('endpoint', 'unknown')}")
            metrics = endpoint_data.get("metrics", {})
            mean_times.append(metrics.get("mean", 0) * 1000)  # Convert to ms
            p95_times.append(metrics.get("p95", 0) * 1000)    # Convert to ms
        
        if not endpoints:
            return charts
            
        x = np.arange(len(endpoints))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, mean_times, width, label='Mean', color='#3498db')
        ax.bar(x + width/2, p95_times, width, label='P95', color='#e74c3c')
        
        ax.set_xlabel('Endpoints')
        ax.set_ylabel('Response Time (ms)')
        ax.set_title('API Response Times by Endpoint')
        ax.set_xticks(x)
        ax.set_xticklabels(endpoints, rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        response_times_file = os.path.join(charts_dir, f"response_times.png")
        plt.savefig(response_times_file)
        plt.close()
        
        charts["response_times"] = os.path.relpath(response_times_file, os.path.dirname(self.output_file))
        
        # Generate success rates chart
        plt.figure(figsize=(10, 6))
        success_rates = [endpoint_data.get("metrics", {}).get("success_rate", 0) * 100 
                        for endpoint_data in perf_data.get("endpoints", {}).values() 
                        if isinstance(endpoint_data, dict) and "metrics" in endpoint_data]
        
        plt.bar(endpoints, success_rates, color=['#2ecc71' if rate > 95 else '#f39c12' if rate > 80 else '#e74c3c' for rate in success_rates])
        plt.xlabel('Endpoints')
        plt.ylabel('Success Rate (%)')
        plt.title('API Success Rates by Endpoint')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.ylim(0, 105)
        
        plt.axhline(y=95, color='r', linestyle='--', alpha=0.7, label='95% Threshold')
        plt.legend()
        
        success_rates_file = os.path.join(charts_dir, f"success_rates.png")
        plt.savefig(success_rates_file)
        plt.close()
        
        charts["success_rates"] = os.path.relpath(success_rates_file, os.path.dirname(self.output_file))
        
        return charts
    
    def prepare_template_data(self) -> Dict:
        """Prepare data for the HTML template."""
        # Security summary
        security_data = {
            "pass_rate": 100,
            "issues": 0,
            "vulnerabilities": []
        }
        
        for result in self.results["security"].values():
            security_data["issues"] += result.get("issues", 0)
            security_data["vulnerabilities"].extend(result.get("vulnerabilities", []))
            # Use the lowest pass rate
            security_data["pass_rate"] = min(security_data["pass_rate"], result.get("pass_rate", 100))
        
        # Test summary
        test_data = {
                "total": 0,
                "passed": 0,
            "failures": 0,
            "failures": []
        }
        
        for result in self.results["tests"].values():
            test_data["total"] += result.get("total", 0)
            test_data["passed"] += result.get("passed", 0)
            test_data["failures"].extend(result.get("failed_tests", []))
        
        test_data["pass_rate"] = (test_data["passed"] / test_data["total"] * 100) if test_data["total"] > 0 else 100
        
        # API test summary
        api_data = {
            "total": 0,
            "passed": 0,
            "failures": []
        }
        
        for result in self.results["api"].values():
            api_data["total"] += result.get("total", 0)
            api_data["passed"] += result.get("passed", 0)
            api_data["failures"].extend(result.get("failed_tests", []))
        
        api_data["pass_rate"] = (api_data["passed"] / api_data["total"] * 100) if api_data["total"] > 0 else 100
        
        # Performance summary
        performance_data = {
            "avg_response": 0,
            "endpoints": [],
            "charts": self.generate_performance_charts(),
            "rating": "unknown"
        }
        
        # Process performance data if available
        total_response = 0
        count = 0
        
        for perf_file, perf_result in self.results["performance"].items():
            for endpoint_key, endpoint_data in perf_result.get("endpoints", {}).items():
                if not isinstance(endpoint_data, dict) or "metrics" not in endpoint_data:
            continue
            
                metrics = endpoint_data.get("metrics", {})
                if metrics.get("mean") is not None:
                    mean_ms = metrics.get("mean", 0) * 1000  # Convert to ms
                    p95_ms = metrics.get("p95", 0) * 1000    # Convert to ms
                    success_rate = metrics.get("success_rate", 0)
                    
                    performance_data["endpoints"].append({
                        "path": endpoint_data.get("endpoint", "unknown"),
                        "method": endpoint_data.get("method", "GET"),
                        "mean_ms": mean_ms,
                        "p95_ms": p95_ms,
                        "success_rate": success_rate
                    })
                    
                    total_response += mean_ms
                    count += 1
        
        if count > 0:
            performance_data["avg_response"] = total_response / count
            
            # Determine overall performance rating
            if performance_data["avg_response"] < 100:
                performance_data["rating"] = "excellent"
            elif performance_data["avg_response"] < 300:
                performance_data["rating"] = "good"
            elif performance_data["avg_response"] < 1000:
                performance_data["rating"] = "acceptable"
            else:
                performance_data["rating"] = "poor"
        
        return {
            "timestamp": self.results["timestamp"],
            "security": security_data,
            "tests": test_data,
            "api": api_data,
            "performance": performance_data
        }
    
    def generate_html_report(self) -> None:
        """Generate HTML report from template."""
        template = self.env.get_template("report_template.html")
        
        template_data = self.prepare_template_data()
        
        html = template.render(**template_data)
        
        with open(self.output_file, 'w') as f:
            f.write(html)
        
        print(f"HTML report generated: {self.output_file}")
    
    def generate_report(self) -> None:
        """Generate the complete report."""
        self.find_test_results()
        self.generate_html_report()

def main():
    """Main function to run the report generator."""
    parser = argparse.ArgumentParser(description='Generate API test report')
    parser.add_argument('--input-dir', required=True, help='Directory containing test results')
    parser.add_argument('--output-file', required=True, help='Output HTML report file')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.input_dir, args.output_file)
    generator.generate_report()
    
    print(f"Report generation complete: {args.output_file}")

if __name__ == "__main__":
    main() 