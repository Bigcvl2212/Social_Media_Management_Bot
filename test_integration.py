"""
Integration Test Script
Quick validation of backend services and API endpoints
"""

import asyncio
import json
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"


class ContentManagerTester:
    """Test suite for content manager API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client()
        self.results = []
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
        })
    
    # ==================== BASIC CONNECTIVITY ====================
    
    def test_health_check(self):
        """Test API health endpoint"""
        try:
            response = self.client.get(f"{self.base_url}/health")
            passed = response.status_code == 200
            self.log_result(
                "Health Check",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = self.client.get(f"{self.base_url.replace('/api/v1', '')}/")
            passed = response.status_code == 200
            self.log_result(
                "Root Endpoint",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_result("Root Endpoint", False, str(e))
            return False
    
    # ==================== AI GENERATION ====================
    
    def test_generate_captions(self):
        """Test caption generation"""
        try:
            data = {
                'content_description': 'Gym workout for beginners',
                'platform': 'instagram',
                'hashtags': 'true',
            }
            response = self.client.post(
                f"{self.base_url}/generate/captions",
                data=data
            )
            passed = response.status_code == 200
            if passed:
                result = response.json()
                details = f"Generated caption with {len(result.get('hashtags', []))} hashtags"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_result("Generate Captions", passed, details)
            return passed
        except Exception as e:
            self.log_result("Generate Captions", False, str(e))
            return False
    
    def test_generate_ideas(self):
        """Test content ideas generation"""
        try:
            params = {
                'topic': 'fitness training',
                'platform': 'tiktok',
                'count': '3',
            }
            response = self.client.get(
                f"{self.base_url}/generate/ideas",
                params=params
            )
            passed = response.status_code == 200
            if passed:
                result = response.json()
                idea_count = len(result.get('ideas', []))
                details = f"Generated {idea_count} content ideas"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_result("Generate Content Ideas", passed, details)
            return passed
        except Exception as e:
            self.log_result("Generate Content Ideas", False, str(e))
            return False
    
    def test_analyze_trending(self):
        """Test trending topics analysis"""
        try:
            params = {
                'platform': 'instagram',
                'region': 'global',
            }
            response = self.client.get(
                f"{self.base_url}/analyze/trending",
                params=params
            )
            passed = response.status_code == 200
            if passed:
                details = "Successfully retrieved trending topics"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_result("Analyze Trending Topics", passed, details)
            return passed
        except Exception as e:
            self.log_result("Analyze Trending Topics", False, str(e))
            return False
    
    def test_viral_potential(self):
        """Test viral potential prediction"""
        try:
            data = {
                'content_description': 'Quick 30-second workout routine',
                'platform': 'tiktok',
                'target_audience': 'fitness enthusiasts',
            }
            response = self.client.post(
                f"{self.base_url}/analyze/viral-potential",
                data=data
            )
            passed = response.status_code == 200
            if passed:
                details = "Successfully analyzed viral potential"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_result("Viral Potential Analysis", passed, details)
            return passed
        except Exception as e:
            self.log_result("Viral Potential Analysis", False, str(e))
            return False
    
    def test_generate_script(self):
        """Test script generation"""
        try:
            data = {
                'topic': 'How to do push-ups correctly',
                'duration_seconds': '60',
                'style': 'educational',
            }
            response = self.client.post(
                f"{self.base_url}/generate/script",
                data=data
            )
            passed = response.status_code == 200
            if passed:
                result = response.json()
                script_length = len(result.get('script', ''))
                details = f"Generated script ({script_length} chars)"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_result("Generate Script", passed, details)
            return passed
        except Exception as e:
            self.log_result("Generate Script", False, str(e))
            return False
    
    # ==================== OAUTH ====================
    
    def test_oauth_url_generation(self):
        """Test OAuth URL generation"""
        try:
            params = {
                'platform': 'instagram',
                'client_id': 'test-client-id',
                'redirect_uri': 'http://localhost:3000/callback',
                'state': 'test-state-123',
            }
            response = self.client.get(
                f"{self.base_url}/auth/oauth-url",
                params=params
            )
            passed = response.status_code == 200
            if passed:
                result = response.json()
                url_length = len(result.get('oauth_url', ''))
                details = f"Generated OAuth URL ({url_length} chars)"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_result("OAuth URL Generation", passed, details)
            return passed
        except Exception as e:
            self.log_result("OAuth URL Generation", False, str(e))
            return False
    
    # ==================== SUMMARY ====================
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "="*60)
        
        return passed == total
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Content Manager API Tests...\n")
        
        # Basic connectivity
        print("📡 Basic Connectivity Tests:")
        self.test_health_check()
        self.test_root_endpoint()
        
        print("\n🤖 AI Generation Tests:")
        self.test_generate_captions()
        self.test_generate_ideas()
        self.test_analyze_trending()
        self.test_viral_potential()
        self.test_generate_script()
        
        print("\n🔐 OAuth Tests:")
        self.test_oauth_url_generation()
        
        # Print summary
        return self.print_summary()


async def main():
    """Main test runner"""
    tester = ContentManagerTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    print("Content Manager API - Integration Tests\n")
    print("Make sure the backend is running: python backend/main.py\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {str(e)}")
        exit(1)
