# Email Integration Setup

This document provides instructions for setting up and using the email functionality in the 3&7 Training Platform.

## Overview

The 3&7 Training Platform uses the [Resend API](https://resend.com) for sending emails. This integration allows the platform to send various types of emails, including:

- Test emails for verifying email functionality
- Training session notifications
- Report delivery
- System notifications

## Setup Instructions

### 1. Create a Resend Account

1. Sign up for a Resend account at [https://resend.com](https://resend.com)
2. Verify your domain or use the provided sandbox domain for testing
3. Create an API key in the Resend dashboard

### 2. Configure Environment Variables

Add the following environment variables to your `.env` file:

```
RESEND_API_KEY=your_api_key_here
```

### 3. Install Dependencies

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### Sending Test Emails

You can send test emails using the email test page at `/email-test` or by making a POST request to the `/email/send-test` endpoint.

### Sending Custom Emails

To send a custom email, make a POST request to the `/email/send` endpoint with the following JSON payload:

```json
{
  "to_email": "recipient@example.com",
  "subject": "Email Subject",
  "html_content": "<h1>Hello</h1><p>This is a test email.</p>",
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"]
}
```

### Frontend Integration

The frontend includes a `SendTestEmailButton` component that can be used to send test emails. This component is used on the email test page.

## Load Testing

The platform includes load testing scripts for testing the email functionality under load. To run the load tests:

```bash
# Install locust if not already installed
pip install locust

# Run the load tests
locust -f locustfile.py --headless -u 10 -r 1 --run-time 1m --host http://localhost:8000 -c EmailTestUser
```

## Troubleshooting

If you encounter issues with the email functionality:

1. Check that the `RESEND_API_KEY` environment variable is set correctly
2. Verify that your Resend account is active and has available credits
3. Check the server logs for any error messages
4. Try sending a test email using the email test page

## Security Considerations

- The email API endpoints are protected by authentication
- API keys should be kept secure and not committed to version control
- Consider implementing rate limiting for email endpoints to prevent abuse 