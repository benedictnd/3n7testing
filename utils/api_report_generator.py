import os
import json
import logging
import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import webbrowser

class APIReportGenerator:
    """
    Generates interactive HTML reports with visualizations for API test results
    """
    
    def __init__(self, input_file=None, report_data=None):
        """Initialize the report generator with either an input file or report data"""
        self.logger = logging.getLogger('api_report_generator')
        
        # Initialize instance variables
        self.output_dir = 'reports'
        self.template_dir = os.path.join('utils', 'templates')
        self.template_file = 'api_report_template.html'
        self.input_file = input_file
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize with empty data structure
        self.report_data = {
            'metadata': {
                'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'environment': 'Production',
                'api_version': 'v1.0'
            },
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'security_issues': 0
            },
            'charts': {
                'success_rates': {
                    'labels': ['Passed', 'Failed'],
                    'data': [0, 0]
                },
                'performance_trend': {
                    'labels': [],
                    'data': []
                },
                'failure_breakdown': {
                    'labels': [],
                    'data': []
                }
            },
            'analogies': {
                'overall': '',
                'success_rate': '',
                'performance': '',
                'security': ''
            },
            'visual_summary': {
                'success': {'emoji': '🏆', 'value': '', 'color': ''},
                'performance': {'emoji': '⚡', 'value': '', 'color': ''},
                'security': {'emoji': '🔒', 'value': '', 'color': ''},
                'reliability': {'emoji': '📶', 'value': '', 'color': ''}
            },
            'action_items': [],
            'slow_tests': []
        }
        
        # Load data from input file if provided
        if input_file and os.path.exists(input_file):
            self.load_data_from_file(input_file)
        elif report_data:
            self.report_data.update(report_data)
    
    def load_data_from_file(self, input_file):
        """Load test results data from a JSON file"""
        try:
            with open(input_file, 'r') as f:
                raw_data = json.load(f)
            
            self.logger.info(f"Loaded data from {input_file}")
            self.process_input_data(raw_data)
        except Exception as e:
            self.logger.error(f"Error loading data from {input_file}: {str(e)}")
            raise
    
    def process_input_data(self, raw_data):
        """Process input data and convert it to the format needed for report generation"""
        # Update metadata
        if 'metadata' in raw_data:
            self.report_data['metadata'].update(raw_data['metadata'])
        else:
            # Use timestamp from file if available
            self.report_data['metadata']['generated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Process test results
        if 'test_results' in raw_data:
            results = raw_data['test_results']
            
            # Calculate summary statistics
            total_tests = len(results)
            passed_tests = sum(1 for test in results if test.get('status') == 'pass')
            failed_tests = total_tests - passed_tests
            
            # Calculate success rate
            success_rate = round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0
            
            # Calculate average response time
            response_times = [test.get('response_time', 0) for test in results if test.get('response_time')]
            avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
            
            # Count security issues
            security_issues = sum(1 for test in results if test.get('category') == 'security' and test.get('status') == 'fail')
            
            # Update summary
            self.report_data['summary'] = {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'security_issues': security_issues
            }
            
            # Update chart data for success rates
            self.report_data['charts']['success_rates']['data'] = [passed_tests, failed_tests]
            
            # Update performance trend data
            if response_times:
                # Take latest 10 test response times for trend
                latest_tests = sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
                self.report_data['charts']['performance_trend']['labels'] = [
                    f"Test {i+1}" for i in range(len(latest_tests))
                ]
                self.report_data['charts']['performance_trend']['data'] = [
                    test.get('response_time', 0) for test in latest_tests
                ]
            
            # Update failure breakdown
            failure_categories = {}
            for test in results:
                if test.get('status') == 'fail':
                    category = test.get('category', 'Unknown')
                    failure_categories[category] = failure_categories.get(category, 0) + 1
            
            self.report_data['charts']['failure_breakdown']['labels'] = list(failure_categories.keys())
            self.report_data['charts']['failure_breakdown']['data'] = list(failure_categories.values())
            
            # Generate enhanced communication features
            self.generate_analogies()
            self.generate_visual_summary()
            self.generate_action_items(results)
            self.identify_slow_tests(results)
    
    def generate_analogies(self):
        """Generate helpful analogies based on test results"""
        summary = self.report_data['summary']
        
        # Success rate analogy
        success_rate = summary['success_rate']
        if success_rate >= 90:
            analogy = f"Your API is like an A-grade student, scoring {success_rate}% on its tests. It's performing excellently!"
        elif success_rate >= 75:
            analogy = f"With a {success_rate}% success rate, your API is like a solid B student - doing well but has room to improve."
        elif success_rate >= 60:
            analogy = f"At {success_rate}%, your API is like a C student - passing, but needs significant improvement."
        else:
            analogy = f"With only {success_rate}% passing tests, your API needs immediate attention - it's like a struggling student."
        
        self.report_data['analogies']['success_rate'] = analogy
        
        # Performance analogy
        avg_time = summary['avg_response_time']
        if avg_time <= 100:
            analogy = f"Your API responds in {avg_time}ms on average - as quick as a Formula 1 pit stop!"
        elif avg_time <= 250:
            analogy = f"With an average response time of {avg_time}ms, your API is like a quick coffee order - fast enough for most."
        elif avg_time <= 500:
            analogy = f"Your API takes {avg_time}ms on average - like waiting for a microwave meal to heat up."
        else:
            analogy = f"At {avg_time}ms average response time, your API is slow like waiting for water to boil. Time to optimize!"
        
        self.report_data['analogies']['performance'] = analogy
        
        # Security analogy
        security_issues = summary['security_issues']
        if security_issues == 0:
            analogy = "Your API security is like a bank vault - no issues detected!"
        elif security_issues <= 2:
            analogy = f"With {security_issues} security issues, your API is like a house with a few windows unlocked. Fix them soon."
        elif security_issues <= 5:
            analogy = f"Finding {security_issues} security issues is like discovering your fence has several holes. Address these promptly."
        else:
            analogy = f"With {security_issues} security issues, your API is like leaving your front door wide open. Urgent attention needed!"
        
        self.report_data['analogies']['security'] = analogy
        
        # Overall analogy
        if success_rate >= 85 and avg_time <= 200 and security_issues <= 1:
            overall = "Your API is running like a well-maintained luxury car - smooth, fast, and secure!"
        elif success_rate >= 70 and avg_time <= 350 and security_issues <= 3:
            overall = "Your API is like a reliable family sedan - gets the job done but could use a tune-up in some areas."
        else:
            overall = "Your API is like a car that needs a trip to the mechanic - several issues require attention before it runs smoothly."
        
        self.report_data['analogies']['overall'] = overall
    
    def generate_visual_summary(self):
        """Generate visual summary with emoji indicators"""
        summary = self.report_data['summary']
        
        # Success rate indicators
        success_rate = summary['success_rate']
        if success_rate >= 90:
            self.report_data['visual_summary']['success'] = {
                'emoji': '🏆',
                'value': f"{success_rate}%",
                'color': '#2ecc71'
            }
        elif success_rate >= 75:
            self.report_data['visual_summary']['success'] = {
                'emoji': '🥈',
                'value': f"{success_rate}%",
                'color': '#3498db'
            }
        elif success_rate >= 60:
            self.report_data['visual_summary']['success'] = {
                'emoji': '🥉',
                'value': f"{success_rate}%",
                'color': '#f39c12'
            }
        else:
            self.report_data['visual_summary']['success'] = {
                'emoji': '⚠️',
                'value': f"{success_rate}%",
                'color': '#e74c3c'
            }
        
        # Performance indicators
        avg_time = summary['avg_response_time']
        if avg_time <= 100:
            self.report_data['visual_summary']['performance'] = {
                'emoji': '⚡',
                'value': f"{avg_time}ms",
                'color': '#2ecc71'
            }
        elif avg_time <= 250:
            self.report_data['visual_summary']['performance'] = {
                'emoji': '🚀',
                'value': f"{avg_time}ms",
                'color': '#3498db'
            }
        elif avg_time <= 500:
            self.report_data['visual_summary']['performance'] = {
                'emoji': '🐌',
                'value': f"{avg_time}ms",
                'color': '#f39c12'
            }
        else:
            self.report_data['visual_summary']['performance'] = {
                'emoji': '🐢',
                'value': f"{avg_time}ms",
                'color': '#e74c3c'
            }
        
        # Security indicators
        security_issues = summary['security_issues']
        if security_issues == 0:
            self.report_data['visual_summary']['security'] = {
                'emoji': '🔒',
                'value': f"{security_issues} issues",
                'color': '#2ecc71'
            }
        elif security_issues <= 2:
            self.report_data['visual_summary']['security'] = {
                'emoji': '🔓',
                'value': f"{security_issues} issues",
                'color': '#3498db'
            }
        elif security_issues <= 5:
            self.report_data['visual_summary']['security'] = {
                'emoji': '⚠️',
                'value': f"{security_issues} issues",
                'color': '#f39c12'
            }
        else:
            self.report_data['visual_summary']['security'] = {
                'emoji': '🚨',
                'value': f"{security_issues} issues",
                'color': '#e74c3c'
            }
        
        # Reliability indicators (based on network failures)
        network_failures = 0
        if 'charts' in self.report_data and 'failure_breakdown' in self.report_data['charts']:
            labels = self.report_data['charts']['failure_breakdown']['labels']
            data = self.report_data['charts']['failure_breakdown']['data']
            
            for i, label in enumerate(labels):
                if 'network' in label.lower() or 'connection' in label.lower():
                    network_failures += data[i]
        
        if network_failures == 0:
            self.report_data['visual_summary']['reliability'] = {
                'emoji': '📶',
                'value': f"{network_failures} failures",
                'color': '#2ecc71'
            }
        elif network_failures <= 2:
            self.report_data['visual_summary']['reliability'] = {
                'emoji': '📡',
                'value': f"{network_failures} failures",
                'color': '#3498db'
            }
        elif network_failures <= 4:
            self.report_data['visual_summary']['reliability'] = {
                'emoji': '📉',
                'value': f"{network_failures} failures",
                'color': '#f39c12'
            }
        else:
            self.report_data['visual_summary']['reliability'] = {
                'emoji': '🔌',
                'value': f"{network_failures} failures",
                'color': '#e74c3c'
            }
    
    def generate_action_items(self, test_results):
        """Generate prioritized action items based on test results"""
        # Count issues by type
        validation_errors = 0
        server_errors = 0
        network_issues = 0
        security_findings = 0
        endpoints_with_issues = set()
        
        for test in test_results:
            if test.get('status') == 'fail':
                test_number = test.get('test_number', '')
                endpoints_with_issues.add(test_number)
                
                # Categorize the failure
                error_type = test.get('error_type', '').lower()
                category = test.get('category', '').lower()
                
                if 'validation' in error_type or 'schema' in error_type:
                    validation_errors += 1
                elif 'server' in error_type or '5' in error_type:
                    server_errors += 1
                elif 'network' in error_type or 'connection' in error_type or 'timeout' in error_type:
                    network_issues += 1
                
                if 'security' in category:
                    security_findings += 1
        
        # Generate action items in priority order
        action_items = []
        
        # Validation errors (priority 1)
        if validation_errors > 0:
            action_items.append({
                'priority': 1,
                'icon': '🔍',
                'description': f"Fix {validation_errors} validation errors",
                'detail': "These validation failures indicate mismatches between expected and actual API responses."
            })
        
        # Server errors (priority 1)
        if server_errors > 0:
            action_items.append({
                'priority': 1,
                'icon': '🛑',
                'description': f"Investigate {server_errors} server-side errors",
                'detail': "These 5xx errors suggest server-side issues that need immediate attention."
            })
        
        # Security findings (priority 1-2 depending on count)
        if security_findings > 0:
            priority = 1 if security_findings > 3 else 2
            action_items.append({
                'priority': priority,
                'icon': '🔒',
                'description': f"Address {security_findings} security findings",
                'detail': "Security vulnerabilities could expose sensitive data or functionality."
            })
        
        # Network issues (priority 2)
        if network_issues > 0:
            action_items.append({
                'priority': 2,
                'icon': '📡',
                'description': f"Improve stability for {network_issues} network issues",
                'detail': "Network-related failures could indicate connectivity problems with dependencies."
            })
        
        # Performance optimization (priority 3)
        if self.report_data['summary']['avg_response_time'] > 300 and len(self.report_data.get('slow_tests', [])) > 0:
            action_items.append({
                'priority': 3,
                'icon': '⚡',
                'description': f"Optimize {len(self.report_data['slow_tests'])} slow endpoints",
                'detail': f"Average response time is {self.report_data['summary']['avg_response_time']}ms, which could impact user experience."
            })
        
        self.report_data['action_items'] = action_items
    
    def identify_slow_tests(self, test_results):
        """Identify the slowest tests that need optimization"""
        # Get tests with response times
        tests_with_time = [
            {
                'test_number': test.get('test_number', ''),
                'response_time': test.get('response_time', 0),
                'endpoint': test.get('endpoint', ''),
                'severity': 'high' if test.get('response_time', 0) > 500 else
                           'medium' if test.get('response_time', 0) > 300 else 'low'
            }
            for test in test_results if test.get('response_time')
        ]
        
        # Sort by response time (descending) and take top 5
        slow_tests = sorted(tests_with_time, key=lambda x: x['response_time'], reverse=True)[:5]
        self.report_data['slow_tests'] = slow_tests
    
    def generate_report(self, output_file=None):
        """Generate an HTML report using the template and data"""
        try:
            # Set default output file name if not provided
            if not output_file:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(self.output_dir, f'api_test_report_{timestamp}.html')
            
            # Load the template
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template(self.template_file)
            
            # Render the template with data
            html_content = template.render(**self.report_data)
            
            # Write to output file with UTF-8 encoding to handle emojis
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Report generated successfully: {output_file}")
            
            return output_file
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
    
    def open_in_browser(self, report_file):
        """Open the generated report in the default web browser"""
        try:
            report_path = os.path.abspath(report_file)
            webbrowser.open(f'file://{report_path}')
            self.logger.info(f"Opened report in browser: {report_path}")
        except Exception as e:
            self.logger.error(f"Error opening report in browser: {str(e)}")
            
# Command-line interface
if __name__ == '__main__':
    import argparse
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate API test report')
    parser.add_argument('--input', '-i', help='Input JSON file with test results')
    parser.add_argument('--output', '-o', help='Output HTML report file')
    parser.add_argument('--open', '-b', action='store_true', help='Open report in browser after generation')
    
    args = parser.parse_args()
    
    # Validate input file
    if args.input and not os.path.exists(args.input):
        logging.error(f"Input file does not exist: {args.input}")
        exit(1)
    
    # Generate the report
    try:
        generator = APIReportGenerator(input_file=args.input)
        report_file = generator.generate_report(args.output)
        
        if args.open:
            generator.open_in_browser(report_file)
            
        logging.info(f"Report generated successfully: {report_file}")
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        exit(1)
