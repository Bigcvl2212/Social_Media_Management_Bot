"""
Test configuration and utilities for integration tests.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path so we can import backend modules
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config():
    """Provide test configuration settings."""
    return {
        "test_database_url": "sqlite+aiosqlite:///:memory:",
        "test_secret_key": "test-secret-key",
        "test_user_email": "test@example.com",
        "test_user_password": "testpassword123",
        "api_base_url": "http://localhost:8000",
        "timeout": 30
    }

# Mock social media platform credentials for testing
@pytest.fixture
def mock_social_accounts():
    """Mock social media account configurations for testing."""
    return {
        "instagram": {
            "platform": "instagram",
            "account_id": "test_instagram_123",
            "access_token": "mock_ig_token",
            "account_name": "@test_account"
        },
        "twitter": {
            "platform": "twitter", 
            "account_id": "test_twitter_456",
            "access_token": "mock_twitter_token",
            "account_name": "@test_twitter"
        },
        "tiktok": {
            "platform": "tiktok",
            "account_id": "test_tiktok_789",
            "access_token": "mock_tiktok_token", 
            "account_name": "@test_tiktok"
        }
    }

@pytest.fixture
def sample_content():
    """Sample content for testing posting and scheduling."""
    return {
        "text_post": {
            "content": "This is a test post for our Social Media Management Bot! 🚀 #Testing #SocialMedia",
            "platform": "instagram",
            "type": "text"
        },
        "image_post": {
            "content": "Check out this amazing image post!",
            "platform": "instagram", 
            "type": "image",
            "media_url": "https://example.com/test-image.jpg"
        },
        "video_post": {
            "content": "Exciting video content coming your way!",
            "platform": "tiktok",
            "type": "video", 
            "media_url": "https://example.com/test-video.mp4"
        }
    }

@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing analytics retrieval."""
    return {
        "instagram": {
            "followers": 1250,
            "following": 345,
            "posts": 87,
            "engagement_rate": 4.2,
            "reach": 2450,
            "impressions": 5320
        },
        "twitter": {
            "followers": 892,
            "following": 156,
            "tweets": 234,
            "engagement_rate": 3.8,
            "retweets": 45,
            "likes": 312
        },
        "tiktok": {
            "followers": 3420,
            "following": 89,
            "videos": 45,
            "engagement_rate": 6.7,
            "views": 125000,
            "likes": 8500
        }
    }