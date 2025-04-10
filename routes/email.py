from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import os
import requests
from typing import Optional

from dependencies.auth import get_current_user
from dependencies.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    html_content: str
    cc: Optional[list[EmailStr]] = None
    bcc: Optional[list[EmailStr]] = None

class TestEmailRequest(BaseModel):
    to_email: Optional[EmailStr] = None

@router.post("/send")
async def send_email(
    email_data: EmailRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Send an email using the Resend API
    
    Args:
        email_data: Email data including recipient, subject, and content
        db_session: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message with message ID
    """
    api_key = os.getenv("RESEND_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Email service not configured"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": "training@3and7.com",
        "to": email_data.to_email,
        "subject": email_data.subject,
        "html": email_data.html_content
    }
    
    # Add CC and BCC if provided
    if email_data.cc:
        payload["cc"] = email_data.cc
    if email_data.bcc:
        payload["bcc"] = email_data.bcc

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return {"status": "success", "message_id": response.json()["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Email sending failed: {str(e)}"
        )

@router.post("/send-test")
async def send_test_email(
    test_data: TestEmailRequest = TestEmailRequest(),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Send a test email to verify email functionality
    
    Args:
        test_data: Optional test email data
        db_session: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message with message ID
    """
    # Use provided email or current user's email
    to_email = test_data.to_email or current_user.email
    
    email_data = EmailRequest(
        to_email=to_email,
        subject="3&7 Training Platform - Test Email",
        html_content="""
        <html>
            <body>
                <h1>Test Email from 3&7 Training Platform</h1>
                <p>This is a test email to verify that the email functionality is working correctly.</p>
                <p>If you received this email, the email service is configured properly.</p>
                <p>Thank you for using the 3&7 Training Platform!</p>
            </body>
        </html>
        """
    )
    
    return await send_email(email_data, db_session, current_user) 