# Integrated Training System - Mock Test

## Overview

This project contains a mock implementation of an Integrated Training System for basketball teams, with comprehensive testing to validate the functionality. The example data is based on the Jaya Jakarta Basketball team.

## Structure

The project is organized into the following components:

### Models

- `Team`: Represents a basketball team with coaches and athletes
- `Coach`: Represents a coaching staff member
- `Athlete`: Represents a basketball player with positions
- `TrainingSession`: Represents a training session with activities and feedback
- `TrainingActivity`: Represents a specific activity during a training session
- `Feedback`: Contains ratings and notes for a training session
- `Attendance`: Tracks athlete attendance at training sessions

### Services

- `TeamService`: Manages team, coach, and athlete data
- `TrainingService`: Manages training sessions and activities
- `FeedbackService`: Manages feedback for training sessions
- `AttendanceService`: Tracks and reports on athlete attendance

### Tests

- `test_integrated_training_system.py`: Comprehensive tests for the training system using mock data for Jaya Jakarta Basketball

## Test Coverage

The mock tests cover the following aspects of the system:

1. **Team Composition**: Validates coach and athlete data, including positions
2. **Training Schedule**: Tests the training schedule for specific time periods
3. **Coach Attendance**: Verifies which coaches attended which sessions
4. **Athlete Attendance**: Tests tracking of athlete attendance, including absences
5. **Training Ratings**: Validates recording and retrieval of training ratings
6. **Athlete Issues**: Tests tracking of issues like injuries and soreness
7. **Position Updates**: Validates recording of athlete position changes
8. **Training Activities**: Tests duration and content of training activities
9. **Reporting**: Tests generation of weekly training reports and statistics

## Sample Data

The system is pre-loaded with mock data for the Jaya Jakarta Basketball team, including:

- 4 coaches with different roles
- 11 athletes with various positions
- 10 training sessions for January Week 1
- Detailed attendance records for all sessions
- Comprehensive feedback and notes for each session

## Running the Tests

To run the tests, execute the following command:

```
python -m pytest tests/test_integrated_training_system.py -v
```

## Adding Real Implementation

This project currently uses mock services with predefined data. To implement a real system:

1. Replace the mock services with actual database-backed implementations
2. Implement the database models and migrations
3. Create API endpoints for interacting with the system
4. Develop a frontend user interface
5. Add authentication and authorization

The tests can then be updated to use the real services instead of mocks, while maintaining the same functionality. 