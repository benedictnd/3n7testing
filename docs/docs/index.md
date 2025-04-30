# 3&7 Training Platform Documentation

Welcome to the documentation for the 3&7 Training Platform. This documentation provides comprehensive information about the API endpoints, database schema, and other aspects of the platform.

## Table of Contents

- [API Documentation](api_documentation.md) - Detailed information about the API endpoints and how to use them
- [Database Schema](database_schema.md) - Documentation of the database structure and relationships
- [API Architecture Guidelines](api_architecture.md) - Guidelines for creating and maintaining APIs
- [Database Schema Guidelines](db_schema_guidelines.md) - Guidelines for working with database schemas

## API Endpoints Quick Reference

### Authentication
- `/api/auth/login` - Login with email and password
- `/api/auth/register` - Register a new user
- `/api/auth/refresh` - Refresh the access token
- `/api/auth/logout` - Logout and invalidate the token

### Users
- `/api/users` - Get list of all users
- `/api/users/{user_id}` - Get user details by ID

### Training Sessions
- `/api/training-sessions` - Get list of training sessions
- `/api/training-sessions/{session_id}` - Get training session details
- `/api/training-sessions/{session_id}/attendance` - Get/mark session attendance records
- `/api/training-sessions/{session_id}/self-attendance` - Mark attendance for the current athlete

### Independent Training
- `/api/independent-training` - Get list of independent training sessions
- `/api/independent-training/{session_id}` - Get independent training session details

### Reports
- `/api/reports/training` - Get training reports
- `/api/reports/attendance` - Get attendance reports
- `/api/reports/feedback` - Get feedback reports
- `/api/reports/monthly` - Get monthly overview reports
- `/api/reports/overview` - Get general overview reports
- `/api/reports/export/pdf` - Export reports as PDF
- `/api/reports/export/json` - Export reports as JSON data
- `/api/reports/export/ppt` - Export reports as PowerPoint presentation

## API Documentation URLs

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Contributing to the Documentation

If you'd like to contribute to this documentation, please follow these steps:

1. Fork the repository
2. Make your changes
3. Submit a pull request

## Additional Resources

- [README.md](../README.md) - Project overview and setup instructions
- [DOCKER_README.md](../DOCKER_README.md) - Docker setup instructions
- [TEST_PLAN.md](../TEST_PLAN.md) - Testing strategy and procedures 