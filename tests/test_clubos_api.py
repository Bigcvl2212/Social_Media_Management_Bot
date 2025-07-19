"""
Tests for ClubOS API Client functionality
"""

import pytest
import requests_mock
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSCredentials, MessageRequest
from services.authentication.clubhub_token_capture import ClubHubTokenCapture
from config.constants import (
    CLUBOS_BASE_URL, 
    CLUBOS_LOGIN_URL,
    MESSAGE_TYPE_SMS,
    MESSAGE_TYPE_EMAIL,
    DEFAULT_MEMBER_ID
)

class TestClubOSCredentials:
    """Test ClubOS credentials data class"""
    
    def test_credentials_creation(self):
        """Test creating credentials"""
        creds = ClubOSCredentials(username="test_user", password="test_pass")
        assert creds.username == "test_user"
        assert creds.password == "test_pass"

class TestMessageRequest:
    """Test message request data class"""
    
    def test_sms_message_request(self):
        """Test creating SMS message request"""
        request = MessageRequest(
            member_id="123456",
            message_type=MESSAGE_TYPE_SMS,
            message_content="Test SMS message"
        )
        assert request.member_id == "123456"
        assert request.message_type == MESSAGE_TYPE_SMS
        assert request.message_content == "Test SMS message"
        assert request.subject is None
    
    def test_email_message_request(self):
        """Test creating Email message request"""
        request = MessageRequest(
            member_id="123456",
            message_type=MESSAGE_TYPE_EMAIL,
            message_content="Test email content",
            subject="Test Subject"
        )
        assert request.member_id == "123456"
        assert request.message_type == MESSAGE_TYPE_EMAIL
        assert request.message_content == "Test email content"
        assert request.subject == "Test Subject"

class TestClubOSAPIClient:
    """Test ClubOS API Client functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        creds = ClubOSCredentials(username="test_user", password="test_pass")
        return ClubOSAPIClient(creds)
    
    @pytest.fixture
    def mock_login_response(self):
        """Mock successful login response"""
        return """
        <html>
        <head>
            <meta name="csrf-token" content="test-csrf-token-123">
        </head>
        <body>
            <div>Dashboard</div>
            <script>
                window.config = {
                    apiV3AccessToken: "test-api-token-456"
                };
            </script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def mock_member_profile_response(self):
        """Mock member profile page response"""
        return """
        <html>
        <body>
            <form action="/action/Dashboard/member/123456" method="POST">
                <input type="hidden" name="_token" value="form-csrf-token">
                <input type="hidden" name="member_id" value="123456">
                <textarea name="message_content"></textarea>
                <select name="message_type">
                    <option value="sms">SMS</option>
                    <option value="email">Email</option>
                </select>
                <button type="submit">Send Message</button>
            </form>
        </body>
        </html>
        """
    
    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.credentials.username == "test_user"
        assert client.credentials.password == "test_pass"
        assert not client.session_manager.authenticated
        assert client.session_manager.csrf_token is None
    
    def test_csrf_token_extraction(self, client, mock_login_response):
        """Test CSRF token extraction from HTML"""
        token = client._extract_csrf_token(mock_login_response)
        assert token == "test-csrf-token-123"
    
    def test_csrf_token_extraction_no_token(self, client):
        """Test CSRF token extraction when no token present"""
        html = "<html><body>No token here</body></html>"
        token = client._extract_csrf_token(html)
        assert token is None
    
    def test_form_data_extraction(self, client, mock_member_profile_response):
        """Test form data extraction from member profile"""
        message_request = MessageRequest(
            member_id="123456",
            message_type=MESSAGE_TYPE_SMS,
            message_content="Test message"
        )
        
        form_data = client._extract_form_data(mock_member_profile_response, message_request)
        
        assert "_token" in form_data
        assert form_data["_token"] == "form-csrf-token"
        assert form_data["member_id"] == "123456"
        assert form_data["message_content"] == "Test message"
        assert form_data["message_type"] == MESSAGE_TYPE_SMS
    
    def test_login_success(self, requests_mock, client, mock_login_response):
        """Test successful login"""
        # Mock login page GET
        requests_mock.get(CLUBOS_LOGIN_URL, text=mock_login_response)
        
        # Mock login POST with redirect to dashboard
        dashboard_url = f"{CLUBOS_BASE_URL}/action/Dashboard"
        requests_mock.post(CLUBOS_LOGIN_URL, headers={'Location': dashboard_url}, status_code=302)
        requests_mock.get(dashboard_url, text='<html><body>Dashboard</body></html>')
        
        success = client.login()
        assert success
        assert client.session_manager.authenticated
        assert client.session_manager.csrf_token == "test-csrf-token-123"
    
    def test_login_failure(self, requests_mock, client):
        """Test login failure"""
        # Mock login page GET
        requests_mock.get(CLUBOS_LOGIN_URL, text="<html><body>Login</body></html>")
        
        # Mock login POST that stays on login page (failure)
        requests_mock.post(CLUBOS_LOGIN_URL, text="<html><body>Login failed</body></html>")
        
        success = client.login()
        assert not success
        assert not client.session_manager.authenticated
    
    def test_session_expiry(self, client):
        """Test session expiry detection"""
        # New session should be expired
        assert client.session_manager.is_expired()
        
        # After updating activity, should not be expired
        client.session_manager.update_activity()
        assert not client.session_manager.is_expired()
    
    def test_get_session_info(self, client):
        """Test session info retrieval"""
        info = client.get_session_info()
        
        assert "authenticated" in info
        assert "csrf_token" in info
        assert "api_access_token" in info
        assert "last_activity" in info
        assert "cookies" in info
        assert "is_expired" in info
        
        assert info["authenticated"] == False
        assert info["csrf_token"] is None

class TestClubHubTokenCapture:
    """Test token capture functionality"""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock session"""
        session = Mock()
        session.cookies = []
        return session
    
    @pytest.fixture
    def token_capture(self, mock_session):
        """Create token capture instance"""
        return ClubHubTokenCapture(mock_session)
    
    def test_html_token_extraction(self, token_capture):
        """Test token extraction from HTML"""
        html = """
        <html>
        <head>
            <meta name="csrf-token" content="test-csrf-123">
        </head>
        <body>
            <script>
                var apiToken = "test-api-456";
                var csrf_token = "test-csrf-script";
                window.config = {
                    _token: "test-token-789"
                };
            </script>
        </body>
        </html>
        """
        
        tokens = token_capture._capture_html_tokens(html)
        # Check that some tokens were found
        assert len(tokens) > 0
        # The regex should find api_token and _token from script
        assert "api_token" in tokens
        assert tokens["api_token"] == "test-api-456"
    
    def test_meta_token_extraction(self, token_capture):
        """Test meta tag token extraction"""
        html = """
        <html>
        <head>
            <meta name="csrf-token" content="meta-csrf-token">
            <meta name="_token" content="meta-general-token">
        </head>
        </html>
        """
        
        meta_tokens = token_capture._capture_meta_tokens(html)
        assert "csrf-token" in meta_tokens
        assert meta_tokens["csrf-token"] == "meta-csrf-token"
        assert "_token" in meta_tokens
        assert meta_tokens["_token"] == "meta-general-token"
    
    def test_form_data_extraction(self, token_capture):
        """Test form data extraction"""
        html = """
        <html>
        <body>
            <form action="/submit" method="POST">
                <input type="hidden" name="csrf_token" value="form-csrf-123">
                <input type="hidden" name="session_id" value="session-456">
                <input type="text" name="username" placeholder="Username">
                <select name="role">
                    <option value="admin">Admin</option>
                    <option value="user">User</option>
                </select>
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
        """
        
        forms = token_capture._capture_form_data(html)
        assert len(forms) == 1
        
        form = forms[0]
        assert form["action"] == "/submit"
        assert form["method"] == "POST"
        assert "csrf_token" in form["hidden_fields"]
        assert form["hidden_fields"]["csrf_token"] == "form-csrf-123"
        assert "username" in form["input_fields"]
        assert "role" in form["select_fields"]

class TestIntegration:
    """Integration tests for the ClubOS API system"""
    
    @pytest.fixture
    def test_credentials(self):
        """Get test credentials from environment or use defaults"""
        return ClubOSCredentials(
            username=os.getenv('CLUBOS_TEST_USERNAME', 'test_user'),
            password=os.getenv('CLUBOS_TEST_PASSWORD', 'test_pass')
        )
    
    def test_message_request_creation(self):
        """Test creating different types of message requests"""
        # SMS message
        sms_request = MessageRequest(
            member_id=DEFAULT_MEMBER_ID,
            message_type=MESSAGE_TYPE_SMS,
            message_content="Test SMS content"
        )
        assert sms_request.message_type == MESSAGE_TYPE_SMS
        assert sms_request.subject is None
        
        # Email message
        email_request = MessageRequest(
            member_id=DEFAULT_MEMBER_ID,
            message_type=MESSAGE_TYPE_EMAIL,
            message_content="Test email content",
            subject="Test Subject"
        )
        assert email_request.message_type == MESSAGE_TYPE_EMAIL
        assert email_request.subject == "Test Subject"
    
    def test_client_workflow_structure(self, test_credentials):
        """Test the basic client workflow structure"""
        client = ClubOSAPIClient(test_credentials)
        
        # Test that client is properly initialized
        assert client.credentials.username == test_credentials.username
        assert client.credentials.password == test_credentials.password
        assert not client.session_manager.authenticated
        
        # Test session info retrieval
        info = client.get_session_info()
        assert isinstance(info, dict)
        assert "authenticated" in info
        assert info["authenticated"] == False
    
    @patch('requests.Session.get')
    @patch('requests.Session.post')
    def test_mock_successful_workflow(self, mock_post, mock_get, test_credentials):
        """Test successful workflow with mocked responses"""
        client = ClubOSAPIClient(test_credentials)
        
        # Mock login page response
        login_page_response = Mock()
        login_page_response.text = '<meta name="csrf-token" content="test-token">'
        login_page_response.status_code = 200
        
        # Mock login post response (redirect to dashboard)
        login_post_response = Mock()
        login_post_response.url = f"{CLUBOS_BASE_URL}/action/Dashboard"
        login_post_response.text = '<html><body>Dashboard</body></html>'
        login_post_response.status_code = 200
        
        # Configure mocks
        mock_get.return_value = login_page_response
        mock_post.return_value = login_post_response
        
        # Test login
        success = client.login()
        assert success
        assert client.session_manager.authenticated
        
        # Verify requests were made
        assert mock_get.called
        assert mock_post.called

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])