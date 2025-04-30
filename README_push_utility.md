# GitHub Push Utility

A Python-based command-line utility for streamlining GitHub operations within the 3&7 Training Platform project.

## Features

- **Simplified Git Operations**: Automates common git commands with a single interface
- **File Staging**: Stage specific files or all modified files with a single command
- **Custom Commit Messages**: Easily add meaningful commit messages or use auto-generated timestamped messages
- **Branch Management**: Push to the current branch or specify a target branch
- **Dry Run Mode**: Preview changes without actually committing or pushing
- **Comprehensive Error Handling**: Clear error messages and guidance for failed operations
- **Detailed Output**: See exactly what's happening at each step of the process

## Installation

The utility is included in the project repository. No additional installation is required beyond the standard Python environment.

## Usage

### Basic Usage

```bash
python push_to_github.py
```

This will stage all modified files, create a commit with a timestamped message, and push to the current branch.

### Command-Line Options

```bash
python push_to_github.py --message "Your commit message" --files file1.py file2.js --branch feature-branch
```

### Available Options

- `--message`, `-m`: Specify a custom commit message
- `--files`, `-f`: Specify specific files to stage (space-separated)
- `--branch`, `-b`: Specify a branch to push to (defaults to current branch)
- `--force`: Force push (use with caution)
- `--dry-run`: Show what would be done without actually doing it

## Examples

### Stage and Commit Specific Files

```bash
python push_to_github.py -f src/components/Button.tsx src/styles/components.css -m "Update Button component styling"
```

### Preview Changes Before Pushing

```bash
python push_to_github.py --dry-run
```

### Push to a Different Branch

```bash
python push_to_github.py -b release-candidate -m "Prepare for v1.2.0 release"
```

### Force Push to Current Branch

```bash
python push_to_github.py --force -m "Fix history after revisions"
```

## Error Handling

The utility provides detailed error messages for common issues:

- Git command failures
- Non-existent files
- Permission issues
- Network connectivity problems
- Authentication failures

Each error includes the command that failed, the error message, and any additional output that might help diagnose the issue.

## Integration with Workflow

This utility is designed to integrate seamlessly with the 3&7 Training Platform development workflow:

1. Make code changes locally
2. Run tests to ensure changes work as expected
3. Use the push utility to stage, commit, and push changes
4. Create pull requests through GitHub's web interface or GitHub CLI

## Contributing

To enhance this utility:

1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request with a clear description of your improvements

## License

This utility is part of the 3&7 Training Platform and is subject to the same licensing terms as the main project. 