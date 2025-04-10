#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test execution script with timeout monitoring and process tracking
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import threading
import time
import psutil
from datetime import datetime

# Configure logging
log_format = '[%(asctime)s] [%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

# If debug mode is enabled via environment variable, set logging to DEBUG
if os.environ.get('DEBUG_LOGGING', '').lower() in ('debug', '1', 'true', 'yes'):
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled")

class ProcessMonitor:
    """Monitor processes and network connections during test execution."""
    
    def __init__(self, interval=5):
        """Initialize the process monitor.
        
        Args:
            interval (int): Monitoring interval in seconds
        """
        self.interval = interval
        self.running = False
        self.monitor_thread = None
        self.start_time = None
        self.python_processes_before = {}
        self.network_connections_before = set()

    def _get_python_processes(self):
        """Get all running Python processes."""
        python_processes = {}
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes[proc.pid] = {
                        'create_time': proc.info['create_time'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return python_processes

    def _get_network_connections(self):
        """Get all active network connections."""
        connections = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                connections.add(f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip if conn.raddr else 'None'}:{conn.raddr.port if conn.raddr else 'None'}")
        return connections

    def start(self):
        """Start the process monitor."""
        self.running = True
        self.start_time = time.time()
        
        # Get initial state
        self.python_processes_before = self._get_python_processes()
        self.network_connections_before = self._get_network_connections()
        
        logger.debug(f"Initial Python processes: {len(self.python_processes_before)}")
        logger.debug(f"Initial network connections: {len(self.network_connections_before)}")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        last_log_time = time.time()
        
        while self.running:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # Every interval seconds, log system state
            if current_time - last_log_time >= self.interval:
                python_processes = self._get_python_processes()
                network_connections = self._get_network_connections()
                
                logger.debug(f"[MONITOR] Elapsed time: {elapsed:.2f}s")
                logger.debug(f"[MONITOR] Active Python processes: {len(python_processes)}")
                logger.debug(f"[MONITOR] Active network connections: {len(network_connections)}")
                
                # Check for new Python processes since start
                for pid, info in python_processes.items():
                    if pid not in self.python_processes_before and info['create_time'] > self.start_time:
                        logger.info(f"[MONITOR] New Python process detected: PID={pid}, CMD={info['cmdline']}")
                
                # Check for new network connections
                current_connections = network_connections - self.network_connections_before
                if current_connections:
                    logger.info(f"[MONITOR] New network connections detected: {len(current_connections)}")
                    for conn in current_connections:
                        logger.debug(f"[MONITOR] New connection: {conn}")
                
                last_log_time = current_time
            
            time.sleep(0.5)  # Check frequently but don't hog CPU
    
    def stop(self):
        """Stop the process monitor and generate report."""
        if not self.running:
            return
            
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        # Get final state for reporting
        end_time = time.time()
        elapsed = end_time - self.start_time
        python_processes_after = self._get_python_processes()
        network_connections_after = self._get_network_connections()
        
        # Generate report
        logger.info(f"===== Process Monitor Report =====")
        logger.info(f"Total execution time: {elapsed:.2f} seconds")
        
        # Look for potentially hanging processes
        new_processes = {}
        for pid, info in python_processes_after.items():
            if pid not in self.python_processes_before and info['create_time'] > self.start_time:
                new_processes[pid] = info
        
        if new_processes:
            logger.info(f"Potential hanging processes: {len(new_processes)}")
            for pid, info in new_processes.items():
                logger.info(f"  - PID: {pid}, Command: {info['cmdline']}")
        
        # Check for potentially leaked connections
        new_connections = network_connections_after - self.network_connections_before
        if new_connections:
            logger.info(f"Potential leaked network connections: {len(new_connections)}")
            for conn in new_connections:
                logger.info(f"  - {conn}")
        
        logger.info(f"==================================")


def run_test_with_timeout(test_file, timeout, debug=False):
    """
    Run the specified test file with monitoring and timeout.
    
    Args:
        test_file (str): Path to the test file to run
        timeout (int): Timeout in seconds
        debug (bool): If True, enable debug mode
    
    Returns:
        int: Exit code of the test process
    """
    # Set up environment variables
    env = os.environ.copy()
    if debug:
        env['DEBUG_MODE'] = '1'
        env['DEBUG_TIMEOUT'] = '1'
        env['DEBUG_NETWORK'] = '1'
        env['DEBUG_LOGGING'] = 'debug'
    
    # Start the process monitor
    monitor = ProcessMonitor(interval=10)
    monitor.start()
    
    logger.info(f"Starting test: {test_file}")
    logger.info(f"Timeout set to {timeout} seconds")
    
    # Start the test process
    start_time = time.time()
    process = None
    try:
        # Run the test with Python and capture output
        process = subprocess.Popen(
            [sys.executable, test_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            universal_newlines=True
        )
        
        # Monitor the process and implement timeout
        stdout_data = ""
        stderr_data = ""
        exit_code = None
        
        # Use communicate with timeout to handle both output capture and timeouts
        try:
            stdout_data, stderr_data = process.communicate(timeout=timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"Test execution timed out after {timeout} seconds!")
            
            # Try to get more information about what the process is doing
            try:
                p = psutil.Process(process.pid)
                logger.error(f"Process status: {p.status()}")
                logger.error(f"CPU usage: {p.cpu_percent(interval=1.0)}%")
                logger.error(f"Memory usage: {p.memory_info().rss / (1024 * 1024):.2f} MB")
                
                # Check for child processes
                children = p.children(recursive=True)
                if children:
                    logger.error(f"Child processes: {len(children)}")
                    for child in children:
                        logger.error(f"  - PID: {child.pid}, Name: {child.name()}")
                
                # Get open files
                open_files = p.open_files()
                if open_files:
                    logger.error(f"Open files:")
                    for file in open_files:
                        logger.error(f"  - {file.path}")
                
                # Get network connections
                connections = p.connections()
                if connections:
                    logger.error(f"Network connections:")
                    for conn in connections:
                        logger.error(f"  - {conn.laddr} -> {conn.raddr if conn.raddr else 'None'} ({conn.status})")
            except:
                logger.exception("Failed to get additional process information")
            
            # Kill the process and all children
            logger.warning("Terminating test process due to timeout")
            for child in psutil.Process(process.pid).children(recursive=True):
                child.terminate()
            process.terminate()
            
            try:
                # Wait for process to terminate
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate gracefully. Killing...")
                process.kill()
            
            exit_code = -1  # Timeout exit code
        
        # Process output
        if stdout_data:
            logger.info("Test output:")
            for line in stdout_data.splitlines():
                logger.info(f"  {line}")
        
        if stderr_data:
            logger.warning("Test errors:")
            for line in stderr_data.splitlines():
                logger.warning(f"  {line}")
        
        end_time = time.time()
        logger.info(f"Test completed in {end_time - start_time:.2f} seconds with exit code: {exit_code}")
        
        return exit_code
    
    except KeyboardInterrupt:
        logger.warning("Test execution interrupted by user")
        if process and process.poll() is None:
            process.terminate()
        return 130  # Standard exit code for interrupt
    
    except Exception as e:
        logger.exception(f"Error running test: {e}")
        return 1
    
    finally:
        # Stop the process monitor
        monitor.stop()
        
        # Make sure the process is terminated
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run tests with timeout and monitoring')
    parser.add_argument('--test_file', required=True, help='Path to the test file to run')
    parser.add_argument('--timeout', type=int, default=180, help='Timeout in seconds (default: 180)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Validate test file
    if not os.path.isfile(args.test_file):
        logger.error(f"Test file not found: {args.test_file}")
        return 1
    
    # Run the test with timeout
    exit_code = run_test_with_timeout(args.test_file, args.timeout, args.debug)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 