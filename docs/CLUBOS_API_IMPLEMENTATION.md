# ClubOS API Implementation Guide

## Overview
This document provides detailed implementation guidance for integrating ClubOS messaging functionality into applications, based on our research and working solutions.

## Architecture

### Core Components

#### 1. ClubOSAPIClient (`services/api/clubos_api_client.py`)
Main client class that handles authentication and messaging operations.

```python
from services.api.clubos_api_client import ClubOSAPIClient, ClubOSCredentials, MessageRequest

# Initialize client
credentials = ClubOSCredentials(username="your_username", password="your_password")
client = ClubOSAPIClient(credentials)

# Send SMS message (working approach)
message_request = MessageRequest(
    member_id="187032782",
    message_type="sms", 
    message_content="Hello from ClubOS API!"
)
success = client.send_message_via_form_submission(message_request)
```

#### 2. ClubHubTokenCapture (`services/authentication/clubhub_token_capture.py`)
Utility for capturing and analyzing authentication tokens and session data.

```python
from services.authentication.clubhub_token_capture import ClubHubTokenCapture

# Capture tokens from session
token_capture = ClubHubTokenCapture(session)
tokens = token_capture.capture_all_tokens(response, "member_profile")
```

#### 3. Configuration (`config/constants.py`)
Central configuration for URLs, headers, and API settings.

## Implementation Approaches

### ✅ Working Approach: Form Submission

This approach works reliably and should be used for production implementations.

#### Process Flow
1. **Authenticate**: Login with username/password
2. **Navigate**: Access member profile page
3. **Extract**: Get form data and hidden fields
4. **Submit**: POST form data to profile page

#### Example Implementation
```python
def send_message_working(client, member_id, message_type, content, subject=None):
    """Send message using working form submission approach"""
    
    # Ensure authenticated
    if not client.login():
        return False
    
    # Create message request
    message_request = MessageRequest(
        member_id=member_id,
        message_type=message_type,
        message_content=content,
        subject=subject
    )
    
    # Send via form submission
    return client.send_message_via_form_submission(message_request)
```

#### Key Success Factors
- **Browser Headers**: Use realistic browser User-Agent and headers
- **Session Cookies**: Maintain all session cookies throughout the process
- **CSRF Tokens**: Extract and include CSRF tokens from the member profile page
- **Hidden Fields**: Include all hidden form fields in the submission
- **Correct Referer**: Set Referer header to the member profile URL

### ❌ API Endpoint Approach (Currently Failing)

This approach is implemented for research purposes but currently fails.

#### Process Flow
1. **Authenticate**: Login with username/password  
2. **Extract Tokens**: Get CSRF and API access tokens
3. **Call API**: POST to `/action/Api/send-message` endpoint

#### Current Issues
- Returns "Something isn't right" error
- Fails even with proper authentication context
- Missing some required authentication layer

#### Example Implementation (For Research)
```python
def send_message_api_research(client, member_id, message_type, content):
    """Research approach using API endpoints (currently fails)"""
    
    # Ensure authenticated
    if not client.login():
        return False, "Authentication failed"
    
    # Create message request
    message_request = MessageRequest(
        member_id=member_id,
        message_type=message_type,
        message_content=content
    )
    
    # Try API endpoint (will likely fail)
    success, error = client.send_message_via_api_endpoint(message_request)
    return success, error
```

## Authentication Implementation

### Session Management
```python
class ClubOSSession:
    """Manages ClubOS session state"""
    
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.csrf_token = None
        self.api_access_token = None
        self.last_activity = None
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.last_activity:
            return True
        return time.time() - self.last_activity > SESSION_TIMEOUT
```

### Login Process
```python
def login(self) -> bool:
    """Authenticate with ClubOS"""
    
    # Get login page
    response = self.session_manager.session.get(CLUBOS_LOGIN_URL)
    
    # Extract CSRF token
    csrf_token = self._extract_csrf_token(response.text)
    
    # Prepare login data
    login_data = {
        'username': self.credentials.username,
        'password': self.credentials.password
    }
    
    if csrf_token:
        login_data['_token'] = csrf_token
    
    # Submit login
    response = self.session_manager.session.post(
        CLUBOS_LOGIN_URL,
        data=login_data,
        headers=headers
    )
    
    return self._check_login_success(response)
```

### Token Extraction
```python
def _extract_csrf_token(self, html_content: str) -> Optional[str]:
    """Extract CSRF token from HTML"""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Common CSRF patterns
    patterns = [
        ('meta', {'name': 'csrf-token'}),
        ('input', {'name': '_token'}),
    ]
    
    for tag_name, attrs in patterns:
        element = soup.find(tag_name, attrs)
        if element:
            return element.get('content') or element.get('value')
    
    return None
```

## Message Sending Implementation

### SMS Messages
```python
def send_sms(client, member_id: str, message: str) -> bool:
    """Send SMS message to ClubOS member"""
    
    message_request = MessageRequest(
        member_id=member_id,
        message_type=MESSAGE_TYPE_SMS,
        message_content=message
    )
    
    return client.send_message_via_form_submission(message_request)
```

### Email Messages
```python
def send_email(client, member_id: str, subject: str, message: str) -> bool:
    """Send Email message to ClubOS member"""
    
    message_request = MessageRequest(
        member_id=member_id,
        message_type=MESSAGE_TYPE_EMAIL,
        message_content=message,
        subject=subject
    )
    
    return client.send_message_via_form_submission(message_request)
```

## Error Handling

### Common Error Patterns
```python
ERROR_PATTERNS = [
    "Something isn't right",
    "unauthorized",
    "invalid",
    "error"
]

def _check_message_success(self, response: requests.Response) -> bool:
    """Check if message was sent successfully"""
    
    if response.status_code != 200:
        return False
    
    content = response.text.lower()
    
    # Check for error patterns
    if any(error in content for error in ERROR_PATTERNS):
        return False
    
    # Look for success indicators
    success_indicators = ['success', 'sent', 'delivered']
    return any(indicator in content for indicator in success_indicators)
```

### Session Recovery
```python
def _ensure_authenticated(self) -> bool:
    """Ensure valid authenticated session"""
    
    if not self.session_manager.authenticated or self.session_manager.is_expired():
        logger.info("Re-authenticating...")
        return self.login()
    
    return True
```

## Configuration Setup

### Environment Variables
```bash
# Required credentials
export CLUBOS_USERNAME="your_clubos_username"
export CLUBOS_PASSWORD="your_clubos_password"

# Optional configuration
export CLUBOS_MEMBER_ID="187032782"  # Default test member (Jeremy Mayo)
```

### Header Configuration
```python
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
```

## Testing and Validation

### Basic Functionality Test
```python
def test_clubos_messaging():
    """Test ClubOS messaging functionality"""
    
    # Setup
    credentials = ClubOSCredentials(
        username=os.getenv('CLUBOS_USERNAME'),
        password=os.getenv('CLUBOS_PASSWORD')
    )
    client = ClubOSAPIClient(credentials)
    
    # Test SMS
    sms_success = client.send_message_via_form_submission(
        MessageRequest(
            member_id="187032782",
            message_type="sms",
            message_content="Test SMS message"
        )
    )
    
    # Test Email
    email_success = client.send_message_via_form_submission(
        MessageRequest(
            member_id="187032782", 
            message_type="email",
            message_content="Test email message",
            subject="Test Email Subject"
        )
    )
    
    return sms_success and email_success
```

### Debug Session Information
```python
def debug_session_info(client):
    """Get debugging information about current session"""
    
    info = client.get_session_info()
    print(f"Authenticated: {info['authenticated']}")
    print(f"CSRF Token: {info['csrf_token']}")
    print(f"API Token: {info['api_access_token']}")
    print(f"Cookies: {len(info['cookies'])} cookies")
    print(f"Session Expired: {info['is_expired']}")
```

## Performance Considerations

### Session Reuse
- Maintain session objects across multiple message sends
- Check session expiration before each operation
- Re-authenticate only when necessary

### Rate Limiting
- Implement delays between consecutive messages
- Monitor for rate limiting responses
- Queue messages for batch processing

### Error Recovery
- Retry failed messages with exponential backoff
- Log detailed error information for debugging
- Implement circuit breaker pattern for repeated failures

## Security Best Practices

### Credential Management
- Store credentials securely using environment variables
- Never commit credentials to source control
- Use secure credential storage systems in production

### Session Security
- Clear session data after use
- Implement session timeout handling
- Use HTTPS for all requests

### Logging Security
- Sanitize logs to remove sensitive data
- Log authentication events for audit trails
- Implement proper log rotation and retention

## Integration Examples

### FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class SMSRequest(BaseModel):
    member_id: str
    message: str

@app.post("/send-sms")
async def send_sms_endpoint(request: SMSRequest):
    """Send SMS via ClubOS API"""
    
    try:
        client = get_clubos_client()  # Your client initialization
        success = send_sms(client, request.member_id, request.message)
        
        if success:
            return {"status": "success", "message": "SMS sent"}
        else:
            raise HTTPException(status_code=500, detail="SMS sending failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Celery Task Integration
```python
from celery import Celery

app = Celery('clubos_tasks')

@app.task(bind=True, max_retries=3)
def send_clubos_message(self, member_id, message_type, content, subject=None):
    """Async task for sending ClubOS messages"""
    
    try:
        client = get_clubos_client()
        
        message_request = MessageRequest(
            member_id=member_id,
            message_type=message_type,
            message_content=content,
            subject=subject
        )
        
        success = client.send_message_via_form_submission(message_request)
        
        if not success:
            raise Exception("Message sending failed")
            
        return {"status": "success"}
        
    except Exception as e:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            raise e
```

## Conclusion

The current working implementation provides a reliable way to send SMS and Email messages through ClubOS using form submission. While direct API endpoint calls remain unsuccessful, the form submission approach offers a stable foundation for production use.

Future development should focus on:
1. Understanding why API endpoints fail
2. Optimizing the form submission approach
3. Implementing robust error handling and retry logic
4. Adding comprehensive monitoring and logging

The implementation is designed to be maintainable and extensible, with clear separation of concerns and comprehensive error handling.