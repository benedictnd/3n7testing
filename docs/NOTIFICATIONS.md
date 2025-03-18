# Notification System Documentation

This document provides an overview of the notification system implemented in the 3&7 Training & Recovery Platform.

## Overview

The notification system allows coaches to receive real-time notifications when athletes submit post-training feedback. This feature enhances communication between athletes and coaches, ensuring coaches can promptly review and respond to athlete feedback.

## Architecture

The notification system follows a full-stack approach:

1. **Backend (FastAPI)**:
   - Database models for storing notifications
   - API endpoints for creating, fetching, and managing notifications
   - Service layer to handle business logic

2. **Frontend (Next.js)**:
   - Notification UI component (bell icon with unread count)
   - Hooks for fetching and managing notifications
   - Real-time updates with polling

## Technical Components

### Database Models

The primary model is the `Notification` table with the following fields:
- `id`: Unique identifier
- `title`: Notification title
- `message`: Detailed notification message
- `notification_type`: Type of notification (e.g., feedback_submitted)
- `recipient_id`: User ID of the notification recipient
- `sender_id`: User ID of the notification sender (optional)
- `related_id`: ID of related entity (e.g., feedback ID)
- `link`: URL to redirect when clicked
- `is_read`: Boolean indicating if the notification has been read
- `created_at`: Timestamp when the notification was created

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/training/notifications` | GET | Get notifications for the current user |
| `/training/notifications/{id}/read` | POST | Mark a notification as read |
| `/training/notifications/read-all` | POST | Mark all notifications as read |

### Frontend Components

- `NotificationBell`: UI component displaying the notification icon and count
- `useNotifications`: Custom React hook for managing notifications state

## Workflow

1. **Feedback Submission**:
   - Athlete submits post-training feedback through the feedback form
   - Backend processes the feedback and saves it to the database
   - A notification is created for the coach of that training session

2. **Notification Display**:
   - Coach sees the notification count in the notification bell
   - Unread notifications are highlighted
   - Coach can click on a notification to view the feedback details

3. **Notification Management**:
   - Clicking a notification marks it as read and navigates to the relevant page
   - Coach can mark all notifications as read at once
   - Backend updates the notification status in the database

## Implementation Notes

### Backend

- Notifications are created asynchronously when feedback is submitted
- The system fetches coach information from the training session
- Proper error handling ensures notifications are delivered reliably

### Frontend

- Notifications are fetched periodically (default: every 30 seconds)
- Optimistic UI updates improve user experience
- Proper error handling prevents UI disruptions

## Configuration

The notification system can be configured through environment variables:
- `POLLING_INTERVAL`: Time in milliseconds between notification checks (default: 30000)
- `NOTIFICATION_RETENTION_DAYS`: Days to keep notifications before automatic cleanup

## Future Enhancements

1. **Real-time Notifications**: Implement WebSockets for instant notification delivery
2. **Notification Preferences**: Allow users to configure notification preferences
3. **Push Notifications**: Add support for browser and mobile push notifications
4. **Advanced Filtering**: Enable filtering notifications by type, date, etc.
5. **Read Receipts**: Track when notifications are viewed for analytics

## Troubleshooting

Common issues and solutions:

1. **Notifications not showing**:
   - Check if the user is authenticated
   - Verify database connection
   - Ensure the correct coach ID is associated with the training session

2. **Duplicate notifications**:
   - Check for multiple submission events firing
   - Verify the feedback submission logic to prevent duplicates

3. **Slow notification delivery**:
   - Optimize database queries
   - Adjust polling interval
   - Consider implementing WebSockets for real-time updates 