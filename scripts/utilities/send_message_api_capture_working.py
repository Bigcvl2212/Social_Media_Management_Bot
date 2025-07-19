"""
ClubOS API Capture Working Implementation

This script captures and analyzes the exact network traffic patterns
from both working form submissions and failing API endpoint calls
to understand what's different between them.
"""

import os
import sys
import logging
import json
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSCredentials, MessageRequest
from services.authentication.clubhub_token_capture import ClubHubTokenCapture
from config.constants import MESSAGE_TYPE_SMS, MESSAGE_TYPE_EMAIL, DEFAULT_MEMBER_ID

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClubOSTrafficCapture:
    """Captures and analyzes ClubOS API traffic patterns"""
    
    def __init__(self, username: str, password: str):
        self.credentials = ClubOSCredentials(username=username, password=password)
        self.client = ClubOSAPIClient(self.credentials)
        self.token_capture = None
        self.captured_data = {}
        
    def capture_full_workflow(self, member_id: str = DEFAULT_MEMBER_ID) -> Dict[str, Any]:
        """
        Capture the complete workflow from login to message sending,
        analyzing each step for authentication patterns.
        """
        logger.info("Starting full workflow capture...")
        
        # Initialize token capture with the client's session
        self.token_capture = ClubHubTokenCapture(self.client.session_manager.session)
        
        # Step 1: Capture login process
        logger.info("Step 1: Capturing login process...")
        login_success = self._capture_login()
        
        if not login_success:
            logger.error("Login failed - cannot continue capture")
            return {}
        
        # Step 2: Capture dashboard navigation
        logger.info("Step 2: Capturing dashboard navigation...")
        self._capture_dashboard()
        
        # Step 3: Capture member profile access
        logger.info("Step 3: Capturing member profile access...")
        self._capture_member_profile(member_id)
        
        # Step 4: Capture working form submission
        logger.info("Step 4: Capturing working form submission...")
        self._capture_form_submission(member_id)
        
        # Step 5: Capture failing API endpoint call
        logger.info("Step 5: Capturing failing API endpoint call...")
        self._capture_api_endpoint_call(member_id)
        
        # Step 6: Analyze differences
        logger.info("Step 6: Analyzing differences...")
        analysis = self._analyze_captured_data()
        
        return {
            'captured_data': self.captured_data,
            'analysis': analysis,
            'recommendations': self._generate_recommendations(analysis)
        }
    
    def _capture_login(self) -> bool:
        """Capture login process and tokens"""
        try:
            # Get login page
            response = self.client.session_manager.session.get(
                self.client.credentials.username  # Using login URL from constants
            )
            
            # Capture tokens from login page
            login_page_data = self.token_capture.capture_all_tokens(response, 'login_page')
            self.captured_data['login_page'] = login_page_data
            
            # Perform login
            login_success = self.client.login()
            
            if login_success:
                # Capture post-login state
                dashboard_response = self.client.session_manager.session.get(
                    f"{self.client.credentials.username}/action/Dashboard"  # Dashboard URL
                )
                
                post_login_data = self.token_capture.capture_all_tokens(dashboard_response, 'post_login')
                self.captured_data['post_login'] = post_login_data
            
            return login_success
            
        except Exception as e:
            logger.error(f"Error capturing login: {str(e)}")
            return False
    
    def _capture_dashboard(self):
        """Capture dashboard state and tokens"""
        try:
            from config.constants import CLUBOS_DASHBOARD_URL
            
            response = self.client.session_manager.session.get(CLUBOS_DASHBOARD_URL)
            dashboard_data = self.token_capture.capture_all_tokens(response, 'dashboard')
            self.captured_data['dashboard'] = dashboard_data
            
        except Exception as e:
            logger.error(f"Error capturing dashboard: {str(e)}")
    
    def _capture_member_profile(self, member_id: str):
        """Capture member profile page state and tokens"""
        try:
            from config.constants import CLUBOS_MEMBER_PROFILE_URL
            
            member_url = f"{CLUBOS_MEMBER_PROFILE_URL}/{member_id}"
            response = self.client.session_manager.session.get(member_url)
            
            profile_data = self.token_capture.capture_all_tokens(response, 'member_profile')
            self.captured_data['member_profile'] = profile_data
            
        except Exception as e:
            logger.error(f"Error capturing member profile: {str(e)}")
    
    def _capture_form_submission(self, member_id: str):
        """Capture the working form submission process"""
        try:
            logger.info("Capturing working form submission process...")
            
            # Create a test message request
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_SMS,
                message_content="Test capture message - ignore"
            )
            
            # Capture the form submission (without actually sending)
            member_url = f"{CLUBOS_MEMBER_PROFILE_URL}/{member_id}"
            
            # Get the form page first
            response = self.client.session_manager.session.get(member_url)
            form_page_data = self.token_capture.capture_all_tokens(response, 'form_page')
            self.captured_data['form_page'] = form_page_data
            
            # Extract form data that would be submitted
            form_data = self.client._extract_form_data(response.text, message_request)
            self.captured_data['form_submission_data'] = {
                'url': member_url,
                'method': 'POST',
                'form_data': form_data,
                'headers': dict(self.client.session_manager.session.headers)
            }
            
            logger.info(f"Captured form data: {list(form_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error capturing form submission: {str(e)}")
    
    def _capture_api_endpoint_call(self, member_id: str):
        """Capture the failing API endpoint call"""
        try:
            logger.info("Capturing API endpoint call process...")
            
            from config.constants import CLUBOS_API_SEND_MESSAGE_URL, API_HEADERS
            
            # Create a test message request
            message_request = MessageRequest(
                member_id=member_id,
                message_type=MESSAGE_TYPE_SMS,
                message_content="Test API capture message - ignore"
            )
            
            # Prepare API data (without actually sending)
            api_data = {
                'member_id': message_request.member_id,
                'message_type': message_request.message_type,
                'message': message_request.message_content
            }
            
            # Prepare headers
            headers = API_HEADERS.copy()
            headers['Referer'] = f"{CLUBOS_MEMBER_PROFILE_URL}/{member_id}"
            
            # Add authentication headers
            if self.client.session_manager.csrf_token:
                headers['X-CSRF-TOKEN'] = self.client.session_manager.csrf_token
                
            if self.client.session_manager.api_access_token:
                headers['Authorization'] = f"Bearer {self.client.session_manager.api_access_token}"
            
            self.captured_data['api_endpoint_data'] = {
                'url': CLUBOS_API_SEND_MESSAGE_URL,
                'method': 'POST',
                'api_data': api_data,
                'headers': headers,
                'cookies': dict(self.client.session_manager.session.cookies)
            }
            
            logger.info("Captured API endpoint configuration")
            
        except Exception as e:
            logger.error(f"Error capturing API endpoint: {str(e)}")
    
    def _analyze_captured_data(self) -> Dict[str, Any]:
        """Analyze differences between working and failing approaches"""
        analysis = {
            'header_differences': {},
            'data_differences': {},
            'token_differences': {},
            'url_differences': {},
            'method_differences': {}
        }
        
        try:
            # Compare form submission vs API endpoint
            form_data = self.captured_data.get('form_submission_data', {})
            api_data = self.captured_data.get('api_endpoint_data', {})
            
            # Header differences
            form_headers = form_data.get('headers', {})
            api_headers = api_data.get('headers', {})
            
            analysis['header_differences'] = {
                'form_only': {k: v for k, v in form_headers.items() if k not in api_headers},
                'api_only': {k: v for k, v in api_headers.items() if k not in form_headers},
                'different_values': {
                    k: {'form': form_headers[k], 'api': api_headers[k]} 
                    for k in set(form_headers.keys()) & set(api_headers.keys())
                    if form_headers[k] != api_headers[k]
                }
            }
            
            # Data format differences
            form_payload = form_data.get('form_data', {})
            api_payload = api_data.get('api_data', {})
            
            analysis['data_differences'] = {
                'form_fields': list(form_payload.keys()),
                'api_fields': list(api_payload.keys()),
                'form_only_fields': [k for k in form_payload.keys() if k not in api_payload],
                'api_only_fields': [k for k in api_payload.keys() if k not in form_payload]
            }
            
            # URL differences
            analysis['url_differences'] = {
                'form_url': form_data.get('url', ''),
                'api_url': api_data.get('url', ''),
                'same_domain': self._same_domain(form_data.get('url', ''), api_data.get('url', ''))
            }
            
            # Token analysis
            if 'member_profile' in self.captured_data:
                profile_tokens = self.captured_data['member_profile'].get('tokens', {})
                analysis['token_differences'] = self.token_capture.analyze_token_differences(
                    {'tokens': profile_tokens},
                    {'tokens': profile_tokens}  # Same for now, will be different in real scenario
                )
            
        except Exception as e:
            logger.error(f"Error analyzing captured data: {str(e)}")
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        try:
            # Check header differences
            header_diff = analysis.get('header_differences', {})
            if header_diff.get('form_only'):
                recommendations.append(
                    f"Add form-specific headers to API calls: {list(header_diff['form_only'].keys())}"
                )
            
            # Check data differences
            data_diff = analysis.get('data_differences', {})
            if data_diff.get('form_only_fields'):
                recommendations.append(
                    f"Include form-specific fields in API payload: {data_diff['form_only_fields']}"
                )
            
            # Check URL patterns
            url_diff = analysis.get('url_differences', {})
            if not url_diff.get('same_domain', True):
                recommendations.append("Ensure API calls use the same domain as form submissions")
            
            # General recommendations
            recommendations.extend([
                "Ensure all hidden form fields are included in API calls",
                "Verify CSRF tokens are properly extracted and included",
                "Check that session cookies are maintained between requests",
                "Confirm Content-Type headers match form submission pattern",
                "Validate that Referer headers point to the correct member profile page"
            ])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def _same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs have the same domain"""
        try:
            from urllib.parse import urlparse
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            return domain1 == domain2
        except:
            return False
    
    def save_capture_data(self, filename: str = "clubos_capture_data.json"):
        """Save captured data to file for analysis"""
        try:
            # Create output directory
            output_dir = "/tmp/clubos_analysis"
            os.makedirs(output_dir, exist_ok=True)
            
            filepath = os.path.join(output_dir, filename)
            
            # Prepare data for JSON serialization
            serializable_data = self._make_serializable(self.captured_data)
            
            with open(filepath, 'w') as f:
                json.dump(serializable_data, f, indent=2)
            
            logger.info(f"Capture data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving capture data: {str(e)}")
            return None
    
    def _make_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format"""
        if isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif hasattr(data, '__dict__'):
            return self._make_serializable(data.__dict__)
        else:
            try:
                json.dumps(data)
                return data
            except (TypeError, ValueError):
                return str(data)

def main():
    """Main function for traffic capture and analysis"""
    
    # Get credentials
    username = os.getenv('CLUBOS_USERNAME', 'your_username')
    password = os.getenv('CLUBOS_PASSWORD', 'your_password')
    member_id = os.getenv('CLUBOS_MEMBER_ID', DEFAULT_MEMBER_ID)
    
    if username == 'your_username' or password == 'your_password':
        logger.warning("Please set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables")
        return
    
    # Create capture instance
    capture = ClubOSTrafficCapture(username, password)
    
    # Run full capture workflow
    logger.info("Starting ClubOS traffic capture and analysis...")
    results = capture.capture_full_workflow(member_id)
    
    # Save results
    filepath = capture.save_capture_data()
    
    # Display summary
    logger.info("=" * 60)
    logger.info("CAPTURE SUMMARY")
    logger.info("=" * 60)
    
    if results.get('analysis'):
        analysis = results['analysis']
        
        logger.info("Header Differences:")
        for key, value in analysis.get('header_differences', {}).items():
            if value:
                logger.info(f"  {key}: {len(value)} items")
        
        logger.info("\nData Differences:")
        data_diff = analysis.get('data_differences', {})
        logger.info(f"  Form fields: {len(data_diff.get('form_fields', []))}")
        logger.info(f"  API fields: {len(data_diff.get('api_fields', []))}")
        logger.info(f"  Form-only fields: {data_diff.get('form_only_fields', [])}")
        
        logger.info("\nRecommendations:")
        for i, rec in enumerate(results.get('recommendations', []), 1):
            logger.info(f"  {i}. {rec}")
    
    if filepath:
        logger.info(f"\nDetailed analysis saved to: {filepath}")
    
    logger.info("\n✅ Capture and analysis complete!")

if __name__ == "__main__":
    main()