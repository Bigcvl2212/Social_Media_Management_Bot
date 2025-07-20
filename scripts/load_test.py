#!/usr/bin/env python3
"""
Social Media Management Bot - Load Testing Script

This script performs load testing to simulate realistic user scenarios
and identify performance bottlenecks under high load.
"""

import asyncio
import aiohttp
import time
import json
import random
import argparse
from typing import List, Dict, Any
import statistics
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading


@dataclass
class TestResult:
    """Container for test result data."""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error: str = None


class LoadTester:
    """Load testing class with realistic user scenarios."""
    
    def __init__(self, base_url: str, num_users: int = 10, duration: int = 60):
        self.base_url = base_url.rstrip('/')
        self.num_users = num_users
        self.duration = duration
        self.results: List[TestResult] = []
        self.start_time = None
        self.session = None
        
        # Test scenarios with different API endpoints
        self.scenarios = [
            self.health_check_scenario,
            self.auth_scenario,
            self.content_list_scenario,
            self.social_accounts_scenario,
            self.analytics_scenario,
            self.ai_features_scenario
        ]
    
    async def create_session(self):
        """Create aiohttp session with proper configuration."""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """Make HTTP request and record metrics."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                success = 200 <= response.status < 400
                
                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    response_time=response_time,
                    success=success
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def health_check_scenario(self):
        """Health check endpoint testing."""
        return await self.make_request("GET", "/health")
    
    async def auth_scenario(self):
        """Authentication endpoint testing."""
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/me"
        ]
        endpoint = random.choice(endpoints)
        
        if endpoint in ["/api/v1/auth/login", "/api/v1/auth/register"]:
            return await self.make_request("POST", endpoint, json={
                "email": f"test{random.randint(1, 1000)}@example.com",
                "password": "testpassword123"
            })
        else:
            return await self.make_request("GET", endpoint)
    
    async def content_list_scenario(self):
        """Content management endpoints."""
        endpoints = [
            "/api/v1/content",
            "/api/v1/content/templates",
            "/api/v1/content/scheduled"
        ]
        endpoint = random.choice(endpoints)
        return await self.make_request("GET", endpoint)
    
    async def social_accounts_scenario(self):
        """Social media accounts endpoints."""
        endpoints = [
            "/api/v1/social-accounts",
            "/api/v1/social-accounts/platforms",
            "/api/v1/social-accounts/connected"
        ]
        endpoint = random.choice(endpoints)
        return await self.make_request("GET", endpoint)
    
    async def analytics_scenario(self):
        """Analytics endpoints."""
        endpoints = [
            "/api/v1/analytics",
            "/api/v1/analytics/dashboard",
            "/api/v1/analytics/performance"
        ]
        endpoint = random.choice(endpoints)
        return await self.make_request("GET", endpoint)
    
    async def ai_features_scenario(self):
        """AI features endpoints."""
        endpoints = [
            "/api/v1/ai-multimodal/ai-voiceover/generate",
            "/api/v1/ai-multimodal/image-to-video/create",
            "/api/v1/ai-multimodal/enhanced-memes/trending"
        ]
        endpoint = random.choice(endpoints)
        
        # POST requests for AI features
        test_data = {
            "text": "Test content for AI processing",
            "parameters": {"quality": "high"}
        }
        return await self.make_request("POST", endpoint, json=test_data)
    
    async def user_simulation(self, user_id: int):
        """Simulate a single user's behavior."""
        user_results = []
        end_time = self.start_time + self.duration
        
        while time.time() < end_time:
            # Random delay between requests (1-5 seconds)
            await asyncio.sleep(random.uniform(1, 5))
            
            # Select random scenario
            scenario = random.choice(self.scenarios)
            result = await scenario()
            user_results.append(result)
            
            # Add to global results thread-safely
            self.results.append(result)
        
        return user_results
    
    async def run_load_test(self):
        """Execute the load test with multiple concurrent users."""
        print(f"Starting load test with {self.num_users} users for {self.duration} seconds")
        print(f"Target URL: {self.base_url}")
        print("-" * 60)
        
        await self.create_session()
        self.start_time = time.time()
        
        try:
            # Run concurrent user simulations
            tasks = [
                self.user_simulation(i) 
                for i in range(self.num_users)
            ]
            
            await asyncio.gather(*tasks)
            
        finally:
            await self.close_session()
        
        self.generate_report()
    
    def generate_report(self):
        """Generate and display load test results."""
        if not self.results:
            print("No test results to analyze")
            return
        
        # Basic statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        # Response time statistics
        response_times = [r.response_time for r in self.results]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        median_response_time = statistics.median(response_times)
        
        # Percentiles
        response_times_sorted = sorted(response_times)
        p95_response_time = response_times_sorted[int(0.95 * len(response_times_sorted))]
        p99_response_time = response_times_sorted[int(0.99 * len(response_times_sorted))]
        
        # Requests per second
        actual_duration = max(r.response_time for r in self.results) if self.results else self.duration
        rps = total_requests / self.duration
        
        # Group by endpoint
        endpoint_stats = {}
        for result in self.results:
            endpoint = result.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'total': 0,
                    'success': 0,
                    'response_times': []
                }
            
            endpoint_stats[endpoint]['total'] += 1
            if result.success:
                endpoint_stats[endpoint]['success'] += 1
            endpoint_stats[endpoint]['response_times'].append(result.response_time)
        
        # Status code distribution
        status_codes = {}
        for result in self.results:
            code = result.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Print report
        print("\n" + "=" * 80)
        print("LOAD TEST RESULTS")
        print("=" * 80)
        
        print(f"\nTest Configuration:")
        print(f"  Duration: {self.duration} seconds")
        print(f"  Concurrent Users: {self.num_users}")
        print(f"  Target URL: {self.base_url}")
        
        print(f"\nOverall Performance:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Successful Requests: {successful_requests}")
        print(f"  Failed Requests: {failed_requests}")
        print(f"  Success Rate: {success_rate:.2f}%")
        print(f"  Requests/Second: {rps:.2f}")
        
        print(f"\nResponse Time Statistics (seconds):")
        print(f"  Average: {avg_response_time:.3f}")
        print(f"  Minimum: {min_response_time:.3f}")
        print(f"  Maximum: {max_response_time:.3f}")
        print(f"  Median: {median_response_time:.3f}")
        print(f"  95th Percentile: {p95_response_time:.3f}")
        print(f"  99th Percentile: {p99_response_time:.3f}")
        
        print(f"\nHTTP Status Code Distribution:")
        for code, count in sorted(status_codes.items()):
            percentage = (count / total_requests) * 100
            print(f"  {code}: {count} ({percentage:.1f}%)")
        
        print(f"\nEndpoint Performance:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100
            avg_time = statistics.mean(stats['response_times'])
            print(f"  {endpoint}:")
            print(f"    Requests: {stats['total']}")
            print(f"    Success Rate: {success_rate:.1f}%")
            print(f"    Avg Response Time: {avg_time:.3f}s")
        
        # Performance assessment
        print(f"\nPerformance Assessment:")
        if avg_response_time > 2.0:
            print("  ⚠️  High average response time (>2s) - investigate performance issues")
        elif avg_response_time > 1.0:
            print("  ⚠️  Moderate response time (>1s) - monitor for improvements")
        else:
            print("  ✅ Good response time (<1s)")
        
        if success_rate < 95:
            print("  ❌ Low success rate (<95%) - critical issues need attention")
        elif success_rate < 99:
            print("  ⚠️  Moderate success rate (<99%) - investigate errors")
        else:
            print("  ✅ Excellent success rate (>99%)")
        
        if p95_response_time > 5.0:
            print("  ❌ High 95th percentile response time (>5s) - performance issues")
        elif p95_response_time > 3.0:
            print("  ⚠️  Moderate 95th percentile response time (>3s)")
        else:
            print("  ✅ Good 95th percentile response time (<3s)")
        
        # Error analysis
        if failed_requests > 0:
            print(f"\nError Analysis:")
            error_types = {}
            for result in self.results:
                if not result.success:
                    error = result.error or f"HTTP {result.status_code}"
                    error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in error_types.items():
                print(f"  {error}: {count} occurrences")


def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(description="Load test for Social Media Management Bot")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000", 
        help="Base URL for the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--users", 
        type=int, 
        default=10, 
        help="Number of concurrent users (default: 10)"
    )
    parser.add_argument(
        "--duration", 
        type=int, 
        default=60, 
        help="Test duration in seconds (default: 60)"
    )
    
    args = parser.parse_args()
    
    # Run the load test
    load_tester = LoadTester(
        base_url=args.url,
        num_users=args.users,
        duration=args.duration
    )
    
    try:
        asyncio.run(load_tester.run_load_test())
    except KeyboardInterrupt:
        print("\nLoad test interrupted by user")
    except Exception as e:
        print(f"Error during load test: {e}")


if __name__ == "__main__":
    main()