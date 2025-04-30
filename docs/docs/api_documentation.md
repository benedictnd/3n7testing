# 3&7 Training Platform API Documentation

This document provides information about the available API endpoints in the 3&7 Training Platform.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.training.3and7.com`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

You can obtain a token by using the `/api/auth/login` endpoint.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email and password |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/refresh` | Refresh the access token |
| POST | `/api/auth/logout` | Logout and invalidate the token |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get list of all users |
| GET | `/api/users/{user_id}` | Get user details by ID |
| PUT | `/api/users/{user_id}` | Update user information |
| DELETE | `/api/users/{user_id}` | Delete a user |

### Training Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/training-sessions` | Get list of training sessions |
| GET | `/api/training-sessions/{session_id}` | Get training session details |
| POST | `/api/training-sessions` | Create a new training session |
| PUT | `/api/training-sessions/{session_id}` | Update an existing training session |
| DELETE | `/api/training-sessions/{session_id}` | Delete a training session |
| POST | `/api/training-sessions/{session_id}/attendance` | Mark attendance for multiple athletes |
| GET | `/api/training-sessions/{session_id}/attendance` | Get session attendance records |
| POST | `/api/training-sessions/{session_id}/self-attendance` | Mark attendance for the current athlete |

### Independent Training

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/independent-training` | Get list of independent training sessions |
| GET | `/api/independent-training/{session_id}` | Get independent training session details |
| POST | `/api/independent-training` | Create a new independent training session |
| PUT | `/api/independent-training/{session_id}` | Update an independent training session |
| DELETE | `/api/independent-training/{session_id}` | Delete an independent training session |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/training` | Get training reports |
| GET | `/api/reports/attendance` | Get attendance reports |
| GET | `/api/reports/feedback` | Get feedback reports |
| GET | `/api/reports/monthly` | Get monthly overview reports |
| GET | `/api/reports/overview` | Get general overview reports |
| GET | `/api/reports/export/pdf` | Export reports as PDF |
| GET | `/api/reports/export/json` | Export reports as JSON data |
| GET | `/api/reports/export/ppt` | Export reports as PowerPoint presentation |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health status |

## Request and Response Examples

### Login

**Request:**
```json
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "role": "athlete"
  }
}
```

### Create Training Session

**Request:**
```json
POST /api/training-sessions
{
  "type": "Sprint",
  "date": "2025-04-22",
  "start_time": "2025-04-22T09:00:00",
  "end_time": "2025-04-22T11:00:00",
  "training_quality": 8,
  "expectations": 7,
  "team_condition": 9,
  "notes": "Focus on sprint techniques",
  "documentation": "Detailed documentation..."
}
```

**Response:**
```json
{
  "id": 1,
  "coach_id": 2,
  "type": "Sprint",
  "date": "2025-04-22",
  "start_time": "2025-04-22T09:00:00",
  "end_time": "2025-04-22T11:00:00",
  "training_quality": 8,
  "expectations": 7,
  "team_condition": 9,
  "notes": "Focus on sprint techniques",
  "documentation": "Detailed documentation...",
  "created_at": "2025-04-22T03:45:12",
  "updated_at": "2025-04-22T03:45:12"
}
```

### Create Independent Training Session

**Request:**
```json
POST /api/independent-training
{
  "title": "Morning Run",
  "description": "Easy run to build endurance",
  "date": "2025-04-22",
  "intensity": 6,
  "notes": "Felt good throughout the session"
}
```

**Response:**
```json
{
  "id": "1",
  "athlete_id": 3,
  "title": "Morning Run",
  "description": "Easy run to build endurance",
  "date": "2025-04-22",
  "intensity": 6,
  "notes": "Felt good throughout the session",
  "created_at": "2025-04-22T03:45:12",
  "updated_at": "2025-04-22T03:45:12"
}
```

## Error Responses

The API uses standard HTTP status codes to indicate the success or failure of requests.

Common error responses:

```json
{
  "detail": "Not found"
}
```

```json
{
  "detail": "Authentication credentials were not provided"
}
```

```json
{
  "detail": "Could not validate credentials"
}
```

## Pagination

Endpoints that return lists of items support pagination through query parameters:

- `page`: Page number (starting from 1)
- `size`: Number of items per page

Example:
```
GET /api/training-sessions?page=2&size=10
```

Response includes pagination metadata:
```json
{
  "sessions": [...],
  "total": 45,
  "page": 2,
  "size": 10
}
```

## Filtering

Many list endpoints support filtering through query parameters.

Examples:
```
GET /api/training-sessions?start_date=2025-04-01&end_date=2025-04-30&type=Sprint
```

```
GET /api/reports/attendance?athlete_id=3&month=4&year=2025
```

## API Documentation

Swagger UI documentation is available at `/docs` endpoint.
ReDoc alternative documentation is available at `/redoc` endpoint. 