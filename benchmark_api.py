#!/usr/bin/env python3
import requests
import time
import json
import logging
import argparse
import statistics
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import os
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test-logs/benchmark.log")
    ]
)
logger = logging.getLogger(__name__)

class APIBenchmark:
    """API Performance Benchmarking Tool"""
    
    def __init__(self, base_url: str, email: str = None, password: str = None):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None
        self.session = requests.Session()
        
        # Create directories if they don't exist
        Path("test-logs").mkdir(exist_ok=True)
        Path("benchmark-data").mkdir(exist_ok=True)
        Path("benchmark-reports").mkdir(exist_ok=True)
        
        # Initialize results dictionary
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "endpoints": {},
            "summary": {}
        }
        
    def login(self) -> bool:
        """Authenticate with the API and get token"""
        # Skip if no credentials provided
        if not self.email or not self.password:
            logger.info("No credentials provided, skipping login")
            return True
            
        try:
            logger.info(f"Attempting login to {self.base_url}/auth/login")
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": self.email,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    logger.info("Login successful, token obtained")
                    return True
                else:
                    logger.error("Login response did not contain token")
                    return False
            else:
                logger.error(f"Login failed with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
    
    def benchmark_endpoint(self, 
                          endpoint: str, 
                          method: str = "GET", 
                          data: Dict[str, Any] = None, 
                          params: Dict[str, Any] = None,
                          samples: int = 10,
                          warmup_samples: int = 2) -> Dict[str, Any]:
        """
        Benchmark a specific API endpoint
        
        Args:
            endpoint: API endpoint to benchmark
            method: HTTP method to use
            data: Request body for POST/PUT requests
            params: Query parameters for GET requests
            samples: Number of samples to collect
            warmup_samples: Number of warmup samples to discard
        
        Returns:
            Dict containing benchmark results
        """
        logger.info(f"Benchmarking {method} {endpoint} with {samples} samples")
        
        url = f"{self.base_url}{endpoint}"
        response_times = []
        status_codes = []
        response_sizes = []
        
        # Perform the requests
        for i in range(samples + warmup_samples):
            # Clear any previous request-specific headers
            for key in ['content-length', 'content-type']:
                if key in self.session.headers:
                    del self.session.headers[key]
                    
            start_time = time.time()
            
            try:
                if method == "GET":
                    response = self.session.get(url, params=params)
                elif method == "POST":
                    response = self.session.post(url, json=data)
                elif method == "PUT":
                    response = self.session.put(url, json=data)
                elif method == "DELETE":
                    response = self.session.delete(url)
                else:
                    logger.error(f"Unsupported method: {method}")
                    continue
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Skip warmup samples
                if i >= warmup_samples:
                    response_times.append(duration)
                    status_codes.append(response.status_code)
                    response_sizes.append(len(response.content))
                    
                    logger.debug(f"Request {i-warmup_samples+1}/{samples}: {duration:.2f}ms, Status: {response.status_code}")
                else:
                    logger.debug(f"Warmup {i+1}/{warmup_samples}: {duration:.2f}ms, Status: {response.status_code}")
                
                # Add a small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in request {i+1}: {str(e)}")
                # Still count failed requests, with a very high response time
                if i >= warmup_samples:
                    response_times.append(10000)  # 10 seconds as a penalty
                    status_codes.append(0)
                    response_sizes.append(0)
        
        # Calculate statistics
        if not response_times:
            logger.error(f"No valid responses collected for {method} {endpoint}")
            return {
                "endpoint": endpoint,
                "method": method,
                "samples": 0,
                "success": False,
                "error": "No valid responses collected"
            }
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "samples": len(response_times),
            "success": all(200 <= code < 300 for code in status_codes),
            "timing": {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": np.percentile(response_times, 95),
                "p99": np.percentile(response_times, 99),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            "status_codes": {code: status_codes.count(code) for code in set(status_codes)},
            "response_size": {
                "min": min(response_sizes),
                "max": max(response_sizes),
                "mean": statistics.mean(response_sizes),
                "median": statistics.median(response_sizes),
                "total": sum(response_sizes)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Log summary
        logger.info(f"Benchmark results for {method} {endpoint}:")
        logger.info(f"  Mean response time: {result['timing']['mean']:.2f}ms")
        logger.info(f"  Median response time: {result['timing']['median']:.2f}ms")
        logger.info(f"  95th percentile: {result['timing']['p95']:.2f}ms")
        logger.info(f"  Status codes: {result['status_codes']}")
        
        # Store the result
        endpoint_key = f"{method} {endpoint}"
        self.results["endpoints"][endpoint_key] = result
        
        return result
    
    def benchmark_common_endpoints(self, samples: int = 10) -> Dict[str, Any]:
        """Benchmark common API endpoints"""
        
        endpoints = [
            # Format: (endpoint, method, data, params)
            ("/health", "GET", None, None),
            ("/users/me", "GET", None, None),
            ("/training-sessions", "GET", None, None),
            ("/training-sessions", "POST", {"title": "Benchmark Test", "description": "Test session"}, None),
            ("/users/me", "PUT", {"name": "Benchmark User"}, None),
        ]
        
        # Benchmark each endpoint
        for endpoint, method, data, params in endpoints:
            self.benchmark_endpoint(endpoint, method, data, params, samples=samples)
        
        # Calculate overall statistics
        all_response_times = []
        success_count = 0
        total_count = len(self.results["endpoints"])
        
        for endpoint_result in self.results["endpoints"].values():
            if endpoint_result["success"]:
                success_count += 1
            all_response_times.extend([endpoint_result["timing"]["min"], 
                                      endpoint_result["timing"]["mean"], 
                                      endpoint_result["timing"]["max"]])
        
        self.results["summary"] = {
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "total_endpoints": total_count,
            "successful_endpoints": success_count,
            "overall_timing": {
                "min": min(all_response_times) if all_response_times else 0,
                "max": max(all_response_times) if all_response_times else 0,
                "mean": statistics.mean(all_response_times) if all_response_times else 0
            }
        }
        
        return self.results
    
    def save_results(self, detailed: bool = True) -> Tuple[str, str]:
        """
        Save benchmark results to files
        
        Args:
            detailed: Whether to save detailed results or just summary
            
        Returns:
            Tuple of (json_file_path, csv_file_path)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare data for CSV
        csv_rows = []
        for endpoint_key, data in self.results["endpoints"].items():
            row = {
                "timestamp": timestamp,
                "endpoint": endpoint_key,
                "min_ms": data["timing"]["min"],
                "mean_ms": data["timing"]["mean"],
                "median_ms": data["timing"]["median"],
                "max_ms": data["timing"]["max"],
                "p95_ms": data["timing"]["p95"],
                "p99_ms": data["timing"]["p99"],
                "std_dev_ms": data["timing"]["std_dev"],
                "success": data["success"],
                "successful_status": sum(data["status_codes"].get(code, 0) for code in range(200, 300)),
                "error_status": sum(data["status_codes"].get(code, 0) for code in range(400, 600)),
                "avg_size_bytes": data["response_size"]["mean"]
            }
            csv_rows.append(row)
        
        # Save summary CSV for historical tracking
        csv_file = f"benchmark-data/benchmark_{timestamp}.csv"
        
        # Check if history file exists and create with headers if not
        history_csv = "benchmark-data/benchmark_history.csv"
        write_headers = not os.path.exists(history_csv)
        
        # Save to history CSV
        with open(history_csv, "a", newline="") as f:
            fieldnames = csv_rows[0].keys() if csv_rows else []
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if write_headers:
                writer.writeheader()
                
            writer.writerows(csv_rows)
        
        # Save individual benchmark CSV
        with open(csv_file, "w", newline="") as f:
            fieldnames = csv_rows[0].keys() if csv_rows else []
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        # Save full JSON results
        json_file = f"benchmark-data/benchmark_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
            
        logger.info(f"Benchmark results saved to {json_file} and {csv_file}")
        logger.info(f"Historical data updated in {history_csv}")
        
        return json_file, csv_file
    
    def generate_report(self, 
                       json_file: str,
                       csv_file: str,
                       compare_with: str = None) -> str:
        """
        Generate a benchmark report with visualizations
        
        Args:
            json_file: Path to the JSON results file
            csv_file: Path to the CSV results file
            compare_with: Path to previous JSON results file to compare with
            
        Returns:
            Path to the generated HTML report
        """
        logger.info("Generating benchmark report")
        
        # Load the benchmark data
        with open(json_file, "r") as f:
            data = json.load(f)
            
        # Load comparison data if provided
        comparison_data = None
        if compare_with and os.path.exists(compare_with):
            try:
                with open(compare_with, "r") as f:
                    comparison_data = json.load(f)
                logger.info(f"Loaded comparison data from {compare_with}")
            except Exception as e:
                logger.error(f"Error loading comparison data: {str(e)}")
        
        # Create report timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create plots directory
        plots_dir = "benchmark-reports/plots"
        Path(plots_dir).mkdir(exist_ok=True, parents=True)
        
        # Generate response time plot
        plt.figure(figsize=(12, 6))
        
        endpoints = list(data["endpoints"].keys())
        mean_times = [data["endpoints"][ep]["timing"]["mean"] for ep in endpoints]
        p95_times = [data["endpoints"][ep]["timing"]["p95"] for ep in endpoints]
        
        # Comparison data if available
        if comparison_data:
            comparison_means = []
            for ep in endpoints:
                # Find the endpoint in comparison data
                comp_ep = comparison_data["endpoints"].get(ep)
                if comp_ep:
                    comparison_means.append(comp_ep["timing"]["mean"])
                else:
                    comparison_means.append(0)
        
        x = np.arange(len(endpoints))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        rects1 = ax.bar(x - width/2, mean_times, width, label='Mean (Current)')
        
        if comparison_data:
            rects2 = ax.bar(x + width/2, comparison_means, width, label='Mean (Previous)', alpha=0.7)
        
        ax.set_ylabel('Response Time (ms)')
        ax.set_title('API Endpoint Performance')
        ax.set_xticks(x)
        ax.set_xticklabels(endpoints, rotation=45, ha='right')
        ax.legend()
        
        # Add some text for labels
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.1f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        autolabel(rects1)
        if comparison_data:
            autolabel(rects2)
            
        fig.tight_layout()
        
        # Save the plot
        response_time_plot = f"{plots_dir}/response_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(response_time_plot)
        plt.close()
        
        # Generate p95 vs mean plot
        plt.figure(figsize=(12, 6))
        
        for i, ep in enumerate(endpoints):
            plt.bar([i-0.2, i+0.2], 
                   [data["endpoints"][ep]["timing"]["mean"], data["endpoints"][ep]["timing"]["p95"]], 
                   width=0.4,
                   label=ep if i == 0 else "")
        
        plt.ylabel('Response Time (ms)')
        plt.title('Mean vs 95th Percentile Response Times')
        plt.xticks(range(len(endpoints)), ["Mean", "p95"] * len(endpoints), rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # Save the plot
        percentile_plot = f"{plots_dir}/percentiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(percentile_plot)
        plt.close()
        
        # Generate historical trend plot if we have history
        history_csv = "benchmark-data/benchmark_history.csv"
        if os.path.exists(history_csv):
            try:
                # Read the history
                history = []
                with open(history_csv, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        history.append(row)
                
                # Group by timestamp and endpoint
                grouped_history = {}
                for row in history:
                    timestamp = row["timestamp"]
                    endpoint = row["endpoint"]
                    
                    if timestamp not in grouped_history:
                        grouped_history[timestamp] = {}
                        
                    grouped_history[timestamp][endpoint] = row
                
                # Get unique endpoints
                all_endpoints = set()
                for ts_data in grouped_history.values():
                    all_endpoints.update(ts_data.keys())
                
                # Get timestamps in order
                timestamps = sorted(grouped_history.keys())
                
                # For each endpoint, plot the trend
                for endpoint in all_endpoints:
                    plt.figure(figsize=(12, 6))
                    
                    mean_times = []
                    p95_times = []
                    
                    for ts in timestamps:
                        if endpoint in grouped_history[ts]:
                            mean_times.append(float(grouped_history[ts][endpoint]["mean_ms"]))
                            p95_times.append(float(grouped_history[ts][endpoint]["p95_ms"]))
                        else:
                            mean_times.append(None)
                            p95_times.append(None)
                    
                    plt.plot(range(len(timestamps)), mean_times, 'o-', label='Mean')
                    plt.plot(range(len(timestamps)), p95_times, 's-', label='95th Percentile')
                    
                    plt.ylabel('Response Time (ms)')
                    plt.title(f'Historical Trend for {endpoint}')
                    plt.xticks(range(len(timestamps)), 
                              [datetime.strptime(ts, "%Y%m%d_%H%M%S").strftime("%m-%d %H:%M") for ts in timestamps], 
                              rotation=45)
                    plt.legend()
                    plt.tight_layout()
                    
                    # Save the plot
                    trend_plot = f"{plots_dir}/trend_{endpoint.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    plt.savefig(trend_plot)
                    plt.close()
            except Exception as e:
                logger.error(f"Error generating historical trend: {str(e)}")
        
        # Generate the HTML report
        html_file = f"benchmark-reports/benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(html_file, "w") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>API Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .warning {{ color: orange; }}
        .card {{ box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); padding: 16px; margin-bottom: 20px; }}
        .plot {{ width: 100%; max-width: 1000px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>API Benchmark Report</h1>
    <p>Generated on: {timestamp}</p>
    <p>Target API: {data['base_url']}</p>
    
    <div class="card">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Success Rate</td>
                <td class="{
                    'success' if data['summary']['success_rate'] > 0.9 else 
                    'warning' if data['summary']['success_rate'] > 0.7 else 
                    'failure'
                }">{data['summary']['success_rate']*100:.1f}%</td>
            </tr>
            <tr>
                <td>Total Endpoints Tested</td>
                <td>{data['summary']['total_endpoints']}</td>
            </tr>
            <tr>
                <td>Successful Endpoints</td>
                <td>{data['summary']['successful_endpoints']}</td>
            </tr>
            <tr>
                <td>Overall Min Response Time</td>
                <td>{data['summary']['overall_timing']['min']:.2f} ms</td>
            </tr>
            <tr>
                <td>Overall Mean Response Time</td>
                <td>{data['summary']['overall_timing']['mean']:.2f} ms</td>
            </tr>
            <tr>
                <td>Overall Max Response Time</td>
                <td>{data['summary']['overall_timing']['max']:.2f} ms</td>
            </tr>
        </table>
    </div>
    
    <div class="card">
        <h2>Response Time Visualization</h2>
        <img src="{os.path.relpath(response_time_plot, 'benchmark-reports')}" class="plot" alt="Response Time Plot">
        
        <h3>Mean vs 95th Percentile</h3>
        <img src="{os.path.relpath(percentile_plot, 'benchmark-reports')}" class="plot" alt="Percentile Plot">
    </div>
    
    <div class="card">
        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>Endpoint</th>
                <th>Min (ms)</th>
                <th>Mean (ms)</th>
                <th>Median (ms)</th>
                <th>95th (ms)</th>
                <th>Max (ms)</th>
                <th>Std Dev</th>
                <th>Status</th>
            </tr>
            {
                ''.join([
                    f"""<tr>
                        <td>{endpoint}</td>
                        <td>{data['endpoints'][endpoint]['timing']['min']:.2f}</td>
                        <td>{data['endpoints'][endpoint]['timing']['mean']:.2f}</td>
                        <td>{data['endpoints'][endpoint]['timing']['median']:.2f}</td>
                        <td>{data['endpoints'][endpoint]['timing']['p95']:.2f}</td>
                        <td>{data['endpoints'][endpoint]['timing']['max']:.2f}</td>
                        <td>{data['endpoints'][endpoint]['timing']['std_dev']:.2f}</td>
                        <td class="{'success' if data['endpoints'][endpoint]['success'] else 'failure'}">
                            {
                                ', '.join([f"{code}: {count}" for code, count in 
                                            data['endpoints'][endpoint]['status_codes'].items()])
                            }
                        </td>
                    </tr>"""
                    for endpoint in data['endpoints']
                ])
            }
        </table>
    </div>
    
    <div class="card">
        <h2>Historical Trends</h2>
        {
            ''.join([
                f"<h3>Trend for {endpoint}</h3><img src='{os.path.relpath(f'{plots_dir}/trend_{endpoint.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png', 'benchmark-reports')}' class='plot'>"
                for endpoint in all_endpoints
            ]) if 'all_endpoints' in locals() else "<p>No historical data available</p>"
        }
    </div>
    
    <div class="card">
        <h2>Comparison with Previous Run</h2>
        {
            f"<p>Comparing with benchmark from: {comparison_data['timestamp']}</p>"
            if comparison_data else "<p>No comparison data available</p>"
        }
        {
            f"""<table>
                <tr>
                    <th>Endpoint</th>
                    <th>Current Mean (ms)</th>
                    <th>Previous Mean (ms)</th>
                    <th>Difference</th>
                    <th>Change %</th>
                </tr>
                {
                    ''.join([
                        f"""<tr>
                            <td>{endpoint}</td>
                            <td>{data['endpoints'][endpoint]['timing']['mean']:.2f}</td>
                            <td>{comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 'N/A')}</td>
                            <td class="{
                                'success' if comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 0) > data['endpoints'][endpoint]['timing']['mean'] else
                                'failure' if comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 0) < data['endpoints'][endpoint]['timing']['mean'] else
                                ''
                            }">{
                                f"{data['endpoints'][endpoint]['timing']['mean'] - comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 0):.2f}"
                                if comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 'N/A') != 'N/A'
                                else 'N/A'
                            }</td>
                            <td class="{
                                'success' if comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 0) > data['endpoints'][endpoint]['timing']['mean'] else
                                'failure' if comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 0) < data['endpoints'][endpoint]['timing']['mean'] else
                                ''
                            }">{
                                f"{((data['endpoints'][endpoint]['timing']['mean'] / comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 1)) - 1) * 100:.2f}%"
                                if comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 'N/A') != 'N/A' and comparison_data['endpoints'].get(endpoint, {}).get('timing', {}).get('mean', 0) != 0
                                else 'N/A'
                            }</td>
                        </tr>"""
                        for endpoint in data['endpoints']
                        if endpoint in comparison_data.get('endpoints', {})
                    ])
                }
            </table>"""
            if comparison_data else ""
        }
    </div>
    
    <footer>
        <p>Generated by API Benchmark Tool</p>
    </footer>
</body>
</html>""")
        
        logger.info(f"Benchmark report generated: {html_file}")
        return html_file

def main():
    parser = argparse.ArgumentParser(description="API Performance Benchmarking Tool")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--email", help="Email for authentication")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--samples", type=int, default=10, help="Number of samples to collect per endpoint")
    parser.add_argument("--compare", help="Path to previous benchmark JSON to compare with")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the benchmark
    benchmark = APIBenchmark(args.url, args.email, args.password)
    
    if not benchmark.login():
        logger.error("Login failed, exiting")
        return 1
    
    benchmark.benchmark_common_endpoints(samples=args.samples)
    json_file, csv_file = benchmark.save_results()
    
    report_file = benchmark.generate_report(json_file, csv_file, args.compare)
    
    print(f"\nBenchmark Results:")
    print(f"  Report: {report_file}")
    print(f"  JSON: {json_file}")
    print(f"  CSV: {csv_file}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 