from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, EmailStr, Field
import os
import requests
from typing import Optional, List, Dict, Any
import tempfile
import aiofiles
import asyncio
from starlette.responses import JSONResponse

from dependencies.auth import get_current_user
from dependencies.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/email",
    tags=["email"],
    responses={404: {"description": "Not found"}},
)

# Constants for file size limits
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_ATTACHMENTS_SIZE = 25 * 1024 * 1024  # 25MB

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    html_content: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

class TestEmailRequest(BaseModel):
    to_email: Optional[EmailStr] = None

class EmailResponse(BaseModel):
    status: str
    message_id: str

class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str

class FileAttachment:
    """Helper class to manage attachment processing with proper resource cleanup"""
    
    def __init__(self, file: UploadFile):
        self.file = file
        self.temp_file_path = None
        self.size = 0
        
    async def process(self) -> str:
        """Process the attachment in chunks to avoid memory issues"""
        temp_fd, self.temp_file_path = tempfile.mkstemp(prefix="attachment_", suffix="")
        os.close(temp_fd)  # Close the file descriptor immediately
        
        try:
            # Process file in chunks to avoid memory issues
            chunk_size = 1024 * 1024  # 1MB chunks
            async with aiofiles.open(self.temp_file_path, 'wb') as out_file:
                # Read and write the file in chunks
                while True:
                    chunk = await self.file.read(chunk_size)
                    if not chunk:
                        break
                        
                    self.size += len(chunk)
                    
                    # Check if file size exceeds the limit
                    if self.size > MAX_ATTACHMENT_SIZE:
                        self.cleanup()
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Attachment too large. Maximum size is {MAX_ATTACHMENT_SIZE / (1024 * 1024)}MB"
                        )
                    
                    await out_file.write(chunk)
                    
            # Reset file position
            await self.file.seek(0)
            return self.temp_file_path
            
        except Exception as e:
            # Clean up temp file if there's an error
            self.cleanup()
            raise e
    
    def cleanup(self):
        """Clean up the temporary file"""
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.unlink(self.temp_file_path)
                self.temp_file_path = None
            except Exception as e:
                # Log error but don't raise - this is cleanup code
                print(f"Error removing temporary file: {str(e)}")

    def __del__(self):
        """Ensure cleanup on garbage collection"""
        self.cleanup()

@router.post("/send", response_model=EmailResponse)
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
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 413:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Email content too large"
            )
        elif e.response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded, please try again later"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Email sending failed: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Email sending failed: {str(e)}"
        )

@router.post("/send-with-attachments")
async def send_email_with_attachments(
    to_email: str = Form(...),
    subject: str = Form(...),
    html_content: str = Form(...),
    attachments: List[UploadFile] = File(None),
    cc: Optional[str] = Form(None),
    bcc: Optional[str] = Form(None),
    db_session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """Send an email with attachments using streaming processing"""
    api_key = os.getenv("RESEND_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Email service not configured"
        )

    # Process attachments if any
    attachment_handlers = []
    total_size = 0
    
    try:
        if attachments:
            for attachment in attachments:
                if not attachment.filename:
                    continue
                
                # Create attachment handler
                handler = FileAttachment(attachment)
                attachment_handlers.append(handler)
                
                # Process file with proper memory management
                await handler.process()
                
                # Track total size
                total_size += handler.size
                
                # Check total size
                if total_size > MAX_TOTAL_ATTACHMENTS_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Total attachments size too large. Maximum size is {MAX_TOTAL_ATTACHMENTS_SIZE / (1024 * 1024)}MB"
                    )

        # Prepare email data
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": "training@3and7.com",
            "to": to_email,
            "subject": subject,
            "html": html_content
        }
        
        # Add CC and BCC if provided
        if cc:
            payload["cc"] = [email.strip() for email in cc.split(",")]
        if bcc:
            payload["bcc"] = [email.strip() for email in bcc.split(",")]
            
        # Add attachments if any were processed
        if attachment_handlers:
            payload["attachments"] = []
            for handler in attachment_handlers:
                if handler.temp_file_path:
                    # Read file in chunks
                    with open(handler.temp_file_path, "rb") as f:
                        content = f.read()
                    
                    # Add to payload
                    payload["attachments"].append({
                        "filename": handler.file.filename,
                        "content": content
                    })

        # Send the email
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        return {"status": "success", "message_id": response.json()["id"]}
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 413:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Email content too large"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Email sending failed: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Email sending failed: {str(e)}"
        )
    finally:
        # Ensure all temporary files are cleaned up
        for handler in attachment_handlers:
            handler.cleanup()

@router.post("/send-test", response_model=EmailResponse)
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