#!/usr/bin/env python3
"""
ClubOS API Demo Script

This script demonstrates the ClubOS API messaging implementation and shows
how to use both the working form submission approach and the research API endpoint approach.

Usage:
    python demo_clubos_api.py

Environment Variables Required:
    CLUBOS_USERNAME - Your ClubOS username
    CLUBOS_PASSWORD - Your ClubOS password
    CLUBOS_MEMBER_ID - Target member ID (optional, defaults to Jeremy Mayo)
"""

import os
import sys
import logging
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSCredentials, MessageRequest
from services.authentication.clubhub_token_capture import ClubHubTokenCapture
from config.constants import (
    MESSAGE_TYPE_SMS,
    MESSAGE_TYPE_EMAIL, 
    DEFAULT_MEMBER_ID,
    CLUBOS_BASE_URL
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/clubos_api_demo.log')
    ]
)
logger = logging.getLogger(__name__)

class ClubOSAPIDemo:
    """Demonstration of ClubOS API messaging functionality"""
    
    def __init__(self):
        self.client = None
        self.credentials = None
        self.setup_credentials()
    
    def setup_credentials(self):
        """Setup credentials from environment variables"""
        username = os.getenv('CLUBOS_USERNAME')
        password = os.getenv('CLUBOS_PASSWORD')
        
        if not username or not password:
            logger.error("Missing required environment variables!")
            logger.error("Please set:")
            logger.error("  export CLUBOS_USERNAME='your_username'")
            logger.error("  export CLUBOS_PASSWORD='your_password'")
            logger.error("  export CLUBOS_MEMBER_ID='member_id'  # Optional, defaults to Jeremy Mayo")
            raise ValueError("Missing credentials")
        
        self.credentials = ClubOSCredentials(username=username, password=password)
        self.client = ClubOSAPIClient(self.credentials)
        
        logger.info(f"Credentials setup for user: {username}")
        logger.info(f"Target ClubOS base URL: {CLUBOS_BASE_URL}")
    
    def demo_authentication(self) -> bool:
        """Demonstrate authentication process"""
        logger.info("=" * 60)
        logger.info("AUTHENTICATION DEMO")
        logger.info("=" * 60)
        
        try:
            logger.info("Attempting login to ClubOS...")
            success = self.client.login()
            
            if success:
                logger.info("✅ Login successful!")
                
                # Show session information
                session_info = self.client.get_session_info()
                logger.info("Session Details:")
                logger.info(f"  Authenticated: {session_info['authenticated']}")
                logger.info(f"  CSRF Token: {session_info['csrf_token']}")
                logger.info(f"  API Token: {session_info['api_access_token']}")
                logger.info(f"  Cookies: {len(session_info['cookies'])} cookies stored")
                logger.info(f"  Session Expired: {session_info['is_expired']}")
                
                return True
            else:
                logger.error("❌ Login failed!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    def demo_working_sms(self, member_id: str) -> bool:
        """Demonstrate working SMS sending via form submission"""
        logger.info("=" * 60)
        logger.info("SMS MESSAGING DEMO (Working Approach)")
        logger.info("=" * 60)
        
        try:
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_SMS,
                message_content="Hello from ClubOS API Demo! This is a test SMS message sent via form submission. Please ignore this test message."
            )
            
            logger.info(f"Sending SMS to member: {member_id}")
            logger.info(f"Message: {message_request.message_content}")
            
            success = self.client.send_message_via_form_submission(message_request)
            
            if success:
                logger.info("✅ SMS sent successfully via form submission!")
                return True
            else:
                logger.error("❌ SMS sending failed via form submission")
                return False
                
        except Exception as e:
            logger.error(f"❌ SMS demo error: {str(e)}")
            return False
    
    def demo_working_email(self, member_id: str) -> bool:
        """Demonstrate working Email sending via form submission"""
        logger.info("=" * 60)
        logger.info("EMAIL MESSAGING DEMO (Working Approach)")
        logger.info("=" * 60)
        
        try:
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_EMAIL,
                message_content="Hello from ClubOS API Demo!\n\nThis is a test email message sent via the form submission approach. The implementation successfully replicates the web interface workflow without using Selenium.\n\nKey features:\n- Session management\n- CSRF token handling\n- Proper browser headers\n- Form data extraction\n\nPlease ignore this test message.\n\nBest regards,\nClubOS API Demo",
                subject="Test Email from ClubOS API Demo"
            )
            
            logger.info(f"Sending Email to member: {member_id}")
            logger.info(f"Subject: {message_request.subject}")
            logger.info(f"Content length: {len(message_request.message_content)} characters")
            
            success = self.client.send_message_via_form_submission(message_request)
            
            if success:
                logger.info("✅ Email sent successfully via form submission!")
                return True
            else:
                logger.error("❌ Email sending failed via form submission")
                return False
                
        except Exception as e:
            logger.error(f"❌ Email demo error: {str(e)}")
            return False
    
    def demo_api_endpoint_research(self, member_id: str) -> Dict[str, Any]:
        """Demonstrate API endpoint research (expected to fail)"""
        logger.info("=" * 60)
        logger.info("API ENDPOINT RESEARCH DEMO (Expected to Fail)")
        logger.info("=" * 60)
        
        results = {
            'sms_success': False,
            'sms_error': '',
            'email_success': False,
            'email_error': '',
            'session_info': {}
        }
        
        try:
            # Test SMS via API endpoint
            logger.info("Testing SMS via API endpoint...")
            sms_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_SMS,
                message_content="Test SMS via API endpoint - should fail"
            )
            
            sms_success, sms_error = self.client.send_message_via_api_endpoint(sms_request)
            results['sms_success'] = sms_success
            results['sms_error'] = sms_error
            
            if sms_success:
                logger.info("🎉 SMS via API endpoint worked! (Unexpected success)")
            else:
                logger.warning(f"❌ SMS via API endpoint failed as expected: {sms_error}")
            
            # Test Email via API endpoint
            logger.info("Testing Email via API endpoint...")
            email_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_EMAIL,
                message_content="Test email via API endpoint - should fail",
                subject="Test API Endpoint"
            )
            
            email_success, email_error = self.client.send_message_via_api_endpoint(email_request)
            results['email_success'] = email_success
            results['email_error'] = email_error
            
            if email_success:
                logger.info("🎉 Email via API endpoint worked! (Unexpected success)")
            else:
                logger.warning(f"❌ Email via API endpoint failed as expected: {email_error}")
            
            # Capture session information for debugging
            results['session_info'] = self.client.get_session_info()
            
            return results
            
        except Exception as e:
            logger.error(f"❌ API endpoint research error: {str(e)}")
            results['sms_error'] = str(e)
            results['email_error'] = str(e)
            return results
    
    def demo_token_capture(self, member_id: str):
        """Demonstrate token capture and analysis"""
        logger.info("=" * 60)
        logger.info("TOKEN CAPTURE AND ANALYSIS DEMO")
        logger.info("=" * 60)
        
        try:
            # Initialize token capture
            token_capture = ClubHubTokenCapture(self.client.session_manager.session)
            
            # Capture from member profile page
            from config.constants import CLUBOS_MEMBER_PROFILE_URL
            member_url = f"{CLUBOS_MEMBER_PROFILE_URL}/{member_id}"
            
            logger.info(f"Capturing tokens from: {member_url}")
            response = self.client.session_manager.session.get(member_url)
            
            captured_data = token_capture.capture_all_tokens(response, "member_profile")
            
            logger.info("Token Capture Results:")
            logger.info(f"  Tokens found: {len(captured_data.get('tokens', {}))}")
            logger.info(f"  Cookies captured: {len(captured_data.get('cookies', {}))}")
            logger.info(f"  Forms found: {len(captured_data.get('forms', []))}")
            logger.info(f"  Scripts analyzed: {len(captured_data.get('scripts', {}))}")
            
            # Show token details
            for token_name, token_value in captured_data.get('tokens', {}).items():
                logger.info(f"  Token '{token_name}': {token_value[:20]}...")
            
            # Generate summary
            summary = token_capture.get_capture_summary()
            logger.info("Capture Summary:")
            logger.info(f"  Unique tokens: {len(summary['unique_tokens'])}")
            logger.info(f"  Common patterns: {summary['common_patterns']}")
            logger.info(f"  API requirements: {summary['potential_api_requirements']}")
            
        except Exception as e:
            logger.error(f"❌ Token capture error: {str(e)}")
    
    def run_full_demo(self):
        """Run the complete demonstration"""
        logger.info("🚀 Starting ClubOS API Demo")
        logger.info("=" * 80)
        
        member_id = os.getenv('CLUBOS_MEMBER_ID', DEFAULT_MEMBER_ID)
        logger.info(f"Target Member ID: {member_id} (Jeremy Mayo)")
        
        results = {
            'authentication': False,
            'sms_working': False,
            'email_working': False,
            'api_research': {},
            'errors': []
        }
        
        try:
            # Step 1: Authentication
            results['authentication'] = self.demo_authentication()
            if not results['authentication']:
                logger.error("❌ Cannot continue without authentication")
                return results
            
            # Step 2: Working SMS
            results['sms_working'] = self.demo_working_sms(member_id)
            
            # Step 3: Working Email
            results['email_working'] = self.demo_working_email(member_id)
            
            # Step 4: API Endpoint Research
            results['api_research'] = self.demo_api_endpoint_research(member_id)
            
            # Step 5: Token Capture
            self.demo_token_capture(member_id)
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {str(e)}")
            results['errors'].append(str(e))
        
        # Final Summary
        self.print_final_summary(results)
        
        return results
    
    def print_final_summary(self, results: Dict[str, Any]):
        """Print final demonstration summary"""
        logger.info("=" * 80)
        logger.info("FINAL DEMO SUMMARY")
        logger.info("=" * 80)
        
        logger.info("Results:")
        logger.info(f"  ✅ Authentication: {'SUCCESS' if results['authentication'] else 'FAILED'}")
        logger.info(f"  ✅ SMS (Form Submission): {'SUCCESS' if results['sms_working'] else 'FAILED'}")
        logger.info(f"  ✅ Email (Form Submission): {'SUCCESS' if results['email_working'] else 'FAILED'}")
        
        api_research = results.get('api_research', {})
        logger.info(f"  🔬 SMS (API Endpoint): {'SUCCESS' if api_research.get('sms_success') else 'FAILED (Expected)'}")
        logger.info(f"  🔬 Email (API Endpoint): {'SUCCESS' if api_research.get('email_success') else 'FAILED (Expected)'}")
        
        logger.info("\nKey Findings:")
        logger.info("  ✅ Form submission approach works reliably")
        logger.info("  ❌ Direct API endpoints fail with 'Something isn't right' errors")
        logger.info("  🔍 Session management and authentication work correctly")
        logger.info("  📋 Token capture system identifies authentication patterns")
        
        logger.info("\nRecommendations:")
        logger.info("  1. Use form submission approach for production")
        logger.info("  2. Continue researching API endpoint requirements")
        logger.info("  3. Analyze network traffic from successful form submissions")
        logger.info("  4. Investigate additional authentication layers")
        
        if results['errors']:
            logger.warning("\nErrors encountered:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        logger.info("\n🎯 Demo complete! Check /tmp/clubos_api_demo.log for detailed logs.")

def main():
    """Main demo function"""
    try:
        demo = ClubOSAPIDemo()
        demo.run_full_demo()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("\nTo run this demo:")
        logger.error("1. Set environment variables:")
        logger.error("   export CLUBOS_USERNAME='your_username'")
        logger.error("   export CLUBOS_PASSWORD='your_password'")
        logger.error("   export CLUBOS_MEMBER_ID='member_id'  # Optional")
        logger.error("2. Run: python demo_clubos_api.py")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")

if __name__ == "__main__":
    main()