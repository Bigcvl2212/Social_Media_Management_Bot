"""
Credential Resolver
Looks up a user's Facebook (or other platform) credentials from the
social_accounts table.  Falls back to .env values when no DB row exists
(so your Fond du Lac account keeps working without an OAuth flow).

Usage in any service:
    creds = await get_facebook_credentials(user_id=42, db=session)
    fb = FacebookService(page_id=creds.page_id, page_token=creds.page_token)
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decrypt_token
from app.models.social_account import SocialAccount, SocialPlatform, AccountStatus

import logging
logger = logging.getLogger(__name__)


@dataclass
class FacebookCredentials:
    page_id: str
    page_token: str
    app_id: str
    app_secret: str
    ad_account_id: str  # for Marketing API


async def get_facebook_credentials(
    db: AsyncSession,
    user_id: Optional[int] = None,
) -> FacebookCredentials:
    """Resolve Facebook credentials for a specific user.

    Priority:
    1. If user_id is given, look up their SocialAccount row → decrypt token.
    2. Fall back to .env values (covers the owner's hardcoded token).
    """
    if user_id is not None:
        q = select(SocialAccount).where(
            and_(
                SocialAccount.user_id == user_id,
                SocialAccount.platform == SocialPlatform.FACEBOOK,
                SocialAccount.status == AccountStatus.CONNECTED,
            )
        )
        result = await db.execute(q)
        account = result.scalar_one_or_none()

        if account and account.access_token:
            page_id = account.platform_user_id or ""
            try:
                page_token = decrypt_token(account.access_token)
            except Exception:
                # Token might be stored unencrypted from an older version
                page_token = account.access_token
                logger.warning("Could not decrypt token for user %s — using raw value", user_id)

            ad_account_id = ""
            if account.platform_data and isinstance(account.platform_data, dict):
                ad_account_id = account.platform_data.get("ad_account_id", "")

            return FacebookCredentials(
                page_id=page_id,
                page_token=page_token,
                app_id=settings.FACEBOOK_APP_ID or "",
                app_secret=settings.FACEBOOK_APP_SECRET or "",
                ad_account_id=ad_account_id or (settings.FACEBOOK_AD_ACCOUNT_ID or ""),
            )

    # Fallback: .env values (owner's hardcoded credentials)
    return FacebookCredentials(
        page_id=settings.FACEBOOK_PAGE_ID or "",
        page_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN or "",
        app_id=settings.FACEBOOK_APP_ID or "",
        app_secret=settings.FACEBOOK_APP_SECRET or "",
        ad_account_id=settings.FACEBOOK_AD_ACCOUNT_ID or "",
    )
