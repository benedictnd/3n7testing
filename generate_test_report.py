#!/usr/bin/env python3
import argparse
import json
import os
import sys
import glob
import logging
import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test-logs/report_generator.log")
    ]
)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate comprehensive test reports from API test results and benchmarks"""
    
    def __init__(self, test_dir="test-logs", benchmark_dir="benchmark-data", output_dir="test-reports"):
        """Initialize the report generator"""
        self.test_dir = test_dir
        self.benchmark_dir = benchmark_dir
        self.output_dir = output_dir
        
        # Create directories if they don't exist
        Path(output_dir).mkdir(exist_ok=True, parents=True)
        Path(f"{output_dir}/assets").mkdir(exist_ok=True, parents=True)
        
        # Track statistics
        self.stats = {
            "tests_total": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "performance_tests": 0,
            "security_tests": 0,
            "start_time": None,
            "end_time": None,
            "duration": None,
            "endpoints_tested": set(),
            "benchmarks": []
        }
    
    def find_latest_files(self, days_to_include=7):
        """Find the latest test and benchmark files within the specified timeframe"""
        cutoff_date = datetime.now() - timedelta(days=days_to_include)
        
        # Find test result files
        test_files = []
        for file_pattern in ["*_test_results.json", "*_advanced_tests.json"]:
            for filepath in glob.glob(f"{self.test_dir}/{file_pattern}"):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time >= cutoff_date:
                    test_files.append((filepath, file_time))
        
        # Find benchmark files
        benchmark_files = []
        for filepath in glob.glob(f"{self.benchmark_dir}/benchmark_*.json"):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time >= cutoff_date:
                benchmark_files.append((filepath, file_time))
        
        # Sort files by timestamp
        test_files.sort(key=lambda x: x[1], reverse=True)
        benchmark_files.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "test_files": [f[0] for f in test_files],
            "benchmark_files": [f[0] for f in benchmark_files]
        }
    
    def load_test_results(self, filepath):
        """Load and parse test results from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error loading test results from {filepath}: {str(e)}")
            return None
    
    def process_test_results(self, files):
        """Process test result files and collect statistics"""
        all_results = []
        
        for filepath in files:
            logger.info(f"Processing test results from {filepath}")
            results = self.load_test_results(filepath)
            if not results:
                continue
                
            all_results.append(results)
            
            # Extract file type from filename
            file_type = "standard"
            if "advanced" in filepath:
                file_type = "advanced"
            
            # Update overall statistics
            if "start_time" in results:
                file_start = datetime.fromisoformat(results["start_time"]) if isinstance(results["start_time"], str) else results["start_time"]
                file_end = datetime.fromisoformat(results["end_time"]) if isinstance(results["end_time"], str) else results["end_time"]
                
                if self.stats["start_time"] is None or file_start < self.stats["start_time"]:
                    self.stats["start_time"] = file_start
                
                if self.stats["end_time"] is None or file_end > self.stats["end_time"]:
                    self.stats["end_time"] = file_end
            
            # Process test results based on file type
            if file_type == "standard":
                self._process_standard_test_results(results)
            elif file_type == "advanced":
                self._process_advanced_test_results(results)
        
        # Calculate duration
        if self.stats["start_time"] and self.stats["end_time"]:
            self.stats["duration"] = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        return all_results
    
    def _process_standard_test_results(self, results):
        """Process standard API test results"""
        if "tests" not in results:
            logger.warning("Test results file does not contain 'tests' key")
            return
            
        for test in results["tests"]:
            self.stats["tests_total"] += 1
            
            if test.get("result", "").lower() == "pass":
                self.stats["tests_passed"] += 1
            else:
                self.stats["tests_failed"] += 1
                
            # Extract endpoint information if available
            if "endpoint" in test:
                self.stats["endpoints_tested"].add(test["endpoint"])
                
            # Track performance tests
            if "performance" in test.get("type", "").lower():
                self.stats["performance_tests"] += 1
    
    def _process_advanced_test_results(self, results):
        """Process advanced API test results"""
        # Security tests
        if "security_headers" in results:
            for endpoint, tests in results["security_headers"].items():
                self.stats["endpoints_tested"].add(endpoint)
                for header, result in tests.items():
                    self.stats["tests_total"] += 1
                    self.stats["security_tests"] += 1
                    if result.get("result", "").lower() == "pass":
                        self.stats["tests_passed"] += 1
                    else:
                        self.stats["tests_failed"] += 1
        
        # Rate limiting tests
        if "rate_limiting" in results:
            for endpoint, result in results["rate_limiting"].items():
                self.stats["endpoints_tested"].add(endpoint)
                self.stats["tests_total"] += 1
                if result.get("enforced", False):
                    self.stats["tests_passed"] += 1
                else:
                    self.stats["tests_failed"] += 1
        
        # Input validation tests
        if "input_validation" in results:
            for endpoint, tests in results["input_validation"].items():
                self.stats["endpoints_tested"].add(endpoint)
                for test_case in tests:
                    self.stats["tests_total"] += 1
                    if test_case.get("result", "").lower() == "pass":
                        self.stats["tests_passed"] += 1
                    else:
                        self.stats["tests_failed"] += 1
    
    def process_benchmark_data(self, files):
        """Process benchmark data files"""
        all_benchmarks = []
        
        for filepath in files:
            logger.info(f"Processing benchmark data from {filepath}")
            benchmark = self.load_test_results(filepath)
            if not benchmark:
                continue
                
            all_benchmarks.append(benchmark)
            self.stats["benchmarks"].append(benchmark)
            
            # Add endpoints to the set of tested endpoints
            for endpoint in benchmark.get("endpoints", {}):
                # Extract endpoint path from the format "METHOD /path"
                parts = endpoint.split(" ", 1)
                if len(parts) > 1:
                    self.stats["endpoints_tested"].add(parts[1])
        
        return all_benchmarks
    
    def generate_performance_charts(self):
        """Generate performance charts from benchmark data"""
        if not self.stats["benchmarks"]:
            logger.warning("No benchmark data available for charting")
            return {}
            
        charts = {}
        plots_dir = f"{self.output_dir}/assets"
        
        try:
            # Get the most recent benchmark
            latest_benchmark = self.stats["benchmarks"][0]
            
            # Response time by endpoint chart
            plt.figure(figsize=(12, 6))
            
            endpoints = list(latest_benchmark["endpoints"].keys())
            mean_times = [latest_benchmark["endpoints"][ep]["timing"]["mean"] for ep in endpoints]
            p95_times = [latest_benchmark["endpoints"][ep]["timing"]["p95"] for ep in endpoints]
            
            x = np.arange(len(endpoints))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(x - width/2, mean_times, width, label='Mean')
            ax.bar(x + width/2, p95_times, width, label='95th Percentile', alpha=0.7)
            
            ax.set_ylabel('Response Time (ms)')
            ax.set_title('API Endpoint Performance')
            ax.set_xticks(x)
            ax.set_xticklabels(endpoints, rotation=45, ha='right')
            ax.legend()
            
            fig.tight_layout()
            
            # Save the plot
            response_time_plot = f"{plots_dir}/response_times.png"
            plt.savefig(response_time_plot)
            plt.close()
            charts["response_times"] = os.path.relpath(response_time_plot, self.output_dir)
            
            # Historical performance chart if we have multiple benchmarks
            if len(self.stats["benchmarks"]) > 1:
                # Extract data from benchmarks
                timestamps = []
                endpoint_data = defaultdict(lambda: {"mean": [], "p95": []})
                
                for benchmark in reversed(self.stats["benchmarks"]):  # Oldest first
                    timestamps.append(datetime.fromisoformat(benchmark["timestamp"]))
                    
                    for endpoint, data in benchmark["endpoints"].items():
                        endpoint_data[endpoint]["mean"].append(data["timing"]["mean"])
                        endpoint_data[endpoint]["p95"].append(data["timing"]["p95"])
                
                # Create a chart for each endpoint
                for endpoint, data in endpoint_data.items():
                    if len(data["mean"]) < 2:  # Need at least 2 points for a trend
                        continue
                        
                    plt.figure(figsize=(12, 6))
                    plt.plot(range(len(timestamps)), data["mean"], 'o-', label='Mean')
                    plt.plot(range(len(timestamps)), data["p95"], 's-', label='95th Percentile')
                    
                    plt.ylabel('Response Time (ms)')
                    plt.title(f'Historical Trend for {endpoint}')
                    plt.xticks(range(len(timestamps)), 
                              [ts.strftime("%m-%d %H:%M") for ts in timestamps], 
                              rotation=45)
                    plt.legend()
                    plt.tight_layout()
                    
                    # Save the plot
                    safe_endpoint = endpoint.replace(" ", "_").replace("/", "_")
                    trend_plot = f"{plots_dir}/trend_{safe_endpoint}.png"
                    plt.savefig(trend_plot)
                    plt.close()
                    
                    if "trends" not in charts:
                        charts["trends"] = {}
                    charts["trends"][endpoint] = os.path.relpath(trend_plot, self.output_dir)
            
        except Exception as e:
            logger.error(f"Error generating performance charts: {str(e)}")
        
        return charts
    
    def generate_test_summary_charts(self):
        """Generate test summary charts"""
        plots_dir = f"{self.output_dir}/assets"
        charts = {}
        
        try:
            # Test Pass/Fail Pie Chart
            plt.figure(figsize=(8, 8))
            labels = ['Passed', 'Failed']
            sizes = [self.stats["tests_passed"], self.stats["tests_failed"]]
            colors = ['#4CAF50', '#F44336']
            explode = (0.1, 0)  # explode the 1st slice (Passed)
            
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                    shadow=True, startangle=140)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Test Results')
            
            # Save the plot
            pie_chart = f"{plots_dir}/test_results_pie.png"
            plt.savefig(pie_chart)
            plt.close()
            charts["test_results_pie"] = os.path.relpath(pie_chart, self.output_dir)
            
            # Test Types Bar Chart
            plt.figure(figsize=(10, 6))
            test_types = ['API Tests', 'Performance Tests', 'Security Tests']
            test_counts = [
                self.stats["tests_total"] - self.stats["performance_tests"] - self.stats["security_tests"],
                self.stats["performance_tests"],
                self.stats["security_tests"]
            ]
            
            plt.bar(test_types, test_counts, color=['#2196F3', '#FF9800', '#9C27B0'])
            plt.ylabel('Number of Tests')
            plt.title('Test Types')
            
            # Save the plot
            bar_chart = f"{plots_dir}/test_types_bar.png"
            plt.savefig(bar_chart)
            plt.close()
            charts["test_types_bar"] = os.path.relpath(bar_chart, self.output_dir)
            
        except Exception as e:
            logger.error(f"Error generating test summary charts: {str(e)}")
        
        return charts
    
    def generate_html_report(self, charts):
        """Generate an HTML report with all the collected data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_file = f"{self.output_dir}/api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        success_rate = (self.stats["tests_passed"] / self.stats["tests_total"] * 100) if self.stats["tests_total"] > 0 else 0
        
        try:
            with open(report_file, "w") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>API Test Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background-color: #333;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            position: relative;
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card h2 {{
            margin-top: 0;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
            color: #333;
        }}
        .stat {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
            text-align: center;
        }}
        .success {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .error {{ color: #F44336; }}
        .neutral {{ color: #2196F3; }}
        .chart-container {{
            width: 100%;
            margin: 20px 0;
        }}
        .chart {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            display: block;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        .section {{
            margin-top: 40px;
        }}
        .tab {{
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 8px 8px 0 0;
        }}
        .tab button {{
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 16px;
        }}
        .tab button:hover {{
            background-color: #ddd;
        }}
        .tab button.active {{
            background-color: #333;
            color: white;
        }}
        .tabcontent {{
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 8px 8px;
            background-color: white;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #777;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>API Test Report</h1>
        <p>Generated on: {timestamp}</p>
    </header>
    
    <div class="container">
        <div class="dashboard">
            <div class="card">
                <h2>Test Results Summary</h2>
                <div class="stat {
                    'success' if success_rate > 90 else 'warning' if success_rate > 70 else 'error'
                }">{success_rate:.1f}%</div>
                <p>Success Rate</p>
                <table>
                    <tr>
                        <td>Total Tests:</td>
                        <td>{self.stats["tests_total"]}</td>
                    </tr>
                    <tr>
                        <td>Passed:</td>
                        <td class="success">{self.stats["tests_passed"]}</td>
                    </tr>
                    <tr>
                        <td>Failed:</td>
                        <td class="error">{self.stats["tests_failed"]}</td>
                    </tr>
                </table>
            </div>
            
            <div class="card">
                <h2>Test Types</h2>
                <table>
                    <tr>
                        <td>API Functionality Tests:</td>
                        <td>{self.stats["tests_total"] - self.stats["performance_tests"] - self.stats["security_tests"]}</td>
                    </tr>
                    <tr>
                        <td>Performance Tests:</td>
                        <td>{self.stats["performance_tests"]}</td>
                    </tr>
                    <tr>
                        <td>Security Tests:</td>
                        <td>{self.stats["security_tests"]}</td>
                    </tr>
                </table>
                <div class="chart-container">
                    {f'<img src="{charts["test_types_bar"]}" class="chart" alt="Test Types">' if "test_types_bar" in charts else ''}
                </div>
            </div>
            
            <div class="card">
                <h2>Test Duration</h2>
                <div class="stat neutral">
                    {str(timedelta(seconds=int(self.stats["duration"]))) if self.stats["duration"] else "N/A"}
                </div>
                <p>Total Test Duration</p>
                <table>
                    <tr>
                        <td>Start Time:</td>
                        <td>{self.stats["start_time"].strftime("%Y-%m-%d %H:%M:%S") if self.stats["start_time"] else "N/A"}</td>
                    </tr>
                    <tr>
                        <td>End Time:</td>
                        <td>{self.stats["end_time"].strftime("%Y-%m-%d %H:%M:%S") if self.stats["end_time"] else "N/A"}</td>
                    </tr>
                </table>
            </div>
            
            <div class="card">
                <h2>Coverage</h2>
                <div class="stat neutral">{len(self.stats["endpoints_tested"])}</div>
                <p>Endpoints Tested</p>
            </div>
            
            <div class="card full-width">
                <h2>Test Results Distribution</h2>
                <div class="chart-container">
                    {f'<img src="{charts["test_results_pie"]}" class="chart" alt="Test Results">' if "test_results_pie" in charts else ''}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="tab">
                <button class="tablinks" onclick="openTab(event, 'PerformanceTab')" id="defaultOpen">Performance Results</button>
                <button class="tablinks" onclick="openTab(event, 'EndpointsTab')">Endpoints</button>
                <button class="tablinks" onclick="openTab(event, 'TrendsTab')">Historical Trends</button>
            </div>
            
            <div id="PerformanceTab" class="tabcontent">
                <h2>API Performance Results</h2>
                <div class="chart-container">
                    {f'<img src="{charts["response_times"]}" class="chart" alt="Response Times">' if "response_times" in charts else '<p>No performance data available</p>'}
                </div>
                
                <h3>Latest Benchmark Results</h3>
                {
                    f"""<table>
                        <tr>
                            <th>Endpoint</th>
                            <th>Mean (ms)</th>
                            <th>Median (ms)</th>
                            <th>95th Percentile (ms)</th>
                            <th>Success</th>
                        </tr>
                        {
                            ''.join([
                                f"""<tr>
                                    <td>{endpoint}</td>
                                    <td>{data["timing"]["mean"]:.2f}</td>
                                    <td>{data["timing"]["median"]:.2f}</td>
                                    <td>{data["timing"]["p95"]:.2f}</td>
                                    <td class="{'success' if data["success"] else 'error'}">
                                        {'✓' if data["success"] else '✗'}
                                    </td>
                                </tr>"""
                                for endpoint, data in self.stats["benchmarks"][0]["endpoints"].items()
                            ]) if self.stats["benchmarks"] else ""
                        }
                    </table>"""
                    if self.stats["benchmarks"] else "<p>No benchmark data available</p>"
                }
            </div>
            
            <div id="EndpointsTab" class="tabcontent">
                <h2>Endpoints Tested</h2>
                <table>
                    <tr>
                        <th>Endpoint</th>
                    </tr>
                    {
                        ''.join([
                            f"<tr><td>{endpoint}</td></tr>"
                            for endpoint in sorted(self.stats["endpoints_tested"])
                        ])
                    }
                </table>
            </div>
            
            <div id="TrendsTab" class="tabcontent">
                <h2>Historical Performance Trends</h2>
                {
                    ''.join([
                        f"""<div class="chart-container">
                            <h3>{endpoint}</h3>
                            <img src="{chart_path}" class="chart" alt="{endpoint} Trend">
                        </div>"""
                        for endpoint, chart_path in charts.get("trends", {}).items()
                    ]) if "trends" in charts and charts["trends"] else "<p>Not enough historical data available to show trends</p>"
                }
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by API Test Report Generator</p>
    </div>
    
    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}
        
        // Get the element with id="defaultOpen" and click on it
        document.getElementById("defaultOpen").click();
    </script>
</body>
</html>""")
            
            logger.info(f"HTML report generated: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return None
    
    def generate_pdf_report(self, html_report):
        """Generate a PDF version of the report using weasyprint if available"""
        if not html_report:
            return None
            
        try:
            # Check if weasyprint is available
            import weasyprint
            logger.info("Generating PDF report using weasyprint")
            
            pdf_file = html_report.replace(".html", ".pdf")
            weasyprint.HTML(html_report).write_pdf(pdf_file)
            
            logger.info(f"PDF report generated: {pdf_file}")
            return pdf_file
            
        except ImportError:
            logger.warning("weasyprint not available, skipping PDF generation")
            return None
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            return None
    
    def send_email_report(self, html_report, pdf_report=None, recipients=None):
        """Send the report via email to specified recipients"""
        if not recipients:
            logger.warning("No recipients specified, skipping email")
            return False
            
        if not html_report:
            logger.error("No HTML report to send")
            return False
            
        try:
            # Read email configuration from environment or config file
            smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.environ.get("SMTP_PORT", 587))
            smtp_user = os.environ.get("SMTP_USER", "")
            smtp_password = os.environ.get("SMTP_PASSWORD", "")
            
            if not smtp_user or not smtp_password:
                logger.error("SMTP credentials not configured, skipping email")
                return False
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"API Test Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Add HTML content
            with open(html_report, 'r') as f:
                html_content = f.read()
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add PDF attachment if available
            if pdf_report and os.path.exists(pdf_report):
                with open(pdf_report, 'rb') as f:
                    attach = MIMEBase('application', 'pdf')
                    attach.set_payload(f.read())
                    encoders.encode_base64(attach)
                    attach.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(pdf_report)}"')
                    msg.attach(attach)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email report sent to {', '.join(recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email report: {str(e)}")
            return False
    
    def archive_reports(self, max_age_days=30):
        """Archive old reports to save space"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        archive_dir = f"{self.output_dir}/archive"
        Path(archive_dir).mkdir(exist_ok=True)
        
        # Find old reports
        for filepath in glob.glob(f"{self.output_dir}/*.html") + glob.glob(f"{self.output_dir}/*.pdf"):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff_date:
                # Move to archive
                filename = os.path.basename(filepath)
                archive_path = f"{archive_dir}/{filename}"
                
                try:
                    shutil.move(filepath, archive_path)
                    logger.info(f"Archived old report: {filename}")
                except Exception as e:
                    logger.error(f"Error archiving report {filename}: {str(e)}")
    
    def generate_report(self, days_to_include=7, send_email=False, email_recipients=None):
        """Generate a complete report from test results and benchmarks"""
        logger.info(f"Generating API test report for the last {days_to_include} days")
        
        # Find latest files
        files = self.find_latest_files(days_to_include)
        
        # Process test results
        test_results = self.process_test_results(files["test_files"])
        
        # Process benchmark data
        benchmark_data = self.process_benchmark_data(files["benchmark_files"])
        
        # Generate charts
        charts = {}
        charts.update(self.generate_test_summary_charts())
        charts.update(self.generate_performance_charts())
        
        # Generate HTML report
        html_report = self.generate_html_report(charts)
        
        # Generate PDF report
        pdf_report = self.generate_pdf_report(html_report)
        
        # Send email if requested
        if send_email and email_recipients:
            self.send_email_report(html_report, pdf_report, email_recipients)
        
        # Archive old reports
        self.archive_reports()
        
        return {
            "html_report": html_report,
            "pdf_report": pdf_report,
            "stats": self.stats
        }

def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive test reports")
    parser.add_argument("--days", type=int, default=7, help="Number of days of data to include")
    parser.add_argument("--test-dir", default="test-logs", help="Directory containing test results")
    parser.add_argument("--benchmark-dir", default="benchmark-data", help="Directory containing benchmark data")
    parser.add_argument("--output-dir", default="test-reports", help="Output directory for reports")
    parser.add_argument("--email", action="store_true", help="Send report via email")
    parser.add_argument("--recipients", help="Comma-separated list of email recipients")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Convert recipients to list
    recipients = args.recipients.split(",") if args.recipients else []
    
    # Generate the report
    report_generator = ReportGenerator(args.test_dir, args.benchmark_dir, args.output_dir)
    result = report_generator.generate_report(
        days_to_include=args.days,
        send_email=args.email,
        email_recipients=recipients
    )
    
    if result["html_report"]:
        print(f"\nReport Generation Summary:")
        print(f"  HTML Report: {result['html_report']}")
        if result["pdf_report"]:
            print(f"  PDF Report: {result['pdf_report']}")
        print(f"\nTest Statistics:")
        print(f"  Total Tests: {result['stats']['tests_total']}")
        print(f"  Passed: {result['stats']['tests_passed']}")
        print(f"  Failed: {result['stats']['tests_failed']}")
        print(f"  Success Rate: {(result['stats']['tests_passed'] / result['stats']['tests_total'] * 100) if result['stats']['tests_total'] > 0 else 0:.1f}%")
        print(f"  Endpoints Tested: {len(result['stats']['endpoints_tested'])}")
        return 0
    else:
        print("Report generation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 