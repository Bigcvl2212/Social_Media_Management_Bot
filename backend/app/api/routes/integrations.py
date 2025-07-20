"""
API routes for integrations management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.integration import IntegrationType
from app.schemas.integration import (
    Integration,
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationWithConfig,
)
from app.services.integration_service import integration_service

router = APIRouter()


@router.post("/", response_model=Integration, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration"""
    return await integration_service.create_integration(
        db=db,
        integration_data=integration_data,
        user_id=current_user.id
    )


@router.get("/", response_model=List[Integration])
async def get_integrations(
    integration_type: Optional[IntegrationType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all integrations for the current user"""
    return await integration_service.get_user_integrations(
        db=db,
        user_id=current_user.id,
        integration_type=integration_type
    )


@router.get("/{integration_id}", response_model=Integration)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific integration"""
    integration = await integration_service.get_integration(
        db=db,
        integration_id=integration_id,
        user_id=current_user.id
    )
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return integration


@router.get("/{integration_id}/config", response_model=IntegrationWithConfig)
async def get_integration_config(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get integration with configuration data (admin only)"""
    if not current_user.can_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    integration = await integration_service.get_integration(
        db=db,
        integration_id=integration_id,
        user_id=current_user.id
    )
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return integration


@router.put("/{integration_id}", response_model=Integration)
async def update_integration(
    integration_id: int,
    integration_data: IntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an integration"""
    integration = await integration_service.update_integration(
        db=db,
        integration_id=integration_id,
        integration_data=integration_data,
        user_id=current_user.id
    )
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an integration"""
    deleted = await integration_service.delete_integration(
        db=db,
        integration_id=integration_id,
        user_id=current_user.id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )


@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test an integration connection"""
    return await integration_service.test_integration(
        db=db,
        integration_id=integration_id,
        user_id=current_user.id
    )