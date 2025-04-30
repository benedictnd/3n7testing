# 3&7 Training Platform API Documentation

## Overview

Welcome to the 3&7 Training Platform API documentation. This API provides comprehensive access to the training management system, allowing you to retrieve information about teams, training sessions, and performance metrics.

## Key Features

The 3&7 Training Platform API offers:

- **Team Management**: Access team profiles, coaches, and athletes
- **Training Session Management**: View comprehensive training session data
- **Performance Analytics**: Access detailed training statistics and feedback

## Training Analytics

The API provides detailed training analytics including:

- **Training Type Distribution**: Core training vs Speed & Endurance training
- **Session Time Analysis**: Morning, Afternoon, and Night session counts
- **Duration Statistics**: Shortest, longest, and average session durations
- **Segment Time Breakdown**: Warm-up, Main, and Cool-down segment averages
- **Post-Training Feedback**: Coach ratings for quality, athlete condition, and expectation fulfillment

## Authentication

Authentication is required for accessing the API endpoints. Please contact the system administrator to obtain your API credentials.

## Rate Limiting

To ensure system stability, API requests are subject to rate limiting:
- 100 requests per minute for standard users
- 1000 requests per minute for premium users

## Getting Started

To start using the API:

1. Obtain your API credentials
2. Use the interactive documentation at `/docs` to explore endpoints
3. Test endpoints directly through the documentation interface

## Common Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/teams` | Get a list of all teams |
| `/api/teams/{team_id}` | Get details for a specific team |
| `/api/training-sessions` | Get comprehensive training session statistics |
| `/api/training-sessions/{session_id}` | Get details for a specific training session |

## Detailed Documentation

For more detailed information, please refer to the [ReDoc](/redoc) or [Swagger UI](/docs) documentation interfaces.

## Support

For technical support, please contact:
- Email: support@3and7.com
- Support Portal: https://support.3and7.com

---

© 2025 3&7 Training and Recovery Platform. All rights reserved.
