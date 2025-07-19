"""
ClubHub Token Capture Utility

This module captures and manages various tokens and authentication data
from ClubOS sessions to understand what's needed for successful API calls.
"""

import re
import json
import logging
from typing import Dict, Optional, List, Any
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

class ClubHubTokenCapture:
    """Captures and analyzes authentication tokens from ClubOS sessions"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.captured_tokens = {}
        self.captured_headers = {}
        self.captured_cookies = {}
        
    def capture_all_tokens(self, response: requests.Response, page_type: str = "unknown") -> Dict[str, Any]:
        """
        Capture all possible tokens and authentication data from a response.
        
        Args:
            response: HTTP response to analyze
            page_type: Type of page (login, dashboard, member_profile, etc.)
            
        Returns:
            Dict containing all captured authentication data
        """
        capture_data = {
            'page_type': page_type,
            'url': response.url,
            'status_code': response.status_code,
            'tokens': self._capture_html_tokens(response.text),
            'cookies': self._capture_cookies(response),
            'headers': self._capture_response_headers(response),
            'scripts': self._capture_script_tokens(response.text),
            'forms': self._capture_form_data(response.text),
            'meta_tags': self._capture_meta_tokens(response.text)
        }
        
        # Store in instance for later analysis
        self.captured_tokens[page_type] = capture_data
        
        logger.info(f"Captured tokens for {page_type}: {len(capture_data['tokens'])} tokens found")
        return capture_data
    
    def _capture_html_tokens(self, html_content: str) -> Dict[str, str]:
        """Extract tokens from HTML content using various patterns"""
        tokens = {}
        
        # Common token patterns
        token_patterns = [
            (r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', 'csrf_token'),
            (r'_token["\']?\s*[:=]\s*["\']([^"\']+)', '_token'),
            (r'api[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', 'api_token'),
            (r'access[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', 'access_token'),
            (r'auth[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', 'auth_token'),
            (r'session[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', 'session_token'),
            (r'apiV3AccessToken["\']?\s*[:=]\s*["\']([^"\']+)', 'api_v3_access_token'),
            (r'X-CSRF-TOKEN["\']?\s*[:=]\s*["\']([^"\']+)', 'x_csrf_token'),
            (r'authenticity[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', 'authenticity_token'),
        ]
        
        for pattern, name in token_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                tokens[name] = matches[0]
                logger.debug(f"Found {name}: {matches[0][:20]}...")
        
        return tokens
    
    def _capture_cookies(self, response: requests.Response) -> Dict[str, str]:
        """Extract all cookies from response"""
        cookies = {}
        
        for cookie in response.cookies:
            cookies[cookie.name] = cookie.value
            
        # Also check Set-Cookie headers
        set_cookies = response.headers.get_list('Set-Cookie') if hasattr(response.headers, 'get_list') else []
        for cookie_header in set_cookies:
            # Parse cookie header
            cookie_parts = cookie_header.split(';')[0].split('=', 1)
            if len(cookie_parts) == 2:
                name, value = cookie_parts
                cookies[name.strip()] = value.strip()
        
        logger.debug(f"Captured {len(cookies)} cookies")
        return cookies
    
    def _capture_response_headers(self, response: requests.Response) -> Dict[str, str]:
        """Extract relevant headers from response"""
        relevant_headers = [
            'X-CSRF-Token',
            'X-Auth-Token', 
            'Authorization',
            'X-Requested-With',
            'X-API-Token',
            'X-Session-Token',
            'Location',
            'Set-Cookie'
        ]
        
        headers = {}
        for header in relevant_headers:
            if header in response.headers:
                headers[header] = response.headers[header]
        
        return headers
    
    def _capture_script_tokens(self, html_content: str) -> Dict[str, Any]:
        """Extract tokens and configuration from JavaScript code"""
        script_data = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for configuration objects
                    config_patterns = [
                        (r'window\.config\s*=\s*({[^}]+})', 'window_config'),
                        (r'window\.Laravel\s*=\s*({[^}]+})', 'laravel_config'),
                        (r'window\.App\s*=\s*({[^}]+})', 'app_config'),
                        (r'var\s+config\s*=\s*({[^}]+})', 'var_config'),
                        (r'const\s+config\s*=\s*({[^}]+})', 'const_config'),
                    ]
                    
                    for pattern, name in config_patterns:
                        match = re.search(pattern, script_content, re.IGNORECASE | re.DOTALL)
                        if match:
                            try:
                                # Try to parse as JSON
                                config_obj = json.loads(match.group(1))
                                script_data[name] = config_obj
                            except json.JSONDecodeError:
                                # Store as string if JSON parsing fails
                                script_data[name] = match.group(1)
                    
                    # Look for API endpoints
                    api_patterns = [
                        r'api[_/]send[_-]message["\']?\s*[:=]\s*["\']([^"\']+)',
                        r'api[_/]follow[_-]up["\']?\s*[:=]\s*["\']([^"\']+)',
                        r'api[_/]member["\']?\s*[:=]\s*["\']([^"\']+)',
                        r'apiEndpoint["\']?\s*[:=]\s*["\']([^"\']+)',
                        r'baseUrl["\']?\s*[:=]\s*["\']([^"\']+)',
                    ]
                    
                    for pattern in api_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        if matches:
                            script_data[f'api_endpoint_{len(script_data)}'] = matches[0]
            
        except Exception as e:
            logger.warning(f"Error capturing script tokens: {str(e)}")
        
        return script_data
    
    def _capture_form_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract form data and hidden fields"""
        forms_data = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET'),
                    'hidden_fields': {},
                    'input_fields': {},
                    'select_fields': {}
                }
                
                # Extract hidden inputs
                hidden_inputs = form.find_all('input', {'type': 'hidden'})
                for input_field in hidden_inputs:
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    if name:
                        form_data['hidden_fields'][name] = value
                
                # Extract other inputs
                inputs = form.find_all('input')
                for input_field in inputs:
                    input_type = input_field.get('type', 'text')
                    if input_type != 'hidden':
                        name = input_field.get('name')
                        if name:
                            form_data['input_fields'][name] = {
                                'type': input_type,
                                'value': input_field.get('value', ''),
                                'placeholder': input_field.get('placeholder', ''),
                                'required': input_field.get('required', False)
                            }
                
                # Extract select fields
                selects = form.find_all('select')
                for select in selects:
                    name = select.get('name')
                    if name:
                        options = [option.get('value', '') for option in select.find_all('option')]
                        form_data['select_fields'][name] = {
                            'options': options,
                            'selected': select.get('value', '')
                        }
                
                forms_data.append(form_data)
        
        except Exception as e:
            logger.warning(f"Error capturing form data: {str(e)}")
        
        return forms_data
    
    def _capture_meta_tokens(self, html_content: str) -> Dict[str, str]:
        """Extract tokens from meta tags"""
        meta_tokens = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Common meta tag patterns for tokens
            meta_patterns = [
                {'name': 'csrf-token'},
                {'name': '_token'},
                {'name': 'api-token'},
                {'property': 'csrf-token'},
                {'http-equiv': 'X-CSRF-Token'}
            ]
            
            for pattern in meta_patterns:
                meta_tag = soup.find('meta', pattern)
                if meta_tag:
                    content = meta_tag.get('content', '')
                    if content:
                        key = list(pattern.values())[0]
                        meta_tokens[key] = content
            
        except Exception as e:
            logger.warning(f"Error capturing meta tokens: {str(e)}")
        
        return meta_tokens
    
    def analyze_token_differences(self, working_tokens: Dict, failing_tokens: Dict) -> Dict[str, Any]:
        """
        Compare tokens from working vs failing requests to identify differences.
        
        Args:
            working_tokens: Tokens from successful form submission
            failing_tokens: Tokens from failed API call
            
        Returns:
            Analysis of differences
        """
        analysis = {
            'missing_in_failing': {},
            'different_values': {},
            'unique_to_failing': {},
            'recommendations': []
        }
        
        # Find tokens present in working but missing in failing
        for key, value in working_tokens.get('tokens', {}).items():
            if key not in failing_tokens.get('tokens', {}):
                analysis['missing_in_failing'][key] = value
        
        # Find tokens with different values
        for key, working_value in working_tokens.get('tokens', {}).items():
            if key in failing_tokens.get('tokens', {}):
                failing_value = failing_tokens['tokens'][key]
                if working_value != failing_value:
                    analysis['different_values'][key] = {
                        'working': working_value,
                        'failing': failing_value
                    }
        
        # Find tokens unique to failing
        for key, value in failing_tokens.get('tokens', {}).items():
            if key not in working_tokens.get('tokens', {}):
                analysis['unique_to_failing'][key] = value
        
        # Generate recommendations
        if analysis['missing_in_failing']:
            analysis['recommendations'].append(
                f"Add missing tokens to API calls: {list(analysis['missing_in_failing'].keys())}"
            )
        
        if analysis['different_values']:
            analysis['recommendations'].append(
                f"Check token generation for: {list(analysis['different_values'].keys())}"
            )
        
        return analysis
    
    def get_capture_summary(self) -> Dict[str, Any]:
        """Get summary of all captured authentication data"""
        summary = {
            'pages_analyzed': list(self.captured_tokens.keys()),
            'total_tokens_found': sum(len(data.get('tokens', {})) for data in self.captured_tokens.values()),
            'unique_tokens': set(),
            'common_patterns': {},
            'potential_api_requirements': []
        }
        
        # Collect all unique tokens
        for page_data in self.captured_tokens.values():
            summary['unique_tokens'].update(page_data.get('tokens', {}).keys())
        
        summary['unique_tokens'] = list(summary['unique_tokens'])
        
        # Identify common patterns
        token_counts = {}
        for page_data in self.captured_tokens.values():
            for token_name in page_data.get('tokens', {}).keys():
                token_counts[token_name] = token_counts.get(token_name, 0) + 1
        
        # Tokens that appear on multiple pages are likely important
        for token, count in token_counts.items():
            if count > 1:
                summary['common_patterns'][token] = count
        
        # Generate API requirements based on patterns
        if 'csrf_token' in summary['unique_tokens']:
            summary['potential_api_requirements'].append("Include CSRF token in API headers")
        
        if 'api_v3_access_token' in summary['unique_tokens']:
            summary['potential_api_requirements'].append("Include API v3 access token in Authorization header")
        
        return summary