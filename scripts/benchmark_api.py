#!/usr/bin/env python3
import argparse
import json
import os
import statistics
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import sys

import requests
import matplotlib.pyplot as plt
import numpy as np

# Add the project root to sys.path to allow importing modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    from test_config import config
except ImportError:
    print("Error: Could not import test_config module. Make sure it's in your PYTHONPATH")
    sys.exit(1)

class APIBenchmark:
    """API performance benchmarking tool for measuring response times and reliability."""
    
    def __init__(self, base_url: str, email: str = None, password: str = None, output_dir: str = "reports"):
        """
        Initialize the benchmark tool.
        
        Args:
            base_url: Base URL of the API to benchmark
            email: Email for authentication (optional)
            password: Password for authentication (optional)
            output_dir: Directory to store benchmark results and reports
        """
        self.base_url = base_url
        self.email = email or config.TEST_EMAIL
        self.password = password or config.TEST_PASSWORD
        self.output_dir = output_dir
        self.auth_token = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "timestamp": self.timestamp,
            "base_url": base_url,
            "endpoints": {}
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load historical data if available
        self.history_file = os.path.join(output_dir, "benchmark_history.json")
        self.history = self._load_history()
        
        print(f"API Benchmark initialized for {base_url}")
    
    def _load_history(self) -> Dict:
        """Load benchmark history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse history file {self.history_file}, creating new history")
        
        # Create new history structure if file doesn't exist or can't be parsed
        return {
            "base_url": self.base_url,
            "runs": []
        }
    
    def _save_history(self):
        """Save benchmark results to history file."""
        # Update history with current results
        current_run = {
            "timestamp": self.timestamp,
            "endpoints": self.results["endpoints"]
        }
        
        self.history["runs"].append(current_run)
        
        # Keep only the last 10 runs to prevent file from growing too large
        if len(self.history["runs"]) > 10:
            self.history["runs"] = self.history["runs"][-10:]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"Benchmark history updated: {self.history_file}")
    
    def login(self) -> bool:
        """Authenticate with the API and store authentication token."""
        print(f"Authenticating with email: {self.email}")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                print("Authentication successful")
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return False
    
    def benchmark_endpoint(self, 
                         endpoint: str, 
                         method: str = "GET", 
                         data: Dict[str, Any] = None, 
                         params: Dict[str, Any] = None,
                         samples: int = 10,
                         warmup_samples: int = 2) -> Dict[str, Any]:
        """
        Benchmark a specific API endpoint.
        
        Args:
            endpoint: API endpoint path (e.g., "/users")
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request body data for POST/PUT requests
            params: Query parameters for GET requests
            samples: Number of requests to make for benchmarking
            warmup_samples: Number of warmup requests before actual benchmarking
            
        Returns:
            Dictionary with benchmark results
        """
        method = method.upper()
        full_url = f"{self.base_url}{endpoint}"
        
        print(f"Benchmarking {method} {endpoint} with {samples} samples...")
        
        # Prepare request headers
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Perform warmup requests
        print(f"Performing {warmup_samples} warmup requests...")
        for i in range(warmup_samples):
            try:
                requests.request(
                    method,
                    full_url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=10
                )
            except requests.exceptions.RequestException:
                pass
        
        # Perform benchmark requests
        response_times = []
        status_codes = []
        errors = []
        
        for i in range(samples):
            start_time = time.monotonic()
            
            try:
                response = requests.request(
                    method,
                    full_url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=10
                )
                status_codes.append(response.status_code)
                elapsed = time.monotonic() - start_time
                response_times.append(elapsed)
                print(f"  Request {i+1}/{samples}: {elapsed:.4f}s (Status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                elapsed = time.monotonic() - start_time
                response_times.append(elapsed)
                errors.append({"request": i, "error": str(e), "time": elapsed})
                print(f"  Request {i+1}/{samples}: Error - {str(e)}")
            
            # Small delay between requests to prevent hammering the server
            time.sleep(0.1)
        
        # Calculate metrics
        metrics = self._calculate_metrics(response_times, status_codes, errors)
        
        # Store results
        result = {
            "endpoint": endpoint,
            "method": method,
            "samples": samples,
            "data": data,
            "params": params,
            "metrics": metrics,
            "response_times": response_times,
            "status_codes": status_codes,
            "errors": errors
        }
        
        # Add to overall results
        self.results["endpoints"][f"{method}_{endpoint}"] = {
            "endpoint": endpoint,
            "method": method,
            "metrics": metrics
        }
        
        print(f"Benchmark completed for {method} {endpoint}")
        print(f"  Mean: {metrics['mean']:.4f}s, P95: {metrics['p95']:.4f}s, Success: {metrics['success_rate']:.1%}")
        
        return result
    
    def _calculate_metrics(self, 
                         response_times: List[float], 
                         status_codes: List[int], 
                         errors: List[Dict]) -> Dict:
        """Calculate performance metrics from benchmark data."""
        if not response_times:
            return {
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "p90": 0,
                "p95": 0,
                "p99": 0,
                "std_dev": 0,
                "success_rate": 0,
                "error_rate": 1.0
            }
        
        # Sort response times for percentile calculations
        sorted_times = sorted(response_times)
        
        # Calculate success rate (2xx, 3xx status codes)
        success_count = sum(1 for code in status_codes if 200 <= code < 400)
        
        return {
            "mean": statistics.mean(response_times) if response_times else 0,
            "median": statistics.median(response_times) if response_times else 0,
            "min": min(response_times) if response_times else 0,
            "max": max(response_times) if response_times else 0,
            "p90": sorted_times[int(len(sorted_times) * 0.9)] if response_times else 0,
            "p95": sorted_times[int(len(sorted_times) * 0.95)] if response_times else 0,
            "p99": sorted_times[int(len(sorted_times) * 0.99)] if response_times else 0,
            "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
            "success_rate": success_count / len(status_codes) if status_codes else 0,
            "error_rate": len(errors) / len(response_times) if response_times else 1.0,
            "total_requests": len(response_times),
            "error_count": len(errors)
        }
    
    def benchmark_common_endpoints(self, samples: int = 10) -> Dict[str, Any]:
        """
        Benchmark a set of common API endpoints.
        
        Args:
            samples: Number of samples for each endpoint
            
        Returns:
            Dictionary with benchmark results for all endpoints
        """
        # Authenticate first if credentials provided
        if self.email and self.password:
            self.login()
        
        # Non-authenticated endpoints
        self.benchmark_endpoint("/health", "GET", samples=samples)
        
        # Authenticated endpoints if logged in
        if self.auth_token:
            self.benchmark_endpoint("/users/me", "GET", samples=samples)
            self.benchmark_endpoint("/training-sessions", "GET", samples=samples)
            self.benchmark_endpoint("/email/send-test", "POST", samples=samples)
        
        # Save results and history
        self.save_results()
        
        return self.results
    
    def save_results(self, detailed: bool = True) -> Tuple[str, str]:
        """
        Save benchmark results to files.
        
        Args:
            detailed: Whether to include detailed response data
            
        Returns:
            Tuple with paths to JSON and CSV output files
        """
        # Create results directory if it doesn't exist
        results_dir = os.path.join(self.output_dir, "benchmark_results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Create output filenames with timestamp
        json_file = os.path.join(results_dir, f"benchmark_{self.timestamp}.json")
        
        # If not detailed, remove the raw data to keep files smaller
        output_results = self.results.copy()
        if not detailed:
            for endpoint_key, endpoint_data in output_results["endpoints"].items():
                if "response_times" in endpoint_data:
                    del endpoint_data["response_times"]
                if "status_codes" in endpoint_data:
                    del endpoint_data["status_codes"]
                if "errors" in endpoint_data:
                    del endpoint_data["errors"]
        
        # Save JSON results
        with open(json_file, 'w') as f:
            json.dump(output_results, f, indent=2)
        
        print(f"Benchmark results saved to {json_file}")
        
        # Save to history
        self._save_history()
        
        # Generate and save visualizations
        pdf_file = self.generate_report(json_file)
        
        return json_file, pdf_file
    
    def generate_report(self, json_file: str) -> str:
        """
        Generate visual report of benchmark results.
        
        Args:
            json_file: Path to JSON results file
            
        Returns:
            Path to generated PDF report
        """
        plt.style.use('ggplot')
        
        # Read results
        with open(json_file, 'r') as f:
            results = json.load(f)
        
        # Create figure for response time comparison
        plt.figure(figsize=(12, 8))
        
        # Extract data
        endpoints = []
        mean_times = []
        p95_times = []
        
        for endpoint_key, endpoint_data in results["endpoints"].items():
            endpoints.append(f"{endpoint_data['method']} {endpoint_data['endpoint']}")
            mean_times.append(endpoint_data["metrics"]["mean"])
            p95_times.append(endpoint_data["metrics"]["p95"])
        
        # Create bar plot
        x = np.arange(len(endpoints))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, mean_times, width, label='Mean', color='#3498db')
        ax.bar(x + width/2, p95_times, width, label='P95', color='#e74c3c')
        
        # Add labels and legend
        ax.set_xlabel('Endpoints')
        ax.set_ylabel('Response Time (seconds)')
        ax.set_title('API Response Times by Endpoint')
        ax.set_xticks(x)
        ax.set_xticklabels(endpoints, rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        # Save figure
        response_times_file = os.path.join(self.output_dir, f"response_times_{self.timestamp}.png")
        plt.savefig(response_times_file)
        plt.close()
        
        # Create success rate chart
        plt.figure(figsize=(10, 6))
        success_rates = [endpoint_data["metrics"]["success_rate"] * 100 for endpoint_data in results["endpoints"].values()]
        
        plt.bar(endpoints, success_rates, color=['#2ecc71' if rate > 95 else '#f39c12' if rate > 80 else '#e74c3c' for rate in success_rates])
        plt.xlabel('Endpoints')
        plt.ylabel('Success Rate (%)')
        plt.title('API Success Rates by Endpoint')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.ylim(0, 105)  # Set y-axis to go from 0 to 105%
        
        # Add threshold line
        plt.axhline(y=95, color='r', linestyle='--', alpha=0.7, label='95% Threshold')
        plt.legend()
        
        # Save success rate chart
        success_rate_file = os.path.join(self.output_dir, f"success_rates_{self.timestamp}.png")
        plt.savefig(success_rate_file)
        plt.close()
        
        # If we have historical data, create trend chart
        if len(self.history["runs"]) > 1:
            self._generate_trend_chart()
        
        # Generate HTML report with all charts
        report_file = self._generate_html_report(response_times_file, success_rate_file)
        
        return report_file
    
    def _generate_trend_chart(self) -> str:
        """Generate chart showing performance trends over time."""
        plt.figure(figsize=(12, 6))
        
        # Extract trend data for each endpoint
        endpoint_trends = {}
        timestamps = []
        
        for run in self.history["runs"]:
            timestamps.append(run["timestamp"])
            for endpoint_key, endpoint_data in run["endpoints"].items():
                if endpoint_key not in endpoint_trends:
                    endpoint_trends[endpoint_key] = {
                        "mean": [],
                        "p95": []
                    }
                
                endpoint_trends[endpoint_key]["mean"].append(endpoint_data["metrics"]["mean"])
                endpoint_trends[endpoint_key]["p95"].append(endpoint_data["metrics"]["p95"])
        
        # Plot trends for each endpoint
        for endpoint_key, data in endpoint_trends.items():
            if len(data["mean"]) > 1:  # Only plot if we have more than one data point
                plt.plot(timestamps, data["p95"], label=f"{endpoint_key} (P95)", marker='o')
        
        plt.xlabel('Benchmark Run')
        plt.ylabel('Response Time (seconds)')
        plt.title('API Performance Trends Over Time (P95)')
        plt.xticks(rotation=45, ha='right')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        
        # Save trend chart
        trend_file = os.path.join(self.output_dir, f"trends_{self.timestamp}.png")
        plt.savefig(trend_file)
        plt.close()
        
        return trend_file
    
    def _generate_html_report(self, response_times_chart: str, success_rates_chart: str) -> str:
        """Generate HTML report with embedded charts."""
        report_file = os.path.join(self.output_dir, f"benchmark_report_{self.timestamp}.html")
        
        # Simple HTML template
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>API Benchmark Report - {self.timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .charts {{ margin-top: 30px; }}
        .chart {{ margin-bottom: 30px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>API Benchmark Report</h1>
        <p><strong>Base URL:</strong> {self.base_url}</p>
        <p><strong>Timestamp:</strong> {self.timestamp}</p>
    </div>
    
    <div class="charts">
        <div class="chart">
            <h2>Response Times</h2>
            <img src="{os.path.basename(response_times_chart)}" alt="Response Times Chart" style="max-width: 100%;">
        </div>
        
        <div class="chart">
            <h2>Success Rates</h2>
            <img src="{os.path.basename(success_rates_chart)}" alt="Success Rates Chart" style="max-width: 100%;">
        </div>
    </div>
    
    <div class="results">
        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>Endpoint</th>
                <th>Method</th>
                <th>Mean (s)</th>
                <th>P95 (s)</th>
                <th>Success Rate</th>
            </tr>
"""
        
        # Add a row for each endpoint
        for endpoint_key, endpoint_data in self.results["endpoints"].items():
            metrics = endpoint_data["metrics"]
            html_content += f"""
            <tr>
                <td>{endpoint_data["endpoint"]}</td>
                <td>{endpoint_data["method"]}</td>
                <td>{metrics["mean"]:.4f}</td>
                <td>{metrics["p95"]:.4f}</td>
                <td>{metrics["success_rate"]*100:.1f}%</td>
            </tr>"""
        
        # Close the HTML
        html_content += """
        </table>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {report_file}")
        return report_file

def main():
    """Main function to run benchmark from command line."""
    parser = argparse.ArgumentParser(description='API Benchmark Tool')
    parser.add_argument('--base-url', required=True, help='Base URL of the API')
    parser.add_argument('--email', help='Email for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples per endpoint')
    parser.add_argument('--output', default='reports', help='Output directory for reports')
    parser.add_argument('--endpoints', nargs='+', help='Specific endpoints to benchmark (e.g., /health /users)')
    
    args = parser.parse_args()
    
    # Initialize benchmark
    benchmark = APIBenchmark(args.base_url, args.email, args.password, args.output)
    
    # Authenticate if credentials provided
    if args.email and args.password:
        benchmark.login()
    
    # Benchmark specific endpoints if provided, otherwise use common endpoints
    if args.endpoints:
        for endpoint in args.endpoints:
            benchmark.benchmark_endpoint(endpoint, samples=args.samples)
    else:
        benchmark.benchmark_common_endpoints(samples=args.samples)
    
    # Save results and generate report
    json_file, report_file = benchmark.save_results()
    
    print(f"Benchmark completed. Results saved to {json_file}")
    print(f"HTML report saved to {report_file}")

if __name__ == "__main__":
    main() 