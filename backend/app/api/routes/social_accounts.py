"""
Social accounts management routes with OAuth integration
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
import secrets
import urllib.parse

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.social_account import SocialAccount, SocialPlatform, AccountStatus

router = APIRouter()

# Pydantic models
class SocialAccountResponse(BaseModel):
    id: int
    platform: SocialPlatform
    username: str
    display_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    status: AccountStatus
    auto_post: bool
    auto_engage: bool
    created_at: str
    last_sync: Optional[str] = None
    permissions: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class SocialAccountUpdate(BaseModel):
    auto_post: Optional[bool] = None
    auto_engage: Optional[bool] = None

class OAuthStartResponse(BaseModel):
    auth_url: str
    state: str

# Platform configurations (in production, these would be in environment variables)
PLATFORM_CONFIGS = {
    SocialPlatform.INSTAGRAM: {
        "name": "Instagram",
        "auth_url": "https://api.instagram.com/oauth/authorize",
        "client_id": "your-instagram-app-id",
        "scope": "user_profile,user_media",
        "redirect_uri": "http://localhost:3000/auth/callback/instagram"
    },
    SocialPlatform.TWITTER: {
        "name": "Twitter/X",
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "client_id": "your-twitter-client-id",
        "scope": "tweet.read tweet.write users.read",
        "redirect_uri": "http://localhost:3000/auth/callback/twitter"
    },
    SocialPlatform.FACEBOOK: {
        "name": "Facebook",
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "client_id": "your-facebook-app-id",
        "scope": "pages_manage_posts,pages_read_engagement",
        "redirect_uri": "http://localhost:3000/auth/callback/facebook"
    },
    SocialPlatform.YOUTUBE: {
        "name": "YouTube",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "client_id": "your-google-client-id",
        "scope": "https://www.googleapis.com/auth/youtube.upload",
        "redirect_uri": "http://localhost:3000/auth/callback/youtube"
    },
    SocialPlatform.LINKEDIN: {
        "name": "LinkedIn",
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "client_id": "your-linkedin-client-id",
        "scope": "w_member_social",
        "redirect_uri": "http://localhost:3000/auth/callback/linkedin"
    },
    SocialPlatform.TIKTOK: {
        "name": "TikTok",
        "auth_url": "https://www.tiktok.com/auth/authorize",
        "client_id": "your-tiktok-client-key",
        "scope": "user.info.basic,video.upload",
        "redirect_uri": "http://localhost:3000/auth/callback/tiktok"
    }
}

@router.get("/", response_model=List[SocialAccountResponse])
async def list_social_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's connected social media accounts"""
    try:
        query = select(SocialAccount).where(SocialAccount.user_id == current_user.id)
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        return [SocialAccountResponse.model_validate(account) for account in accounts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch social accounts: {str(e)}")

@router.get("/platforms")
async def get_available_platforms():
    """Get list of available social media platforms"""
    platforms = []
    for platform, config in PLATFORM_CONFIGS.items():
        platforms.append({
            "platform": platform.value,
            "name": config["name"],
            "supported": True
        })
    return {"platforms": platforms}

@router.post("/connect/{platform}/start", response_model=OAuthStartResponse)
async def start_oauth_flow(
    platform: SocialPlatform,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start OAuth flow for connecting a social media account"""
    try:
        if platform not in PLATFORM_CONFIGS:
            raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
        config = PLATFORM_CONFIGS[platform]
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Store state in session or database (simplified for demo)
        # In production, you'd store this securely
        
        # Build OAuth URL
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "response_type": "code",
            "state": state
        }
        
        auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"
        
        return OAuthStartResponse(auth_url=auth_url, state=state)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start OAuth flow: {str(e)}")

@router.post("/connect/{platform}/callback")
async def oauth_callback(
    platform: SocialPlatform,
    code: str,
    state: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback and save account credentials"""
    try:
        # In a real implementation, you would:
        # 1. Verify the state parameter
        # 2. Exchange the code for access tokens
        # 3. Fetch user info from the platform API
        # 4. Store the encrypted tokens in the database
        
        # For demo purposes, create a mock account
        mock_account = SocialAccount(
            user_id=current_user.id,
            platform=platform,
            platform_user_id=f"mock_{platform.value}_{current_user.id}",
            username=f"@{current_user.username}_{platform.value}",
            display_name=f"{current_user.first_name or current_user.username} on {platform.value.title()}",
            profile_image_url=None,
            status=AccountStatus.CONNECTED,
            access_token="mock_access_token",  # Would be encrypted in production
            permissions=["read", "write", "manage"]
        )
        
        # Check if account already exists
        existing_query = select(SocialAccount).where(
            and_(
                SocialAccount.user_id == current_user.id,
                SocialAccount.platform == platform
            )
        )
        existing_result = await db.execute(existing_query)
        existing_account = existing_result.scalar_one_or_none()
        
        if existing_account:
            # Update existing account
            existing_account.status = AccountStatus.CONNECTED
            existing_account.access_token = mock_account.access_token
            existing_account.username = mock_account.username
            existing_account.display_name = mock_account.display_name
            account = existing_account
        else:
            # Create new account
            db.add(mock_account)
            account = mock_account
        
        await db.commit()
        await db.refresh(account)
        
        return {"message": f"Successfully connected {platform.value} account", "account_id": account.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@router.delete("/{account_id}")
async def disconnect_social_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect a social media account"""
    try:
        # Get account and verify ownership
        query = select(SocialAccount).where(
            and_(SocialAccount.id == account_id, SocialAccount.user_id == current_user.id)
        )
        result = await db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")
        
        # Update status to disconnected (keep for historical data)
        account.status = AccountStatus.DISCONNECTED
        account.access_token = None
        account.refresh_token = None
        
        await db.commit()
        
        return {"message": f"Successfully disconnected {account.platform.value} account"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect account: {str(e)}")

@router.put("/{account_id}", response_model=SocialAccountResponse)
async def update_social_account(
    account_id: int,
    update_data: SocialAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update social account settings"""
    try:
        # Get account and verify ownership
        query = select(SocialAccount).where(
            and_(SocialAccount.id == account_id, SocialAccount.user_id == current_user.id)
        )
        result = await db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")
        
        # Update account settings
        update_data_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_data_dict.items():
            setattr(account, field, value)
        
        await db.commit()
        await db.refresh(account)
        
        return SocialAccountResponse.model_validate(account)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update account: {str(e)}")

@router.post("/{account_id}/sync")
async def sync_social_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync account data with the platform"""
    try:
        # Get account and verify ownership
        query = select(SocialAccount).where(
            and_(SocialAccount.id == account_id, SocialAccount.user_id == current_user.id)
        )
        result = await db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")
        
        # In a real implementation, this would:
        # 1. Refresh access tokens if needed
        # 2. Fetch latest profile information
        # 3. Update account data
        
        # For demo, just update the last_sync timestamp
        from datetime import datetime
        account.last_sync = datetime.utcnow()
        
        await db.commit()
        
        return {"message": f"Successfully synced {account.platform.value} account"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync account: {str(e)}")

@router.get("/stats")
async def get_social_accounts_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social accounts statistics"""
    try:
        query = select(SocialAccount).where(SocialAccount.user_id == current_user.id)
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        total_accounts = len(accounts)
        connected_accounts = len([acc for acc in accounts if acc.status == AccountStatus.CONNECTED])
        platforms_connected = list(set([acc.platform for acc in accounts if acc.status == AccountStatus.CONNECTED]))
        
        return {
            "total_accounts": total_accounts,
            "connected_accounts": connected_accounts,
            "disconnected_accounts": total_accounts - connected_accounts,
            "platforms_connected": [platform.value for platform in platforms_connected],
            "connection_rate": (connected_accounts / max(1, total_accounts)) * 100
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch account stats: {str(e)}")