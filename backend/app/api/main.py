"""
Main API router combining all endpoints
"""

from fastapi import APIRouter

from app.api.routes import (
    auth, users, social_accounts, content, analytics, upload,
    integrations, campaigns, api_management, zapier, admin
)

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(social_accounts.router, prefix="/social-accounts", tags=["social-accounts"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])

# New integration routes
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(api_management.router, prefix="/api", tags=["api-management"])
api_router.include_router(zapier.router, prefix="/zapier", tags=["zapier"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])