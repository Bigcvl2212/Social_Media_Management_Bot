"""
ClubOS API Client
Main client for interacting with ClubOS platform for member messaging.
"""

import requests
import re
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass

from config.constants import (
    CLUBOS_BASE_URL,
    CLUBOS_LOGIN_URL,
    CLUBOS_DASHBOARD_URL,
    CLUBOS_MEMBER_PROFILE_URL,
    CLUBOS_API_SEND_MESSAGE_URL,
    DEFAULT_HEADERS,
    API_HEADERS,
    MESSAGE_TYPE_SMS,
    MESSAGE_TYPE_EMAIL,
    SESSION_TIMEOUT,
    REQUEST_TIMEOUT,
    AUTH_SUCCESS_INDICATORS,
    ERROR_PATTERNS
)

logger = logging.getLogger(__name__)

@dataclass
class ClubOSCredentials:
    """ClubOS login credentials"""
    username: str
    password: str

@dataclass
class MessageRequest:
    """Message request data"""
    member_id: str
    message_type: str  # 'sms' or 'email'
    message_content: str
    subject: Optional[str] = None  # For email messages

class ClubOSSession:
    """Manages ClubOS session state and authentication"""
    
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.csrf_token = None
        self.api_access_token = None
        self.last_activity = None
        
    def set_default_headers(self):
        """Set browser-like headers for the session"""
        self.session.headers.update(DEFAULT_HEADERS)
        
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.last_activity:
            return True
        return time.time() - self.last_activity > SESSION_TIMEOUT
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()

class ClubOSAPIClient:
    """
    ClubOS API Client for member messaging.
    
    This client implements the working form submission approach while
    also providing methods to test direct API endpoint calls.
    """
    
    def __init__(self, credentials: ClubOSCredentials):
        self.credentials = credentials
        self.session_manager = ClubOSSession()
        
    def login(self) -> bool:
        """
        Authenticate with ClubOS using username and password.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.session_manager.set_default_headers()
            
            # Get login page to extract any CSRF tokens
            logger.info("Fetching login page...")
            response = self.session_manager.session.get(
                CLUBOS_LOGIN_URL, 
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Extract CSRF token if present
            csrf_token = self._extract_csrf_token(response.text)
            if csrf_token:
                self.session_manager.csrf_token = csrf_token
                logger.info(f"Extracted CSRF token: {csrf_token[:20]}...")
            
            # Prepare login data
            login_data = {
                'username': self.credentials.username,
                'password': self.credentials.password
            }
            
            # Add CSRF token if available
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Set proper headers for login
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = CLUBOS_LOGIN_URL
            headers['Origin'] = CLUBOS_BASE_URL
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            # Perform login
            logger.info("Attempting login...")
            response = self.session_manager.session.post(
                CLUBOS_LOGIN_URL,
                data=login_data,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            
            # Check if login was successful
            success = self._check_login_success(response)
            if success:
                self.session_manager.authenticated = True
                self.session_manager.update_activity()
                self._extract_api_tokens(response.text)
                logger.info("Login successful!")
                return True
            else:
                logger.error("Login failed!")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def send_message_via_form_submission(self, message_request: MessageRequest) -> bool:
        """
        Send message using the working form submission approach.
        
        This is the approach that works: navigate to member profile and submit form.
        
        Args:
            message_request: Message details
            
        Returns:
            bool: True if message sent successfully
        """
        if not self._ensure_authenticated():
            return False
            
        try:
            # Navigate to member profile page
            member_url = f"{CLUBOS_MEMBER_PROFILE_URL}/{message_request.member_id}"
            logger.info(f"Navigating to member profile: {member_url}")
            
            response = self.session_manager.session.get(
                member_url,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Extract any form tokens or hidden fields
            form_data = self._extract_form_data(response.text, message_request)
            
            # Set proper headers for form submission
            headers = DEFAULT_HEADERS.copy()
            headers['Referer'] = member_url
            headers['Origin'] = CLUBOS_BASE_URL
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            # Submit message via form
            logger.info(f"Sending {message_request.message_type} message...")
            response = self.session_manager.session.post(
                member_url,  # Submit back to the same profile page
                data=form_data,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            # Check if message was sent successfully
            success = self._check_message_success(response)
            if success:
                logger.info("Message sent successfully via form submission!")
                return True
            else:
                logger.error("Message sending failed via form submission")
                return False
                
        except Exception as e:
            logger.error(f"Form submission error: {str(e)}")
            return False
    
    def send_message_via_api_endpoint(self, message_request: MessageRequest) -> Tuple[bool, str]:
        """
        Attempt to send message using direct API endpoint calls.
        
        This is the approach that currently fails with "Something isn't right" errors.
        We use this to research what's missing compared to form submission.
        
        Args:
            message_request: Message details
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if not self._ensure_authenticated():
            return False, "Not authenticated"
            
        try:
            # Prepare API headers
            headers = API_HEADERS.copy()
            headers['Referer'] = f"{CLUBOS_MEMBER_PROFILE_URL}/{message_request.member_id}"
            headers['Origin'] = CLUBOS_BASE_URL
            
            # Add authentication headers
            if self.session_manager.csrf_token:
                headers['X-CSRF-TOKEN'] = self.session_manager.csrf_token
                
            if self.session_manager.api_access_token:
                headers['Authorization'] = f"Bearer {self.session_manager.api_access_token}"
            
            # Prepare API data
            api_data = {
                'member_id': message_request.member_id,
                'message_type': message_request.message_type,
                'message': message_request.message_content
            }
            
            if message_request.subject and message_request.message_type == MESSAGE_TYPE_EMAIL:
                api_data['subject'] = message_request.subject
            
            # Try the API endpoint
            logger.info(f"Attempting API call to {CLUBOS_API_SEND_MESSAGE_URL}")
            response = self.session_manager.session.post(
                CLUBOS_API_SEND_MESSAGE_URL,
                data=api_data,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"API Response Body: {response.text[:500]}")
            
            # Check for success
            if response.status_code == 200:
                # Check response content for success indicators
                if not any(error in response.text.lower() for error in ERROR_PATTERNS):
                    logger.info("API call appears successful!")
                    return True, "Success"
                else:
                    error_msg = f"API returned error: {response.text}"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"API endpoint error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authenticated session"""
        if not self.session_manager.authenticated or self.session_manager.is_expired():
            logger.info("Re-authenticating...")
            return self.login()
        return True
    
    def _extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Extract CSRF token from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for common CSRF token patterns
            csrf_patterns = [
                ('meta', {'name': 'csrf-token'}),
                ('meta', {'name': '_token'}),
                ('input', {'name': '_token'}),
                ('input', {'name': 'csrf_token'}),
            ]
            
            for tag_name, attrs in csrf_patterns:
                element = soup.find(tag_name, attrs)
                if element:
                    token = element.get('content') or element.get('value')
                    if token:
                        return token
                        
            # Also look in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    csrf_match = re.search(r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', script.string, re.IGNORECASE)
                    if csrf_match:
                        return csrf_match.group(1)
                        
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting CSRF token: {str(e)}")
            return None
    
    def _extract_api_tokens(self, html_content: str):
        """Extract API access tokens from page content"""
        try:
            # Look for API access token in cookies
            for cookie in self.session_manager.session.cookies:
                if 'apiV3AccessToken' in cookie.name:
                    self.session_manager.api_access_token = cookie.value
                    logger.info(f"Found API access token: {cookie.value[:20]}...")
                    break
                    
            # Also look in script tags or HTML
            api_token_patterns = [
                r'apiV3AccessToken["\']?\s*[:=]\s*["\']([^"\']+)',
                r'api[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)',
                r'access[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)'
            ]
            
            for pattern in api_token_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    self.session_manager.api_access_token = match.group(1)
                    logger.info(f"Found API token in HTML: {match.group(1)[:20]}...")
                    break
                    
        except Exception as e:
            logger.warning(f"Error extracting API tokens: {str(e)}")
    
    def _check_login_success(self, response: requests.Response) -> bool:
        """Check if login was successful based on response"""
        try:
            # Check URL - successful login usually redirects to dashboard
            if any(indicator in response.url.lower() for indicator in AUTH_SUCCESS_INDICATORS):
                return True
                
            # Check response content for success indicators
            content = response.text.lower()
            return any(indicator in content for indicator in AUTH_SUCCESS_INDICATORS)
            
        except Exception:
            return False
    
    def _extract_form_data(self, html_content: str, message_request: MessageRequest) -> Dict[str, str]:
        """Extract form data needed for message submission"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            form_data = {}
            
            # Find the message form
            form = soup.find('form') or soup
            
            # Extract all hidden inputs
            hidden_inputs = form.find_all('input', {'type': 'hidden'})
            for input_field in hidden_inputs:
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value
            
            # Add message-specific data
            form_data.update({
                'member_id': message_request.member_id,
                'message_type': message_request.message_type,
                'message_content': message_request.message_content,
                'message': message_request.message_content,  # Sometimes both fields are needed
            })
            
            if message_request.subject and message_request.message_type == MESSAGE_TYPE_EMAIL:
                form_data['subject'] = message_request.subject
                form_data['email_subject'] = message_request.subject
            
            # Add CSRF token if available
            if self.session_manager.csrf_token:
                form_data['_token'] = self.session_manager.csrf_token
                form_data['csrf_token'] = self.session_manager.csrf_token
            
            logger.info(f"Extracted form data: {list(form_data.keys())}")
            return form_data
            
        except Exception as e:
            logger.error(f"Error extracting form data: {str(e)}")
            return {}
    
    def _check_message_success(self, response: requests.Response) -> bool:
        """Check if message was sent successfully"""
        try:
            # Check status code
            if response.status_code != 200:
                return False
                
            # Check response content for error patterns
            content = response.text.lower()
            if any(error in content for error in ERROR_PATTERNS):
                return False
                
            # Look for success indicators
            success_indicators = ['success', 'sent', 'delivered', 'message sent']
            return any(indicator in content for indicator in success_indicators)
            
        except Exception:
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information for debugging"""
        return {
            'authenticated': self.session_manager.authenticated,
            'csrf_token': self.session_manager.csrf_token[:20] + "..." if self.session_manager.csrf_token else None,
            'api_access_token': self.session_manager.api_access_token[:20] + "..." if self.session_manager.api_access_token else None,
            'last_activity': self.session_manager.last_activity,
            'cookies': dict(self.session_manager.session.cookies),
            'is_expired': self.session_manager.is_expired()
        }