#!/usr/bin/env python3
"""
GitHub File Auditing and Backup Tool

This script performs the following tasks:
1. Scans GitHub repositories and generates a URL inventory
2. Cross-references local files with GitHub repositories
3. Creates backups of local-only files

Requirements:
- PyGithub: pip install PyGithub
- gitpython: pip install gitpython
"""

import os
import sys
import csv
import shutil
import logging
import datetime
import argparse
import time
from typing import List, Dict, Set, Tuple, Optional
import subprocess
import re

try:
    from github import Github, Repository, GithubException
    import git
except ImportError:
    print("Required packages not found. Please install using:")
    print("pip install PyGithub gitpython")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("github_audit_backup")

# File extensions to skip during backup
BINARY_EXTENSIONS = {
    ".zip", ".exe", ".dll", ".so", ".dylib", ".jar", ".war", ".ear", ".rar", ".tar", 
    ".gz", ".7z", ".iso", ".img", ".bin", ".dat", ".db", ".sqlite", ".pyc", ".pyo", 
    ".o", ".obj", ".class", ".pkl", ".pyd", ".msi", ".dmg"
}

class GitHubAuditBackup:
    """
    Main class for GitHub file auditing and backup operations
    """
    def __init__(self, github_token: str, local_root_dir: str, output_dir: Optional[str] = None):
        """
        Initialize with GitHub token and local root directory
        
        Args:
            github_token: GitHub personal access token
            local_root_dir: Root directory to scan for local files
            output_dir: Directory for outputs (default: local_root_dir)
        """
        self.github_token = github_token
        self.local_root_dir = os.path.abspath(local_root_dir)
        self.output_dir = os.path.abspath(output_dir) if output_dir else self.local_root_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize GitHub API client
        self.github_client = Github(github_token)
        
        # Current timestamp for naming backup folders
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_folder_name = f"Backup_Folder_{self.timestamp}"
        self.backup_folder_path = os.path.join(self.output_dir, self.backup_folder_name)
        
        # Create backup folder
        os.makedirs(self.backup_folder_path, exist_ok=True)
        
        # Setup output file paths
        self.inventory_csv_path = os.path.join(self.output_dir, "GitHub_URL_Inventory.csv")
        self.backup_log_path = os.path.join(self.backup_folder_path, "backup_log.txt")
        self.error_log_path = os.path.join(self.output_dir, "github_audit_error.log")
        
        # Initialize backup log file
        with open(self.backup_log_path, 'w') as f:
            f.write("File Path | Backup Status | Timestamp\n")
            f.write("-" * 80 + "\n")
        
        # Initialize the error log file
        with open(self.error_log_path, 'w') as f:
            f.write(f"GitHub Audit and Backup Error Log - {self.timestamp}\n")
            f.write("=" * 80 + "\n")
        
    def log_error(self, message: str) -> None:
        """
        Log error to the error log file
        
        Args:
            message: Error message to log
        """
        logger.error(message)
        with open(self.error_log_path, 'a') as f:
            f.write(f"{datetime.datetime.now().isoformat()} - {message}\n")
    
    def log_backup(self, file_path: str, status: str) -> None:
        """
        Log backup status to the backup log file
        
        Args:
            file_path: Path of the file being backed up
            status: Status of the backup operation (success/failed)
        """
        timestamp = datetime.datetime.now().isoformat()
        with open(self.backup_log_path, 'a') as f:
            f.write(f"{file_path} | {status} | {timestamp}\n")
    
    def scan_github_repositories(self) -> List[Repository.Repository]:
        """
        Scan all GitHub repositories under the authenticated user
        
        Returns:
            List of GitHub repository objects
        """
        logger.info("Scanning GitHub repositories...")
        
        try:
            user = self.github_client.get_user()
            repositories = list(user.get_repos())
            logger.info(f"Found {len(repositories)} repositories")
            return repositories
        except GithubException as e:
            error_msg = f"Failed to scan GitHub repositories: {str(e)}"
            self.log_error(error_msg)
            raise Exception(error_msg)
    
    def generate_url_inventory(self, repositories: List[Repository.Repository]) -> None:
        """
        Generate inventory of all URLs associated with GitHub repositories
        
        Args:
            repositories: List of GitHub repository objects
        """
        logger.info("Generating URL inventory...")
        
        with open(self.inventory_csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Repo Name', 'URL Type', 'URL', 'Last Updated']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for repo in repositories:
                repo_name = repo.name
                last_updated = repo.updated_at.isoformat()
                
                # Repository URL
                writer.writerow({
                    'Repo Name': repo_name,
                    'URL Type': 'Repository',
                    'URL': repo.html_url,
                    'Last Updated': last_updated
                })
                
                try:
                    # Get all files in the repository (default branch)
                    contents = repo.get_contents("")
                    while contents:
                        file_content = contents.pop(0)
                        if file_content.type == "dir":
                            contents.extend(repo.get_contents(file_content.path))
                        else:
                            writer.writerow({
                                'Repo Name': repo_name,
                                'URL Type': 'Raw Content',
                                'URL': file_content.download_url,
                                'Last Updated': last_updated
                            })
                    
                    # Pull Request URLs
                    for pr in repo.get_pulls(state='all')[:10]:  # Limit to recent 10 PRs to avoid rate limits
                        writer.writerow({
                            'Repo Name': repo_name,
                            'URL Type': 'Pull Request',
                            'URL': pr.html_url,
                            'Last Updated': pr.updated_at.isoformat()
                        })
                    
                    # Issue URLs
                    for issue in repo.get_issues(state='all')[:10]:  # Limit to recent 10 issues
                        writer.writerow({
                            'Repo Name': repo_name,
                            'URL Type': 'Issue',
                            'URL': issue.html_url,
                            'Last Updated': issue.updated_at.isoformat()
                        })
                        
                except GithubException as e:
                    self.log_error(f"Error processing repo {repo_name}: {str(e)}")
                    continue
        
        logger.info(f"URL inventory generated: {self.inventory_csv_path}")
    
    def get_git_repositories(self) -> Dict[str, str]:
        """
        Find all Git repositories in the local directory
        
        Returns:
            Dictionary mapping repository paths to their remote URLs
        """
        logger.info(f"Scanning for Git repositories in {self.local_root_dir}...")
        
        git_repos = {}
        for root, dirs, files in os.walk(self.local_root_dir):
            if '.git' in dirs:
                repo_path = root
                try:
                    # Try to get the remote URL
                    repo = git.Repo(repo_path)
                    for remote in repo.remotes:
                        for url in remote.urls:
                            if 'github.com' in url:
                                git_repos[repo_path] = url
                                break
                        if repo_path in git_repos:
                            break
                except git.InvalidGitRepositoryError:
                    continue
                except git.GitCommandError as e:
                    self.log_error(f"Git command error in {repo_path}: {str(e)}")
                    continue
        
        logger.info(f"Found {len(git_repos)} Git repositories")
        return git_repos
    
    def get_files_in_repo(self, repo_path: str) -> Set[str]:
        """
        Get all tracked files in a Git repository
        
        Args:
            repo_path: Path to the Git repository
            
        Returns:
            Set of absolute paths to tracked files
        """
        try:
            repo = git.Repo(repo_path)
            tracked_files = set()
            
            try:
                # Get list of tracked files using git command
                tracked_output = repo.git.ls_files().splitlines()
                for rel_path in tracked_output:
                    abs_path = os.path.abspath(os.path.join(repo_path, rel_path))
                    tracked_files.add(abs_path)
            except git.GitCommandError:
                self.log_error(f"Error listing tracked files in {repo_path}")
            
            return tracked_files
        except git.InvalidGitRepositoryError:
            self.log_error(f"Invalid Git repository: {repo_path}")
            return set()
        except Exception as e:
            self.log_error(f"Error processing repository {repo_path}: {str(e)}")
            return set()
    
    def get_all_local_files(self) -> Set[str]:
        """
        Get all files in the local directory
        
        Returns:
            Set of absolute paths to all files
        """
        logger.info(f"Scanning all files in {self.local_root_dir}...")
        
        all_files = set()
        excluded_dirs = {
            '.git', 'node_modules', 'venv', '.venv', '__pycache__', 
            '.idea', '.vscode', 'build', 'dist', 'target'
        }
        
        for root, dirs, files in os.walk(self.local_root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                all_files.add(file_path)
        
        logger.info(f"Found {len(all_files)} local files")
        return all_files
    
    def identify_local_only_files(self) -> Set[str]:
        """
        Identify files that exist locally but not in any GitHub repository
        
        Returns:
            Set of absolute paths to local-only files
        """
        logger.info("Identifying local-only files...")
        
        # Get all files in the local directory
        all_local_files = self.get_all_local_files()
        
        # Get all files tracked in Git repositories
        git_repos = self.get_git_repositories()
        tracked_files = set()
        
        for repo_path in git_repos:
            repo_tracked_files = self.get_files_in_repo(repo_path)
            tracked_files.update(repo_tracked_files)
        
        # Files that exist locally but are not tracked in any Git repository
        local_only_files = all_local_files - tracked_files
        
        # Filter out binary files
        filtered_local_only_files = set()
        for file_path in local_only_files:
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in BINARY_EXTENSIONS:
                filtered_local_only_files.add(file_path)
        
        logger.info(f"Found {len(filtered_local_only_files)} local-only files (excluding binaries)")
        return filtered_local_only_files
    
    def backup_local_only_files(self, local_only_files: Set[str]) -> None:
        """
        Backup local-only files to the backup folder
        
        Args:
            local_only_files: Set of absolute paths to local-only files
        """
        logger.info(f"Backing up {len(local_only_files)} local-only files...")
        
        backup_count = 0
        error_count = 0
        
        for file_path in local_only_files:
            try:
                # Determine the relative path from the local root
                rel_path = os.path.relpath(file_path, self.local_root_dir)
                
                # Create the destination path in the backup folder
                dest_path = os.path.join(self.backup_folder_path, rel_path)
                
                # Create the directory structure
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy the file
                shutil.copy2(file_path, dest_path)
                
                # Log the successful backup
                self.log_backup(rel_path, "Success")
                backup_count += 1
                
            except Exception as e:
                # Log the failed backup
                self.log_backup(file_path, f"Failed: {str(e)}")
                self.log_error(f"Failed to backup {file_path}: {str(e)}")
                error_count += 1
        
        logger.info(f"Backup completed: {backup_count} files backed up, {error_count} errors")
        logger.info(f"Backup folder: {self.backup_folder_path}")
        logger.info(f"Backup log: {self.backup_log_path}")
    
    def run(self) -> None:
        """
        Run the full GitHub audit and backup process
        """
        logger.info("Starting GitHub audit and backup process...")
        
        try:
            # Step 1: Scan GitHub repositories and generate URL inventory
            repositories = self.scan_github_repositories()
            self.generate_url_inventory(repositories)
            
            # Step 2: Identify local-only files
            local_only_files = self.identify_local_only_files()
            
            # Step 3: Backup local-only files
            self.backup_local_only_files(local_only_files)
            
            logger.info("GitHub audit and backup process completed successfully")
            
        except Exception as e:
            error_msg = f"GitHub audit and backup process failed: {str(e)}"
            self.log_error(error_msg)
            logger.error(error_msg)
            raise

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="GitHub File Auditing and Backup Tool")
    
    parser.add_argument(
        "--token", "-t",
        required=True,
        help="GitHub personal access token"
    )
    parser.add_argument(
        "--local-dir", "-l",
        required=True,
        help="Local root directory to scan"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for reports and backups (default: local root directory)"
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    try:
        audit_backup = GitHubAuditBackup(
            github_token=args.token,
            local_root_dir=args.local_dir,
            output_dir=args.output_dir
        )
        audit_backup.run()
        print("\nGitHub audit and backup completed successfully!")
        print(f"URL inventory: {audit_backup.inventory_csv_path}")
        print(f"Backup folder: {audit_backup.backup_folder_path}")
        print(f"Backup log: {audit_backup.backup_log_path}")
        print(f"Error log: {audit_backup.error_log_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
