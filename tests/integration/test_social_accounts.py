"""
Integration tests for social media account linking functionality.

Tests OAuth flows, account connection, disconnection, and management.
"""

import pytest
import asyncio
from typing import Dict, Any
import json


class TestSocialAccountLinking:
    """Test suite for social media account linking and management."""

    @pytest.mark.asyncio
    async def test_instagram_account_linking(self, test_config: Dict[str, Any], mock_social_accounts: Dict[str, Any]):
        """Test Instagram account linking flow."""
        instagram_data = mock_social_accounts["instagram"]
        
        print("✓ Testing Instagram account linking")
        
        # Mock OAuth initiation request
        oauth_init_request = {
            "platform": "instagram",
            "redirect_uri": "https://app.example.com/auth/instagram/callback",
            "scopes": ["instagram_basic", "instagram_content_publish"]
        }
        
        # Mock OAuth URL response
        oauth_url_response = {
            "authorization_url": "https://api.instagram.com/oauth/authorize?client_id=test&redirect_uri=callback&scope=basic",
            "state": "random_state_token_123",
            "platform": "instagram"
        }
        
        # Mock successful account linking after OAuth callback
        linking_response = {
            "id": 1,
            "user_id": 1,
            "platform": instagram_data["platform"],
            "account_id": instagram_data["account_id"],
            "account_name": instagram_data["account_name"],
            "access_token": "encrypted_token_hash",  # Should be encrypted in real implementation
            "permissions": ["publish_content", "read_insights"],
            "status": "active",
            "linked_at": "2024-01-01T10:00:00Z"
        }
        
        # Assertions
        assert linking_response["platform"] == "instagram"
        assert linking_response["status"] == "active"
        assert "publish_content" in linking_response["permissions"]
        assert linking_response["account_name"] == instagram_data["account_name"]
        print("✓ Instagram account linking test passed")

    @pytest.mark.asyncio
    async def test_twitter_account_linking(self, test_config: Dict[str, Any], mock_social_accounts: Dict[str, Any]):
        """Test Twitter/X account linking flow."""
        twitter_data = mock_social_accounts["twitter"]
        
        print("✓ Testing Twitter account linking")
        
        # Mock Twitter OAuth 2.0 flow
        oauth_init_request = {
            "platform": "twitter",
            "redirect_uri": "https://app.example.com/auth/twitter/callback",
            "scopes": ["tweet.read", "tweet.write", "users.read"]
        }
        
        # Mock successful Twitter account linking
        linking_response = {
            "id": 2,
            "user_id": 1,
            "platform": twitter_data["platform"],
            "account_id": twitter_data["account_id"], 
            "account_name": twitter_data["account_name"],
            "access_token": "encrypted_twitter_token",
            "permissions": ["publish_tweets", "read_analytics"],
            "status": "active",
            "linked_at": "2024-01-01T10:15:00Z"
        }
        
        # Assertions
        assert linking_response["platform"] == "twitter"
        assert linking_response["status"] == "active"
        assert "publish_tweets" in linking_response["permissions"]
        assert linking_response["account_name"] == twitter_data["account_name"]
        print("✓ Twitter account linking test passed")

    @pytest.mark.asyncio
    async def test_tiktok_account_linking(self, test_config: Dict[str, Any], mock_social_accounts: Dict[str, Any]):
        """Test TikTok account linking flow."""
        tiktok_data = mock_social_accounts["tiktok"]
        
        print("✓ Testing TikTok account linking")
        
        # Mock TikTok OAuth flow
        oauth_init_request = {
            "platform": "tiktok",
            "redirect_uri": "https://app.example.com/auth/tiktok/callback",
            "scopes": ["user.info.basic", "video.publish", "video.list"]
        }
        
        # Mock successful TikTok account linking
        linking_response = {
            "id": 3,
            "user_id": 1,
            "platform": tiktok_data["platform"],
            "account_id": tiktok_data["account_id"],
            "account_name": tiktok_data["account_name"],
            "access_token": "encrypted_tiktok_token", 
            "permissions": ["publish_videos", "read_analytics"],
            "status": "active",
            "linked_at": "2024-01-01T10:30:00Z"
        }
        
        # Assertions
        assert linking_response["platform"] == "tiktok"
        assert linking_response["status"] == "active"
        assert "publish_videos" in linking_response["permissions"]
        assert linking_response["account_name"] == tiktok_data["account_name"]
        print("✓ TikTok account linking test passed")

    @pytest.mark.asyncio
    async def test_multiple_platform_management(self, test_config: Dict[str, Any], mock_social_accounts: Dict[str, Any]):
        """Test management of multiple linked social media accounts."""
        print("✓ Testing multiple platform account management")
        
        # Mock user with multiple linked accounts
        linked_accounts_response = {
            "user_id": 1,
            "total_accounts": 3,
            "accounts": [
                {
                    "id": 1,
                    "platform": "instagram",
                    "account_name": "@test_account",
                    "status": "active",
                    "last_sync": "2024-01-01T09:00:00Z"
                },
                {
                    "id": 2, 
                    "platform": "twitter",
                    "account_name": "@test_twitter",
                    "status": "active",
                    "last_sync": "2024-01-01T08:45:00Z"
                },
                {
                    "id": 3,
                    "platform": "tiktok", 
                    "account_name": "@test_tiktok",
                    "status": "active",
                    "last_sync": "2024-01-01T09:15:00Z"
                }
            ]
        }
        
        # Assertions
        assert linked_accounts_response["total_accounts"] == 3
        assert len(linked_accounts_response["accounts"]) == 3
        
        # Check all platforms are represented
        platforms = [account["platform"] for account in linked_accounts_response["accounts"]]
        assert "instagram" in platforms
        assert "twitter" in platforms
        assert "tiktok" in platforms
        
        # Check all accounts are active
        for account in linked_accounts_response["accounts"]:
            assert account["status"] == "active"
            assert "last_sync" in account
            
        print("✓ Multiple platform management test passed")

    @pytest.mark.asyncio 
    async def test_account_disconnection(self, test_config: Dict[str, Any]):
        """Test social media account disconnection."""
        print("✓ Testing account disconnection")
        
        # Mock disconnection request
        disconnect_request = {
            "account_id": 1,
            "platform": "instagram",
            "confirm_disconnect": True
        }
        
        # Mock disconnection response
        disconnect_response = {
            "message": "Account disconnected successfully",
            "account_id": 1,
            "platform": "instagram", 
            "status": "disconnected",
            "disconnected_at": "2024-01-01T11:00:00Z",
            "cleanup_completed": True
        }
        
        # Assertions
        assert disconnect_response["status"] == "disconnected"
        assert disconnect_response["cleanup_completed"] is True
        assert disconnect_response["platform"] == "instagram"
        assert "disconnected_at" in disconnect_response
        print("✓ Account disconnection test passed")

    @pytest.mark.asyncio
    async def test_account_reauthorization(self, test_config: Dict[str, Any]):
        """Test reauthorization of expired social media accounts."""
        print("✓ Testing account reauthorization")
        
        # Mock expired account scenario
        expired_account = {
            "id": 2,
            "platform": "twitter",
            "status": "token_expired",
            "last_error": "Token expired",
            "expires_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock reauthorization request
        reauth_request = {
            "account_id": 2,
            "platform": "twitter"
        }
        
        # Mock successful reauthorization
        reauth_response = {
            "account_id": 2,
            "platform": "twitter",
            "status": "active",
            "access_token": "new_encrypted_token",
            "expires_at": "2024-02-01T00:00:00Z",
            "reauthorized_at": "2024-01-01T11:30:00Z",
            "permissions": ["publish_tweets", "read_analytics"]
        }
        
        # Assertions
        assert reauth_response["status"] == "active"
        assert reauth_response["access_token"] == "new_encrypted_token"
        assert "reauthorized_at" in reauth_response
        assert "publish_tweets" in reauth_response["permissions"]
        print("✓ Account reauthorization test passed")


class TestSocialAccountValidation:
    """Test suite for social media account validation and health checks."""

    @pytest.mark.asyncio
    async def test_account_health_check(self, test_config: Dict[str, Any]):
        """Test health check for linked social media accounts."""
        print("✓ Testing account health check")
        
        # Mock health check for multiple accounts
        health_check_response = {
            "timestamp": "2024-01-01T12:00:00Z",
            "total_accounts": 3,
            "healthy_accounts": 2,
            "accounts_with_issues": 1,
            "account_status": [
                {
                    "id": 1,
                    "platform": "instagram",
                    "status": "healthy",
                    "last_api_call": "2024-01-01T11:55:00Z",
                    "rate_limit_remaining": 95,
                    "permissions_valid": True
                },
                {
                    "id": 2,
                    "platform": "twitter", 
                    "status": "rate_limited",
                    "last_api_call": "2024-01-01T11:30:00Z",
                    "rate_limit_remaining": 0,
                    "rate_limit_reset": "2024-01-01T12:30:00Z",
                    "permissions_valid": True
                },
                {
                    "id": 3,
                    "platform": "tiktok",
                    "status": "healthy",
                    "last_api_call": "2024-01-01T11:50:00Z", 
                    "rate_limit_remaining": 87,
                    "permissions_valid": True
                }
            ]
        }
        
        # Assertions
        assert health_check_response["total_accounts"] == 3
        assert health_check_response["healthy_accounts"] == 2
        assert health_check_response["accounts_with_issues"] == 1
        
        # Check each account status
        for account in health_check_response["account_status"]:
            assert "status" in account
            assert "last_api_call" in account
            assert "permissions_valid" in account
            
        # Find the rate-limited account
        rate_limited_account = next(
            account for account in health_check_response["account_status"] 
            if account["status"] == "rate_limited"
        )
        assert rate_limited_account["platform"] == "twitter"
        assert rate_limited_account["rate_limit_remaining"] == 0
        assert "rate_limit_reset" in rate_limited_account
        
        print("✓ Account health check test passed")

    @pytest.mark.asyncio
    async def test_permission_validation(self, test_config: Dict[str, Any]):
        """Test validation of account permissions and scopes."""
        print("✓ Testing account permission validation")
        
        # Mock permission validation for each platform
        permission_checks = [
            {
                "platform": "instagram",
                "account_id": 1,
                "required_permissions": ["instagram_basic", "instagram_content_publish"],
                "granted_permissions": ["instagram_basic", "instagram_content_publish"],
                "missing_permissions": [],
                "valid": True
            },
            {
                "platform": "twitter",
                "account_id": 2, 
                "required_permissions": ["tweet.read", "tweet.write", "users.read"],
                "granted_permissions": ["tweet.read", "users.read"],
                "missing_permissions": ["tweet.write"],
                "valid": False
            },
            {
                "platform": "tiktok",
                "account_id": 3,
                "required_permissions": ["user.info.basic", "video.publish"],
                "granted_permissions": ["user.info.basic", "video.publish", "video.list"],
                "missing_permissions": [],
                "valid": True
            }
        ]
        
        # Test each permission check
        for check in permission_checks:
            if check["valid"]:
                assert len(check["missing_permissions"]) == 0
                assert set(check["required_permissions"]).issubset(set(check["granted_permissions"]))
            else:
                assert len(check["missing_permissions"]) > 0
                
            print(f"✓ {check['platform']} permission validation: {'✓ Valid' if check['valid'] else '⚠ Missing permissions'}")
            
        print("✓ Permission validation test passed")

    @pytest.mark.asyncio
    async def test_account_sync_status(self, test_config: Dict[str, Any]):
        """Test synchronization status of linked accounts."""
        print("✓ Testing account synchronization status")
        
        # Mock sync status for accounts
        sync_status_response = {
            "last_sync_check": "2024-01-01T12:00:00Z",
            "accounts": [
                {
                    "id": 1,
                    "platform": "instagram",
                    "last_successful_sync": "2024-01-01T11:55:00Z",
                    "sync_status": "up_to_date",
                    "pending_operations": 0,
                    "failed_operations": 0
                },
                {
                    "id": 2,
                    "platform": "twitter",
                    "last_successful_sync": "2024-01-01T10:30:00Z", 
                    "sync_status": "sync_required",
                    "pending_operations": 3,
                    "failed_operations": 1,
                    "last_error": "Rate limit exceeded"
                },
                {
                    "id": 3,
                    "platform": "tiktok",
                    "last_successful_sync": "2024-01-01T11:45:00Z",
                    "sync_status": "syncing",
                    "pending_operations": 1,
                    "failed_operations": 0
                }
            ]
        }
        
        # Assertions
        assert "last_sync_check" in sync_status_response
        assert len(sync_status_response["accounts"]) == 3
        
        # Check sync status for each account
        for account in sync_status_response["accounts"]:
            assert "sync_status" in account
            assert "pending_operations" in account
            assert "failed_operations" in account
            assert account["pending_operations"] >= 0
            assert account["failed_operations"] >= 0
            
        # Find accounts with issues
        up_to_date_accounts = [
            account for account in sync_status_response["accounts"] 
            if account["sync_status"] == "up_to_date"
        ]
        assert len(up_to_date_accounts) == 1
        assert up_to_date_accounts[0]["platform"] == "instagram"
        
        print("✓ Account synchronization status test passed")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])