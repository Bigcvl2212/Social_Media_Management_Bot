"""
Social accounts management routes with OAuth integration
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
import secrets
import urllib.parse
from datetime import datetime, timezone

import httpx

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_user
from app.core.security import encrypt_token
from app.models.user import User
from app.models.social_account import SocialAccount, SocialPlatform, AccountStatus

router = APIRouter()

# ── Pydantic models ──────────────────────────────────────

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

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

class PageSelectRequest(BaseModel):
    account_id: int
    page_id: str

class PageOption(BaseModel):
    page_id: str
    name: str
    category: str
    access_token_preview: str  # last-4 chars only

# ── In-memory state store (production: Redis or signed JWT) ──
_oauth_states: Dict[str, int] = {}

GRAPH_API = "https://graph.facebook.com/v21.0"

# ── Platform configs ─────────────────────────────────────

PLATFORM_CONFIGS = {
    SocialPlatform.FACEBOOK: {
        "name": "Facebook",
        "auth_url": "https://www.facebook.com/v21.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v21.0/oauth/access_token",
        "scope": (
            "pages_show_list,pages_manage_posts,pages_manage_metadata,"
            "pages_manage_engagement,pages_read_engagement,"
            "pages_read_user_content,read_insights,business_management"
        ),
        "redirect_uri": f"{settings.ALLOWED_HOSTS.split(',')[0].strip() if settings.ALLOWED_HOSTS != '*' else 'http://localhost:3000'}/auth/callback/facebook",
    },
    SocialPlatform.INSTAGRAM: {
        "name": "Instagram",
        "auth_url": "https://api.instagram.com/oauth/authorize",
        "scope": "user_profile,user_media",
        "redirect_uri": "http://localhost:3000/auth/callback/instagram",
    },
    SocialPlatform.TWITTER: {
        "name": "Twitter/X",
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "scope": "tweet.read tweet.write users.read",
        "redirect_uri": "http://localhost:3000/auth/callback/twitter",
    },
    SocialPlatform.YOUTUBE: {
        "name": "YouTube",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "scope": "https://www.googleapis.com/auth/youtube.upload",
        "redirect_uri": "http://localhost:3000/auth/callback/youtube",
    },
    SocialPlatform.LINKEDIN: {
        "name": "LinkedIn",
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "scope": "w_member_social",
        "redirect_uri": "http://localhost:3000/auth/callback/linkedin",
    },
    SocialPlatform.TIKTOK: {
        "name": "TikTok",
        "auth_url": "https://www.tiktok.com/auth/authorize",
        "scope": "user.info.basic,video.upload",
        "redirect_uri": "http://localhost:3000/auth/callback/tiktok",
    },
}


# ══════════════════════════════════════════════════════════
# LIST / PLATFORMS / STATS  (unchanged)
# ══════════════════════════════════════════════════════════

@router.get("/", response_model=List[SocialAccountResponse])
async def list_social_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SocialAccount).where(SocialAccount.user_id == current_user.id)
    result = await db.execute(query)
    accounts = result.scalars().all()
    return [SocialAccountResponse.model_validate(account) for account in accounts]


@router.get("/platforms")
async def get_available_platforms():
    return {
        "platforms": [
            {"platform": p.value, "name": c["name"], "supported": True}
            for p, c in PLATFORM_CONFIGS.items()
        ]
    }


# ══════════════════════════════════════════════════════════
# OAUTH START
# ══════════════════════════════════════════════════════════

@router.post("/connect/{platform}/start", response_model=OAuthStartResponse)
async def start_oauth_flow(
    platform: SocialPlatform,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if platform not in PLATFORM_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")

    config = PLATFORM_CONFIGS[platform]
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = current_user.id  # bind state → user

    params = {
        "client_id": settings.FACEBOOK_APP_ID or "",
        "redirect_uri": config["redirect_uri"],
        "scope": config["scope"],
        "response_type": "code",
        "state": state,
    }
    auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"
    return OAuthStartResponse(auth_url=auth_url, state=state)


# ══════════════════════════════════════════════════════════
# OAUTH CALLBACK — REAL TOKEN EXCHANGE
# ══════════════════════════════════════════════════════════

@router.post("/connect/{platform}/callback")
async def oauth_callback(
    platform: SocialPlatform,
    body: OAuthCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exchange authorization code for real access token, fetch user pages."""

    # 1. Verify state
    expected_user = _oauth_states.pop(body.state, None)
    if expected_user is None or expected_user != current_user.id:
        raise HTTPException(status_code=403, detail="Invalid or expired OAuth state")

    if platform != SocialPlatform.FACEBOOK:
        raise HTTPException(status_code=501, detail=f"OAuth callback for {platform.value} not yet implemented")

    config = PLATFORM_CONFIGS[SocialPlatform.FACEBOOK]

    # 2. Exchange code → short-lived user token
    async with httpx.AsyncClient(timeout=30) as client:
        token_resp = await client.get(
            config["token_url"],
            params={
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "redirect_uri": config["redirect_uri"],
                "code": body.code,
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Facebook token exchange failed: {token_resp.text}")
        token_data = token_resp.json()
        short_token = token_data["access_token"]

        # 3. Exchange short-lived → long-lived user token (60 days)
        ll_resp = await client.get(
            f"{GRAPH_API}/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": settings.FACEBOOK_APP_ID,
                "client_secret": settings.FACEBOOK_APP_SECRET,
                "fb_exchange_token": short_token,
            },
        )
        if ll_resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Long-lived token exchange failed: {ll_resp.text}")
        ll_data = ll_resp.json()
        long_lived_token = ll_data["access_token"]
        expires_in = ll_data.get("expires_in", 5184000)  # default 60 days

        # 4. Get user profile
        me_resp = await client.get(
            f"{GRAPH_API}/me",
            params={"fields": "id,name,email", "access_token": long_lived_token},
        )
        me_data = me_resp.json() if me_resp.status_code == 200 else {}

        # 5. Get user's Pages (they'll pick one in the next step)
        pages_resp = await client.get(
            f"{GRAPH_API}/me/accounts",
            params={
                "fields": "id,name,category,access_token",
                "access_token": long_lived_token,
            },
        )
        if pages_resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to fetch pages: {pages_resp.text}")
        pages_data = pages_resp.json().get("data", [])

    # 6. Upsert SocialAccount with the USER-level long-lived token
    #    (page token stored after page selection)
    from datetime import timedelta
    token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    existing_q = select(SocialAccount).where(
        and_(
            SocialAccount.user_id == current_user.id,
            SocialAccount.platform == SocialPlatform.FACEBOOK,
        )
    )
    result = await db.execute(existing_q)
    account = result.scalar_one_or_none()

    fb_user_id = me_data.get("id", "unknown")
    fb_name = me_data.get("name", "Facebook User")

    if account:
        account.status = AccountStatus.CONNECTED
        account.access_token = encrypt_token(long_lived_token)
        account.platform_user_id = fb_user_id
        account.display_name = fb_name
        account.token_expires_at = token_expiry
        account.platform_data = {"pages": [
            {"id": p["id"], "name": p["name"], "category": p.get("category", "")}
            for p in pages_data
        ]}
    else:
        account = SocialAccount(
            user_id=current_user.id,
            platform=SocialPlatform.FACEBOOK,
            platform_user_id=fb_user_id,
            username=fb_name,
            display_name=fb_name,
            status=AccountStatus.CONNECTED,
            access_token=encrypt_token(long_lived_token),
            token_expires_at=token_expiry,
            permissions=config["scope"].split(","),
            platform_data={"pages": [
                {"id": p["id"], "name": p["name"], "category": p.get("category", "")}
                for p in pages_data
            ]},
        )
        db.add(account)

    await db.commit()
    await db.refresh(account)

    # 7. Return pages for the user to choose from
    return {
        "account_id": account.id,
        "facebook_name": fb_name,
        "pages": [
            PageOption(
                page_id=p["id"],
                name=p["name"],
                category=p.get("category", ""),
                access_token_preview=f"...{p['access_token'][-4:]}",
            ).model_dump()
            for p in pages_data
        ],
        "message": "Select which Facebook Page to manage.",
    }


# ══════════════════════════════════════════════════════════
# PAGE SELECTION — user picks which Page to manage
# ══════════════════════════════════════════════════════════

@router.post("/connect/facebook/select-page")
async def select_facebook_page(
    body: PageSelectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """After OAuth, the gym owner picks which Page this account manages."""

    # 1. Load the account
    q = select(SocialAccount).where(
        and_(
            SocialAccount.id == body.account_id,
            SocialAccount.user_id == current_user.id,
            SocialAccount.platform == SocialPlatform.FACEBOOK,
        )
    )
    result = await db.execute(q)
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Facebook account not found")

    # 2. Fetch a never-expiring Page Access Token from the long-lived user token
    from app.core.security import decrypt_token
    user_token = decrypt_token(account.access_token)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{GRAPH_API}/{body.page_id}",
            params={
                "fields": "id,name,category,access_token",
                "access_token": user_token,
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to get page token: {resp.text}")
        page_data = resp.json()

    permanent_page_token = page_data.get("access_token", "")
    if not permanent_page_token:
        raise HTTPException(status_code=502, detail="Facebook did not return a page access token")

    # 3. Store the encrypted page token + page_id in the account
    account.access_token = encrypt_token(permanent_page_token)
    account.platform_user_id = body.page_id
    account.username = page_data.get("name", "")
    account.display_name = page_data.get("name", "")
    account.token_expires_at = None  # permanent token never expires
    account.platform_data = {
        **(account.platform_data or {}),
        "selected_page_id": body.page_id,
        "selected_page_name": page_data.get("name", ""),
    }

    await db.commit()
    await db.refresh(account)

    return {
        "message": f"Now managing: {page_data.get('name', body.page_id)}",
        "page_id": body.page_id,
        "page_name": page_data.get("name", ""),
        "account_id": account.id,
    }

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