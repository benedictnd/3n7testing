"""
Test Data Generator for API Report

Utility to generate sample test data for the API report generator.
"""

import json
import random
import datetime
from pathlib import Path
from typing import Dict, List, Any

def generate_test_results() -> Dict[str, Any]:
    """Generate sample test results data"""
    total_tests = random.randint(80, 120)
    passed = random.randint(int(total_tests * 0.7), total_tests)
    failed = total_tests - passed
    
    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": round((passed / total_tests) * 100, 1),
        "environment": random.choice(["development", "staging", "production"]),
        "api_version": f"1.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "duration": random.randint(20, 120),
        "covered_endpoints": random.randint(25, 35),
        "total_endpoints": 35,
        "status_distribution": {
            "200": random.randint(70, 90),
            "201": random.randint(5, 10),
            "400": random.randint(3, 8),
            "401": random.randint(1, 5),
            "404": random.randint(1, 3),
            "500": random.randint(0, 3)
        },
        "validation_errors": random.randint(3, 8),
        "server_errors": random.randint(0, 3),
        "network_errors": random.randint(0, 2)
    }

def generate_performance_data() -> Dict[str, Any]:
    """Generate sample performance data"""
    # Generate random response times between 50-500ms with occasional spikes
    response_times = []
    for _ in range(random.randint(20, 30)):
        # 10% chance of a spike
        if random.random() < 0.1:
            response_times.append(random.randint(400, 800))
        else:
            response_times.append(random.randint(50, 300))
    
    # Sort response times for percentile calculations
    sorted_times = sorted(response_times)
    total = len(sorted_times)
    
    return {
        "response_times": response_times,
        "avg_response_time": round(sum(response_times) / len(response_times)),
        "requests_per_second": round(random.uniform(10.5, 30.5), 1),
        "p50": sorted_times[int(total * 0.5)],
        "p90": sorted_times[int(total * 0.9)],
        "p95": sorted_times[int(total * 0.95)],
        "p99": sorted_times[int(total * 0.99)]
    }

def generate_security_findings() -> Dict[str, Any]:
    """Generate sample security test findings"""
    vuln_count = random.randint(0, 5)
    vulnerabilities = []
    
    vuln_types = [
        "SQL Injection", "XSS", "CSRF", "Open Redirect", 
        "Information Disclosure", "Insecure Cookies"
    ]
    
    for _ in range(vuln_count):
        vulnerabilities.append({
            "type": random.choice(vuln_types),
            "severity": random.choice(["Low", "Medium", "High"]),
            "location": f"/api/{random.choice(['users', 'auth', 'products', 'orders'])}",
            "description": "Potential security issue detected"
        })
    
    return {
        "vulnerabilities": vulnerabilities,
        "issues": vulnerabilities,  # Duplicate key for compatibility
        "csp_implemented": random.choice([True, False]),
        "hsts_implemented": random.choice([True, False]),
        "x_content_type_implemented": True,  # Usually implemented
        "owasp_coverage": random.randint(70, 100)
    }

def generate_flaky_tests() -> Dict[str, Any]:
    """Generate sample flaky test data"""
    flaky_count = random.randint(1, 8)
    flaky_tests = []
    test_details = {}
    
    test_names = [
        "test_auth_login", "test_user_profile", "test_order_creation",
        "test_product_search", "test_payment_processing", "test_file_upload",
        "test_notification_sending", "test_rate_limiting", "test_cache_invalidation",
        "test_data_export"
    ]
    
    # Randomly select some tests to be flaky
    selected_tests = random.sample(test_names, flaky_count)
    
    for test_name in selected_tests:
        flaky_score = round(random.uniform(0.1, 0.9), 2)
        flaky_tests.append(test_name)
        test_details[test_name] = {
            "name": test_name,
            "flakiness_score": flaky_score,
            "failures": random.randint(1, 10),
            "total_runs": random.randint(10, 20),
            "last_failed": (datetime.datetime.now() - 
                           datetime.timedelta(hours=random.randint(1, 72))).isoformat()
        }
    
    return {
        "flaky_tests": flaky_tests,
        "test_details": test_details,
        "retry_stats": {
            "total_retries": random.randint(flaky_count, flaky_count * 3),
            "successful_retries": random.randint(1, flaky_count * 2),
            "avg_retries_per_test": round(random.uniform(1.1, 2.5), 1)
        }
    }

def generate_all_data(output_dir: str = "test-data"):
    """Generate all sample data files and save to JSON"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Generate all data types
    test_results = generate_test_results()
    performance_data = generate_performance_data()
    security_findings = generate_security_findings()
    flaky_tests = generate_flaky_tests()
    
    # Save to JSON files
    with open(output_path / "test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    with open(output_path / "performance_metrics.json", "w") as f:
        json.dump(performance_data, f, indent=2)
    
    with open(output_path / "security_scan.json", "w") as f:
        json.dump(security_findings, f, indent=2)
    
    with open(output_path / "flaky_tests.json", "w") as f:
        json.dump(flaky_tests, f, indent=2)
    
    print(f"Generated sample data files in '{output_dir}' directory")
    return {
        "test_results": test_results,
        "performance_data": performance_data,
        "security_findings": security_findings,
        "flaky_tests": flaky_tests
    }

if __name__ == "__main__":
    generate_all_data() 