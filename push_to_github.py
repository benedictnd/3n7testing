#!/usr/bin/env python3
"""
GitHub Push Utility

This script automates the process of pushing changes to GitHub, handling file staging,
committing with meaningful messages, and pushing to the appropriate branch.
It can be run from any directory within the repository.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

def run_command(command, capture_output=True):
    """
    Run a shell command and return its output
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=capture_output
        )
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error details: {str(e)}")
        if capture_output and e.stdout:
            print(f"Command output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def get_current_branch():
    """
    Get the name of the current git branch
    """
    return run_command("git branch --show-current")

def get_modified_files():
    """
    Get a list of modified files in the repository
    """
    status_output = run_command("git status --porcelain")
    if not status_output:
        return []
    
    files = []
    for line in status_output.split('\n'):
        if line.strip():
            # Extract file status and name
            status = line[:2].strip()
            file_name = line[3:].strip()
            files.append((status, file_name))
    
    return files

def stage_files(files_to_stage=None):
    """
    Stage files for commit
    """
    if files_to_stage:
        for file_path in files_to_stage:
            run_command(f'git add "{file_path}"')
        print(f"Staged {len(files_to_stage)} files")
    else:
        run_command("git add .")
        print("Staged all modified files")
    
    return True

def commit_changes(message):
    """
    Commit staged changes with the provided message
    """
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Update codebase - {timestamp}"
    
    result = run_command(f'git commit -m "{message}"')
    if result:
        print(f"Committed changes with message: {message}")
        return True
    return False

def push_to_remote(branch=None, force=False):
    """
    Push changes to the remote repository
    """
    command = "git push"
    
    if branch:
        command += f" origin {branch}"
    
    if force:
        command += " --force"
    
    result = run_command(command, capture_output=False)
    if result:
        pushed_branch = branch or get_current_branch()
        print(f"Successfully pushed to {pushed_branch}")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Push changes to GitHub")
    parser.add_argument("--message", "-m", help="Commit message")
    parser.add_argument("--files", "-f", nargs="+", help="Specific files to stage")
    parser.add_argument("--branch", "-b", help="Branch to push to")
    parser.add_argument("--force", action="store_true", help="Force push")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually doing it")
    
    args = parser.parse_args()
    
    # Get current branch
    current_branch = get_current_branch()
    print(f"Current branch: {current_branch}")
    
    # Get modified files
    modified_files = get_modified_files()
    
    if not modified_files:
        print("No changes to commit")
        return
    
    print("Modified files:")
    for status, file_name in modified_files:
        print(f"  {status} {file_name}")
    
    if args.dry_run:
        print("\nDRY RUN - No changes were made")
        return
    
    # Stage files
    stage_files(args.files)
    
    # Commit changes
    if not commit_changes(args.message):
        print("Failed to commit changes")
        return
    
    # Push to remote
    target_branch = args.branch or current_branch
    if push_to_remote(target_branch, args.force):
        print(f"\nSuccessfully pushed changes to {target_branch}")
    else:
        print(f"\nFailed to push changes to {target_branch}")

if __name__ == "__main__":
    main() 