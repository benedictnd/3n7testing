#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Performance Monitor

This module provides tools for measuring, tracking, and analyzing API performance metrics
over time. It stores historical performance data, compares current performance against
baselines, and generates performance reports.

Usage:
    python api_performance_monitor.py --endpoint /api/users --requests 100 --output performance_report.json
"""

import argparse
import json
import logging
import os
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test-logs/performance.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("api_performance")

# Ensure test-logs directory exists
os.makedirs("test-logs", exist_ok=True)

# Default performance thresholds (in seconds)
DEFAULT_THRESHOLDS = {
    "excellent": 0.1,     # < 100ms is excellent
    "good": 0.3,          # < 300ms is good
    "acceptable": 0.8,    # < 800ms is acceptable
    "poor": 1.5,          # < 1.5s is poor
    # > 1.5s is critical
}

# Default performance history file
DEFAULT_HISTORY_FILE = "test-logs/performance_history.json"


class PerformanceMonitor:
    """Monitors and analyzes API performance metrics."""

    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        history_file: str = DEFAULT_HISTORY_FILE,
        thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the performance monitor.

        Args:
            base_url: Base URL of the API to test
            auth_token: Optional authentication token
            history_file: File to store performance history
            thresholds: Performance thresholds in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.history_file = history_file
        self.thresholds = thresholds or DEFAULT_THRESHOLDS
        self.session = requests.Session()
        self.results = defaultdict(list)
        
        # Setup headers
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
            
        # Load historical data if available
        self.history = self._load_history()
        logger.info(f"Initialized performance monitor for {base_url}")

    def _load_history(self) -> Dict:
        """Load performance history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    return json.load(f)
            return {"endpoints": {}, "metadata": {"last_updated": None}}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading performance history: {str(e)}")
            return {"endpoints": {}, "metadata": {"last_updated": None}}

    def _save_history(self):
        """Save performance history to file."""
        try:
            self.history["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Saved performance history to {self.history_file}")
        except IOError as e:
            logger.error(f"Error saving performance history: {str(e)}")

    def measure_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        num_requests: int = 10,
        delay: float = 0.1
    ) -> Dict:
        """
        Measure performance of a specific endpoint.

        Args:
            endpoint: API endpoint to test (e.g., "/api/users")
            method: HTTP method to use
            params: Query parameters
            data: Request body data
            num_requests: Number of requests to make
            delay: Delay between requests in seconds

        Returns:
            Dictionary containing performance metrics
        """
        url = f"{self.base_url}{endpoint}"
        response_times = []
        status_codes = []
        errors = []
        
        logger.info(f"Testing endpoint {method} {endpoint} with {num_requests} requests")
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                
                if method.upper() == "GET":
                    response = self.session.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = self.session.post(url, headers=self.headers, json=data)
                elif method.upper() == "PUT":
                    response = self.session.put(url, headers=self.headers, json=data)
                elif method.upper() == "DELETE":
                    response = self.session.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                status_codes.append(response.status_code)
                
                if response.status_code >= 400:
                    errors.append({
                        "request_num": i + 1,
                        "status_code": response.status_code,
                        "message": response.text[:100] if response.text else "No response body"
                    })
                
                # Wait between requests to avoid rate limiting
                if i < num_requests - 1:
                    time.sleep(delay)
                    
            except RequestException as e:
                logger.error(f"Request error on {endpoint}: {str(e)}")
                errors.append({
                    "request_num": i + 1,
                    "error": str(e),
                    "type": type(e).__name__
                })
        
        # Calculate metrics
        metrics = self._calculate_metrics(response_times, status_codes, errors)
        
        # Store results for this endpoint
        endpoint_key = f"{method} {endpoint}"
        self.results[endpoint_key] = metrics
        
        # Update history
        self._update_history(endpoint_key, metrics)
        
        return metrics

    def _calculate_metrics(
        self, 
        response_times: List[float], 
        status_codes: List[int], 
        errors: List[Dict]
    ) -> Dict:
        """Calculate performance metrics from raw data."""
        if not response_times:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": "No successful responses"
            }
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "sample_size": len(response_times),
            "success_rate": (len(response_times) - len(errors)) / len(response_times) if response_times else 0,
            "error_count": len(errors),
            "errors": errors[:10],  # Limit to first 10 errors
            "status_code_distribution": {str(code): status_codes.count(code) for code in set(status_codes)},
            "response_time": {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p90": np.percentile(response_times, 90),
                "p95": np.percentile(response_times, 95),
                "p99": np.percentile(response_times, 99),
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        }
        
        # Classify performance based on thresholds
        mean_time = metrics["response_time"]["mean"]
        if mean_time < self.thresholds["excellent"]:
            metrics["performance_rating"] = "excellent"
        elif mean_time < self.thresholds["good"]:
            metrics["performance_rating"] = "good"
        elif mean_time < self.thresholds["acceptable"]:
            metrics["performance_rating"] = "acceptable"
        elif mean_time < self.thresholds["poor"]:
            metrics["performance_rating"] = "poor"
        else:
            metrics["performance_rating"] = "critical"
            
        return metrics

    def _update_history(self, endpoint_key: str, metrics: Dict):
        """Update performance history with new metrics."""
        if endpoint_key not in self.history["endpoints"]:
            self.history["endpoints"][endpoint_key] = []
        
        # Keep only essential metrics for history
        historical_entry = {
            "timestamp": metrics["timestamp"],
            "mean": metrics["response_time"]["mean"],
            "median": metrics["response_time"]["median"],
            "p95": metrics["response_time"]["p95"],
            "success_rate": metrics["success_rate"],
            "performance_rating": metrics["performance_rating"]
        }
        
        # Limit history size (keep last 100 entries)
        self.history["endpoints"][endpoint_key].append(historical_entry)
        if len(self.history["endpoints"][endpoint_key]) > 100:
            self.history["endpoints"][endpoint_key] = self.history["endpoints"][endpoint_key][-100:]

    def compare_with_baseline(self, endpoint_key: str) -> Dict:
        """
        Compare current performance with historical baseline.
        
        Args:
            endpoint_key: The endpoint key (e.g., "GET /api/users")
            
        Returns:
            Dictionary with comparison results
        """
        if endpoint_key not in self.results:
            return {"error": f"No current data for {endpoint_key}"}
        
        if endpoint_key not in self.history["endpoints"] or not self.history["endpoints"][endpoint_key]:
            return {"error": f"No historical data for {endpoint_key}"}
        
        current = self.results[endpoint_key]
        
        # Get baseline (average of last 5 runs)
        history = self.history["endpoints"][endpoint_key]
        baseline_count = min(5, len(history) - 1)  # Use up to 5 previous runs, excluding the current one
        
        if baseline_count <= 0:
            return {"error": "Insufficient historical data for comparison"}
        
        baseline_entries = history[-(baseline_count+1):-1]  # Exclude the current run which is the last entry
        
        baseline = {
            "mean": statistics.mean([entry["mean"] for entry in baseline_entries]),
            "median": statistics.mean([entry["median"] for entry in baseline_entries]),
            "p95": statistics.mean([entry["p95"] for entry in baseline_entries]),
            "success_rate": statistics.mean([entry["success_rate"] for entry in baseline_entries])
        }
        
        # Calculate percentage changes
        changes = {
            "mean": ((current["response_time"]["mean"] - baseline["mean"]) / baseline["mean"]) * 100,
            "median": ((current["response_time"]["median"] - baseline["median"]) / baseline["median"]) * 100,
            "p95": ((current["response_time"]["p95"] - baseline["p95"]) / baseline["p95"]) * 100,
            "success_rate": ((current["success_rate"] - baseline["success_rate"]) / baseline["success_rate"]) * 100 if baseline["success_rate"] > 0 else 0
        }
        
        # Determine if there's a performance regression
        # A positive change in response time is bad, a negative change in success rate is bad
        regression = changes["mean"] > 10 or changes["p95"] > 15 or (changes["success_rate"] < -5 and current["success_rate"] < 0.95)
        
        return {
            "current": {
                "mean": current["response_time"]["mean"],
                "median": current["response_time"]["median"],
                "p95": current["response_time"]["p95"],
                "success_rate": current["success_rate"]
            },
            "baseline": baseline,
            "changes_percentage": changes,
            "regression_detected": regression,
            "comparison_baseline": f"Average of last {baseline_count} runs"
        }

    def generate_report(self, output_file: Optional[str] = None) -> Dict:
        """
        Generate a comprehensive performance report.
        
        Args:
            output_file: Optional file to save the report
            
        Returns:
            Dictionary containing the full performance report
        """
        if not self.results:
            return {"error": "No performance tests have been run"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "endpoints_tested": len(self.results),
            "endpoints": {},
            "summary": {
                "fastest_endpoint": None,
                "slowest_endpoint": None,
                "least_reliable_endpoint": None,
                "performance_regressions": []
            }
        }
        
        # Process each endpoint
        fastest_time = float('inf')
        slowest_time = 0
        lowest_success_rate = 1.0
        
        for endpoint_key, metrics in self.results.items():
            report["endpoints"][endpoint_key] = {
                "metrics": metrics,
                "comparison": self.compare_with_baseline(endpoint_key)
            }
            
            mean_time = metrics["response_time"]["mean"]
            success_rate = metrics["success_rate"]
            
            # Track fastest/slowest/least reliable
            if mean_time < fastest_time:
                fastest_time = mean_time
                report["summary"]["fastest_endpoint"] = {
                    "endpoint": endpoint_key,
                    "mean_response_time": mean_time
                }
                
            if mean_time > slowest_time:
                slowest_time = mean_time
                report["summary"]["slowest_endpoint"] = {
                    "endpoint": endpoint_key,
                    "mean_response_time": mean_time
                }
                
            if success_rate < lowest_success_rate:
                lowest_success_rate = success_rate
                report["summary"]["least_reliable_endpoint"] = {
                    "endpoint": endpoint_key,
                    "success_rate": success_rate
                }
                
            # Check for regressions
            comparison = report["endpoints"][endpoint_key]["comparison"]
            if "regression_detected" in comparison and comparison["regression_detected"]:
                report["summary"]["performance_regressions"].append({
                    "endpoint": endpoint_key,
                    "changes": comparison["changes_percentage"]
                })
        
        # Overall score (0-100)
        scores = []
        for endpoint_key, data in report["endpoints"].items():
            metrics = data["metrics"]
            
            # Calculate a score from 0-100 based on response time and success rate
            time_score = 0
            mean_time = metrics["response_time"]["mean"]
            
            if mean_time < self.thresholds["excellent"]:
                time_score = 100
            elif mean_time < self.thresholds["good"]:
                time_score = 80
            elif mean_time < self.thresholds["acceptable"]:
                time_score = 60
            elif mean_time < self.thresholds["poor"]:
                time_score = 40
            else:
                time_score = 20
                
            # Success rate score (0-100)
            success_score = metrics["success_rate"] * 100
            
            # Combined score (weighted 60% response time, 40% success rate)
            combined_score = (time_score * 0.6) + (success_score * 0.4)
            scores.append(combined_score)
        
        # Overall API performance score
        report["summary"]["overall_score"] = statistics.mean(scores) if scores else 0
        report["summary"]["performance_rating"] = self._get_rating_from_score(report["summary"]["overall_score"])
        
        # Save report if requested
        if output_file:
            try:
                with open(output_file, "w") as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Performance report saved to {output_file}")
            except IOError as e:
                logger.error(f"Error saving performance report: {str(e)}")
        
        # Always save history
        self._save_history()
        
        return report

    def _get_rating_from_score(self, score: float) -> str:
        """Convert a numeric score to a performance rating."""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "acceptable"
        elif score >= 40:
            return "poor"
        else:
            return "critical"

    def plot_history(self, endpoint_key: str, output_file: Optional[str] = None):
        """
        Generate a performance history plot for an endpoint.
        
        Args:
            endpoint_key: The endpoint to plot
            output_file: File to save the plot (if None, display instead)
        """
        if endpoint_key not in self.history["endpoints"] or len(self.history["endpoints"][endpoint_key]) < 2:
            logger.error(f"Insufficient history for {endpoint_key} to generate plot")
            return
            
        history = self.history["endpoints"][endpoint_key]
        
        # Extract data
        timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in history]
        mean_times = [entry["mean"] for entry in history]
        p95_times = [entry["p95"] for entry in history]
        success_rates = [entry["success_rate"] * 100 for entry in history]  # Convert to percentage
        
        # Create the figure with two subplots (response time and success rate)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Plot response times
        ax1.plot(timestamps, mean_times, 'b-', label='Mean')
        ax1.plot(timestamps, p95_times, 'r-', label='95th Percentile')
        ax1.set_ylabel('Response Time (seconds)')
        ax1.set_title(f'Performance History for {endpoint_key}')
        ax1.legend()
        ax1.grid(True)
        
        # Plot success rate
        ax2.plot(timestamps, success_rates, 'g-')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_ylim(0, 105)  # Give some room above 100%
        ax2.grid(True)
        
        # Format the date on x-axis
        fig.autofmt_xdate()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file)
            logger.info(f"Performance history plot saved to {output_file}")
        else:
            plt.show()
        
        plt.close(fig)


def main():
    """Run the performance monitoring as a CLI tool."""
    parser = argparse.ArgumentParser(description="API Performance Monitor")
    parser.add_argument("--base-url", required=True, help="Base URL of the API")
    parser.add_argument("--endpoint", required=True, help="API endpoint to test")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "DELETE"], 
                        help="HTTP method to use")
    parser.add_argument("--auth-token", help="Authentication token")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests to make")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between requests in seconds")
    parser.add_argument("--data", help="JSON data to send with the request")
    parser.add_argument("--output", help="Output file for the full report")
    parser.add_argument("--plot", help="Generate a performance history plot and save to the specified file")
    parser.add_argument("--history-file", default=DEFAULT_HISTORY_FILE, help="Performance history file")
    
    args = parser.parse_args()
    
    # Parse JSON data if provided
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON data provided")
            return 1
    
    try:
        # Create performance monitor
        monitor = PerformanceMonitor(
            base_url=args.base_url,
            auth_token=args.auth_token,
            history_file=args.history_file
        )
        
        # Run performance test
        logger.info(f"Starting performance test: {args.method} {args.endpoint}")
        monitor.measure_endpoint(
            endpoint=args.endpoint,
            method=args.method,
            data=data,
            num_requests=args.requests,
            delay=args.delay
        )
        
        # Generate report
        report = monitor.generate_report(args.output)
        
        # Summary to console
        endpoint_key = f"{args.method} {args.endpoint}"
        metrics = monitor.results[endpoint_key]
        
        print("\n== Performance Test Results ==")
        print(f"Endpoint: {endpoint_key}")
        print(f"Sample size: {metrics['sample_size']} requests")
        print(f"Mean response time: {metrics['response_time']['mean']:.3f} seconds")
        print(f"95th percentile: {metrics['response_time']['p95']:.3f} seconds")
        print(f"Success rate: {metrics['success_rate'] * 100:.1f}%")
        print(f"Performance rating: {metrics['performance_rating']}")
        
        # Compare with baseline if available
        comparison = monitor.compare_with_baseline(endpoint_key)
        if "error" not in comparison:
            change_mean = comparison["changes_percentage"]["mean"]
            change_direction = "slower" if change_mean > 0 else "faster"
            print(f"\nBaseline comparison: {abs(change_mean):.1f}% {change_direction} than baseline")
            
            if comparison["regression_detected"]:
                print("⚠️ PERFORMANCE REGRESSION DETECTED")
        
        # Generate plot if requested
        if args.plot:
            monitor.plot_history(endpoint_key, args.plot)
            print(f"\nPerformance history plot saved to {args.plot}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Performance monitoring failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 