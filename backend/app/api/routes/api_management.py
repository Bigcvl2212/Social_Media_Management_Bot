"""
API routes for public API key management and public endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.integration import APIKey as APIKeyModel
from app.schemas.integration import (
    APIKey,
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyWithSecret,
)
from app.services.integration_service import api_key_service

router = APIRouter()
security = HTTPBearer()


# API Key Management Routes (Protected)
@router.post("/keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to create API keys"
        )
    
    return await api_key_service.create_api_key(
        db=db,
        api_key_data=api_key_data,
        user_id=current_user.id
    )


@router.get("/keys", response_model=List[APIKey])
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all API keys for the current user"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to view API keys"
        )
    
    return await api_key_service.get_user_api_keys(
        db=db,
        user_id=current_user.id
    )


# Public API Routes (API Key Authentication)
async def get_current_api_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from API key"""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    api_key = await api_key_service.validate_api_key(
        db=db,
        key_value=credentials.credentials
    )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key.user


@router.get("/public/user")
async def get_api_user_info(
    current_user: User = Depends(get_current_api_user)
):
    """Get current user information via API key"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }


@router.get("/public/social-accounts")
async def get_api_social_accounts(
    current_user: User = Depends(get_current_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's social accounts via API"""
    from app.services.user_service import user_service
    
    accounts = await user_service.get_user_social_accounts(
        db=db,
        user_id=current_user.id
    )
    
    return [
        {
            "id": account.id,
            "platform": account.platform,
            "username": account.username,
            "is_active": account.is_active
        }
        for account in accounts
    ]


@router.post("/public/content")
async def create_api_content(
    content_data: dict,
    current_user: User = Depends(get_current_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Create content via API"""
    from app.services.content_service import content_service
    from app.schemas.content import ContentCreate
    
    # Convert dict to ContentCreate schema
    try:
        content_create = ContentCreate(**content_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid content data: {str(e)}"
        )
    
    return await content_service.create_content(
        db=db,
        content_data=content_create,
        user_id=current_user.id
    )


@router.get("/public/analytics")
async def get_api_analytics(
    platform: str = None,
    days: int = 30,
    current_user: User = Depends(get_current_api_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics data via API"""
    # Mock analytics response
    return {
        "user_id": current_user.id,
        "platform": platform,
        "period_days": days,
        "total_posts": 45,
        "total_engagement": 1250,
        "followers_gained": 78,
        "top_performing_post": {
            "id": 123,
            "content": "Sample post content",
            "engagement": 245
        }
    }