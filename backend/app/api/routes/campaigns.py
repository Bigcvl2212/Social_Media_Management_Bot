"""
API routes for campaign management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.integration import (
    Campaign,
    CampaignCreate,
    CampaignUpdate,
)
from app.services.integration_service import campaign_service

router = APIRouter()


@router.post("/", response_model=Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign"""
    return await campaign_service.create_campaign(
        db=db,
        campaign_data=campaign_data,
        user_id=current_user.id
    )


@router.get("/", response_model=List[Campaign])
async def get_campaigns(
    campaign_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all campaigns for the current user"""
    return await campaign_service.get_user_campaigns(
        db=db,
        user_id=current_user.id,
        campaign_type=campaign_type
    )


@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a campaign"""
    if not current_user.can_edit():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Edit permissions required to send campaigns"
        )
    
    return await campaign_service.send_campaign(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id
    )