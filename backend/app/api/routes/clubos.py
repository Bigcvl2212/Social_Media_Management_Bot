"""
ClubOS API Integration for FastAPI Backend

This module provides FastAPI integration for ClubOS messaging functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import os
import logging

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSCredentials, MessageRequest
from config.constants import MESSAGE_TYPE_SMS, MESSAGE_TYPE_EMAIL

logger = logging.getLogger(__name__)

# Pydantic models for API requests
class SendSMSRequest(BaseModel):
    """SMS message request model"""
    member_id: str = Field(..., description="ClubOS member ID")
    message: str = Field(..., min_length=1, max_length=1000, description="SMS message content")

class SendEmailRequest(BaseModel):
    """Email message request model"""
    member_id: str = Field(..., description="ClubOS member ID")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    message: str = Field(..., min_length=1, max_length=5000, description="Email message content")

class MessageResponse(BaseModel):
    """Message response model"""
    success: bool
    message: str
    member_id: str
    message_type: str

# Router for ClubOS API endpoints
clubos_router = APIRouter(prefix="/api/clubos", tags=["ClubOS Messaging"])

def get_clubos_client() -> ClubOSAPIClient:
    """Get ClubOS client instance with credentials from environment"""
    username = os.getenv('CLUBOS_USERNAME')
    password = os.getenv('CLUBOS_PASSWORD')
    
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail="ClubOS credentials not configured. Please set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables."
        )
    
    credentials = ClubOSCredentials(username=username, password=password)
    return ClubOSAPIClient(credentials)

@clubos_router.post("/send-sms", response_model=MessageResponse)
async def send_sms(request: SendSMSRequest, client: ClubOSAPIClient = Depends(get_clubos_client)):
    """
    Send SMS message to ClubOS member using the working form submission approach.
    
    Args:
        request: SMS message request containing member_id and message
        client: ClubOS API client instance
        
    Returns:
        MessageResponse: Result of the SMS sending operation
    """
    try:
        logger.info(f"Sending SMS to member {request.member_id}")
        
        # Create message request
        message_request = MessageRequest(
            member_id=request.member_id,
            message_type=MESSAGE_TYPE_SMS,
            message_content=request.message
        )
        
        # Send using working form submission approach
        success = client.send_message_via_form_submission(message_request)
        
        if success:
            logger.info(f"SMS sent successfully to member {request.member_id}")
            return MessageResponse(
                success=True,
                message="SMS sent successfully",
                member_id=request.member_id,
                message_type=MESSAGE_TYPE_SMS
            )
        else:
            logger.error(f"SMS sending failed for member {request.member_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send SMS message"
            )
            
    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending SMS: {str(e)}"
        )

@clubos_router.post("/send-email", response_model=MessageResponse)
async def send_email(request: SendEmailRequest, client: ClubOSAPIClient = Depends(get_clubos_client)):
    """
    Send Email message to ClubOS member using the working form submission approach.
    
    Args:
        request: Email message request containing member_id, subject, and message
        client: ClubOS API client instance
        
    Returns:
        MessageResponse: Result of the email sending operation
    """
    try:
        logger.info(f"Sending email to member {request.member_id}")
        
        # Create message request
        message_request = MessageRequest(
            member_id=request.member_id,
            message_type=MESSAGE_TYPE_EMAIL,
            message_content=request.message,
            subject=request.subject
        )
        
        # Send using working form submission approach
        success = client.send_message_via_form_submission(message_request)
        
        if success:
            logger.info(f"Email sent successfully to member {request.member_id}")
            return MessageResponse(
                success=True,
                message="Email sent successfully",
                member_id=request.member_id,
                message_type=MESSAGE_TYPE_EMAIL
            )
        else:
            logger.error(f"Email sending failed for member {request.member_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send email message"
            )
            
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending email: {str(e)}"
        )

@clubos_router.get("/health")
async def health_check():
    """Health check endpoint for ClubOS integration"""
    return {
        "status": "healthy",
        "service": "ClubOS API Integration",
        "version": "1.0.0",
        "approach": "form_submission",
        "capabilities": ["SMS", "Email"]
    }

@clubos_router.get("/status")
async def status_check(client: ClubOSAPIClient = Depends(get_clubos_client)):
    """Check ClubOS authentication status"""
    try:
        # Attempt authentication
        auth_success = client.login()
        session_info = client.get_session_info()
        
        return {
            "authenticated": auth_success,
            "session_expired": session_info.get('is_expired', True),
            "csrf_token_available": session_info.get('csrf_token') is not None,
            "api_token_available": session_info.get('api_access_token') is not None,
            "cookies_count": len(session_info.get('cookies', {}))
        }
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking ClubOS status: {str(e)}"
        )

# Usage example for integration with main FastAPI app:
"""
from backend.app.api.routes.clubos import clubos_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(clubos_router)

# Example requests:
# POST /api/clubos/send-sms
# {
#   "member_id": "187032782",
#   "message": "Hello from the API!"
# }

# POST /api/clubos/send-email  
# {
#   "member_id": "187032782",
#   "subject": "Test Email",
#   "message": "Hello from the API email!"
# }
"""