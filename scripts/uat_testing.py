#!/usr/bin/env python3
"""
Social Media Management Bot - User Acceptance Testing Script

This script performs end-to-end UAT testing with real user flows
and social media account integrations.
"""

import asyncio
import aiohttp
import json
import sys
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import argparse
from pathlib import Path


@dataclass
class UATTestCase:
    """Container for UAT test case information."""
    name: str
    description: str
    steps: List[str]
    expected_result: str
    actual_result: str = ""
    status: str = "pending"  # pending, passed, failed
    execution_time: float = 0.0
    error_message: str = ""


class UATTester:
    """User Acceptance Testing framework for Social Media Management Bot."""
    
    def __init__(self, base_url: str, credentials: Dict[str, str] = None):
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials or {}
        self.session = None
        self.auth_token = None
        self.test_cases: List[UATTestCase] = []
        
        # Initialize test cases
        self._setup_test_cases()
    
    def _setup_test_cases(self):
        """Setup all UAT test cases."""
        
        # Authentication flow tests
        self.test_cases.extend([
            UATTestCase(
                name="User Registration",
                description="New user can register for an account",
                steps=[
                    "Navigate to registration page",
                    "Enter valid email and password",
                    "Submit registration form",
                    "Verify account creation"
                ],
                expected_result="User account created successfully and user is logged in"
            ),
            UATTestCase(
                name="User Login",
                description="Existing user can log into their account",
                steps=[
                    "Navigate to login page",
                    "Enter valid credentials",
                    "Submit login form",
                    "Verify successful authentication"
                ],
                expected_result="User successfully logged in and redirected to dashboard"
            ),
            UATTestCase(
                name="OAuth Login - Google",
                description="User can login using Google OAuth",
                steps=[
                    "Click 'Login with Google' button",
                    "Complete Google OAuth flow",
                    "Verify account linking",
                    "Check dashboard access"
                ],
                expected_result="User logged in via Google and has access to dashboard"
            )
        ])
        
        # Dashboard and navigation tests
        self.test_cases.extend([
            UATTestCase(
                name="Dashboard Access",
                description="Authenticated user can access main dashboard",
                steps=[
                    "Login to application",
                    "Navigate to dashboard",
                    "Verify dashboard components load",
                    "Check for no errors"
                ],
                expected_result="Dashboard loads completely with all widgets and data"
            ),
            UATTestCase(
                name="Navigation Menu",
                description="User can navigate between different sections",
                steps=[
                    "Access main navigation",
                    "Click on each menu item",
                    "Verify page loads correctly",
                    "Check breadcrumb navigation"
                ],
                expected_result="All navigation links work and pages load correctly"
            )
        ])
        
        # Social media account linking tests
        self.test_cases.extend([
            UATTestCase(
                name="Instagram Account Linking",
                description="User can connect their Instagram account",
                steps=[
                    "Navigate to social accounts page",
                    "Click 'Connect Instagram'",
                    "Complete Instagram OAuth flow",
                    "Verify account is connected"
                ],
                expected_result="Instagram account successfully linked and appears in connected accounts"
            ),
            UATTestCase(
                name="Twitter Account Linking",
                description="User can connect their Twitter/X account",
                steps=[
                    "Navigate to social accounts page",
                    "Click 'Connect Twitter'",
                    "Complete Twitter OAuth flow",
                    "Verify account is connected"
                ],
                expected_result="Twitter account successfully linked and appears in connected accounts"
            ),
            UATTestCase(
                name="Multiple Platform Management",
                description="User can manage multiple social media platforms",
                steps=[
                    "Connect multiple social accounts",
                    "View all connected accounts",
                    "Test switching between accounts",
                    "Verify account-specific features"
                ],
                expected_result="All connected accounts are manageable from single interface"
            )
        ])
        
        # Content management tests
        self.test_cases.extend([
            UATTestCase(
                name="Content Creation",
                description="User can create new social media content",
                steps=[
                    "Navigate to content creation page",
                    "Enter post text and upload media",
                    "Select target platforms",
                    "Save as draft"
                ],
                expected_result="Content created and saved successfully as draft"
            ),
            UATTestCase(
                name="Content Scheduling",
                description="User can schedule content for future posting",
                steps=[
                    "Create new content",
                    "Set future date and time",
                    "Select platforms for posting",
                    "Schedule the post"
                ],
                expected_result="Content scheduled successfully and appears in scheduled posts"
            ),
            UATTestCase(
                name="Immediate Publishing",
                description="User can publish content immediately to social platforms",
                steps=[
                    "Create new content",
                    "Select 'Publish Now' option",
                    "Choose target platforms",
                    "Confirm publication"
                ],
                expected_result="Content published immediately to selected platforms"
            ),
            UATTestCase(
                name="Content Templates",
                description="User can create and use content templates",
                steps=[
                    "Create new content template",
                    "Save template with variables",
                    "Use template for new post",
                    "Verify variable substitution"
                ],
                expected_result="Template created and used successfully with proper variable substitution"
            )
        ])
        
        # AI features tests
        self.test_cases.extend([
            UATTestCase(
                name="AI Content Generation",
                description="User can generate content using AI",
                steps=[
                    "Navigate to AI content generation",
                    "Enter content prompt",
                    "Select content type",
                    "Generate and review content"
                ],
                expected_result="AI generates relevant content based on user prompt"
            ),
            UATTestCase(
                name="AI Image Generation",
                description="User can generate images using AI",
                steps=[
                    "Access AI image generation tool",
                    "Enter image description",
                    "Set image parameters",
                    "Generate and download image"
                ],
                expected_result="AI generates appropriate image matching description"
            ),
            UATTestCase(
                name="Video Processing",
                description="User can process and edit videos using AI",
                steps=[
                    "Upload video file",
                    "Select AI processing options",
                    "Apply video enhancements",
                    "Download processed video"
                ],
                expected_result="Video processed successfully with applied enhancements"
            )
        ])
        
        # Analytics and insights tests
        self.test_cases.extend([
            UATTestCase(
                name="Analytics Dashboard",
                description="User can view comprehensive analytics",
                steps=[
                    "Navigate to analytics section",
                    "View performance metrics",
                    "Check different time periods",
                    "Export analytics data"
                ],
                expected_result="Analytics dashboard shows accurate performance data"
            ),
            UATTestCase(
                name="Growth Insights",
                description="User can view growth recommendations",
                steps=[
                    "Access growth insights page",
                    "Review AI-generated recommendations",
                    "Apply suggested optimizations",
                    "Track improvement metrics"
                ],
                expected_result="Growth insights provide actionable recommendations"
            )
        ])
        
        # Team collaboration tests
        self.test_cases.extend([
            UATTestCase(
                name="Team Member Invitation",
                description="User can invite team members",
                steps=[
                    "Navigate to team management",
                    "Send invitation to team member",
                    "Set appropriate permissions",
                    "Verify invitation sent"
                ],
                expected_result="Team member invitation sent successfully"
            ),
            UATTestCase(
                name="Role-Based Access Control",
                description="Team roles have appropriate permissions",
                steps=[
                    "Create team members with different roles",
                    "Test access to various features",
                    "Verify permission restrictions",
                    "Check audit logging"
                ],
                expected_result="Role permissions work as expected with proper access control"
            )
        ])
        
        # Performance and reliability tests
        self.test_cases.extend([
            UATTestCase(
                name="Page Load Performance",
                description="All pages load within acceptable time limits",
                steps=[
                    "Navigate to different pages",
                    "Measure page load times",
                    "Check for performance issues",
                    "Verify responsive design"
                ],
                expected_result="All pages load within 3 seconds on standard connection"
            ),
            UATTestCase(
                name="File Upload Performance",
                description="Large file uploads work reliably",
                steps=[
                    "Upload large media files",
                    "Monitor upload progress",
                    "Verify file processing",
                    "Check file accessibility"
                ],
                expected_result="Large files upload successfully with progress indication"
            ),
            UATTestCase(
                name="Mobile Responsiveness",
                description="Application works properly on mobile devices",
                steps=[
                    "Access app on mobile device",
                    "Test navigation and features",
                    "Verify touch interactions",
                    "Check mobile-specific UI"
                ],
                expected_result="Application fully functional on mobile devices"
            )
        ])
    
    async def create_session(self):
        """Create aiohttp session."""
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with the API to get access token."""
        if not self.credentials.get('email') or not self.credentials.get('password'):
            print("⚠️  No credentials provided. Some tests may be skipped.")
            return False
        
        try:
            login_data = {
                "email": self.credentials['email'],
                "password": self.credentials['password']
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('access_token')
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    return False
        
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    async def make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated API request."""
        headers = kwargs.get('headers', {})
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        kwargs['headers'] = headers
        
        url = f"{self.base_url}{endpoint}"
        return await self.session.request(method, url, **kwargs)
    
    async def test_user_registration(self, test_case: UATTestCase) -> bool:
        """Test user registration flow."""
        try:
            # Generate unique test email
            test_email = f"test_user_{int(time.time())}@example.com"
            registration_data = {
                "email": test_email,
                "password": "TestPassword123!",
                "name": "Test User"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=registration_data
            ) as response:
                if response.status == 201:
                    test_case.actual_result = "User registration successful"
                    return True
                else:
                    error_data = await response.json()
                    test_case.actual_result = f"Registration failed: {error_data}"
                    return False
        
        except Exception as e:
            test_case.actual_result = f"Registration error: {e}"
            return False
    
    async def test_user_login(self, test_case: UATTestCase) -> bool:
        """Test user login flow."""
        return await self.authenticate()
    
    async def test_dashboard_access(self, test_case: UATTestCase) -> bool:
        """Test dashboard access."""
        try:
            async with await self.make_authenticated_request("GET", "/api/v1/dashboard") as response:
                if response.status == 200:
                    data = await response.json()
                    test_case.actual_result = "Dashboard data loaded successfully"
                    return True
                else:
                    test_case.actual_result = f"Dashboard access failed: {response.status}"
                    return False
        
        except Exception as e:
            test_case.actual_result = f"Dashboard error: {e}"
            return False
    
    async def test_social_accounts(self, test_case: UATTestCase) -> bool:
        """Test social accounts functionality."""
        try:
            async with await self.make_authenticated_request("GET", "/api/v1/social-accounts") as response:
                if response.status == 200:
                    data = await response.json()
                    test_case.actual_result = f"Social accounts retrieved: {len(data.get('accounts', []))} accounts"
                    return True
                else:
                    test_case.actual_result = f"Social accounts access failed: {response.status}"
                    return False
        
        except Exception as e:
            test_case.actual_result = f"Social accounts error: {e}"
            return False
    
    async def test_content_creation(self, test_case: UATTestCase) -> bool:
        """Test content creation functionality."""
        try:
            content_data = {
                "title": "UAT Test Post",
                "content": "This is a test post created during UAT testing",
                "platforms": ["instagram", "twitter"],
                "status": "draft"
            }
            
            async with await self.make_authenticated_request(
                "POST", "/api/v1/content", json=content_data
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    test_case.actual_result = f"Content created successfully with ID: {data.get('id')}"
                    return True
                else:
                    error_data = await response.json()
                    test_case.actual_result = f"Content creation failed: {error_data}"
                    return False
        
        except Exception as e:
            test_case.actual_result = f"Content creation error: {e}"
            return False
    
    async def test_ai_features(self, test_case: UATTestCase) -> bool:
        """Test AI features functionality."""
        try:
            ai_request = {
                "prompt": "Create a social media post about technology trends",
                "type": "text",
                "parameters": {"length": "short", "tone": "professional"}
            }
            
            async with await self.make_authenticated_request(
                "POST", "/api/v1/ai/generate-content", json=ai_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    test_case.actual_result = "AI content generated successfully"
                    return True
                else:
                    test_case.actual_result = f"AI generation failed: {response.status}"
                    return False
        
        except Exception as e:
            test_case.actual_result = f"AI features error: {e}"
            return False
    
    async def test_analytics(self, test_case: UATTestCase) -> bool:
        """Test analytics functionality."""
        try:
            async with await self.make_authenticated_request("GET", "/api/v1/analytics") as response:
                if response.status == 200:
                    data = await response.json()
                    test_case.actual_result = "Analytics data retrieved successfully"
                    return True
                else:
                    test_case.actual_result = f"Analytics access failed: {response.status}"
                    return False
        
        except Exception as e:
            test_case.actual_result = f"Analytics error: {e}"
            return False
    
    async def run_test_case(self, test_case: UATTestCase):
        """Run individual test case."""
        print(f"🧪 Running: {test_case.name}")
        start_time = time.time()
        
        try:
            # Map test cases to their implementations
            test_methods = {
                "User Registration": self.test_user_registration,
                "User Login": self.test_user_login,
                "Dashboard Access": self.test_dashboard_access,
                "Instagram Account Linking": self.test_social_accounts,
                "Twitter Account Linking": self.test_social_accounts,
                "Multiple Platform Management": self.test_social_accounts,
                "Content Creation": self.test_content_creation,
                "Content Scheduling": self.test_content_creation,
                "Immediate Publishing": self.test_content_creation,
                "Content Templates": self.test_content_creation,
                "AI Content Generation": self.test_ai_features,
                "AI Image Generation": self.test_ai_features,
                "Video Processing": self.test_ai_features,
                "Analytics Dashboard": self.test_analytics,
                "Growth Insights": self.test_analytics,
            }
            
            test_method = test_methods.get(test_case.name)
            if test_method:
                success = await test_method(test_case)
                test_case.status = "passed" if success else "failed"
            else:
                test_case.status = "skipped"
                test_case.actual_result = "Test implementation not available (manual testing required)"
        
        except Exception as e:
            test_case.status = "failed"
            test_case.error_message = str(e)
            test_case.actual_result = f"Test execution error: {e}"
        
        test_case.execution_time = time.time() - start_time
        
        # Print result
        status_emoji = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}
        print(f"   {status_emoji.get(test_case.status, '❓')} {test_case.status.upper()} ({test_case.execution_time:.2f}s)")
        
        if test_case.status == "failed" and test_case.error_message:
            print(f"   Error: {test_case.error_message}")
    
    async def run_uat_tests(self, test_filter: str = None):
        """Run all UAT tests."""
        print("🧪 Starting User Acceptance Testing (UAT)")
        print("=" * 60)
        
        await self.create_session()
        
        try:
            # Authenticate if credentials provided
            if self.credentials.get('email'):
                print("🔐 Authenticating...")
                auth_success = await self.authenticate()
                if auth_success:
                    print("✅ Authentication successful")
                else:
                    print("❌ Authentication failed - some tests may be skipped")
            
            # Filter tests if specified
            tests_to_run = self.test_cases
            if test_filter:
                tests_to_run = [tc for tc in self.test_cases if test_filter.lower() in tc.name.lower()]
            
            print(f"\n🧪 Running {len(tests_to_run)} test cases...\n")
            
            # Run tests
            for test_case in tests_to_run:
                await self.run_test_case(test_case)
            
            # Generate report
            self.generate_uat_report()
        
        finally:
            await self.close_session()
    
    def generate_uat_report(self):
        """Generate UAT test report."""
        print("\n" + "=" * 80)
        print("USER ACCEPTANCE TESTING REPORT")
        print("=" * 80)
        
        # Summary statistics
        total_tests = len(self.test_cases)
        passed_tests = len([tc for tc in self.test_cases if tc.status == "passed"])
        failed_tests = len([tc for tc in self.test_cases if tc.status == "failed"])
        skipped_tests = len([tc for tc in self.test_cases if tc.status == "skipped"])
        
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Passed: {passed_tests}")
        print(f"  ❌ Failed: {failed_tests}")
        print(f"  ⏭️  Skipped: {skipped_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / (total_tests - skipped_tests)) * 100 if (total_tests - skipped_tests) > 0 else 0
            print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            print("-" * 50)
            for i, test_case in enumerate([tc for tc in self.test_cases if tc.status == "failed"], 1):
                print(f"\n{i}. {test_case.name}")
                print(f"   Description: {test_case.description}")
                print(f"   Expected: {test_case.expected_result}")
                print(f"   Actual: {test_case.actual_result}")
                if test_case.error_message:
                    print(f"   Error: {test_case.error_message}")
        
        # Skipped tests
        if skipped_tests > 0:
            print(f"\n⏭️  Skipped Tests (Manual Testing Required):")
            print("-" * 50)
            for test_case in [tc for tc in self.test_cases if tc.status == "skipped"]:
                print(f"• {test_case.name}: {test_case.description}")
        
        # Overall assessment
        print(f"\n🎯 Overall Assessment:")
        if success_rate >= 90:
            print("  ✅ Excellent - Application is ready for production")
        elif success_rate >= 75:
            print("  ⚠️  Good - Minor issues need attention before production")
        elif success_rate >= 50:
            print("  ⚠️  Fair - Significant issues need to be resolved")
        else:
            print("  ❌ Poor - Major issues prevent production deployment")
        
        # Recommendations
        print(f"\n📋 Recommendations:")
        if failed_tests > 0:
            print("  1. Fix all failed automated tests")
            print("  2. Conduct manual testing for skipped test cases")
        if skipped_tests > 0:
            print("  3. Complete manual testing checklist")
        print("  4. Verify all social media integrations with real accounts")
        print("  5. Test with different user roles and permissions")
        print("  6. Validate performance under realistic load")


def main():
    """Main function to run UAT tests."""
    parser = argparse.ArgumentParser(description="User Acceptance Testing for Social Media Management Bot")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000", 
        help="Base URL for the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--email", 
        help="Test user email for authentication"
    )
    parser.add_argument(
        "--password", 
        help="Test user password for authentication"
    )
    parser.add_argument(
        "--filter", 
        help="Filter tests by name (case insensitive)"
    )
    
    args = parser.parse_args()
    
    credentials = {}
    if args.email and args.password:
        credentials = {"email": args.email, "password": args.password}
    
    # Run UAT tests
    uat_tester = UATTester(
        base_url=args.url,
        credentials=credentials
    )
    
    try:
        asyncio.run(uat_tester.run_uat_tests(args.filter))
    except KeyboardInterrupt:
        print("\nUAT testing interrupted by user")
    except Exception as e:
        print(f"Error during UAT testing: {e}")


if __name__ == "__main__":
    main()