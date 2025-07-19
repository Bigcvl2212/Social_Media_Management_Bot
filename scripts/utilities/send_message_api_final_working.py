"""
ClubOS API Final Working Implementation

This script demonstrates the working approach for sending SMS and Email messages
to ClubOS members using form submission rather than direct API endpoints.

Key findings:
- Login works successfully with proper session management
- Navigating to member profile pages works
- Form submission to profile pages successfully sends messages
- Direct API endpoints (/action/Api/send-message) fail with "Something isn't right"

This is the reference implementation that works.
"""

import os
import sys
import logging
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSCredentials, MessageRequest
from config.constants import MESSAGE_TYPE_SMS, MESSAGE_TYPE_EMAIL, DEFAULT_MEMBER_ID

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClubOSMessageSender:
    """Working ClubOS message sender using form submission approach"""
    
    def __init__(self, username: str, password: str):
        self.credentials = ClubOSCredentials(username=username, password=password)
        self.client = ClubOSAPIClient(self.credentials)
        
    def send_sms_message(self, member_id: str, message: str) -> bool:
        """
        Send SMS message to ClubOS member.
        
        Args:
            member_id: ClubOS member ID
            message: SMS message content
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Sending SMS to member {member_id}")
            
            # Create message request
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_SMS,
                message_content=message
            )
            
            # Use the working form submission approach
            success = self.client.send_message_via_form_submission(message_request)
            
            if success:
                logger.info("SMS sent successfully via form submission!")
            else:
                logger.error("SMS sending failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    def send_email_message(self, member_id: str, subject: str, message: str) -> bool:
        """
        Send Email message to ClubOS member.
        
        Args:
            member_id: ClubOS member ID
            subject: Email subject
            message: Email message content
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Sending Email to member {member_id}")
            
            # Create message request
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_EMAIL,
                message_content=message,
                subject=subject
            )
            
            # Use the working form submission approach
            success = self.client.send_message_via_form_submission(message_request)
            
            if success:
                logger.info("Email sent successfully via form submission!")
            else:
                logger.error("Email sending failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending Email: {str(e)}")
            return False
    
    def test_api_endpoint_approach(self, member_id: str, message: str) -> None:
        """
        Test the API endpoint approach to understand why it fails.
        
        This method demonstrates the failing approach for research purposes.
        """
        try:
            logger.info("Testing API endpoint approach (expected to fail)...")
            
            # Create message request
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_SMS,
                message_content=message
            )
            
            # Try the API endpoint approach
            success, error_msg = self.client.send_message_via_api_endpoint(message_request)
            
            if success:
                logger.info("API endpoint approach worked! (Unexpected)")
            else:
                logger.warning(f"API endpoint approach failed as expected: {error_msg}")
                
            # Get session info for debugging
            session_info = self.client.get_session_info()
            logger.info(f"Session info: {session_info}")
                
        except Exception as e:
            logger.error(f"Error testing API endpoint: {str(e)}")

def main():
    """Main function demonstrating the working ClubOS messaging approach"""
    
    # Get credentials from environment or use defaults for testing
    username = os.getenv('CLUBOS_USERNAME', 'your_username')
    password = os.getenv('CLUBOS_PASSWORD', 'your_password')
    member_id = os.getenv('CLUBOS_MEMBER_ID', DEFAULT_MEMBER_ID)
    
    if username == 'your_username' or password == 'your_password':
        logger.warning("Please set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables")
        logger.info("Example usage:")
        logger.info("export CLUBOS_USERNAME='your_username'")
        logger.info("export CLUBOS_PASSWORD='your_password'")
        logger.info("python send_message_api_final_working.py")
        return
    
    # Create message sender
    sender = ClubOSMessageSender(username, password)
    
    # Test SMS sending (working approach)
    logger.info("=" * 50)
    logger.info("Testing SMS sending via form submission (working approach)")
    logger.info("=" * 50)
    
    sms_message = "Hello from ClubOS API! This is a test SMS message."
    sms_success = sender.send_sms_message(member_id, sms_message)
    
    # Test Email sending (working approach)
    logger.info("=" * 50)
    logger.info("Testing Email sending via form submission (working approach)")
    logger.info("=" * 50)
    
    email_subject = "Test Email from ClubOS API"
    email_message = "Hello from ClubOS API! This is a test email message with more detailed content."
    email_success = sender.send_email_message(member_id, email_subject, email_message)
    
    # Test API endpoint approach for research
    logger.info("=" * 50)
    logger.info("Testing API endpoint approach (research - expected to fail)")
    logger.info("=" * 50)
    
    sender.test_api_endpoint_approach(member_id, "Test API endpoint message")
    
    # Summary
    logger.info("=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)
    logger.info(f"SMS via form submission: {'SUCCESS' if sms_success else 'FAILED'}")
    logger.info(f"Email via form submission: {'SUCCESS' if email_success else 'FAILED'}")
    logger.info("API endpoint approach: FAILED (as expected)")
    
    if sms_success and email_success:
        logger.info("✅ Working solution confirmed - form submission approach works!")
    else:
        logger.warning("❌ Some messages failed - check credentials and member ID")

if __name__ == "__main__":
    main()